"""The one morning Telegram update (Rafael, Oct 5): short, to the point — sales, views/watchers, what changed,
and only what needs him. New listings and price changes are not announced separately."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from bot.config import ROOT, load_config

STATS = ROOT / "data" / "stats.json"
DAYLOG = ROOT / "data" / "day_log.json"
SENT = ROOT / "data" / "last_digest_date.txt"
NY = ZoneInfo("America/New_York")


def log_changes(counts: dict) -> None:
    """Called by every sync run: accumulate size counts per change kind until the next morning update."""
    d = json.loads(DAYLOG.read_text()) if DAYLOG.exists() else {}
    for k, v in counts.items():
        d[k] = d.get(k, 0) + v
    DAYLOG.write_text(json.dumps(d))


def due() -> bool:
    now = datetime.now(NY)
    return now.hour >= 6 and (not SENT.exists() or SENT.read_text().strip() != now.strftime("%Y-%m-%d"))


def _stats(token: str) -> dict:
    """Views (HitCount), watchers and sizes on sale for every active listing."""
    from bot.ebay.trading import NS, _call, get_active_item_ids
    from bot.report import short_name
    cfg = load_config().get("sync", {})
    ignore = set(map(str, cfg.get("ignore_items", [])))
    out = {}
    for iid in get_active_item_ids(token):
        if iid in ignore:
            continue
        it = _call("GetItem", f"<ItemID>{iid}</ItemID><DetailLevel>ReturnAll</DetailLevel>"
                              "<IncludeWatchCount>true</IncludeWatchCount>", token).find("e:Item", NS)
        t = lambda p: it.findtext(p, namespaces=NS)
        title = t("e:Title") or ""
        if any(w.lower() in title.lower() for w in cfg.get("ignore_title_words", [])):
            continue
        vs = it.findall("e:Variations/e:Variation", NS)
        live = sum(1 for v in vs if int(v.findtext("e:Quantity", namespaces=NS) or 0)
                   - int(v.findtext("e:SellingStatus/e:QuantitySold", namespaces=NS) or 0) > 0) if vs else \
            int((int(t("e:Quantity") or 0) - int(t("e:SellingStatus/e:QuantitySold") or 0)) > 0)
        out[iid] = {"name": short_name(title, 34), "views": int(t("e:HitCount") or 0),
                    "watchers": int(t("e:WatchCount") or 0), "live": live}
    return out


def _views(ids: list[str]) -> tuple[dict, dict] | None:
    """Listing page views per listing from eBay's Analytics API: (yesterday, last 7 days).
    None when the token lacks the analytics scope (Rafael must re-approve once via connect-ebay)."""
    import requests
    from datetime import timedelta
    from bot.ebay.auth import access_token
    try:
        tok = access_token(analytics=True)
    except Exception as e:
        print("views unavailable:", e)
        return None
    end = datetime.now(NY).date() - timedelta(days=1)
    out = []
    for start in (end, end - timedelta(days=6)):
        got = {}
        for i in range(0, len(ids), 200):
            f = (f"marketplace_ids:{{EBAY_US}},date_range:[{start:%Y%m%d}..{end:%Y%m%d}],"
                 f"listing_ids:{{{'|'.join(ids[i:i + 200])}}}")
            r = requests.get("https://api.ebay.com/sell/analytics/v1/traffic_report",
                             params={"dimension": "LISTING", "metric": "LISTING_VIEWS_TOTAL", "filter": f},
                             headers={"Authorization": f"Bearer {tok}"}, timeout=60)
            if r.status_code != 200:
                print("views error:", r.status_code, r.text[:300])
                return None
            for rec in r.json().get("records", []):
                got[rec["dimensionValues"][0]["value"]] = int(float(rec["metricValues"][0].get("value") or 0))
        out.append(got)
    return out[0], out[1]


def build(token: str) -> str:
    from bot.notices import pop_all
    now = datetime.now(NY)
    today = now.strftime("%Y-%m-%d")
    hist = json.loads(STATS.read_text()) if STATS.exists() else {}
    older = [k for k in hist if k < today]
    prev = hist[max(older)] if older else {}
    cur = _stats(token)
    hist[today] = cur

    on_sale = [i for i, v in cur.items() if v["live"]]
    watchers = sum(v["watchers"] for v in cur.values())
    dw = watchers - sum(v.get("watchers", 0) for v in prev.values()) if prev else None
    sign = lambda x: "" if x is None else f" ({'+' if x >= 0 else ''}{x})"
    views = _views(list(cur))
    if views:                                   # keep per-listing views (yesterday / last 7 days) for later decisions
        for i, v in cur.items():
            v["views"], v["views_7d"] = views[0].get(i, 0), views[1].get(i, 0)
    STATS.write_text(json.dumps({k: hist[k] for k in sorted(hist)[-14:]}))
    lines = [f"<b>☀️ Morning update · {now:%a %b %-d}</b>"]
    # sales since the last update
    sold = []
    f = ROOT / "data" / "sales_log.csv"
    last = SENT.read_text().strip() if SENT.exists() else ""
    if f.exists():
        sold = [r for r in csv.DictReader(f.open()) if r["date"][:10] >= last]
    lines.append(f"<b>💰 Sales: {len(sold)} since yesterday</b>" + "".join(
        f"\n• {escape(r['title'][:40])} US {r['size']} · ${float(r['sold_price']):,.0f}" for r in sold)
        if sold else "Sales: none yet")
    lines.append(f"On sale: {len(on_sale)} listings · {sum(cur[i]['live'] for i in on_sale)} sizes")
    if views:
        y, wk = views
        lines.append(f"Views: {sum(y.values()):,} yesterday · {sum(wk.values()):,} this week")
    else:
        lines.append("Views: not connected yet (needs one eBay re-approval)")
    lines.append(f"Watchers: {watchers}{sign(dw)}")
    wk = views[1] if views else {}
    top = sorted(cur.items(), key=lambda kv: (kv[1]["watchers"], wk.get(kv[0], 0)), reverse=True)[:3]
    if top and top[0][1]["watchers"] + wk.get(top[0][0], 0) > 0:
        lines.append("Most interest: " + "; ".join(
            f"{escape(v['name'])} ({v['watchers']} watching" + (f", {wk.get(i, 0)} views/wk" if views else "") + ")"
            for i, v in top))
    day = json.loads(DAYLOG.read_text()) if DAYLOG.exists() else {}
    label = {"new": "new listings", "relisted": "sizes back on sale", "hidden": "sizes off sale",
             "lowered": "price drops", "raised": "small raises", "titles": "titles improved"}
    ch = [f"{day[k]} {label[k]}" for k in label if day.get(k)]
    if ch:
        lines.append("Since yesterday: " + " · ".join(ch))
    DAYLOG.write_text("{}")
    needs = pop_all()
    # Rafael (Oct 6): only things he can actually act on go under "Needs you". Missing photos (he doesn't own the
    # shoes) and eBay's selling limit are FYI, one short line each.
    act = [n for n in needs if n["kind"] in ("approve", "problem")]
    photos = [n for n in needs if n["kind"] == "photos"]
    st = ROOT / "data" / "drafts_state.json"
    waiting = sum(1 for v in (json.loads(st.read_text()).values() if st.exists() else [])
                  if v.get("status") == "waiting_limit")
    fyi = []
    if waiting:
        fyi.append(f"{waiting} new products ready but waiting for eBay selling-limit room (lists itself when room opens)")
    if photos:
        fyi.append(f"{len(photos)} profitable products skipped: no eBay stock photo")
    if fyi:
        lines.append("FYI: " + " · ".join(fyi))
    if act:
        lines.append("")
        lines.append("<b>⚠️ Needs you:</b>")
        icon = {"approve": "⏳", "problem": "⚠️"}
        lines += [f"{icon.get(n['kind'], '•')} {escape(n['text'])}" for n in act[:6]]
        if len(act) > 6:
            lines.append(f"…and {len(act) - 6} more")
    else:
        lines.append("Nothing for you to do.")
    SENT.write_text(today + "\n")
    return "\n".join(lines)
