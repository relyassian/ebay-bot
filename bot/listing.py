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
  made_in: Italy                     # optional, only if verified
  highlights: [Leather upper, Rubber sole]   # optional, verified features from the brand/store page
  included: [Shoes, Original box, Dust bag]  # optional, only what the source confirms; default = item + box
  fit_note: Runs true to size        # optional, only if verified
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
from bot.profit import floor_price, is_taxable, landed_cost, net_profit, tier

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


STYLE = {"sneaker": "Sneaker", "loafer": "Loafer"}   # eBay requires Style in the shoe categories


TITLE_BRAND = {"Salvatore Ferragamo": "Ferragamo"}


def build_title(c: dict) -> str:
    """Brand Model Colour Men's New (80 max). Trim order: New → Men's → short brand → model words.
    No style code (kept internal only so buyers can't easily price-compare)."""
    brand, model = c["brand"], c["model"].split()
    tail = [c.get("colorway", "")]          # style code never shown on eBay (Rafael, Oct 1: harder to price-compare)
    extra = [f"{c.get('department', 'Men')}'s", "New"]
    if c.get("discontinued_verified"):
        extra.insert(0, "Discontinued")
    join = lambda: " ".join(p for p in [brand, *model, *tail, *extra] if p)
    while len(join()) > 80:
        if "New" in extra:
            extra.remove("New")
        elif extra and extra[-1].endswith("'s"):
            extra.pop()
        elif brand in TITLE_BRAND:
            brand = TITLE_BRAND[brand]
        elif len(model) > 1:
            model.pop()
        else:
            break
    return join()[:80]


def build_specifics(c: dict) -> dict:
    s = {
        "Brand": c["brand"],
        "Model": c["model"],
        "Department": c.get("department", "Men"),
        "Type": TYPE.get(c["category"], "Casual"),
        "Color": c.get("color") or c.get("colorway"),
        "Upper Material": c.get("upper_material"),
        "Product Line": c.get("product_line"),
        "Style": c.get("style") or STYLE.get(c["category"]),
    }
    return {k: v for k, v in s.items() if v}


_CSS = {  # inline styles only: eBay strips <style>/<script>; this reads well on phones (most buyers)
    "wrap": "max-width:760px;margin:0 auto;font-family:Helvetica,Arial,sans-serif;color:#1a1a1a;line-height:1.55;",
    "brand": "font-size:13px;letter-spacing:3px;text-transform:uppercase;color:#777;margin:0 0 4px;",
    "h1": "font-size:24px;font-weight:600;margin:0 0 6px;",
    "sub": "font-size:15px;color:#555;margin:0 0 20px;",
    "badge": "display:inline-block;border:1px solid #1a1a1a;padding:4px 10px;font-size:12px;letter-spacing:1px;"
             "text-transform:uppercase;margin:0 6px 6px 0;",
    "h2": "font-size:13px;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #ddd;"
          "padding-bottom:6px;margin:26px 0 10px;",
    "table": "border-collapse:collapse;width:100%;font-size:14px;",
    "th": "text-align:left;background:#f4f4f4;padding:8px;border:1px solid #e2e2e2;",
    "td": "padding:8px;border:1px solid #e2e2e2;",
    "p": "font-size:14px;margin:0 0 10px;",
    "foot": "font-size:12px;color:#777;margin-top:26px;",
}
SHOES = ("sneaker", "loafer", "dress_shoe")


def _rows(pairs: list[tuple[str, str]]) -> str:
    return "".join(f"<tr><td style='{_CSS['td']}width:38%;color:#555;'>{html.escape(k)}</td>"
                   f"<td style='{_CSS['td']}'>{html.escape(str(v))}</td></tr>" for k, v in pairs if v)


