"""Sale alerts: for every new order, tell Rafael exactly what to buy, where, and the address to paste."""
from __future__ import annotations

from bot.config import ROOT
from bot.report import short_name
from bot.sync import load_sources

SEEN = ROOT / "data" / "seen_orders.txt"


def run() -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_recent_sales

    seen = set(SEEN.read_text().split()) if SEEN.exists() else set()
    sources = load_sources()
    alerts, new_keys = [], []
    for s in get_recent_sales(access_token()):
        key = f"{s.order_id}:{s.item_id}:{s.size}"
        if key in seen:
            continue
        src = sources.get((s.item_id, s.size))
        evtn = any("evtn" in l.lower() for l in s.ship_to)
        name = short_name(s.title, 60)
        if src and src.cost is not None:
            buy = f"1. Buy US {s.size or '-'} at {src.source} for about ${src.cost:.2f}:\n{src.url}"
        else:
            buy = f"1. Buy US {s.size or '-'}: ⚠️ no store on file. Check the stores now."
        ship = "2. Ship it to this address (copy exactly):\n" + "\n".join(s.ship_to)
        warn = ("\n\n⚠️ The line starting with evtn must be address line 2. If the store's form cuts it "
                "short (GOAT does), ship to yourself and forward it." if evtn else "")
        alerts.append(f"💰 SOLD for ${s.price:.2f}: {name}, US {s.size or '-'}\n\n{buy}\n\n{ship}{warn}")
        new_keys.append(key)
    if new_keys:
        SEEN.parent.mkdir(exist_ok=True)
        with SEEN.open("a") as f:
            f.write("\n".join(new_keys) + "\n")
    return alerts
