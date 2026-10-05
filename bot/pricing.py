"""Price testing (CLAUDE.md Pricing 3–4): start high, and if a size hasn't sold after `decay_after_days`
at the same price, drop it `decay_step` (3%), never below the price that still nets the $100 floor.
Price drops are pre-approved. Every size's starting price and every change is kept in data/price_log.json,
and each sale is appended to data/sales_log.csv (start price vs. sold price), so we learn what sells.

price_log.json: {item_id: {size: {"start": first price seen, "price": current, "since": ISO time the
current price was first seen, "drops": n}}}
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timedelta, timezone

from bot.config import ROOT
from bot.profit import floor_price, landed_cost

LOG = ROOT / "data" / "price_log.json"
SALES = ROOT / "data" / "sales_log.csv"


def load_log() -> dict:
    return json.loads(LOG.read_text()) if LOG.exists() else {}


def save_log(d: dict) -> None:
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text(json.dumps(d, indent=1, sort_keys=True))


def _iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def track(log: dict, item_id: str, size: str | None, price: float, now: datetime) -> dict:
    """Record the size's current price; a new price (from anywhere) restarts the clock."""
    row = log.setdefault(item_id, {}).setdefault(size or "", {"start": price, "price": price, "since": _iso(now),
                                                               "drops": 0})
    if abs(row["price"] - price) > 0.005:
        row.update(price=price, since=_iso(now))
    return row


def decay_price(price: float, cost: float, overseas: bool, cfg: dict, taxable: bool = False) -> float | None:
    """Next lower price (−step, ending .99), or None if that would go below the floor price."""
    step = cfg.get("pricing", {}).get("decay_step", 0.03)
    floor = floor_price(landed_cost(cost, cfg, overseas=overseas, taxable=taxable), cfg)
    new = math.floor(price * (1 - step)) - 0.01
    new = max(new, floor)
    return new if new < price - 0.5 else None


def due(row: dict, now: datetime, cfg: dict) -> bool:
    days = cfg.get("pricing", {}).get("decay_after_days", 7)
    since = datetime.fromisoformat(row["since"].replace("Z", "+00:00"))
    return now - since >= timedelta(days=days)


def log_sale(item_id: str, size: str | None, title: str, sold_price: float, order_id: str) -> None:
    """Append start price vs. sold price for this size (Pricing rule 4)."""
    row = load_log().get(item_id, {}).get(size or "", {})
    new = not SALES.exists()
    with SALES.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "order_id", "item_id", "size", "title", "start_price", "sold_price", "price_drops"])
        w.writerow([_iso(datetime.now(timezone.utc)), order_id, item_id, size or "", title,
                    row.get("start", ""), f"{sold_price:.2f}", row.get("drops", "")])
