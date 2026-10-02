"""Plain-English Telegram messages. Rule: what Rafael must do comes first, everything else is grouped
per product with sizes collapsed ("all 13 sizes", "US 9, 10.5"), and every section says why in one line."""
from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

BRANDS = {"Dolce & Gabbana": "D&G", "Dolce and Gabbana": "D&G", "Salvatore Ferragamo": "Ferragamo",
          "Bottega Veneta": "Bottega", "Saint Laurent": "YSL", "Alexander McQueen": "McQueen"}
FILLER = r"\b(Men'?s|Mens|Authentic|NIB|NWB|NWT|Brand New|With Box|w/ ?Box|Size)\b"


def short_name(title: str, limit: int = 48) -> str:
    t = title
    for long, short in BRANDS.items():
        t = re.sub(re.escape(long), short, t, flags=re.I)
    t = re.sub(FILLER, "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" -|,")
    if len(t) <= limit:
        return t
    return t[:limit].rsplit(" ", 1)[0] + "…"


def _size_key(s: str):
    try:
        return (0, float(re.sub(r"[^\d.]", "", s) or 0), s)
    except ValueError:
        return (1, 0, s)


def sizes_text(sizes: list[str | None], total: int) -> str:
    sizes = [s for s in sizes if s]
    if not sizes:
        return ""
    if total > 1 and len(sizes) == total:
        return f"all {total} sizes"
    return "US " + ", ".join(sorted(sizes, key=_size_key))


def today() -> str:
    return datetime.now(ZoneInfo("America/New_York")).strftime("%a %b %-d")


WHY = {
    "relisted": ("✅ BACK ON SALE", "A store has it in stock at a price that still makes you $100+."),
    "hidden": ("🚫 TAKEN OFF SALE", "No store has it in stock right now, so if it sold you'd have to cancel. "
                                   "It comes back on sale by itself when a store restocks."),
    "waiting": ("⏳ KEPT OFF SALE", "It would make money, but only 1 store has it. I wait for a 2nd store so a sale "
                                   "can't turn into a cancellation."),
    "lowered": ("📉 PRICE LOWERED 3%", "No sale in 7 days at the old price. It still makes you $100+, and it drops "
                                     "again next week if it doesn't sell (never below $100 profit)."),
}
MAX_CARDS = 8


def sync_report(live: bool, applied: list[str], groups: dict, raises: list[dict], checked: int) -> list:
    """Messages for Telegram: one short summary, then one picture card per product that changed
    (what happened, why, link). Returns a list of str / {"text", "photo"}."""
    n = {k: len(v) for k, v in groups.items()}
    did = []
    if n.get("hidden"):
        did.append(f"took {n['hidden']} listing{'s' * (n['hidden'] > 1)} (or some sizes) off sale because stores ran out")
    if n.get("relisted"):
        did.append(f"put {n['relisted']} listing{'s' * (n['relisted'] > 1)} back on sale")
    if n.get("lowered"):
        did.append(f"lowered the price 3% on {n['lowered']} listing{'s' * (n['lowered'] > 1)} that hadn't sold in a week")
    if n.get("waiting"):
        did.append(f"kept {n['waiting']} off sale until a 2nd store has them")
    if applied:
        did.append(f"made {len(applied)} change{'s' * (len(applied) > 1)} you approved")
    head = [f"📋 Daily eBay check · {today()}" + ("" if live else " (TEST MODE, nothing changed on eBay)"), ""]
    if did:
        head.append("What I did: " + "; ".join(did) + ".")
    else:
        head.append(f"I checked all {checked} listings. Nothing needed changing.")
    head.append(f"👉 You have {len(raises)} thing{'s' * (len(raises) != 1)} to answer (below)." if raises
                else "Nothing for you to do.")
    if applied:
        head += ["", "Changes you approved:"] + [f"• {a}" for a in applied]
    out: list = ["\n".join(head)]

    for r in raises:
        out.append({"photo": r.get("photo"), "text": (
            f"👉 NEEDS YOUR OK ({r['code']})\n{r['name']} · US {r['size']}\n\n"
            f"Raise the price from ${r['old']:.2f} to ${r['new']:.2f}?\n"
            f"Why: the cheapest store ({r['store']}, ${r['cost']:.0f}) went up, so at today's price you'd make "
            f"under $100. It's off sale until you answer.\n\n"
            f"Reply \"yes {r['code']}\" or \"no {r['code']}\" (or just tell me in your own words).\n"
            f"{r.get('url', '')}")})

    cards = [(k, row) for k in ("relisted", "lowered", "hidden", "waiting") for row in groups.get(k, [])]
    for kind, (name, sizes, total, extra, photo, url) in cards[:MAX_CARDS]:
        title, why = WHY[kind]
        text = (f"{title}\n{name}\nSizes: {sizes_text(sizes, total)}" + (f" · {extra}" if extra else "")
                + f"\n\nWhy: {why}\n{url}")
        out.append({"photo": photo, "text": text})
    if len(cards) > MAX_CARDS:
        rest = cards[MAX_CARDS:]
        out.append("Also changed:\n" + "\n".join(f"• {WHY[k][0].split(' ', 1)[1].title()}: {r[0]} ({sizes_text(r[1], r[2])}) {r[5]}"
                                                for k, r in rest))
    return out
