"""One-off: show Rafael what the new Telegram messages look like, using a real listing."""
import json

from bot.alerts import send
from bot.config import ROOT
from bot.report import short_name


def run() -> None:
    snap = {x["item_id"]: x for x in json.loads((ROOT / "data" / "snapshot.json").read_text())}
    x = snap.get("355422702908") or next(iter(snap.values()))
    url = f"https://www.ebay.com/itm/{x['item_id']}"
    send("👋 New message style. From now on the daily check sends 1 short summary, then 1 card per product "
         "that changed: photo, what happened, why, and the link. Example below.\n\n"
         "You can also just text me like a person, e.g. \"what's off sale right now?\" or \"why was the "
         "Gucci loafer hidden?\"")
    send({"photo": (x.get("photos") or [None])[0], "text":
          f"🚫 TAKEN OFF SALE (example)\n{short_name(x['title'])}\nSizes: all {len(x['sizes'])} sizes\n\n"
          "Why: No store has it in stock right now, so if it sold you'd have to cancel. It comes back on sale "
          f"by itself when a store restocks.\n{url}"})
