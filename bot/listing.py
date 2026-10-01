"""New listings (M3): candidate file → draft → eBay check (Verify) → Rafael approves → live listing.

Candidate files live in data/candidates/<id>.yaml (written by the daily research task or by hand):

  id: dg-new-roma-black              # short slug, used in Telegram commands
  brand: Dolce & Gabbana
  model: New Roma
  colorway: Black
  style_code: CS2036A1065 80999
  category: sneaker                  # sneaker | loafer | dress_shoe | accessory
  department: Men
  color: Black
  upper_material: Leather            # only if verified
  size_system: IT                    # native system printed in the shoe
  retail_price: 725
  discontinued_verified: false
  photos: [https://...]              # eBay-hosted catalog photos or Rafael's own photos only
  price: 699.99                      # proposed eBay price (per size may override)
  sizes:
    - {us: "8", native: "41", cost: 324, source: END US, url: https://..., overseas: false, in_stock_sources: 2}

Rules applied here (CLAUDE.md): quantity 1 per size; a size is only included if it clears the $100 floor at
its own price AND has >= min_sources_per_size stores (or allow_single_source); price never below the floor
price; no photos → the draft is blocked ("needs photos") instead of listed.
"""
from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

from bot.config import ROOT, load_config
from bot.profit import floor_price, landed_cost, net_profit, tier

CANDIDATES = ROOT / "data" / "candidates"
STATE = ROOT / "data" / "drafts_state.json"      # {id: {"status": "sent|approved|skipped|live|blocked", "item_id": ...}}
PAUSE_FLAG = ROOT / "data" / "PAUSED"

CATEGORY_IDS = {           # eBay US leaf categories (eBay's Verify step rejects a wrong one before anything lists)
    "sneaker": "15709",     # Men's Sneakers
    "loafer": "53120",      # Men's Dress Shoes (Rafael's loafer listings live here)
    "dress_shoe": "53120",
    "belt": "2993",         # Men's Accessories > Belts
    "tie": "15662",         # Men's Accessories > Ties
}
TYPE = {"sneaker": "Sneaker", "loafer": "Loafer", "dress_shoe": "Dress", "belt": "Belt", "tie": "Tie"}
# variation name per category; None = one-size item (single SKU, quantity 1)
SIZE_NAME = {"sneaker": "US Shoe Size", "loafer": "US Shoe Size", "dress_shoe": "US Shoe Size",
             "belt": "Size", "tie": None}


@dataclass
class SizeLine:
    us: str
    native: str
    price: float
    cost: float
    source: str
    url: str
    net: float
    tier: str


@dataclass
class Draft:
    id: str
    title: str
    category_id: str
    specifics: dict
    description: str
    photos: list[str]
    sizes: list[SizeLine] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    blocked_reason: str | None = None

    @property
    def best_net(self) -> float:
        return max((s.net for s in self.sizes), default=0)


def build_title(c: dict) -> str:
    parts = [c["brand"], c["model"], c.get("colorway", ""), c.get("style_code", ""),
             f"{c.get('department', 'Men')}'s", "New"]
    if c.get("discontinued_verified"):
        parts.insert(-1, "Discontinued")
    title = " ".join(p for p in parts if p).replace("  ", " ")
    while len(title) > 80 and len(parts) > 3:     # drop least important words first
        for drop in ("New", "Discontinued"):
            if drop in parts:
                parts.remove(drop)
                break
        else:
            parts.pop(2)                          # colorway last resort
        title = " ".join(p for p in parts if p)
    return title[:80]


def build_specifics(c: dict) -> dict:
    s = {
        "Brand": c["brand"],
        "Model": c["model"],
        "Department": c.get("department", "Men"),
        "Type": TYPE.get(c["category"], "Casual"),
        "Style Code": c.get("style_code"),
        "Color": c.get("color") or c.get("colorway"),
        "Upper Material": c.get("upper_material"),
        "Product Line": c.get("product_line"),
    }
    return {k: v for k, v in s.items() if v}


def build_description(c: dict, sizes: list[SizeLine]) -> str:
    if c["category"] in ("belt", "tie"):
        size_note = ""
        if c["category"] == "belt":
            size_note = ("<p><b>Belt sizing:</b> sizes are listed as the brand marks them (usually cm to the middle hole). "
                         + "".join(f"{html.escape(s.us)} " for s in sizes) + "</p>")
        return (f"<h2>{html.escape(c['brand'])} {html.escape(c['model'])} — {html.escape(c.get('colorway',''))}</h2>"
                f"<p>Brand new with original packaging. Style code: {html.escape(c.get('style_code',''))}.</p>"
                f"{size_note}<p>All sales final.</p>")
    rows = "".join(f"<tr><td>US {html.escape(s.us)}</td><td>{html.escape(c.get('size_system','US'))} "
                   f"{html.escape(s.native)}</td></tr>" for s in sizes)
    return (
        f"<h2>{html.escape(c['brand'])} {html.escape(c['model'])} — {html.escape(c.get('colorway',''))}</h2>"
        f"<p>Brand new with original box. Style code: {html.escape(c.get('style_code',''))}.</p>"
        f"<p><b>Sizing:</b> choose your US size. The tag inside the shoe shows the brand's own "
        f"{html.escape(c.get('size_system','US'))} size:</p>"
        f"<table border='1' cellpadding='4'><tr><th>US</th><th>Brand size</th></tr>{rows}</table>"
        "<p>Every pair is inspected by eBay's Authenticity Guarantee before it ships to you.</p>"
        "<p>All sales final.</p>"
    )


