"""Sale alerts: for every new order, tell Rafael exactly what to buy, where, and the address to paste."""
from __future__ import annotations

from bot.config import ROOT
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
        buy = (f"Buy: {src.source} ${src.cost:.2f}\n{src.url}" if src and src.cost is not None
               else "Buy: ⚠️ no source on file — check stores now")
        alerts.append(
            f"💰 SOLD: {s.title}\nSize: US {s.size or '-'}   Sale: ${s.price:.2f}\n{buy}\n\n"
            f"Ship to (paste exactly):\n" + "\n".join(s.ship_to)
            + ("\n\n⚠️ Keep the evtn line on address line 2. If the store's form cuts it (GOAT does), "
               "ship to yourself and forward." if evtn else "")
        )
        new_keys.append(key)
    if new_keys:
        SEEN.parent.mkdir(exist_ok=True)
        with SEEN.open("a") as f:
            f.write("\n".join(new_keys) + "\n")
    return alerts
