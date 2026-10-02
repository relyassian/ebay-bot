"""Promo codes for the store Rafael is about to buy from.

data/promos.yaml is refreshed by the daily research routine (it reads store promo emails in Rafael's Gmail
and the stores' own sites). Format:
  cettire:
    - {code: WELCOME10, discount: "10% off first order", expires: 2026-10-31, source: "Cettire email Oct 1"}
The sale alert shows valid codes for that store plus a one-tap link to search for more.
"""
from __future__ import annotations

import urllib.parse
from datetime import date

import yaml

from bot.config import ROOT

FILE = ROOT / "data" / "promos.yaml"


def _key(store: str) -> str:
    s = (store or "").lower()
    for k in ("cettire", "farfetch", "ssense", "italist", "nugnes", "goat", "stockx", "mytheresa", "end",
              "saks", "neiman", "nordstrom", "gucci", "ferragamo", "dolce"):
        if k in s:
            return k
    return s.split()[0] if s else ""


def lines_for(store: str) -> list[str]:
    key = _key(store)
    data = yaml.safe_load(FILE.read_text()) if FILE.exists() else {}
    out = []
    for p in (data or {}).get(key, []) or []:
        exp = p.get("expires")
        if exp and str(exp) < date.today().isoformat():
            continue
        out.append(f"🏷 Code {p['code']}: {p.get('discount', '')}" + (f" (until {exp})" if exp else ""))
    q = urllib.parse.quote(f"{store.split('(')[0].strip()} promo code")
    out.append(f"More codes: https://www.google.com/search?q={q}")
    return out