def make_draft(c: dict, cfg: dict | None = None) -> Draft:
    cfg = cfg or load_config()
    min_src = cfg["risk"]["min_sources_per_size"]
    single_ok = cfg.get("sync", {}).get("allow_single_source", False)
    lines, skipped = [], []
    for s in c.get("sizes", []):
        if s.get("cost") in (None, ""):
            skipped.append(f"US {s['us']}: no source"); continue
        if s.get("in_stock_sources", 0) < min_src and not single_ok:
            skipped.append(f"US {s['us']}: only {s.get('in_stock_sources', 0)} store(s)"); continue
        landed = landed_cost(float(s["cost"]), cfg, overseas=bool(s.get("overseas")))
        price = max(float(s.get("price") or c.get("price") or 0), floor_price(landed, cfg))
        net = net_profit(price, landed, cfg)
        if tier(net, cfg) == "skip":
            skipped.append(f"US {s['us']}: net ${net:.0f}"); continue
        lines.append(SizeLine(str(s["us"]), str(s.get("native", "")), round(price, 2), float(s["cost"]),
                              s.get("source", ""), s.get("url", ""), round(net, 2), tier(net, cfg)))
    d = Draft(
        id=c["id"], title=build_title(c), category_id=CATEGORY_IDS.get(c["category"], "15709"),
        specifics=build_specifics(c), description=build_description(c, lines),
        photos=list(c.get("photos") or []), sizes=lines, skipped=skipped,
    )
    if c["category"] not in CATEGORY_IDS:
        d.blocked_reason = f"category '{c['category']}' not supported yet"
    elif not d.photos:
        d.blocked_reason = "needs photos (no eBay catalog photo found)"
    elif not d.sizes:
        d.blocked_reason = "no size clears the rules"
    return d


def build_add_xml(d: Draft, seller_profiles_xml: str, postal_code: str, size_name: str | None = "US Shoe Size") -> str:
    specifics = "".join(f"<NameValueList><Name>{escape(k)}</Name><Value>{escape(str(v))}</Value></NameValueList>"
                        for k, v in d.specifics.items())
    size_values = "".join(f"<Value>{escape(s.us)}</Value>" for s in d.sizes)
    variations = "".join(
        "<Variation>"
        f"<SKU>{escape(d.id)}-{escape(s.us)}</SKU><StartPrice>{s.price:.2f}</StartPrice><Quantity>1</Quantity>"
        f"<VariationSpecifics><NameValueList><Name>{escape(size_name or '')}</Name><Value>{escape(s.us)}</Value>"
        "</NameValueList></VariationSpecifics></Variation>" for s in d.sizes)
    if size_name is None:        # one-size item (e.g. a tie): single SKU at the single line's price
        body = (f"<StartPrice>{d.sizes[0].price:.2f}</StartPrice><Quantity>1</Quantity><SKU>{escape(d.id)}</SKU>")
    else:
        body = (f"<Variations><VariationSpecificsSet><NameValueList><Name>{escape(size_name)}</Name>{size_values}"
                f"</NameValueList></VariationSpecificsSet>{variations}</Variations>")
    pics = "".join(f"<PictureURL>{escape(u)}</PictureURL>" for u in d.photos[:24])
    return (
        "<Item>"
        f"<Title>{escape(d.title)}</Title>"
        f"<Description><![CDATA[{d.description}]]></Description>"
        f"<PrimaryCategory><CategoryID>{d.category_id}</CategoryID></PrimaryCategory>"
        "<ConditionID>1000</ConditionID>"
        "<Country>US</Country><Currency>USD</Currency>"
        f"<PostalCode>{escape(postal_code)}</PostalCode>"
        "<ListingDuration>GTC</ListingDuration><ListingType>FixedPriceItem</ListingType>"
        f"<PictureDetails>{pics}</PictureDetails>"
        f"<ItemSpecifics>{specifics}</ItemSpecifics>"
        f"{body}{seller_profiles_xml}"
        "</Item>"
    )


# ---------- state ----------
def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True))


def load_candidates() -> dict[str, dict]:
    out = {}
    for p in sorted(CANDIDATES.glob("*.yaml")) if CANDIDATES.exists() else []:
        c = yaml.safe_load(p.read_text())
        if c and c.get("id"):
            out[c["id"]] = c
    return out


def draft_message(d: Draft) -> str:
    lines = [f"👉 NEW LISTING for your OK: {d.title}", "",
             f"{len(d.sizes)} sizes ready. Each line: eBay price, your profit, where you'd buy it."]
    for s in d.sizes:
        lines.append(f"US {s.us}: sell ${s.price:.2f} · make ${s.net:.0f} · buy {s.source} ${s.cost:.0f}")
    if d.skipped:
        lines += ["", "Left out (not safe or not profitable): " + "; ".join(d.skipped)]
    lines += ["", f"Reply APPROVE {d.id} to list it, or SKIP {d.id}."]
    return "\n".join(lines)
