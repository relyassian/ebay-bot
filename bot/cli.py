"""Command line for M1.

  python -m bot.cli auth-url                 # print eBay consent link (one-time)
  python -m bot.cli auth-code <code>         # swap consent code for a refresh token (one-time)
  python -m bot.cli show <item_id> [...]     # read live sizes, prices, available qty
  python -m bot.cli apply plan.csv           # dry run: print exactly what would change
  python -m bot.cli apply plan.csv --live    # write to eBay (also needs dry_run: false in config.yaml)
  python -m bot.cli alert-test               # send a test alert
  python -m bot.cli sync [--live]            # fix every listing vs data/source_prices.csv, alert Rafael
  python -m bot.cli sales                    # alert Rafael about new orders (what to buy + address)
  python -m bot.cli drafts                   # new candidates → eBay-verified drafts → Telegram for approval
  python -m bot.cli inbox [--live]           # apply Telegram replies (APPROVE/SKIP/PAUSE/RESUME/STATUS), list approved drafts

plan.csv columns: item_id,size,new_price,new_available   (size blank for no-variation items; blank = unchanged)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from bot.config import ROOT, load_config

MAX_DROP = 0.40   # refuse a price cut bigger than 40% in one step unless --force (typo guard)


def read_plan(path: Path) -> dict[str, list]:
    from bot.ebay.trading import Change
    plan: dict[str, list] = defaultdict(list)
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            item = (row.get("item_id") or "").strip()
            if not item:
                continue
            size = (row.get("size") or "").strip() or None
            price = (row.get("new_price") or "").strip()
            avail = (row.get("new_available") or "").strip()
            plan[item].append(Change(item, size,
                                     float(price) if price else None,
                                     int(avail) if avail else None))
    return plan


def check_changes(listing, changes, force: bool) -> list[str]:
    """Return human-readable diff lines; raise on unsafe changes."""
    lines = []
    current = {v.size: v for v in listing.variations} if listing.variations else {None: None}
    for c in changes:
        if listing.variations:
            v = current.get(c.size)
            if v is None:
                raise ValueError(f"{listing.item_id}: size {c.size} not found")
            old_p, old_a = v.price, v.available
        else:
            old_p, old_a = listing.price, (listing.quantity or 0) - (listing.sold or 0)
        if c.new_price is not None:
            if c.new_price <= 0:
                raise ValueError(f"{listing.item_id} {c.size}: price must be > 0")
            if not force and c.new_price < old_p * (1 - MAX_DROP):
                raise ValueError(f"{listing.item_id} {c.size}: ${old_p}→${c.new_price} is a >40% cut; use --force")
        new_p = old_p if c.new_price is None else c.new_price
        new_a = old_a if c.new_available is None else c.new_available
        if (new_p, new_a) != (old_p, old_a):
            lines.append(f"  size {c.size or '-'}: ${old_p:.2f} → ${new_p:.2f} | available {old_a} → {new_a}")
    return lines


def cmd_apply(args) -> int:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_item, revise

    cfg = load_config()
    live = args.live and not cfg.get("dry_run", True)
    if args.live and not live:
        print("config.yaml has dry_run: true → running as DRY RUN.")
    token = access_token()
    log = {"at": datetime.now(timezone.utc).isoformat(), "live": live, "items": {}}
    for item_id, changes in read_plan(Path(args.plan)).items():
        listing = get_item(item_id, token)
        diff = check_changes(listing, changes, args.force)
        print(f"{item_id}  {listing.title}")
        print("\n".join(diff) if diff else "  (no change)")
        log["items"][item_id] = diff
        if diff and live:
            revise(listing, changes, token, cfg["listing"]["quantity_per_size"])
            after = get_item(item_id, token)   # read back to confirm
            print("  ✓ saved; live now:", {v.size: (v.price, v.available) for v in after.variations}
                  or (after.price, (after.quantity or 0) - (after.sold or 0)))
    out = ROOT / "logs"
    out.mkdir(exist_ok=True)
    (out / f"apply_{datetime.now():%Y%m%d_%H%M%S}.json").write_text(json.dumps(log, indent=2))
    print("\nLIVE — changes written to eBay." if live else "\nDRY RUN — nothing was changed on eBay.")
    return 0


def cmd_show(args) -> int:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_item
    token = access_token()
    for item_id in args.item_ids:
        l = get_item(item_id, token)
        print(f"{l.item_id}  {l.title}")
        for v in sorted(l.variations, key=lambda v: float(v.size or 0)):
            print(f"  {v.size:>5}  ${v.price:>8.2f}  available {v.available}  (sold {v.sold})")
        if not l.variations:
            print(f"  ${l.price:.2f}  available {(l.quantity or 0) - (l.sold or 0)}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="bot")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth-url")
    a = sub.add_parser("auth-code"); a.add_argument("code")
    s = sub.add_parser("show"); s.add_argument("item_ids", nargs="+")
    ap = sub.add_parser("apply"); ap.add_argument("plan"); ap.add_argument("--live", action="store_true")
    ap.add_argument("--force", action="store_true")
    sub.add_parser("alert-test")
    sy = sub.add_parser("sync"); sy.add_argument("--live", action="store_true")
    sub.add_parser("sales")
    sub.add_parser("drafts")
    pa = sub.add_parser("ads-on"); pa.add_argument("--live", action="store_true")
    sub.add_parser("demo")
    pl = sub.add_parser("listen"); pl.add_argument("--minutes", type=int, default=25); pl.add_argument("--live", action="store_true")
    sub.add_parser("legacy-plan")
    sub.add_parser("snapshot")
    sub.add_parser("catalog")
    sub.add_parser("dump-shipping")
    pb = sub.add_parser("inbox"); pb.add_argument("--live", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "auth-url":
        from bot.ebay.auth import consent_url
        print(consent_url()); return 0
    if args.cmd == "auth-code":
        from bot.ebay.auth import exchange_code
        body = exchange_code(args.code)
        print("EBAY_REFRESH_TOKEN=" + body["refresh_token"])
        print(f"(valid ~{int(body.get('refresh_token_expires_in', 0)) // 86400} days) — put it in .env and GitHub secrets")
        return 0
    if args.cmd == "show":
        return cmd_show(args)
    if args.cmd == "apply":
        return cmd_apply(args)
    if args.cmd == "ads-on":
        import traceback
        from bot.ads import setup
        from bot.alerts import send as tg_send
        log = ROOT / "data" / "ads_last_run.txt"
        try:
            msgs = setup(args.live)
        except Exception:
            log.write_text(traceback.format_exc()); raise
        log.write_text("\n".join(msgs))
        for m in msgs:
            print(m)
            try:
                tg_send(m)
            except Exception as e:
                log.write_text(log.read_text() + f"\nTELEGRAM SEND FAILED: {e}")
        return 0
    if args.cmd == "demo":
        from bot.demo import run as demo
        demo(); return 0
    if args.cmd == "listen":
        from bot.listen import run as listen
        listen(args.minutes, args.live); return 0
    if args.cmd == "legacy-plan":
        from bot.legacy import make_plan
        print(make_plan()); return 0
    if args.cmd == "snapshot":
        from bot.snapshot import run as snap
        return snap()
    if args.cmd == "dump-shipping":     # read-only: raw shipping/AG settings of the items in requests/dump.txt
        import re as _re
        from bot.ebay.auth import access_token
        from bot.ebay.trading import _call
        import xml.etree.ElementTree as _ET
        tok, out = access_token(), []
        for iid in (ROOT / "requests" / "dump.txt").read_text().split():
            root = _call("GetItem", f"<ItemID>{iid}</ItemID><DetailLevel>ReturnAll</DetailLevel>", tok)
            raw = _ET.tostring(root, encoding="unicode")
            for tag in ("ShippingDetails", "ShippingPackageDetails", "SellerProfiles", "ShipToLocations",
                        "ShippingServiceCostOverrideList", "eBayPlus", "UseRecommendedShippingService", "ShippingTermsInDescription"):
                for m in _re.findall(rf"<(?:\w+:)?{tag}[ >].*?</(?:\w+:)?{tag}>", raw, flags=_re.S):
                    clean = _re.sub(r'<(/?)ns\d+:', lambda mm: '<' + mm.group(1), m)[:3000]
                    out.append(f"== {iid} {tag}\n{clean}")
        (ROOT / "data" / "shipping_dump.txt").write_text("\n".join(out))
        return 0
    if args.cmd == "catalog":
        from bot.catalog import run
        return run()
    if args.cmd == "sync":
        from bot.alerts import send
        from bot.sync import run
        for m in run(args.live):
            print(m)                      # full detail stays in the log (data/sync_log.txt)
        # eBay sale badges (Rafael, Oct 5): keep a markdown sale running on listings with enough margin
        try:
            from bot.markdown import run as markdown_run
            for m in markdown_run(args.live):
                print(m)
        except Exception as e:
            print("markdown error:", e)
            from bot.notices import add
            add("problem", f"Couldn't start the eBay sale: {str(e)[:160]}")
        # Rafael (Oct 5): one short morning update instead of a report per run
        from bot import digest
        if args.live and digest.due():
            from bot.ebay.auth import access_token
            send({"text": digest.build(access_token()), "html": True})
        return 0
    if args.cmd == "sales":
        from bot.alerts import send
        from bot.sales import run
        for a in run():
            print(a); send(a)
        return 0
    if args.cmd == "drafts":
        from bot.alerts import send
        from bot.newlistings import drafts
        for t in drafts():
            print(t); send(t)
        return 0
    if args.cmd == "inbox":
        from bot.newlistings import run_all
        run_all(args.live); return 0
    if args.cmd == "alert-test":
        from bot.alerts import send
        send("✅ eBay bot is connected. Alerts will arrive here."); print("sent"); return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
