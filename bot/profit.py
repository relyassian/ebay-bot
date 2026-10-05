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


def floor_price(landed: float, cfg: dict, *, reship: bool = False, net_target: float | None = None) -> float:
    """Lowest eBay price (ending in .99) that still clears the net target (default: the floor)."""
    p = cfg["profit"]
    target = p["floor"] if net_target is None else net_target
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
