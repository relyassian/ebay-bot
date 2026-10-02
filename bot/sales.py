"""Sale alerts: for every new order, tell Rafael exactly what to buy, where, and the address to paste."""
from __future__ import annotations

from bot.config import ROOT, load_config
from bot.report import short_name
from bot.sync import load_sources

SEEN = ROOT / "data" / "seen_orders.txt"


def run() -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_recent_sales

    seen = set(SEEN.read_text().split()) if SEEN.exists() else set()
    sources = load_sources()
    alerts, new_keys = [], []
    from bot.ebay.trading import get_item
    token = access_token()
    for s in get_recent_sales(token):
        key = f"{s.order_id}:{s.item_id}:{s.size}"
        if key in seen:
            continue
        src = sources.get((s.item_id, s.size))
        evtn = any("evtn" in l.lower() for l in s.ship_to)
        name = short_name(s.title, 60)
        cfg_sync = load_config().get("sync", {})
        own = (s.item_id in set(map(str, cfg_sync.get("ignore_items", [])))
               or any(w.lower() in s.title.lower() for w in cfg_sync.get("ignore_title_words", [])))
        if own:
            buy = "1. This is your own item: just pack it up."
        elif src and src.cost is not None:
            from bot.promos import lines_for
            buy = (f"1. Buy US {s.size or '-'} at {src.source} for about ${src.cost:.2f}:\n{src.url}\n"
                   + "\n".join(lines_for(src.source))
                   + "\nTip: buy through Rakuten for cashback if the store is on it.")
        else:
            buy = f"1. Buy US {s.size or '-'}: ⚠️ no store on file. Check the stores now."
        ship = "2. Ship it to this address (copy exactly):\n" + "\n".join(s.ship_to)
        warn = ("\n\n⚠️ Put the line starting with evtn on address line 2. Ship direct from every store, "
                "GOAT included, even if its form shortens that line." if evtn else "")
        try:
            photo = get_item(s.item_id, token).photo
        except Exception:
            photo = None
        text = (f"💰 SOLD for ${s.price:.2f}: {name}, US {s.size or '-'}\nOrder {s.order_id}\n\n{buy}\n\n{ship}{warn}"
                f"\n\nListing: https://www.ebay.com/itm/{s.item_id}")
        if photo:
            alerts.append({"photo": photo, "text": f"💰 Sold: {name}, US {s.size or '-'} (details next)"})
        alerts.append(text)
        new_keys.append(key)
    if new_keys:
        SEEN.parent.mkdir(exist_ok=True)
        with SEEN.open("a") as f:
            f.write("\n".join(new_keys) + "\n")
    return [a for a in alerts if a]
