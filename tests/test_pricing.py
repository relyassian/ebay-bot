import copy
from datetime import datetime, timedelta, timezone

from bot.config import load_config
from bot.ebay.trading import Listing, Variation
from bot.sync import Source, decays

CFG = copy.deepcopy(load_config())
NOW = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)


def lst(price, avail=1):
    return Listing("1", "Gucci Test", None, None, None, [Variation({"US Shoe Size": "9"}, price, avail, 0)])


def src(cost):
    return {("1", "9"): Source(cost, "StockX", "", False, 1, NOW - timedelta(hours=2))}


def log_since(days, price):
    t = (NOW - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"1": {"9": {"start": price, "price": price, "since": t, "drops": 0}}}


def test_drops_3pct_after_7_days():
    out = decays(lst(999.99), src(450), CFG, log_since(8, 999.99), [], NOW)
    assert len(out) == 1 and 965 <= out[0].new_price <= 970


def test_no_drop_before_7_days():
    assert not decays(lst(999.99), src(450), CFG, log_since(3, 999.99), [], NOW)


def test_never_below_floor():
    # cost 700: floor price ≈ $1,059 → a size at $1,065 can only go to the floor, one at the floor stays
    out = decays(lst(1065.99), src(700), CFG, log_since(8, 1065.99), [], NOW)
    from bot.profit import floor_price, landed_cost
    floor = floor_price(landed_cost(700, CFG, shipping=14.95), CFG)   # StockX: measured $14.95 shipping
    assert out and out[0].new_price == floor
    assert not decays(lst(floor), src(700), CFG, log_since(8, floor), [], NOW)


def test_new_size_starts_clock_and_off_sale_not_dropped():
    log = {}
    assert not decays(lst(999.99), src(450), CFG, log, [], NOW) and log["1"]["9"]["price"] == 999.99
    assert not decays(lst(999.99, avail=0), src(450), CFG, log_since(30, 999.99), [], NOW)


def test_price_change_restarts_clock():
    log = log_since(8, 1099.99)                        # price was changed elsewhere since
    assert not decays(lst(999.99), src(450), CFG, log, [], NOW)
