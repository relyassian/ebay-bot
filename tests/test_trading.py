import xml.etree.ElementTree as ET

import pytest

from bot.ebay.trading import Change, Listing, Variation, build_revise_xml, parse_item
from bot.cli import check_changes

GETITEM = """<?xml version="1.0"?>
<GetItemResponse xmlns="urn:ebay:apis:eBLBaseComponents"><Ack>Success</Ack>
<Item><ItemID>355429340181</ItemID><Title>Gucci Green Ace</Title>
<Variations>
 <Variation><StartPrice currencyID="USD">899.99</StartPrice><Quantity>1</Quantity>
  <SellingStatus><QuantitySold>0</QuantitySold></SellingStatus>
  <VariationSpecifics><NameValueList><Name>US Shoe Size</Name><Value>9.5</Value></NameValueList></VariationSpecifics></Variation>
 <Variation><StartPrice currencyID="USD">899.99</StartPrice><Quantity>1</Quantity>
  <SellingStatus><QuantitySold>1</QuantitySold></SellingStatus>
  <VariationSpecifics><NameValueList><Name>US Shoe Size</Name><Value>10.5</Value></NameValueList></VariationSpecifics></Variation>
</Variations></Item></GetItemResponse>"""


def listing():
    return parse_item(ET.fromstring(GETITEM))


def test_parse_available_excludes_sold():
    l = listing()
    by = {v.size: v for v in l.variations}
    assert by["9.5"].available == 1
    assert by["10.5"].available == 0 and by["10.5"].sold == 1


def test_relist_sold_size_sends_available_only():
    # eBay adds QuantitySold itself on revise; sending sold+1 would put 2 up for sale
    xml = build_revise_xml(listing(), [Change("355429340181", "10.5", new_available=1)])
    assert "<Quantity>1</Quantity>" in xml and "<Quantity>2</Quantity>" not in xml


def test_price_change_on_sold_out_size_keeps_it_sold_out():
    xml = build_revise_xml(listing(), [Change("355429340181", "10.5", new_price=949.99)])
    assert "<Quantity>0</Quantity>" in xml


def test_price_change_keeps_quantity():
    xml = build_revise_xml(listing(), [Change("355429340181", "9.5", new_price=949.99)])
    assert "<StartPrice>949.99</StartPrice>" in xml and "<Quantity>1</Quantity>" in xml


def test_quantity_capped_at_one():
    xml = build_revise_xml(listing(), [Change("355429340181", "9.5", new_available=5)])
    assert "<Quantity>1</Quantity>" in xml


def test_unknown_size_rejected():
    with pytest.raises(ValueError):
        build_revise_xml(listing(), [Change("355429340181", "13", new_price=900)])


def test_big_price_cut_needs_force():
    with pytest.raises(ValueError):
        check_changes(listing(), [Change("355429340181", "9.5", new_price=99.99)], force=False)
    assert check_changes(listing(), [Change("355429340181", "9.5", new_price=99.99)], force=True)


def test_no_variation_item():
    l = Listing("356084785661", "Cufflinks", 450.0, 1, 0, [])
    xml = build_revise_xml(l, [Change("356084785661", None, new_price=599.99)])
    assert "<StartPrice>599.99</StartPrice>" in xml and "<Variations>" not in xml
