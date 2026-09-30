from bot.config import load_config
from bot.profit import floor_price, landed_cost, net_profit, tier

CFG = load_config()


def test_landed_cost_us_and_overseas():
    assert round(landed_cost(500, CFG), 2) == round(500 * 1.06625 + 20, 2)
    assert landed_cost(500, CFG, overseas=True) > landed_cost(500, CFG)


def test_floor_price_clears_floor():
    landed = landed_cost(632, CFG)
    p = floor_price(landed, CFG)
    assert str(p).endswith(".99")
    assert net_profit(p, landed, CFG) >= 100
    assert net_profit(p - 1, landed, CFG) < 100


def test_tiers():
    assert tier(300, CFG) == "A" and tier(150, CFG) == "B" and tier(50, CFG) == "skip"
