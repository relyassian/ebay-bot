"""eBay sale badges (Rafael, Oct 5): an eBay "markdown sale" shows buyers a crossed-out price and "X% off".

Honest discounts only: the crossed-out price is the listing's real current price (eBay and US advertising rules
don't allow raising a price just to show a bigger "discount"). Each listing gets the biggest step in
`markdown.steps` at which EVERY size on sale still makes ≥ `pricing.decay_floor_mult` × the required profit
($150 normally, $300 LV) at the discounted price. Listings that can't take the smallest step stay out.

While a listing is in the sale, the daily sync checks profit at the discounted price and skips the weekly price
drops (the sale replaces them). Any price change takes a listing out of the sale (eBay rule), which is safe.
State: data/markdown.json {"promotion_id", "start", "end", "items": {item_id: pct}}; a new sale is created
when the current one has < 1 day left.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import requests

from bot.config import ROOT, load_config

STATE = ROOT / "data" / "markdown.json"
API = "https://api.ebay.com/sell/marketing/v1"


def _load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def _iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def discount_for(item_id: str) -> float:
    """Current sale discount for a listing (0.0 if not in a running sale)."""
    s = _load()
    if not s.get("end"):
        return 0.0
    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(s["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(s["end"].replace("Z", "+00:00"))
    if not (start - timedelta(hours=1) <= now <= end):
        return 0.0
    return float(s.get("items", {}).get(str(item_id), 0)) / 100


def best_step(listing, sources: dict, cfg: dict, steps: list[int]) -> int:
    """Largest % off at which every size on sale still clears decay_floor_mult × the required profit."""
    from bot.profit import is_taxable, item_min_net, landed_cost, net_profit, required_net, store_shipping
    mult = cfg.get("pricing", {}).get("decay_floor_mult", 1.0)
    base = item_min_net(cfg, listing.item_id)
    rows = ([(v.size, v.price, v.available) for v in listing.variations] if listing.variations
            else [(None, listing.price, (listing.quantity or 0) - (listing.sold or 0))])
    live = [(s, p) for s, p, a in rows if a > 0]
    if not live:
        return 0
    for pct in sorted(steps, reverse=True):
        ok = True
        for size, price in live:
            src = sources.get((listing.item_id, size))
            if not src or src.cost is None:
                ok = False
                break
            landed = landed_cost(src.cost, cfg, overseas=src.overseas, taxable=is_taxable(cfg, listing.item_id),
                                 shipping=store_shipping(cfg, src.source))
            paid = round(price * (1 - pct / 100), 2)
            if net_profit(paid, landed, cfg) < mult * required_net(paid, cfg, base):
                ok = False
                break
        if ok:
            return pct
    return 0


def run(live: bool) -> list[str]:
    cfg = load_config()
    mk = cfg.get("markdown") or {}
    if not mk.get("enabled"):
        return []
    s = _load()
    now = datetime.now(timezone.utc)
    if s.get("end") and datetime.fromisoformat(s["end"].replace("Z", "+00:00")) - now > timedelta(days=1):
        return []                                   # current sale still running
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_active_item_ids, get_item
    from bot.sync import load_sources
    token, sources = access_token(), load_sources()
    ignore = set(map(str, cfg.get("sync", {}).get("ignore_items", [])))
    words = [w.lower() for w in cfg.get("sync", {}).get("ignore_title_words", [])]
    picks, photo = {}, None
    for iid in get_active_item_ids(token):
        if iid in ignore:
            continue
        try:
            lst = get_item(iid, token)
        except Exception as e:
            print("markdown: can't read", iid, e)
            continue
        if any(w in lst.title.lower() for w in words):
            continue
        pct = best_step(lst, sources, cfg, mk.get("steps", [20, 15, 10, 5]))
        print(f"markdown {iid}: {pct}% · {lst.title}")
        if pct:
            picks[iid] = pct
            photo = photo or lst.photo
    if not picks:
        STATE.write_text(json.dumps({}))
        return ["No listing has enough margin for a sale right now."]
    start = now + timedelta(minutes=10)
    end = start + timedelta(days=int(mk.get("days", 14)))
    groups: dict[int, list[str]] = {}
    for iid, pct in picks.items():
        groups.setdefault(pct, []).append(iid)
    body = {
        "name": f"Designer shoes sale {start:%b %d}",
        "description": (mk.get("tagline") or "Authentic designer shoes on sale")[:50],
        "marketplaceId": "EBAY_US",
        "promotionStatus": "SCHEDULED",
        "startDate": _iso(start),
        "endDate": _iso(end),
        "promotionImageUrl": photo,
        "applyFreeShipping": False,
        "autoSelectFutureInventory": False,
        "blockPriceIncreaseInItemRevision": False,
        "selectedInventoryDiscounts": [
            {"discountBenefit": {"percentageOffItem": str(pct)},
             "inventoryCriterion": {"inventoryCriterionType": "INVENTORY_BY_VALUE", "listingIds": ids}}
            for pct, ids in sorted(groups.items(), reverse=True)],
    }
    summary = ", ".join(f"{len(ids)} at {pct}% off" for pct, ids in sorted(groups.items(), reverse=True))
    if not live:
        return [f"(test mode) would start a {mk.get('days', 14)}-day sale: {summary}"]
    tok = access_token(marketing=True)
    r = requests.post(f"{API}/item_price_markdown", json=body, timeout=60, headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json",
        "Content-Language": "en-US", "Accept": "application/json"})
    if r.status_code not in (200, 201):
        raise RuntimeError(f"eBay refused the sale ({r.status_code}): {r.text[:400]}")
    pid = (r.headers.get("Location") or "").rstrip("/").split("/")[-1]
    STATE.write_text(json.dumps({"promotion_id": pid, "start": _iso(start), "end": _iso(end), "items": picks},
                                indent=1))
    return [f"Started a {mk.get('days', 14)}-day eBay sale: {summary}"]
