from bot.config import load_config
from bot.listing import build_add_xml, build_title, make_draft

import copy
CFG = copy.deepcopy(load_config())
CFG.setdefault('sync', {})['allow_single_source'] = False   # tests pin the strict 2-store rule

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
    assert len(t) <= 80 and "CS2036A1065" not in t and t.startswith("Dolce & Gabbana New Roma")


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


def test_tie_is_single_item():
    tie = dict(CAND, id="hermes-tie", category="tie", size_system="", price=399.99,
               sizes=[{"us": "One Size", "native": "", "cost": 150, "source": "X", "url": "u", "in_stock_sources": 2}])
    d = make_draft(tie, CFG)
    xml = build_add_xml(d, "<SellerProfiles/>", "11023", None)
    assert "<Variations>" not in xml and "<Quantity>1</Quantity>" in xml and "<CategoryID>15662</CategoryID>" in xml


def test_belt_uses_size_variation():
    belt = dict(CAND, id="gucci-belt", category="belt", size_system="cm", price=599.99,
                sizes=[{"us": "90", "native": "90", "cost": 250, "source": "X", "url": "u", "in_stock_sources": 2}])
    d = make_draft(belt, CFG)
    xml = build_add_xml(d, "<SellerProfiles/>", "11023", "Size")
    assert "<Name>Size</Name>" in xml and "<CategoryID>2993</CategoryID>" in xml


def test_best_offer_only_on_big_margin_single_items():
    big = dict(CAND, id="cuff", category="tie", price=899.99,
               sizes=[{"us": "One Size", "native": "", "cost": 150, "source": "X", "url": "u", "in_stock_sources": 2}])
    xml = build_add_xml(make_draft(big, CFG), "<SellerProfiles/>", "11023", None)
    assert "<BestOfferEnabled>true</BestOfferEnabled>" in xml and "MinimumBestOfferPrice" in xml
    small = dict(big, price=399.99)
    assert "BestOffer" not in build_add_xml(make_draft(small, CFG), "<SellerProfiles/>", "11023", None)
    assert "BestOffer" not in build_add_xml(make_draft(CAND, CFG), "<SellerProfiles/>", "11023")


def test_style_code_never_on_listing():
    d = make_draft(CAND, CFG)
    xml = build_add_xml(d, "<SellerProfiles/>", "11023")
    assert "CS2036A1065" not in xml


def test_excluded_brands_and_motifs_never_list():
    from bot.config import load_config
    from bot.listing import excluded_reason
    cfg = load_config()
    assert excluded_reason({"brand": "Christian Dior", "model": "B23"}, cfg)
    assert excluded_reason({"brand": "Hermès", "model": "Oran"}, cfg)
    assert excluded_reason({"brand": "Saint Laurent", "model": "Court Classic"}, cfg)
    assert excluded_reason({"brand": "Gucci", "model": "Ace", "colorway": "Medusa Print"}, cfg)
    assert not excluded_reason({"brand": "Gucci", "model": "Ace Sneaker with Web", "colorway": "White"}, cfg)
    assert not excluded_reason({"brand": "Gucci", "model": "Horsebit Driver Loafer", "colorway": "Black"}, cfg)
