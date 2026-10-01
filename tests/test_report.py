from bot import raises
from bot.report import short_name, sizes_text, sync_report


def test_short_name():
    assert short_name("Dolce & Gabbana White Calfskin Nappa New Roma Sneakers Men's Size 9") \
        == "D&G White Calfskin Nappa New Roma Sneakers 9"


def test_sizes_text():
    assert sizes_text(["10", "9.5", "13"], 13) == "US 9.5, 10, 13"
    assert sizes_text([str(x) for x in range(7)], 7) == "all 7 sizes"


def test_report_quiet_day():
    msgs = sync_report(True, [], {}, [], 20)
    assert len(msgs) == 1 and "Nothing for you to do" in msgs[0] and "20 listings" in msgs[0]


def test_report_cards_with_photo_link_and_why():
    r = [{"code": "R1", "name": "Gucci Ace", "size": "9", "old": 699.99, "new": 749.99, "store": "END", "cost": 450,
          "photo": "https://i.ebayimg.com/p.jpg", "url": "https://www.ebay.com/itm/1"}]
    g = {"hidden": [("D&G Tropez", ["6", "7"], 13, "", "https://i.ebayimg.com/t.jpg", "https://www.ebay.com/itm/2")]}
    msgs = sync_report(True, [], g, r, 20)
    assert "1 thing to answer" in msgs[0]
    assert msgs[1]["photo"] and "yes R1" in msgs[1]["text"]          # what needs him comes first
    assert "TAKEN OFF SALE" in msgs[2]["text"] and "Why:" in msgs[2]["text"] and "itm/2" in msgs[2]["text"]
    assert all(len(m["text"]) <= 1024 for m in msgs[1:])              # fits a photo caption


def test_raise_codes_stable(tmp_path, monkeypatch):
    monkeypatch.setattr(raises, "FILE", tmp_path / "r.json")
    p = {"item_id": "1", "size": "9", "old": 1, "new": 2, "name": "x", "store": "s", "cost": 1}
    assert raises.save_proposals([p])[0]["code"] == "R1"
    assert raises.save_proposals([p, dict(p, size="10")])[1]["code"] == "R2"
    assert raises.save_proposals([p])[0]["code"] == "R1"
