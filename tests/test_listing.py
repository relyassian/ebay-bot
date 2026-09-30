from bot.config import load_config
from bot.listing import build_add_xml, build_title, make_draft

CFG = load_config()

CAND = {
    "id": "dg-new-roma-black", "brand": "Dolce & Gabbana", "model": "New Roma", "colorway": "Black",
    "style_code": "CS2036A1065 80999", "category": "sneaker", "department": "Men", "color": "Black",
    "size_system": "IT", "price": 699.99, "photos": ["https://i.ebayimg.com/images/g/x/s-l1600.jpg"],
    "sizes": [
        {"us": "8", "native": "41", "cost": 324, "source": "END US", "url": "u", "in_stock_sources": 2},
        {"us": "9", "native": "42", "cost": 324, "source": "END US", "url": "u", "in_stock_sources": 1},
        {"us": "10", "native": "43", "cost": 690, "source": "Italist", "url": "u", "in_stock_sources": 2},
        {"us": "11", "native": "44", "cost": None, "in_stock_sources": 0},
    ],
}


def test_title_fits_and_has_style_code():
    t = build_title(CAND)
    assert len(t) <= 80 and "CS2036A1065 80999" in t and t.startswith("Dolce & Gabbana New Roma")


def test_title_trims_when_too_long():
    long = dict(CAND, model="New Roma Calfskin Nappa Leather Low Top Sneakers Vintage Edition")
    assert len(build_title(long)) <= 80


def test_draft_applies_rules():
    d = make_draft(CAND, CFG)
    sizes = {s.us: s for s in d.sizes}
    assert "8" in sizes and sizes["8"].net >= 100            # clears floor at $699.99
    assert "9" not in sizes                                    # single source
    assert "11" not in sizes                                   # no source
    assert "10" in sizes and sizes["10"].price > 699.99        # raised to the floor price, never below
    assert d.blocked_reason is None


def test_no_photos_blocks():
    d = make_draft(dict(CAND, photos=[]), CFG)
    assert d.blocked_reason and "photos" in d.blocked_reason


def test_add_xml_quantity_one_and_policies():
    d = make_draft(CAND, CFG)
    xml = build_add_xml(d, "<SellerProfiles><X/></SellerProfiles>", "11023")
    assert xml.count("<Quantity>1</Quantity>") == len(d.sizes)
    assert "<ConditionID>1000</ConditionID>" in xml and "<SellerProfiles>" in xml
    assert "Dolce &amp; Gabbana" in xml
