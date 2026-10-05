"""Promoted Listings (eBay's pay-per-sale ads) for every shoe listing — Rafael's call, Oct 2 2026.

- One "general" (cost-per-sale) campaign: eBay charges `ads.rate` of the sale price only when an ad led to it.
- Every shoe listing gets an ad. Prices on those listings are raised ONCE so the ad fee comes out of the
  buyer's price, not Rafael's profit: new = old × (1 − fees − buffer) / (1 − fees − buffer − rate).
- profit.promoted_rate in config.yaml is set to the same rate, so floors, raises and new drafts include it.
State: data/ads_state.json {"campaign_id", "rate", "raised": [item ids already raised]}.
Needs the sell.marketing permission: Rafael re-approves eBay once (Telegram: CONNECT).
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

import requests

from bot.config import ROOT, load_config

STATE = ROOT / "data" / "ads_state.json"
API = "https://api.ebay.com/sell/marketing/v1"
CAMPAIGN_NAME = "Shoes (bot)"


def _load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"raised": []}


def _save(d: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(d, indent=2))


def shoe_item_ids() -> list[str]:
    """Shoe listings = adopted legacy shoes + listings the bot created for shoe categories."""
    import yaml
    ids = list(yaml.safe_load((ROOT / "data" / "legacy_content.yaml").read_text())["items"].keys())
    st = ROOT / "data" / "drafts_state.json"
    if st.exists():
        from bot.listing import load_candidates
        cands = load_candidates()
        for cid, v in json.loads(st.read_text()).items():
            if v.get("status") == "live" and cands.get(cid, {}).get("category") in ("sneaker", "loafer", "dress_shoe"):
                ids.append(str(v["item_id"]))
    return ids


def bot_created_ids() -> list[str]:
    st = ROOT / "data" / "drafts_state.json"
    if not st.exists():
        return []
    return [str(v["item_id"]) for v in json.loads(st.read_text()).values() if v.get("status") == "live"]


def covered_price(price: float, rate: float, cfg: dict) -> float:
    p = cfg["profit"]
    keep = 1 - p["ebay_fee_rate"] - p["inad_buffer_rate"]
    return math.ceil(price * keep / (keep - rate)) - 0.01


def _h(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"}


def _campaign(tok: str, rate: float) -> str:
    r = requests.get(f"{API}/ad_campaign", headers=_h(tok), params={"campaign_name": CAMPAIGN_NAME}, timeout=30)
    if r.ok and r.json().get("campaigns"):
        return r.json()["campaigns"][0]["campaignId"]
    start = (datetime.now(timezone.utc) + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = {"campaignName": CAMPAIGN_NAME, "marketplaceId": "EBAY_US", "startDate": start,
            "fundingStrategy": {"fundingModel": "COST_PER_SALE", "bidPercentage": f"{rate * 100:.1f}"}}
    r = requests.post(f"{API}/ad_campaign", headers=_h(tok), json=body, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"eBay refused the ad campaign ({r.status_code}): {r.text[:300]}")
    return r.headers["Location"].rstrip("/").split("/")[-1]


def setup(live: bool) -> list[str]:
    """Idempotent: campaign exists, every shoe listing has an ad at the configured rate, prices raised once."""
    from bot.ebay.auth import access_token
    from bot.ebay.trading import Change, get_item, revise
    from bot.report import short_name
    cfg = load_config()
    rate = float(cfg["ads"]["rate"])
    live = live and not cfg.get("dry_run", True)
    d, out = _load(), []
    ids = shoe_item_ids()
    if not live:
        return [f"(test mode) would advertise {len(ids)} shoe listings at {rate:.0%} and raise their prices to cover it."]
    mtok = access_token(marketing=True)
    cid = d.get("campaign_id") or _campaign(mtok, rate)
    d.update(campaign_id=cid, rate=rate)
    _save(d)
    reqs = [{"listingId": i, "bidPercentage": f"{rate * 100:.1f}"} for i in ids]
    r = requests.post(f"{API}/ad_campaign/{cid}/bulk_create_ads_by_listing_id", headers=_h(mtok),
                      json={"requests": reqs}, timeout=60)
    added, already = 0, 0
    if r.ok:
        for resp in r.json().get("responses", []):
            if resp.get("statusCode") in (200, 201):
                added += 1
            elif any("exist" in (e.get("message") or "").lower() for e in resp.get("errors", [])):
                already += 1
    else:
        out.append(f"⚠️ eBay didn't accept the ads ({r.status_code}): {r.text[:200]}")
    # raise prices once per listing so the ad fee doesn't eat the profit. Listings the bot created were
    # priced with the ad fee already included (promoted_rate in config), so they are never raised.
    token, raised = access_token(), []
    for item_id in bot_created_ids():
        if item_id not in d["raised"]:
            d["raised"].append(item_id)
    _save(d)
    for item_id in ids:
        if item_id in d["raised"]:
            continue
        try:
            lst = get_item(item_id, token)
            changes = ([Change(item_id, v.size, new_price=covered_price(v.price, rate, cfg)) for v in lst.variations]
                       if lst.variations else [Change(item_id, None, new_price=covered_price(lst.price, rate, cfg))])
            revise(lst, changes, token, cfg["listing"]["quantity_per_size"])
            d["raised"].append(item_id)
            _save(d)
            lo = min(c.new_price for c in changes)
            raised.append(f"{short_name(lst.title, 40)} → from ${lo:,.2f}")
        except Exception as e:
            out.append(f"⚠️ Couldn't raise {item_id}: {str(e)[:120]}")
    head = (f"📣 Ads are ON: {added + already} shoe listings promoted at {rate:.0%} "
            "(eBay only charges when an ad leads to a sale).")
    if raised:
        head += f"\nPrices raised about {covered_price(100, rate, cfg) - 100:.0f}% to cover the ad fee, so your profit per sale stays the same:\n" \
                + "\n".join(f"• {x}" for x in raised)
    return [head] + out
