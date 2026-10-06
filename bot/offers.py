"""Offers to watchers (eBay Negotiation API). Needs only the sell.inventory permission the bot already has.
READ-ONLY for now (Rafael, Oct 5: "don't send any yet"): eligible() lists which listings eBay would let us send
offers on (listings with interested buyers: watchers / abandoned carts) → data/offers_eligible.json.
Sending (send_offer) is deliberately not wired to anything until Rafael says so."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import requests

from bot.config import ROOT

API = "https://api.ebay.com/sell/negotiation/v1"
OUT = ROOT / "data" / "offers_eligible.json"


def eligible(token: str) -> list[str]:
    ids, offset = [], 0
    while True:
        r = requests.get(f"{API}/find_eligible_items", params={"limit": 200, "offset": offset}, timeout=60,
                         headers={"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
        if r.status_code == 204:
            break
        if r.status_code != 200:
            raise RuntimeError(f"find_eligible_items {r.status_code}: {r.text[:300]}")
        d = r.json()
        ids += [str(x.get("listingId")) for x in d.get("eligibleItems", [])]
        if not d.get("next"):
            break
        offset += 200
    return ids


def run() -> None:
    from bot.ebay.auth import access_token
    try:
        ids, err = eligible(access_token()), None
    except Exception as e:
        ids, err = [], str(e)[:400]
    OUT.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "eligible": ids, "error": err}, indent=1))
    print("offers eligible:", len(ids), err or "")
