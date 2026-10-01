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


def sync_report(live: bool, applied: list[str], groups: dict, raises: list[dict], checked: int) -> str:
    """groups: {kind: [(name, [sizes], total_sizes, extra)]}; kinds: relisted, hidden, unprofitable, waiting."""
    out = [f"📋 Daily eBay check · {today()}"]
    if not live:
        out.append("(test mode: nothing was changed on eBay)")

    if raises:
        out += ["", "👉 NEEDS YOU: raise these prices? They're off sale until you answer, because at "
                    "today's price they'd make less than $100."]
        for r in raises:
            out.append(f"{r['code']} · {r['name']}, US {r['size']}: ${r['old']:.2f} → ${r['new']:.2f} "
                       f"(cheapest store: {r['store']} ${r['cost']:.0f})")
        out.append("Reply APPROVE " + raises[0]["code"] + " (or APPROVE ALL), or SKIP " + raises[0]["code"] + ".")

    if applied:
        out += ["", "✅ Done (you approved these):"] + [f"• {a}" for a in applied]

    sections = [
        ("relisted", "✅ Back on sale (a store has it again):"),
        ("hidden", "🚫 Taken off sale (no store has it in stock, so a sale would mean a cancellation). "
                   "Comes back by itself when a store restocks:"),
        ("waiting", "⏳ Profitable, but only 1 store has it, so kept off sale to be safe:"),
    ]
    for kind, head in sections:
        rows = groups.get(kind) or []
        if rows:
            out += ["", head]
            for name, sizes, total, extra in rows:
                out.append(f"• {name}: {sizes_text(sizes, total)}" + (f" ({extra})" if extra else ""))

    if len(out) <= 2:
        out += ["", f"All good. Checked {checked} listings: nothing changed, nothing for you to do."]
    elif not raises:
        out += ["", "Nothing for you to do."]
    return "\n".join(out)
