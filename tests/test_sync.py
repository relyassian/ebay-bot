from datetime import datetime, timedelta, timezone

from bot.config import load_config
from bot.ebay.trading import Listing, Variation
from bot.sync import Source, decide

import copy
CFG = copy.deepcopy(load_config())
CFG.setdefault('sync', {})['allow_single_source'] = False   # tests pin the strict 2-store rule
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
    assert not auto and notes[0][0] == "waiting"


def test_underwater_size_hidden_and_raise_proposed():
    auto, props, notes = decide(lst(("9", 699.99, 1, 0)), {("1", "9"): src(520)}, CFG, NOW)
    # a raise is needed: small enough (≤15%)? applied automatically and the size stays on sale
    need = [c for c in auto if c.new_price]
    if need and need[0].new_price <= 699.99 * 1.15:
        assert avail(auto) == {"9": 1} and notes[0][0] == "raised"
    else:
        assert avail(auto) == {"9": 0}
    assert not props


def test_unrealistic_raise_not_proposed():
    # the store costs so much the price would need +50%: just stay off sale, don't bother Rafael
    auto, props, notes = decide(lst(("9", 699.99, 1, 0)), {("1", "9"): src(650)}, CFG, NOW)
    assert avail(auto) == {"9": 0} and not props and notes[0][0] == "hidden"


def test_stale_data_does_not_relist():
    auto, _, _ = decide(lst(("9", 899.99, 1, 1)), {("1", "9"): src(450, age_h=72)}, CFG, NOW)
    assert not auto


def test_no_data_hides_live_size():
    # no price data = can't promise the pair can be bought → off sale (cancellation guard)
    auto, props, notes = decide(lst(("9", 899.99, 1, 0)), {}, CFG, NOW)
    assert [c.new_available for c in auto] == [0] and not props
    assert notes[0][0] == "hidden"


def test_single_source_relists_when_allowed():
    cfg = copy.deepcopy(CFG); cfg["sync"]["allow_single_source"] = True
    auto, _, _ = decide(lst(("9", 899.99, 1, 1)), {("1", "9"): src(450, n=1)}, cfg, NOW)
    assert avail(auto) == {"9": 1}
