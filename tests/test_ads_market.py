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


def test_match_rejects_other_colorways_and_womens():
    p = {"brand": "Gucci", "model": "Basket", "colorway": "White Demetra Red"}
    assert _matches("Gucci Basket Low White Demetra Red Men's 9", p)
    assert not _matches("Gucci Basket Low Green White Demetra", p)
    assert not _matches("Gucci Basket Women's White Demetra Red", p)


def test_priced_for_market(monkeypatch, tmp_path):
    import bot.newlistings as nl
    monkeypatch.setattr(nl, "MKT_CACHE", tmp_path / "m.json")
    import bot.market as mk
    c = {"brand": "Gucci", "model": "Ace", "category": "sneaker",
         "sizes": [{"us": "9", "cost": 300.0, "price": 900.0, "source": "GOAT"},
                   {"us": "10", "cost": 600.0, "price": 1100.0, "source": "GOAT"}]}
    monkeypatch.setattr(mk, "product_market", lambda p: {"n": 10, "median": 700.0, "cheapest": 500.0})
    out, why = nl.priced_for_market("x", c)
    assert why is None and [s["us"] for s in out["sizes"]] == ["9"] and out["sizes"][0]["price"] == 699.99
    monkeypatch.setattr(mk, "product_market", lambda p: {"n": 1, "median": 300.0, "cheapest": 300.0})
    (tmp_path / "m.json").unlink()
    out, why = nl.priced_for_market("y", c)
    assert why is None and len(out["sizes"]) == 2      # no real competition: keep our prices


def test_market_drops_never_below_floor(monkeypatch):
    from datetime import datetime, timezone
    import bot.market as mk
    from bot.sync import market_drops
    cfg = load_config()
    now = datetime.now(timezone.utc)
    v1 = NS(size="9", price=900.0, available=1)
    v2 = NS(size="10", price=900.0, available=1)
    lst = NS(item_id="X1", variations=[v1, v2], price=None, quantity=None, sold=None)
    src = {("X1", "9"): NS(cost=300.0, overseas=False, source="GOAT", checked_at=now),
           ("X1", "10"): NS(cost=480.0, overseas=False, source="GOAT", checked_at=now)}
    monkeypatch.setattr(mk, "market_for", lambda iid: {"median": 700.0, "n": 8})
    ch = {c.size: c.new_price for c in market_drops(lst, src, cfg, [], now=now)}
    assert ch["9"] == 699.99                       # matched the market
    assert 700 < ch["10"] < 900                    # as close as the 1.5x floor allows


def test_floor100_items_go_lower(monkeypatch):
    from datetime import datetime, timezone
    import bot.market as mk
    from bot.sync import market_drops
    cfg = load_config()
    now = datetime.now(timezone.utc)
    lst = NS(item_id="X9", variations=[NS(size="10", price=900.0, available=1)], price=None, quantity=None, sold=None)
    src = {("X9", "10"): NS(cost=480.0, overseas=False, source="GOAT", checked_at=now)}
    monkeypatch.setattr(mk, "market_for", lambda iid: {"median": 500.0, "n": 8})
    normal = market_drops(lst, src, cfg, [], now=now)[0].new_price
    cfg2 = dict(cfg, pricing=dict(cfg["pricing"], floor100_items=["X9"]))
    test = market_drops(lst, src, cfg2, [], now=now)[0].new_price
    assert test < normal
