"""eBay Trading API: read and revise Rafael's existing multi-variation listings.

Why Trading API: the 21 legacy listings were created on the website, and the Inventory API
can only manage listings it created. Trading API ReviseFixedPriceItem works on any listing.

Quantity gotcha: a variation's <Quantity> counts units already sold. Available = Quantity - QuantitySold.
To show N available you must send Quantity = QuantitySold + N.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

import requests

ENDPOINT = "https://api.ebay.com/ws/api.dll"
COMPAT = "1193"
NS = {"e": "urn:ebay:apis:eBLBaseComponents"}
SIZE_NAME = "US Shoe Size"


@dataclass
class Variation:
    specifics: dict            # e.g. {"US Shoe Size": "10.5"}
    price: float
    quantity: int              # eBay's total (includes sold)
    sold: int

    @property
    def available(self) -> int:
        return max(self.quantity - self.sold, 0)

    @property
    def size(self) -> str | None:
        return self.specifics.get(SIZE_NAME)


@dataclass
class Listing:
    item_id: str
    title: str
    price: float | None                        # for non-variation items
    quantity: int | None
    sold: int | None
    variations: list[Variation] = field(default_factory=list)


@dataclass
class Change:
    item_id: str
    size: str | None           # None = listing without variations
    new_price: float | None = None
    new_available: int | None = None


def _call(call_name: str, body_xml: str, token: str) -> ET.Element:
    xml = (f'<?xml version="1.0" encoding="utf-8"?>'
           f'<{call_name}Request xmlns="urn:ebay:apis:eBLBaseComponents">{body_xml}</{call_name}Request>')
    r = requests.post(ENDPOINT, data=xml.encode(), timeout=60, headers={
        "X-EBAY-API-CALL-NAME": call_name,
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": COMPAT,
        "X-EBAY-API-IAF-TOKEN": token,
        "Content-Type": "text/xml",
    })
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ack = root.findtext("e:Ack", namespaces=NS)
    if ack not in ("Success", "Warning"):
        errors = [e.findtext("e:LongMessage", namespaces=NS) for e in root.findall("e:Errors", NS)]
        raise RuntimeError(f"{call_name} failed: {errors}")
    return root


def parse_item(root: ET.Element) -> Listing:
    item = root.find("e:Item", NS)
    num = lambda el, path: el.findtext(path, namespaces=NS)
    variations = []
    for v in item.findall("e:Variations/e:Variation", NS):
        specifics = {nv.findtext("e:Name", namespaces=NS): nv.findtext("e:Value", namespaces=NS)
                     for nv in v.findall("e:VariationSpecifics/e:NameValueList", NS)}
        variations.append(Variation(
            specifics=specifics,
            price=float(num(v, "e:StartPrice") or 0),
            quantity=int(num(v, "e:Quantity") or 0),
            sold=int(num(v, "e:SellingStatus/e:QuantitySold") or 0),
        ))
    has_vars = bool(variations)
    return Listing(
        item_id=num(item, "e:ItemID"),
        title=num(item, "e:Title") or "",
        price=None if has_vars else float(num(item, "e:StartPrice") or 0),
        quantity=None if has_vars else int(num(item, "e:Quantity") or 0),
        sold=None if has_vars else int(num(item, "e:SellingStatus/e:QuantitySold") or 0),
        variations=variations,
    )


def get_item(item_id: str, token: str) -> Listing:
    root = _call("GetItem", f"<ItemID>{escape(item_id)}</ItemID><DetailLevel>ReturnAll</DetailLevel>"
                            f"<IncludeItemSpecifics>true</IncludeItemSpecifics>", token)
    return parse_item(root)


def build_revise_xml(listing: Listing, changes: list[Change], max_qty: int = 1) -> str:
    """ReviseFixedPriceItem body. Each changed variation is sent with BOTH price and quantity
    (current values kept for whichever isn't changing) so nothing is reset by accident."""
    parts = [f"<Item><ItemID>{escape(listing.item_id)}</ItemID>"]
    if listing.variations:
        by_size = {v.size: v for v in listing.variations}
        parts.append("<Variations>")
        for c in changes:
            v = by_size.get(c.size)
            if v is None:
                raise ValueError(f"{listing.item_id}: size {c.size!r} not on the listing")
            price = v.price if c.new_price is None else c.new_price
            avail = v.available if c.new_available is None else min(c.new_available, max_qty)
            parts.append(
                "<Variation>"
                f"<StartPrice>{price:.2f}</StartPrice>"
                f"<Quantity>{v.sold + avail}</Quantity>"
                "<VariationSpecifics>"
                + "".join(f"<NameValueList><Name>{escape(k)}</Name><Value>{escape(val)}</Value></NameValueList>"
                          for k, val in v.specifics.items())
                + "</VariationSpecifics></Variation>"
            )
        parts.append("</Variations>")
    else:
        (c,) = changes
        if c.new_price is not None:
            parts.append(f"<StartPrice>{c.new_price:.2f}</StartPrice>")
        if c.new_available is not None:
            parts.append(f"<Quantity>{(listing.sold or 0) + min(c.new_available, max_qty)}</Quantity>")
    parts.append("</Item>")
    return "".join(parts)


def revise(listing: Listing, changes: list[Change], token: str, max_qty: int = 1) -> None:
    _call("ReviseFixedPriceItem", build_revise_xml(listing, changes, max_qty), token)
