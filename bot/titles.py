"""Fuller eBay titles (Rafael, Oct 5): eBay search matches on title words, and most titles used ~40–60 of the
80 characters. We add only words that are true for the listing: what the shoe is (sneakers / loafers / driving
shoes), the upper material from its item specifics, "Authentic" (every pair goes through eBay's Authenticity
Guarantee), and "Made in Italy" only when the listing's own Country of Manufacture says Italy.
Never added: style codes (Rafael, Oct 1), other brands, sizes, hype words.
"""
from __future__ import annotations

import re

MAX = 80
MATERIALS = ("Leather", "Suede", "Canvas", "Calfskin", "Nappa", "Mesh", "Knit", "Demetra", "Denim", "Ripstop",
             "Jacquard", "Nylon", "Patent Leather", "Textile")
SUFFIX = re.compile(r"(\s+Men'?s)?(\s+New)?\s*$", re.I)


def kind_of(title: str) -> str | None:
    t = title.lower()
    if any(w in t for w in ("airpods", "cufflink", "belt", "tie ")):
        return None
    if "driver" in t or "driving" in t:
        return "driver"
    if "moccasin" in t or "loafer" in t:
        return "loafer"
    if any(w in t for w in ("sneaker", "trainer", "basket", "rhyton", "screener", "ace ", "tennis", "mac80",
                            "re-web", "gazelle", "runner", "skate", "run ")):
        return "sneaker"
    return None


def _has(title: str, words: str) -> bool:
    return all(re.search(rf"\b{re.escape(w)}", title, re.I) for w in words.split())


def enhance(title: str, specifics: dict | None = None) -> str | None:
    """Return the fuller title, or None when there's nothing to add / not a shoe."""
    specifics = specifics or {}
    kind = kind_of(title)
    if kind is None:
        return None
    base = SUFFIX.sub("", title).strip()
    extras: list[str] = []          # in priority order (dropped from the end when too long)
    if kind == "sneaker":
        high = _has(base, "High")
        if not _has(base, "Sneakers") and not _has(base, "Shoes"):
            extras.append("High Top Sneakers" if high and not _has(base, "High Top") else
                          ("Sneakers" if high else "Low Top Sneakers"))
    elif kind == "driver":
        if not _has(base, "Driving Shoes"):
            extras.append("Driving Shoes")
    elif kind == "loafer":
        if not _has(base, "Loafers"):
            extras.append("Loafers")
    mat = specifics.get("Upper Material") or ""
    if isinstance(mat, list):
        mat = mat[0] if mat else ""
    mat = next((m for m in MATERIALS if m.lower() == mat.strip().lower()), "")
    if mat and not _has(base, mat):
        extras.append(mat)
    extras.append("Authentic")
    country = specifics.get("Country/Region of Manufacture") or ""
    if isinstance(country, list):
        country = country[0] if country else ""
    if country.strip().lower() == "italy" and not _has(base, "Italy"):
        extras.append("Made in Italy")

    order = {w: i for i, w in enumerate([mat, "Low Top Sneakers", "High Top Sneakers", "Sneakers",
                                          "Driving Shoes", "Loafers", "Authentic", "Made in Italy"])}

    def build(ex):
        # "Men's" right after the product name, then e.g. "Leather Low Top Sneakers Authentic", "New" last
        return " ".join([base, "Men's", *sorted(ex, key=lambda w: order.get(w, 99)), "New"])

    while extras and len(build(extras)) > MAX:
        extras.pop()
    new = build(extras)
    if len(new) > MAX or new == title or len(new) <= len(title):
        return None
    return new
