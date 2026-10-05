"""eBay catalog lookup: find a product's eBay stock photos (eBay-hosted catalog images) by style code.

requests/catalog.txt: one query per line (usually the style code, e.g. "576223 FAD94 1058").
Output: data/catalog_results.json {query: [{epid, title, mpn, gtin, images: [...], aspects: {...}}]}.
Only products whose MPN/title contains the style code are kept as matches ("match": true), so a photo is
never borrowed from a different colourway.
"""
from __future__ import annotations

import json
import re

import requests

from bot.config import ROOT

API = "https://api.ebay.com/commerce/catalog/v1_beta/product_summary/search"
REQ = ROOT / "requests" / "catalog.txt"
OUT = ROOT / "data" / "catalog_results.json"


def _norm(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def search(query: str, token: str, limit: int = 20) -> list[dict]:
    r = requests.get(API, params={"q": query, "limit": limit},
                     headers={"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}, timeout=30)
    if r.status_code == 204:
        return []
    if not r.ok:
        raise RuntimeError(f"catalog search {r.status_code}: {r.text[:300]}")
    code = _norm(query)
    out = []
    for p in r.json().get("productSummaries", []):
        imgs = [i.get("imageUrl") for i in [p.get("image") or {}] + (p.get("additionalImages") or []) if i.get("imageUrl")]
        mpns = p.get("mpn") or []
        aspects = {a.get("localizedName"): a.get("localizedValues") for a in p.get("aspects") or []}
        hay = _norm(" ".join(mpns + [p.get("title", "")] + sum((v or [] for v in aspects.values()), [])))
        out.append({"epid": p.get("epid"), "title": p.get("title"), "mpn": mpns, "gtin": p.get("gtin") or [],
                    "images": imgs, "aspects": aspects, "match": bool(code) and code in hay})
    return out


def full_images(epid: str, token: str) -> list[str]:
    """All catalog images for one ePID (getProduct returns more angles than the search summary)."""
    r = requests.get(f"https://api.ebay.com/commerce/catalog/v1_beta/product/{epid}",
                     headers={"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}, timeout=30)
    if not r.ok:
        return []
    j = r.json()
    return [i.get("imageUrl") for i in [j.get("image") or {}] + (j.get("additionalImages") or []) if i.get("imageUrl")]


def run() -> int:
    from bot.ebay.auth import access_token
    token = access_token()
    queries = [q.strip() for q in REQ.read_text().splitlines() if q.strip() and not q.startswith("#")]
    results = json.loads(OUT.read_text()) if OUT.exists() else {}
    for q in queries:
        try:
            results[q] = search(q, token)
        except Exception as e:
            results[q] = [{"error": str(e)[:300]}]
        for p in [p for p in results[q] if p.get("match")][:5]:     # more angles for exact matches
            try:
                more = full_images(p["epid"], token)
                p["images"] = list(dict.fromkeys(p.get("images", []) + more))
            except Exception as e:
                p["image_error"] = str(e)[:200]
        n = sum(1 for p in results[q] if p.get("match"))
        print(f"{q}: {len(results[q])} products, {n} exact style-code matches")
    OUT.write_text(json.dumps(results, indent=1))
    return 0