def build_description(c: dict, sizes: list[SizeLine]) -> str:
    """Professional, mobile-friendly description. Only facts from the candidate file (verified) are shown."""
    e, cat = html.escape, c["category"]
    shoe = cat in SHOES
    box = "original box" if shoe else "original packaging"
    badges = ["Brand new", f"With {box}"] + (["eBay Authenticity Guarantee"] if shoe else []) + ["Free shipping"]
    details = [("Brand", c["brand"]), ("Model", c["model"]), ("Colour", c.get("colorway") or c.get("color")),
("Material", c.get("upper_material")),
               ("Made in", c.get("made_in")), ("Condition", f"New with {box}, never worn")]
    out = [f"<div style='{_CSS['wrap']}'>",
           f"<p style='{_CSS['brand']}'>{e(c['brand'])}</p>",
           f"<h1 style='{_CSS['h1']}'>{e(c['model'])}</h1>",
           f"<p style='{_CSS['sub']}'>{e(c.get('colorway', ''))}</p>",
           "<div>" + "".join(f"<span style='{_CSS['badge']}'>{e(b)}</span>" for b in badges) + "</div>"]
    if c.get("highlights"):       # verified product features only (from the brand/store page)
        out += [f"<h2 style='{_CSS['h2']}'>Highlights</h2><ul style='font-size:14px;padding-left:18px;margin:0;'>"]
        out += [f"<li style='margin-bottom:4px;'>{e(h)}</li>" for h in c["highlights"]] + ["</ul>"]
    out += [f"<h2 style='{_CSS['h2']}'>Details</h2><table style='{_CSS['table']}'>{_rows(details)}</table>"]
    if shoe and sizes:
        system = c.get("size_system", "US")
        rows = "".join(f"<tr><td style='{_CSS['td']}'>US {e(s.us)}</td><td style='{_CSS['td']}'>{e(system)} {e(s.native)}</td></tr>"
                       for s in sizes)
        out += [f"<h2 style='{_CSS['h2']}'>Size guide</h2>",
                f"<p style='{_CSS['p']}'>Choose your <b>US</b> size from the menu. The label inside the shoe shows "
                f"{e(c['brand'])}'s own {e(system)} size:</p>",
                f"<table style='{_CSS['table']}'><tr><th style='{_CSS['th']}'>US size</th>"
                f"<th style='{_CSS['th']}'>Size on the shoe</th></tr>{rows}</table>"]
        if c.get("fit_note"):
            out.append(f"<p style='{_CSS['p']}margin-top:10px;'>{e(c['fit_note'])}</p>")
    elif cat == "belt" and sizes:
        out += [f"<h2 style='{_CSS['h2']}'>Size guide</h2>",
                f"<p style='{_CSS['p']}'>Belt sizes are as the brand marks them (usually cm, measured to the middle hole). "
                f"Available: {e(', '.join(s.us for s in sizes))}.</p>"]
    included = c.get("included") or [f"The item, in its {box}"]
    out += [f"<h2 style='{_CSS['h2']}'>What's included</h2>",
            "<ul style='font-size:14px;padding-left:18px;margin:0;'>"
            + "".join(f"<li>{e(i)}</li>" for i in included) + "</ul>"]
    days = c.get("handling_days", 3)
    ship = (f"Free shipping. Ships within {days} business days. Because this is a luxury item, it first goes to "
            "eBay's independent authenticators, who inspect it and then send it on to you."
            if shoe else f"Free shipping. Ships within {days} business days.")
    out += [f"<h2 style='{_CSS['h2']}'>Shipping</h2><p style='{_CSS['p']}'>{ship}</p>",
            f"<h2 style='{_CSS['h2']}'>Questions</h2><p style='{_CSS['p']}'>Message us any time before you buy: "
            "sizing, details, extra photos. We reply quickly.</p>",
            f"<p style='{_CSS['foot']}'>All sales are final; please check your size before you buy. "
            "Thank you for shopping with us.</p></div>"]
    return "".join(out)


def excluded_reason(c: dict, cfg: dict) -> str | None:
    """Rafael's rule (Oct 4): never list anything connected to idol worship (excluded brands, or logos/motifs
    like Medusa or crosses). Brand checked exactly; words checked as whole words in model/colorway/title."""
    import re
    ex = cfg.get("exclude", {})
    brand = (c.get("brand") or "").lower()
    if any(brand == b.lower() or brand.startswith(b.lower() + " ") for b in ex.get("brands", [])):
        return f"excluded brand ({c.get('brand')})"
    text = " ".join(str(c.get(k, "")) for k in ("model", "colorway", "title")).lower()
    for w in ex.get("words", []):
        if re.search(rf"\b{re.escape(w.lower())}\b", text):
            return f"excluded word in the product name ({w})"
    return None


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
        landed = landed_cost(float(s["cost"]), cfg, overseas=bool(s.get("overseas")),
                             taxable=is_taxable(cfg, category=c.get("category")))
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
    if (bad := excluded_reason(c, cfg)):
        d.blocked_reason = bad
    elif c["category"] not in CATEGORY_IDS:
        d.blocked_reason = f"category '{c['category']}' not supported yet"
    elif not d.photos:
        d.blocked_reason = "needs photos (no eBay catalog photo found)"
    elif not d.sizes:
        d.blocked_reason = "no size clears the rules"
    return d


def best_offer_xml(line: SizeLine, cfg: dict | None = None) -> str:
    """Best Offer only for big-margin single items (eBay forbids it on multi-variation listings)."""
    cfg = cfg or load_config()
    if line.net < cfg["listing"].get("best_offer_min_net", 10**9):
        return ""
    landed = line.price * (1 - cfg["profit"]["ebay_fee_rate"] - cfg["profit"]["promoted_rate"]
                           - cfg["profit"]["inad_buffer_rate"]) - line.net
    accept = min(floor_price(landed, cfg, net_target=cfg["profit"]["target"]), line.price)
    decline = floor_price(landed, cfg)
    return ("<BestOfferDetails><BestOfferEnabled>true</BestOfferEnabled></BestOfferDetails>"
            f"<ListingDetails><BestOfferAutoAcceptPrice>{accept:.2f}</BestOfferAutoAcceptPrice>"
            f"<MinimumBestOfferPrice>{decline:.2f}</MinimumBestOfferPrice></ListingDetails>")


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
        body += best_offer_xml(d.sizes[0])
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
    lines += ["", f"Reply \"yes {d.id}\" to list it, or \"no {d.id}\" (or just tell me in your own words)."]
    text = "\n".join(lines)
    return {"photo": d.photos[0], "text": text} if d.photos and len(text) <= 1024 else text
