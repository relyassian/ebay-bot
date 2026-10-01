"""Price raises waiting for Rafael's OK (launch mode: raises need approval).

The daily sync proposes them; each gets a short code (R1, R2, ...) shown on Telegram.
Rafael replies APPROVE R1 / APPROVE ALL / SKIP R1. Approving revises the price on eBay right away and
puts the size back on sale if the normal rules allow it (>= 2 stores in stock, clears the floor).
"""
from __future__ import annotations

import json

from bot.config import ROOT, load_config

FILE = ROOT / "data" / "raises.json"     # {"next": 3, "pending": {"R1": {...}}}


def _load() -> dict:
    return json.loads(FILE.read_text()) if FILE.exists() else {"next": 1, "pending": {}}


def _save(d: dict) -> None:
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(d, indent=2, sort_keys=True))


def save_proposals(props: list[dict]) -> list[dict]:
    """Replace the pending list with today's proposals, keeping the same code for the same item+size."""
    d = _load()
    by_key = {(v["item_id"], v["size"]): k for k, v in d["pending"].items()}
    pending = {}
    for p in props:
        code = by_key.get((p["item_id"], p["size"]))
        if not code:
            code = f"R{d['next']}"
            d["next"] += 1
        pending[code] = dict(p, code=code)
    d["pending"] = pending
    _save(d)
    return sorted(pending.values(), key=lambda v: int(v["code"][1:]))


def pending() -> dict:
    return _load()["pending"]


def answer(code: str, approve: bool, live: bool) -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import Change, get_item, revise
    from bot.report import short_name
    from bot.sync import decide, load_sources

    d = _load()
    codes = list(d["pending"]) if code.upper() == "ALL" else [code.upper()]
    if not codes or any(c not in d["pending"] for c in codes):
        return [f"No price raise waiting called '{code}'. Send STATUS to see what's waiting."]
    if not approve:
        for c in codes:
            d["pending"].pop(c)
        _save(d)
        return [f"OK, skipped {', '.join(codes)}. Those sizes stay off sale."]
    cfg = load_config()
    live = live and not cfg.get("dry_run", True)
    token, out, sources = access_token(), [], load_sources()
    for c in codes:
        r = d["pending"][c]
        listing = get_item(r["item_id"], token)
        if live:
            revise(listing, [Change(r["item_id"], r["size"], new_price=r["new"])], token,
                   cfg["listing"]["quantity_per_size"])
            listing = get_item(r["item_id"], token)
            auto, _, notes = decide(listing, sources, cfg)
            relist = [a for a in auto if a.size == r["size"] and a.new_available == 1]
            if relist:
                revise(listing, relist, token, cfg["listing"]["quantity_per_size"])
            status = "back on sale" if relist else "still off sale (fewer than 2 stores have it right now)"
            out.append(f"✅ {c}: {short_name(listing.title)} US {r['size']} is now ${r['new']:.2f}, {status}.")
        else:
            out.append(f"(test mode) {c}: would raise {short_name(listing.title)} US {r['size']} to ${r['new']:.2f}.")
            continue
        d["pending"].pop(c)
    _save(d)
    return out
