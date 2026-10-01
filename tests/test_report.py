from bot import raises
from bot.report import short_name, sizes_text, sync_report


def test_short_name():
    assert short_name("Dolce & Gabbana White Calfskin Nappa New Roma Sneakers Men's Size 9") \
        == "D&G White Calfskin Nappa New Roma Sneakers 9"


def test_sizes_text():
    assert sizes_text(["10", "9.5", "13"], 13) == "US 9.5, 10, 13"
    assert sizes_text([str(x) for x in range(7)], 7) == "all 7 sizes"


def test_report_quiet_day():
    msg = sync_report(True, [], {}, [], 20)
    assert "nothing for you to do" in msg and "LIVE" not in msg


def test_report_puts_raises_first():
    r = [{"code": "R1", "name": "Gucci Ace", "size": "9", "old": 699.99, "new": 749.99, "store": "END", "cost": 450}]
    msg = sync_report(True, [], {"hidden": [("D&G Tropez", ["6", "7"], 13, "")]}, r, 20)
    assert msg.index("NEEDS YOU") < msg.index("Taken off sale") and "APPROVE R1" in msg


def test_raise_codes_stable(tmp_path, monkeypatch):
    monkeypatch.setattr(raises, "FILE", tmp_path / "r.json")
    p = {"item_id": "1", "size": "9", "old": 1, "new": 2, "name": "x", "store": "s", "cost": 1}
    assert raises.save_proposals([p])[0]["code"] == "R1"
    assert raises.save_proposals([p, dict(p, size="10")])[1]["code"] == "R2"
    assert raises.save_proposals([p])[0]["code"] == "R1"
