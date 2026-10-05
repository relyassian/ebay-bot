"""Net-profit math from CLAUDE.md. Pure functions, so they are easy to test."""
from __future__ import annotations

import math


def store_shipping(cfg: dict, source: str | None) -> float | None:
    """Real checkout shipping for stores we've measured (config profit.store_shipping), else None (= default)."""
    s = (source or "").lower()
    for store, cost in (cfg["profit"].get("store_shipping") or {}).items():
        if s.startswith(store.lower()):
            return float(cost)
    return None


def landed_cost(source_price: float, cfg: dict, *, shipping: float | None = None,
                overseas: bool = False, promo_off: float = 0.0, taxable: bool = False) -> float:
    """Everything ships to eBay's authenticator in New Jersey, and NJ doesn't tax clothing or footwear
    (shoes, belts, ties are exempt; jewelry like cufflinks is taxed). So sales tax applies only when taxable."""
    p = cfg["profit"]
    base = max(source_price - promo_off, 0)
    ship = p["default_shipping"] if shipping is None else shipping
    duty = base * p["overseas_duty_rate"] if overseas else 0
    tax = p["sales_tax_rate"] if taxable else 0
    return base * (1 + tax) + ship + duty


def is_taxable(cfg: dict, item_id: str | None = None, category: str | None = None) -> bool:
    if item_id and str(item_id) in set(map(str, cfg["profit"].get("taxable_items", []))):
        return True
    return bool(category) and category in cfg["profit"].get("taxable_categories", [])


def net_profit(ebay_price: float, landed: float, cfg: dict, *, reship: bool = False) -> float:
    p = cfg["profit"]
    keep = 1 - p["ebay_fee_rate"] - p["promoted_rate"] - p["inad_buffer_rate"]
    return ebay_price * keep - landed - (p["reship_cost"] if reship else 0)


def required_net(price: float, cfg: dict, base: float | None = None) -> float:
    """Minimum profit for a sale at `price` (Rafael, Oct 5): the floor ($100, or a brand's own minimum such as
    Louis Vuitton $200); above $1,500 at least $300, plus $100 for every further $500."""
    p = cfg["profit"]
    need = p["floor"] if base is None else base
    t = p.get("price_tiers") or {}
    if t and price > t["above"]:
        need = max(need, t["min_net"] + t["step_net"] * math.floor((price - t["above"]) / t["step_price"]))
    return need


def item_min_net(cfg: dict, item_id: str | None = None, brand: str | None = None) -> float:
    """Base minimum profit for an item: brand minimum (config profit.brand_min_net) or the global floor."""
    p = cfg["profit"]
    mins = p.get("brand_min_net") or {}
    if brand:
        for b, v in mins.items():
            if brand.lower().startswith(b.lower()):
                return float(v)
    if item_id:
        import json
        from bot.config import ROOT
        f = ROOT / "data" / "item_min_net.json"
        if f.exists():
            v = json.loads(f.read_text()).get(str(item_id))
            if v:
                return float(v)
    return float(p["floor"])


def floor_price(landed: float, cfg: dict, *, reship: bool = False, net_target: float | None = None,
                base: float | None = None) -> float:
    """Lowest eBay price (ending in .99) that clears the required profit at that price (tiered above $1,500).
    net_target = a fixed profit target instead (e.g. Tier A)."""
    if net_target is None:
        target = cfg["profit"]["floor"] if base is None else base
        for _ in range(12):
            price = floor_price(landed, cfg, reship=reship, net_target=target)
            need = required_net(price, cfg, base)
            if need <= target:
                return price
            target = need
        return price
    p = cfg["profit"]
    target = net_target
    keep = 1 - p["ebay_fee_rate"] - p["promoted_rate"] - p["inad_buffer_rate"]
    raw = (target + landed + (p["reship_cost"] if reship else 0)) / keep
    return math.ceil(raw + 0.01) - 0.01


def tier(net: float, cfg: dict) -> str:
    p = cfg["profit"]
    if net >= p["target"]:
        return "A"
    if net >= p["floor"]:
        return "B"
    return "skip"
