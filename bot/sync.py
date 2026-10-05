"""Daily sync: compare every live size against the cheapest known source and fix it.

Inputs
- Live listings from eBay (Trading API).
- data/source_prices.csv — one row per item/size with the cheapest current NEW source.
  Written by the source adapters (M2+) or by the daily research task until adapters exist.
  Columns: item_id,size,cost,source,url,overseas,in_stock_sources,checked_at
  (size blank = item without sizes; cost blank = no source found)
- plans/approved/*.csv — changes Rafael approved (e.g. price raises). Applied once, then moved to plans/done/.

Decisions per size (all rules from CLAUDE.md / config.yaml)
- No profitable in-stock source → available 0                         (pre-approved, auto)
- Sold / zeroed size that is profitably sourceable again → available 1 (pre-approved, auto)
- Current price below the floor price for the cheapest source → available 0 now, and a raise is
  PROPOSED to Rafael (raises need approval)
- Price drops only come from approved plans or future pricing logic; never below the floor.
Source data older than `max_source_age_hours`, or no row at all, counts as unknown → a live size is hidden
and a hidden size is not relisted.
"""
from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from bot.config import ROOT, load_config
from bot.ebay.trading import Change, Listing
from bot.profit import (floor_price, is_taxable, item_min_net, landed_cost, net_profit, required_net,
                        store_shipping)

DATA = ROOT / "data" / "source_prices.csv"
ERRORS = ROOT / "data" / "sync_errors.txt"


@dataclass
class Source:
    cost: float | None
    source: str
    url: str
    overseas: bool
    in_stock_sources: int
    checked_at: datetime | None


def load_sources(path: Path = DATA) -> dict[tuple[str, str | None], Source]:
    out = {}
    if not path.exists():
        return out
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            if not r.get("item_id"):
                continue
            ts = r.get("checked_at") or ""
            out[(r["item_id"].strip(), (r.get("size") or "").strip() or None)] = Source(
                cost=float(r["cost"]) if (r.get("cost") or "").strip() else None,
                source=r.get("source", ""), url=r.get("url", ""),
                overseas=(r.get("overseas", "").strip().lower() in ("1", "true", "yes")),
                in_stock_sources=int(r.get("in_stock_sources") or 0),
                checked_at=datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None,
            )
    return out


def decide(listing: Listing, sources: dict, cfg: dict, now: datetime | None = None):
    """Return (auto_changes, proposals, notes). Pure function: easy to test.
    notes: (kind, size, detail) with kind in hidden | relisted | waiting."""
    now = now or datetime.now(timezone.utc)
    max_age = cfg.get("sync", {}).get("max_source_age_hours", 36)
    min_sources = cfg["risk"]["min_sources_per_size"]
    auto, proposals, notes = [], [], []

    rows = ([(v.size, v.price, v.available, v.sold) for v in listing.variations] if listing.variations
            else [(None, listing.price, (listing.quantity or 0) - (listing.sold or 0), listing.sold or 0)])

    for size, price, available, sold in rows:
        src = sources.get((listing.item_id, size))
        fresh = bool(src and src.checked_at and (now - src.checked_at).total_seconds() <= max_age * 3600)
        if not fresh or src.cost is None:
            # No current, in-stock source (none found, no data, or data too old) → never leave it on sale:
            # a sale there could only end in a cancellation. Hidden sizes stay hidden until fresh data says so.
            if available > 0:
                auto.append(Change(listing.item_id, size, new_available=0))
                notes.append(("hidden", size, "" if (fresh and src is not None) else "no current price data"))
            continue
        landed = landed_cost(src.cost, cfg, overseas=src.overseas, taxable=is_taxable(cfg, listing.item_id),
                             shipping=store_shipping(cfg, src.source))
        base = item_min_net(cfg, listing.item_id)
        need = floor_price(landed, cfg, base=base)
        net_now = net_profit(price, landed, cfg)
        enough_sources = (src.in_stock_sources >= min_sources or cfg.get("sync", {}).get("allow_single_source", False)
                          or (src.in_stock_sources >= 1
                              and listing.item_id in set(map(str, cfg.get("sync", {}).get("single_source_items", [])))))

        if net_now < required_net(price, cfg, base):
            # Rafael (Oct 5): price changes don't need his OK. A raise of up to `auto_raise_pct` is applied
            # automatically (and the size stays/goes on sale); a bigger one wouldn't sell, so the size just
            # stays off sale until the store gets cheaper again.
            if need <= price * (1 + cfg.get("sync", {}).get("auto_raise_pct", 0.15)):
                auto.append(Change(listing.item_id, size, new_price=need,
                                   new_available=1 if enough_sources else 0))
                notes.append(("raised", size, need))
            elif available > 0:
                auto.append(Change(listing.item_id, size, new_available=0))
                notes.append(("hidden", size, f"loses money at ${price:.0f} (cheapest: {src.source} ${src.cost:.0f})"))
        elif available == 0 and enough_sources:
            auto.append(Change(listing.item_id, size, new_available=1))
            notes.append(("relisted", size, net_now))
        elif available == 0 and not enough_sources:
            notes.append(("waiting", size, f"only {src.in_stock_sources} source"))
    return auto, proposals, notes


