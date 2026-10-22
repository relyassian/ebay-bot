"""Price check against other eBay sellers (Rafael, Oct 7). Read-only.

For every listing we know the product of (bot drafts + adopted legacy listings), search eBay (Browse API,
app token) for other NEW, fixed-price listings of the same product and compare their cheapest price with our
cheapest live size. Search uses the style code first (most precise), then brand + model + colorway.
A result only counts when its title contains the brand and every word of the model name, so different shoes
don't pollute the comparison. Our own listings are skipped.

Output: data/market.json {"checked": iso, "items": {item_id: {...}}}; the morning update shows a one-line FYI.
Per-size comparison isn't possible from search results (multi-size listings show one price), so this compares
cheapest vs cheapest: a flag means "check this one", not proof we're overpriced in every size.
"""
from __future__ import annotations

import json
import re
import statistics
import time
from datetime import datetime, timezone

import requests

from bot.config import ROOT, load_config

OUT = ROOT / "data" / "market.json"
SELLER = "rafaelelyassian"
BROWSE = "https://api.ebay.com/buy/browse/v1/item_summary/search"
NEW_IDS = "1000"             # eBay "New" (with box); same condition as ours
_tok: dict = {}


def app_token() -> str:
    """Client-credentials token (public data only, no user consent needed)."""
    if _tok.get("exp", 0) > time.time() + 60:
        return _tok["t"]
    from bot.ebay.auth import TOKEN_URL, _basic
    r = requests.post(TOKEN_URL, timeout=30, headers={"Authorization": _basic(),
                      "Content-Type": "application/x-www-form-urlencoded"},
                      data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"})
    r.raise_for_status()
    b = r.json()
    _tok.update(t=b["access_token"], exp=time.time() + int(b.get("expires_in", 7200)))
    return _tok["t"]


def products() -> dict[str, dict]:
    """item_id → {brand, model, colorway, style_code} for every listing we know the product of."""
    import yaml
    out = {}
    leg = ROOT / "data" / "legacy_content.yaml"
    if leg.exists():
        for iid, v in (yaml.safe_load(leg.read_text()).get("items") or {}).items():
            out[str(iid)] = v
    st = ROOT / "data" / "drafts_state.json"
    if st.exists():
        from bot.listing import load_candidates
        cands = load_candidates()
        for cid, v in json.loads(st.read_text()).items():
            if v.get("status") == "live" and cid in cands:
                out[str(v["item_id"])] = cands[cid]
    return out


def _words(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 2 and w not in ("with", "and", "the")]


NOT_SAME = re.compile(r"\b(women'?s?|womens|wmns|ladies|kids?|youth|toddler|infant|baby|boys?|girls?|gs|td|ps|"
                      r"box only|empty box|laces only|dust ?bag only|replacement)\b", re.I)
GENERIC = {"men", "mens", "new", "low", "high", "top", "sneaker", "sneakers", "leather", "canvas"}


def _matches(title: str, p: dict) -> bool:
    """Same product: style code in the title, or brand + every model word + most colorway words.
    Women's/kids'/accessory-only listings never count."""
    if NOT_SAME.search(title):
        return False
    t = set(_words(title))
    code = re.sub(r"\s+", "", (p.get("style_code") or "")).lower()
    if code and code in re.sub(r"[\s-]+", "", title.lower()):
        return True
    brand = _words((p.get("brand") or "").replace("Salvatore ", ""))
    model = _words(p.get("model"))
    if not (all(w in t for w in brand) and all(w in t for w in model)):
        return False
    colors = [w for w in _words((p.get("colorway") or "").replace("/", " ")) if w not in GENERIC]
    if not colors:
        return True
    hit = sum(1 for w in colors if w in t)
    return hit >= (len(colors) if len(colors) <= 3 else len(colors) - 1)


def search(q: str, tok: str) -> list[dict]:
    r = requests.get(BROWSE, timeout=30, headers={"Authorization": f"Bearer {tok}",
                     "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"},
                     params={"q": q[:100], "limit": 100,
                             "filter": f"buyingOptions:{{FIXED_PRICE}},conditionIds:{{{NEW_IDS}}},"
                                       "priceCurrency:USD,itemLocationCountry:US"})
    if r.status_code != 200:
        raise RuntimeError(f"browse {r.status_code}: {r.text[:200]}")
    return r.json().get("itemSummaries", []) or []


def competitors(p: dict, tok: str) -> list[dict]:
    seen, out = set(), []
    queries = []
    if p.get("style_code"):
        queries.append(p["style_code"])
    queries.append(" ".join(x for x in [(p.get("brand") or "").replace("Salvatore ", ""), p.get("model"),
                                        (p.get("colorway") or "").split()[0] if p.get("colorway") else ""] if x))
    for q in queries:
        for it in search(q, tok):
            iid = it.get("legacyItemId") or it.get("itemId")
            if iid in seen or (it.get("seller") or {}).get("username", "").lower() == SELLER:
                continue
            seen.add(iid)
            title = it.get("title", "")
            low = title.lower()
            if any(w in low for w in ("used", "pre-owned", "preowned", "worn", "replica", "inspired")):
                continue
            if not _matches(title, p):
                continue
            price = float((it.get("price") or {}).get("value") or 0)
            ship = it.get("shippingOptions") or [{}]
            ship_cost = float(((ship[0] or {}).get("shippingCost") or {}).get("value") or 0)
            if price:
                out.append({"price": round(price + ship_cost, 2), "title": title[:90],
                            "url": it.get("itemWebUrl"), "seller": (it.get("seller") or {}).get("username")})
        time.sleep(0.3)
    out.sort(key=lambda x: x["price"])
    if len(out) >= 3:       # very low asks are usually fakes or mislabeled; don't compare against them
        mid = statistics.median(c["price"] for c in out)
        out = [c for c in out if c["price"] >= 0.45 * mid]
    return out


def market_for(item_id: str, max_age_h: float = 72, min_n: int = 3) -> dict | None:
    """Fresh market numbers for a listing, or None (too few comparable listings or stale data)."""
    if not OUT.exists():
        return None
    d = json.loads(OUT.read_text())
    try:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(d["checked"].replace("Z", "+00:00"))).total_seconds()
    except Exception:
        return None
    v = d.get("items", {}).get(str(item_id))
    if age > max_age_h * 3600 or not v or (v.get("n") or 0) < min_n or not v.get("median"):
        return None
    return v


