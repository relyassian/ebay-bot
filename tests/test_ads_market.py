from types import SimpleNamespace as NS

from bot.ads import best_rate
from bot.config import load_config
from bot.market import _matches


def _listing(price):
    v = NS(size="10", price=price, available=1)
    return NS(item_id="X1", variations=[v], price=price, quantity=1, sold=0)


def test_best_rate_picks_highest_that_keeps_margin():
    cfg = load_config()
    src = {("X1", "10"): NS(cost=400.0, overseas=False, source="GOAT")}
    # very profitable at $1,000: should take the top step
    assert best_rate(_listing(1000), src, cfg, [0.08, 0.10, 0.12, 0.15]) == 0.15
    # thin margin: no step keeps 1.5x the floor
    assert best_rate(_listing(640), src, cfg, [0.08, 0.10, 0.12, 0.15]) is None


def test_best_rate_needs_a_source():
    cfg = load_config()
    assert best_rate(_listing(1000), {}, cfg, [0.08, 0.15]) is None


def test_market_match():
    p = {"brand": "Gucci", "model": "Ace Sneaker", "style_code": "386750 A38G0 9064"}
    assert _matches("Gucci Men's Ace Sneaker White Leather Size 10", p)
    assert _matches("GUCCI 386750A38G0 9064 trainers", p)
    assert not _matches("Gucci Rhyton Sneaker", p)
