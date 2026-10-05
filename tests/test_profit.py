from bot.config import load_config
from bot.profit import floor_price, landed_cost, net_profit, tier

CFG = load_config()


def test_landed_cost_us_and_overseas():
    # shoes ship to NJ, which doesn't tax footwear: no sales tax
    assert round(landed_cost(500, CFG), 2) == 520.00
    # taxable items (e.g. cufflinks) pay NJ 6.625%
    assert round(landed_cost(500, CFG, taxable=True), 2) == round(500 * 1.06625 + 20, 2)
    assert landed_cost(500, CFG, overseas=True) > landed_cost(500, CFG)


def test_floor_price_clears_floor():
    landed = landed_cost(632, CFG)
    p = floor_price(landed, CFG)
    assert str(p).endswith(".99")
    assert net_profit(p, landed, CFG) >= 100
    assert net_profit(p - 1, landed, CFG) < 100


def test_tiers():
    assert tier(300, CFG) == "A" and tier(150, CFG) == "B" and tier(50, CFG) == "skip"


def test_ad_price_cover_keeps_profit():
    from bot.ads import covered_price
    from bot.config import load_config
    from bot.profit import net_profit
    cfg = load_config()
    base = dict(cfg, profit=dict(cfg["profit"], promoted_rate=0.0))
    ads = dict(cfg, profit=dict(cfg["profit"], promoted_rate=0.08))
    new = covered_price(899.99, 0.08, cfg)
    assert 985 < new < 1000
    assert net_profit(new, 600, ads) >= net_profit(899.99, 600, base) - 1
