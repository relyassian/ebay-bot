from datetime import datetime, timedelta, timezone

from bot.config import load_config
from bot.ebay.trading import Listing, Variation
from bot.sync import Source, decide

CFG = load_config()
NOW = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
S = "US Shoe Size"


def lst(*vs):
    return Listing("1", "Gucci Test", None, None, None,
                   [Variation({S: size}, price, qty, sold) for size, price, qty, sold in vs])


def src(cost, n=2, age_h=1, overseas=False):
    return Source(cost, "StockX", "https://x", overseas, n, NOW - timedelta(hours=age_h))


def avail(changes):
    return {c.size: c.new_available for c in changes}


def test_hides_size_with_no_source():
    auto, props, _ = decide(lst(("9", 899.99, 1, 0)), {("1", "9"): src(None)}, CFG, NOW)
    assert avail(auto) == {"9": 0} and not props


def test_relists_sold_size_when_profitable_with_two_sources():
    auto, props, _ = decide(lst(("9", 899.99, 1, 1)), {("1", "9"): src(450)}, CFG, NOW)
    assert avail(auto) == {"9": 1} and not props


def test_keeps_hidden_with_single_source():
    auto, _, notes = decide(lst(("9", 899.99, 1, 1)), {("1", "9"): src(450, n=1)}, CFG, NOW)
    assert not auto and "only 1 source" in notes[0]


def test_underwater_size_hidden_and_raise_proposed():
    auto, props, _ = decide(lst(("9", 699.99, 1, 0)), {("1", "9"): src(650)}, CFG, NOW)
    assert avail(auto) == {"9": 0}
    assert props and props[0][3] > 699.99


def test_stale_data_does_not_relist():
    auto, _, _ = decide(lst(("9", 899.99, 1, 1)), {("1", "9"): src(450, age_h=72)}, CFG, NOW)
    assert not auto


def test_no_data_leaves_live_size_alone():
    auto, props, _ = decide(lst(("9", 899.99, 1, 0)), {}, CFG, NOW)
    assert not auto and not props