def decays(listing: Listing, sources: dict, cfg: dict, log: dict, auto: list, now: datetime | None = None):
    """Pre-approved 3% price drops for sizes that are on sale, still profitable, and unsold at the same price
    for `pricing.decay_after_days`. Sizes already being changed this run are left alone."""
    from bot.pricing import decay_price, due, track
    now = now or datetime.now(timezone.utc)
    max_age = cfg.get("sync", {}).get("max_source_age_hours", 36)
    touched = {c.size for c in auto}
    out = []
    rows = ([(v.size, v.price, v.available) for v in listing.variations] if listing.variations
            else [(None, listing.price, (listing.quantity or 0) - (listing.sold or 0))])
    for size, price, available in rows:
        row = track(log, listing.item_id, size, price, now)
        if available <= 0 or size in touched or not due(row, now, cfg):
            continue
        src = sources.get((listing.item_id, size))
        if not (src and src.cost is not None and src.checked_at
                and (now - src.checked_at).total_seconds() <= max_age * 3600):
            continue
        new = decay_price(price, src.cost, src.overseas, cfg, taxable=is_taxable(cfg, listing.item_id),
                          shipping=store_shipping(cfg, src.source), base=item_min_net(cfg, listing.item_id))
        if new is not None:
            out.append(Change(listing.item_id, size, new_price=new))
    return out


def load_approved_plans(ext: str = "csv") -> list[Path]:
    d = ROOT / "plans" / "approved"
    return sorted(d.glob(f"*.{ext}")) if d.exists() else []


def apply_raw_plan(path: Path, token: str, live: bool) -> list[str]:
    """JSON plan: [{item_id, item_xml, ...}] → ReviseFixedPriceItem each (titles, descriptions, specifics, offers).
    If eBay refuses a title change (e.g. listing has sales), retry once without the title."""
    import json
    import re
    from bot.ebay.trading import _call
    from bot.report import short_name
    out = []
    for row in json.loads(path.read_text()):
        name = short_name(row.get("new_title") or row.get("old_title") or row["item_id"])
        if not live:
            out.append(f"(test mode) would update {name}")
            continue
        try:
            _call("ReviseFixedPriceItem", row["item_xml"], token)
            out.append(f"{name}: updated")
        except Exception as e:
            if "<Title>" in row["item_xml"] and "itle" in str(e):
                try:
                    _call("ReviseFixedPriceItem", re.sub(r"<Title>.*?</Title>", "", row["item_xml"]), token)
                    out.append(f"{name}: updated (eBay kept the old title)")
                    continue
                except Exception as e2:
                    e = e2
            out.append(f"⚠️ {name}: eBay refused ({str(e)[:160]})")
    return out


def archive_plan(p: Path) -> None:
    done = ROOT / "plans" / "done"
    done.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), done / p.name)