def product_market(p: dict) -> dict:
    """{n, median, cheapest} for a product we haven't listed yet (used to vet new listings)."""
    comp = competitors(p, app_token())
    return {"n": len(comp), "median": round(statistics.median([c["price"] for c in comp]), 2) if comp else None,
            "cheapest": comp[0]["price"] if comp else None}


def scan_requests() -> int:
    """Read-only comps for products we may list (requests/scan.json: [{key, brand, model, colorway, style_code}]).
    Writes data/scan_results.json {key: {n, median, cheapest, p25}}; used by the daily below-market scan."""
    src = ROOT / "requests" / "scan.json"
    if not src.exists():
        return 0
    tok, res = app_token(), {}
    for p in json.loads(src.read_text()):
        try:
            comp = competitors(p, tok)
        except Exception as e:
            res[p["key"]] = {"error": str(e)[:120]}
            continue
        px = [c["price"] for c in comp]
        res[p["key"]] = {"n": len(px), "median": round(statistics.median(px), 2) if px else None,
                         "cheapest": px[0] if px else None, "p25": px[len(px) // 4] if px else None,
                         "top": [c["title"] for c in comp[:2]]}
    (ROOT / "data" / "scan_results.json").write_text(json.dumps(
        {"checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": res}, indent=1))
    return len(res)


ITEM = "https://api.ebay.com/buy/browse/v1/item/"


def _sold_info(item_id: str, tok: str) -> dict | None:
    r = requests.get(ITEM + item_id, timeout=30, headers={"Authorization": f"Bearer {tok}",
                     "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
    if r.status_code != 200:
        return None
    b = r.json()
    est = (b.get("estimatedAvailabilities") or [{}])[0]
    return {"sold": est.get("estimatedSoldQuantity"), "created": b.get("itemCreationDate"),
            "price": float((b.get("price") or {}).get("value") or 0), "title": b.get("title", "")[:80],
            "seller": (b.get("seller") or {}).get("username"), "fb": (b.get("seller") or {}).get("feedbackScore")}


def demand_requests() -> int:
    """Demand check (read-only): for each product in requests/demand.json, look at other sellers' matching NEW
    listings and read eBay's estimated sold quantity + listing age. Writes data/demand_results.json:
    {key: {listings, sold_total, sold_per_30d, median_price, top: [...]}}. Entries may carry `q` (free search)."""
    src = ROOT / "requests" / "demand.json"
    out = ROOT / "data" / "demand_results.json"
    if not src.exists():
        return 0
    if out.exists():     # don't redo a fresh result (the workflow can run several times a day)
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(json.loads(out.read_text())["checked"].replace("Z", "+00:00"))).total_seconds()
            ok = sum(1 for v in json.loads(out.read_text())["items"].values() if "error" not in v)
            if age < 6 * 3600 and ok >= 20:
                return -1
        except Exception:
            pass
    tok, res, now = app_token(), {}, datetime.now(timezone.utc)
    for p in json.loads(src.read_text()):
        try:
            if p.get("q"):
                hits = [it for it in search(p["q"], tok) if not NOT_SAME.search(it.get("title", ""))]
                if p.get("must"):
                    hits = [it for it in hits if all(w in it.get("title", "").lower() for w in p["must"])]
            else:
                hits = []
                for q in ([p["style_code"]] if p.get("style_code") else []) + [
                        " ".join(x for x in [p.get("brand", ""), p.get("model", ""), (p.get("colorway") or "").split()[0] if p.get("colorway") else ""] if x)]:
                    hits += [it for it in search(q, tok) if _matches(it.get("title", ""), p)]
            seen, rows = set(), []
            for it in hits:
                iid = it.get("itemId")
                if iid in seen or (it.get("seller") or {}).get("username", "").lower() == SELLER:
                    continue
                seen.add(iid)
                if len(rows) >= 10:
                    break
                info = _sold_info(iid, tok)
                time.sleep(0.2)
                if info:
                    rows.append(info)
            sold = sum(int(r["sold"] or 0) for r in rows)
            rate = 0.0
            for r in rows:
                try:
                    age = max(7, (now - datetime.fromisoformat(r["created"].replace("Z", "+00:00"))).days)
                except Exception:
                    age = 90
                rate += int(r["sold"] or 0) * 30 / age
            px = [r["price"] for r in rows if r["price"]]
            res[p["key"]] = {"listings": len(rows), "sold_total": sold, "sold_per_30d": round(rate, 1),
                             "median_price": round(statistics.median(px), 2) if px else None,
                             "top": sorted(rows, key=lambda r: -(r["sold"] or 0))[:3]}
        except Exception as e:
            res[p["key"]] = {"error": str(e)[:120]}
    if not any("error" not in v for v in res.values()):     # all failed (eBay daily quota): keep the old file
        return 0
    (ROOT / "data" / "demand_results.json").write_text(json.dumps(
        {"checked": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "items": res}, indent=1))
    return len(res)


def explore_requests() -> int:
    """Category exploration (read-only): requests/explore.json [{key, q, must?}] -> data/explore_results.json
    {key: {n, median_price, p25, sold_total, sold_per_30d, top}}. New fixed-price US listings only."""
    src = ROOT / "requests" / "explore.json"
    if not src.exists():
        return 0
    tok, res, now = app_token(), {}, datetime.now(timezone.utc)
    for p in json.loads(src.read_text()):
        try:
            hits = [it for it in search(p["q"], tok) if (it.get("seller") or {}).get("username", "").lower() != SELLER]
            if p.get("must"):
                hits = [it for it in hits if all(w in it.get("title", "").lower() for w in p["must"])]
            px = sorted(float((it.get("price") or {}).get("value") or 0) for it in hits)
            px = [x for x in px if x > 0]
            rows = []
            for it in hits[:10]:
                info = _sold_info(it.get("itemId"), tok)
                time.sleep(0.2)
                if info:
                    rows.append(info)
            rate = 0.0
            for r in rows:
                try:
                    age = max(7, (now - datetime.fromisoformat(r["created"].replace("Z", "+00:00"))).days)
                except Exception:
                    age = 90
                rate += int(r["sold"] or 0) * 30 / age
            res[p["key"]] = {"n": len(px), "median_price": round(statistics.median(px), 2) if px else None,
                             "p25": px[len(px) // 4] if px else None,
                             "sold_total": sum(int(r["sold"] or 0) for r in rows), "sold_per_30d": round(rate, 1),
                             "top": [{k: r[k] for k in ("title", "price", "sold", "seller")} for r in rows[:4]]}
        except Exception as e:
            res[p["key"]] = {"error": str(e)[:120]}
    (ROOT / "data" / "explore_results.json").write_text(json.dumps(
        {"checked": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "items": res}, indent=1))
    return len(res)


def order_fees() -> int:
    """Read-only: dump every fee eBay charged on recent orders (Trading GetOrders, last 90 days) to
    data/order_fees.json so the real final-value-fee rate per category/price can be checked."""
    from datetime import timedelta
    from bot.ebay.auth import access_token
    from bot.ebay.trading import _call, NS
    token = access_token()
    now = datetime.now(timezone.utc)
    frm = (now - timedelta(days=89)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    to = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    root = _call("GetOrders", f"<CreateTimeFrom>{frm}</CreateTimeFrom><CreateTimeTo>{to}</CreateTimeTo>"
                              "<OrderRole>Seller</OrderRole><OrderStatus>All</OrderStatus>"
                              "<DetailLevel>ReturnAll</DetailLevel>", token)
    out = []
    for o in root.iter("{urn:ebay:apis:eBLBaseComponents}Order"):
        row = {"order": o.findtext("e:OrderID", namespaces=NS), "total": o.findtext("e:Total", namespaces=NS),
               "status": o.findtext("e:OrderStatus", namespaces=NS), "fees": {}, "items": []}
        for el in o.iter():
            tag = el.tag.split("}")[-1]
            if "Fee" in tag and (el.text or "").strip():
                row["fees"].setdefault(tag, []).append(el.text.strip())
        for t in o.iter("{urn:ebay:apis:eBLBaseComponents}Transaction"):
            row["items"].append({"item": t.findtext("e:Item/e:ItemID", namespaces=NS),
                                 "title": (t.findtext("e:Item/e:Title", namespaces=NS) or "")[:80],
                                 "category": t.findtext("e:Item/e:PrimaryCategory/e:CategoryName", namespaces=NS),
                                 "price": t.findtext("e:TransactionPrice", namespaces=NS),
                                 "fvf": t.findtext("e:FinalValueFee", namespaces=NS)})
        out.append(row)
    for row in out:     # Fulfillment API carries the real marketplace fee
        try:
            r = requests.get("https://api.ebay.com/sell/fulfillment/v1/order/" + row["order"], timeout=30,
                             headers={"Authorization": f"Bearer {token}"})
            b = r.json() if r.status_code == 200 else {"error": r.status_code, "body": r.text[:200]}
            row["fulfillment"] = {k: b.get(k) for k in ("totalMarketplaceFee", "pricingSummary", "paymentSummary", "error", "body") if k in b}
            row["fulfillment"]["lineItems"] = [{k: li.get(k) for k in ("title", "total", "lineItemCost", "taxes", "legacyItemId") if k in li}
                                                for li in b.get("lineItems", [])]
        except Exception as e:
            row["fulfillment"] = {"error": str(e)[:100]}
    (ROOT / "data" / "order_fees.json").write_text(json.dumps({"checked": now.isoformat(), "orders": out}, indent=1))
    return len(out)


def run() -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import get_active_item_ids, get_item
    try:
        print("scan:", scan_requests())
        print("demand:", demand_requests())
    except Exception as e:
        print("demand failed:", e)
    try:
        print("explore:", explore_requests())
    except Exception as e:
        print("explore failed:", e)
    try:
        print("order fees:", order_fees())
    except Exception as e:
        print("order fees failed:", e)
    cfg = load_config()
    ignore = set(map(str, cfg.get("sync", {}).get("ignore_items", [])))
    prods, tok, token = products(), app_token(), access_token()
    res, flagged = {}, 0
    for iid in get_active_item_ids(token):
        if iid in ignore or iid not in prods:
            continue
        try:
            lst = get_item(iid, token)
            live = ([v.price for v in lst.variations if v.available > 0] if lst.variations
                    else ([lst.price] if (lst.quantity or 0) - (lst.sold or 0) > 0 else []))
            comp = competitors(prods[iid], tok)
        except Exception as e:
            print("market:", iid, e)
            continue
        ours = min(live) if live else None
        row = {"title": lst.title[:80], "ours_min": ours, "live_sizes": len(live), "n": len(comp),
               "cheapest": comp[0] if comp else None,
               "median": round(statistics.median([c["price"] for c in comp]), 2) if comp else None,
               "others": comp[1:4]}
        if ours and comp:
            row["gap_pct"] = round((ours / comp[0]["price"] - 1) * 100, 1)
            row["flag"] = ours > comp[0]["price"] * 1.05
            flagged += row["flag"]
        res[iid] = row
        print(f"market {iid}: ours {ours} vs cheapest {comp[0]['price'] if comp else '-'} ({len(comp)} others)"
              f" · {lst.title[:50]}")
    if not res and OUT.exists():     # every lookup failed (e.g. eBay daily quota): keep the last good numbers
        return ["Price check skipped: eBay returned no data (quota?). Kept the previous numbers."]
    OUT.write_text(json.dumps({"checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                               "items": res}, indent=1))
    try:
        cats = ["15709", "53120", "24087"]   # athletic, dress, casual men's shoes
        return_options(cats)
    except Exception as e:
        print("return options:", e)
    return [f"Price check: {len(res)} listings compared, {flagged} priced more than 5% above another seller."]


def summary_line() -> str | None:
    """One FYI line for the morning update."""
    if not OUT.exists():
        return None
    items = json.loads(OUT.read_text()).get("items", {})
    hi = [v for v in items.values() if v.get("flag")]
    if not hi:
        return None
    return f"{len(hi)} listings cost more than another eBay seller's cheapest new pair (details in data/market.json)."


def return_options(category_ids: list[str]) -> dict:
    """Which return windows eBay allows in these categories (Metadata API). Read-only, for Rafael's decision."""
    r = requests.get("https://api.ebay.com/sell/metadata/v1/marketplace/EBAY_US/get_return_policies",
                     params={"filter": "categoryIds:{" + "|".join(category_ids) + "}"}, timeout=30,
                     headers={"Authorization": f"Bearer {app_token()}"})
    out = r.json() if r.ok else {"error": r.status_code, "text": r.text[:300]}
    (ROOT / "data" / "return_options.json").write_text(json.dumps(out, indent=1))
    return out
