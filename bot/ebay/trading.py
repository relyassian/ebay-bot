"""eBay Trading API: read and revise Rafael's existing multi-variation listings.

Why Trading API: the 21 legacy listings were created on the website, and the Inventory API
can only manage listings it created. Trading API ReviseFixedPriceItem works on any listing.

Quantity semantics (verified against eBay's Trading API guide, Sept 2026):
- GetItem returns a variation's TOTAL quantity (includes sold). Available = Quantity - QuantitySold.
- ReviseFixedPriceItem takes the AVAILABLE quantity; eBay adds QuantitySold itself.
  So to show N available, send Quantity = N (never add QuantitySold).
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
            avail = min(v.available if c.new_available is None else c.new_available, max_qty)
            parts.append(
                "<Variation>"
                f"<StartPrice>{price:.2f}</StartPrice>"
                f"<Quantity>{avail}</Quantity>"
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
            parts.append(f"<Quantity>{min(c.new_available, max_qty)}</Quantity>")
    parts.append("</Item>")
    return "".join(parts)


def get_active_item_ids(token: str) -> list[str]:
    ids, page = [], 1
    while True:
        root = _call("GetMyeBaySelling",
                     "<ActiveList><Include>true</Include><Pagination>"
                     f"<EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber>"
                     "</Pagination></ActiveList>", token)
        ids += [e.text for e in root.findall("e:ActiveList/e:ItemArray/e:Item/e:ItemID", NS)]
        pages = int(root.findtext("e:ActiveList/e:PaginationResult/e:TotalNumberOfPages", "1", NS) or 1)
        if page >= pages:
            return ids
        page += 1


@dataclass
class Sale:
    order_id: str
    item_id: str
    title: str
    size: str | None
    price: float
    buyer_city: str
    ship_to: list[str]          # address lines exactly as eBay gives them (authenticator + eVTN)
    created: str


def parse_orders(root: ET.Element) -> list[Sale]:
    out = []
    t = lambda el, p: (el.findtext(p, namespaces=NS) or "").strip()
    for o in root.findall("e:OrderArray/e:Order", NS):
        addr = o.find("e:ShippingAddress", NS)
        lines = [t(addr, f"e:{k}") for k in ("Name", "Street1", "Street2", "CityName",
                                              "StateOrProvince", "PostalCode", "Phone")] if addr is not None else []
        for tr in o.findall("e:TransactionArray/e:Transaction", NS):
            size = None
            for nv in tr.findall("e:Variation/e:VariationSpecifics/e:NameValueList", NS):
                if t(nv, "e:Name") == SIZE_NAME:
                    size = t(nv, "e:Value")
            out.append(Sale(
                order_id=t(o, "e:OrderID"), item_id=t(tr, "e:Item/e:ItemID"),
                title=t(tr, "e:Item/e:Title") or t(tr, "e:Variation/e:VariationTitle"),
                size=size, price=float(t(tr, "e:TransactionPrice") or 0),
                buyer_city=t(addr, "e:CityName") if addr is not None else "",
                ship_to=[l for l in lines if l], created=t(o, "e:CreatedTime"),
            ))
    return out


def get_recent_sales(token: str, hours: int = 48) -> list[Sale]:
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    frm = (now - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    to = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    root = _call("GetOrders", f"<CreateTimeFrom>{frm}</CreateTimeFrom><CreateTimeTo>{to}</CreateTimeTo>"
                              "<OrderRole>Seller</OrderRole><OrderStatus>Completed</OrderStatus>", token)
    return parse_orders(root)


def revise(listing: Listing, changes: list[Change], token: str, max_qty: int = 1) -> None:
    _call("ReviseFixedPriceItem", build_revise_xml(listing, changes, max_qty), token)