def run(live: bool) -> list:
    from bot.cli import read_plan
    from bot.ebay.auth import access_token
    from bot.ebay.trading import build_revise_xml, get_active_item_ids, get_item, revise
    from bot.listing import PAUSE_FLAG
    from bot.raises import save_proposals
    from bot.report import short_name, sync_report

    cfg = load_config()
    live = live and not cfg.get("dry_run", True)
    if PAUSE_FLAG.exists():
        return ["⏸ Bot is paused, so no listing changes were made. Send RESUME to turn it back on."]
    token = access_token()
    sources = load_sources()
    ignore = set(map(str, cfg.get("sync", {}).get("ignore_items", [])))
    from bot.pricing import load_log, save_log
    applied, groups, props, checked, errors = [], {}, [], 0, []
    price_log = load_log()

    # 1) approved plans first (e.g. price raises Rafael said yes to)
    for plan in load_approved_plans():
        for item_id, changes in read_plan(plan).items():
            listing = get_item(item_id, token)
            build_revise_xml(listing, changes)          # validates every size exists, even in dry run
            if live:
                revise(listing, changes, token, cfg["listing"]["quantity_per_size"])
            applied.append(f"{short_name(listing.title)}: {len(changes)} size(s) updated")
        if live:
            archive_plan(plan)
    for plan in load_approved_plans("json"):
        applied += apply_raw_plan(plan, token, live)
        if live:
            archive_plan(plan)

    # 2) sync every active listing
    for item_id in get_active_item_ids(token):
        if item_id in ignore:
            continue
        try:
            listing = get_item(item_id, token)
        except Exception as e:
            errors.append(f"{item_id}: couldn't read it from eBay ({str(e)[:200]})")
            continue
        words = [w.lower() for w in cfg.get("sync", {}).get("ignore_title_words", [])]
        if any(w in listing.title.lower() for w in words):
            continue
        checked += 1
        auto, proposals, notes = decide(listing, sources, cfg)
        drops = decays(listing, sources, cfg, price_log, auto) if cfg.get("pricing", {}).get("decay", True) else []
        auto += drops
        notes += [("lowered", c.size, c.new_price) for c in drops]
        if auto and live:
            try:
                revise(listing, auto, token, cfg["listing"]["quantity_per_size"])
            except Exception as e:      # one listing failing must not stop the others
                errors.append(f"{short_name(listing.title)} ({item_id}): eBay refused the change ({str(e)[:300]})")
                continue
        if live:
            from bot.pricing import track
            for c in drops:
                row = track(price_log, item_id, c.size, c.new_price, datetime.now(timezone.utc))
                row["drops"] = row.get("drops", 0) + 1
        name, total = short_name(listing.title), max(len(listing.variations), 1)
        for kind in ("relisted", "hidden", "waiting", "lowered", "raised"):
            rows = [n for n in notes if n[0] == kind]
            if not rows:
                continue
            extra = ""
            if kind in ("lowered", "raised"):
                extra = "now from $" + f"{min(r[2] for r in rows):,.2f}"
            if kind == "relisted":
                nets = [r[2] for r in rows]
                extra = (f"you'd make ${min(nets):.0f}" if min(nets) == max(nets)
                         else f"you'd make ${min(nets):.0f}–${max(nets):.0f}")
            groups.setdefault(kind, []).append((name, [r[1] for r in rows], total, extra, listing.photo, listing.url))
        for p in proposals:
            props.append({"item_id": item_id, "size": p[1], "old": p[2], "new": p[3], "name": name,
                          "store": p[5], "cost": p[6], "photo": listing.photo, "url": listing.url})

    if live:
        save_log(price_log)
    raises = save_proposals(props)
    msgs = sync_report(live, applied, groups, raises, checked)
    if live:
        from bot.digest import log_changes
        log_changes({k: sum(len(r[1]) for r in v) for k, v in groups.items()})
        if errors:
            from bot.notices import add
            for e in errors:
                add("problem", e[:200])
    ERRORS.write_text("\n".join(errors) + ("\n" if errors else ""))
    if errors:
        print("SYNC ERRORS:\n" + "\n".join(errors))
        msgs[0] += "\n\n⚠️ Couldn't update " + str(len(errors)) + " listing(s); I'm looking into it:\n" + "\n".join(
            "• " + e[:160] for e in errors)
    newest = max((x.checked_at for x in sources.values() if x.checked_at), default=None)
    age_h = (datetime.now(timezone.utc) - newest).total_seconds() / 3600 if newest else None
    if age_h is None or age_h > 20:
        msgs[0] += ("\n\n⚠️ Store prices haven't been refreshed yet today. Either the morning research is still running "
                    "(you'll get an updated report when it finishes) or it couldn't reach your Mac. Listings stay as "
                    "they were, a backup run tries again at 10am, and nothing is relisted until stock is confirmed.")
    return msgs
