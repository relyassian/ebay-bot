"""Export every active listing's content (title, specifics, sizes, photos, description) to data/snapshot.json,
so legacy listings can be rewritten offline in the new style and reviewed before anything changes."""
from __future__ import annotations

import json
from xml.sax.saxutils import escape

from bot.config import ROOT

OUT = ROOT / "data" / "snapshot.json"


def run() -> int:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import NS, _call, get_active_item_ids
    token, out = access_token(), []
    for item_id in get_active_item_ids(token):
        root = _call("GetItem", f"<ItemID>{escape(item_id)}</ItemID><DetailLevel>ReturnAll</DetailLevel>"
                                "<IncludeItemSpecifics>true</IncludeItemSpecifics>", token)
        it = root.find("e:Item", NS)
        t = lambda p: it.findtext(p, namespaces=NS)
        specifics = {nv.findtext("e:Name", namespaces=NS): [v.text for v in nv.findall("e:Value", NS)]
                     for nv in it.findall("e:ItemSpecifics/e:NameValueList", NS)}
        sizes = [{**{nv.findtext("e:Name", namespaces=NS): nv.findtext("e:Value", namespaces=NS)
                     for nv in v.findall("e:VariationSpecifics/e:NameValueList", NS)},
                  "price": float(v.findtext("e:StartPrice", namespaces=NS) or 0),
                  "available": int(v.findtext("e:Quantity", namespaces=NS) or 0)
                  - int(v.findtext("e:SellingStatus/e:QuantitySold", namespaces=NS) or 0)}
                 for v in it.findall("e:Variations/e:Variation", NS)]
        out.append({
            "item_id": item_id, "title": t("e:Title"), "category": t("e:PrimaryCategory/e:CategoryID"),
            "category_name": t("e:PrimaryCategory/e:CategoryName"), "condition": t("e:ConditionDisplayName"),
            "sku": t("e:SKU"), "price": t("e:StartPrice"), "specifics": specifics, "sizes": sizes,
            "photos": [p.text for p in it.findall("e:PictureDetails/e:PictureURL", NS)],
            "description": (t("e:Description") or ""),
            "dispatch_days": t("e:DispatchTimeMax"),
            "shipping_type": t("e:ShippingDetails/e:ShippingType"),
            "ship_costs": [c.text for c in it.findall("e:ShippingDetails/e:ShippingServiceOptions/e:ShippingServiceCost", NS)],
            "free_shipping": [c.text for c in it.findall("e:ShippingDetails/e:ShippingServiceOptions/e:FreeShipping", NS)],
            "returns": t("e:ReturnPolicy/e:ReturnsAcceptedOption"),
            "profiles": {"ship": t("e:SellerProfiles/e:SellerShippingProfile/e:ShippingProfileName"),
                         "ret": t("e:SellerProfiles/e:SellerReturnProfile/e:ReturnProfileName")},
            "best_offer": t("e:BestOfferDetails/e:BestOfferEnabled"),
            "product_ref": t("e:ProductListingDetails/e:ProductReferenceID"),
            "sold_total": sum(int(v.findtext("e:SellingStatus/e:QuantitySold", namespaces=NS) or 0)
                              for v in it.findall("e:Variations/e:Variation", NS))
                          or int(t("e:SellingStatus/e:QuantitySold") or 0),
        })
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    try:   # eBay monthly selling limits (CLAUDE.md: read each run)
        root = _call("GetMyeBaySelling", "<SellingSummary><Include>true</Include></SellingSummary>"
                     "<ActiveList><Include>true</Include><Pagination><EntriesPerPage>1</EntriesPerPage></Pagination></ActiveList>",
                     token)
        summ = root.find("e:Summary", NS)
        g = lambda tag: summ.findtext(f"e:{tag}", namespaces=NS) if summ is not None else None
        limits = {k: g(k) for k in ("QuantityLimitRemaining", "AmountLimitRemaining", "ActiveAuctionCount",
                                     "TotalAuctionSellingValue", "TotalSoldCount", "TotalSoldValue")}
        (OUT.parent / "selling_limits.json").write_text(json.dumps(limits, indent=1))
        print("limits:", limits)
    except Exception as e:
        print("limits error:", e)
    print(f"snapshot: {len(out)} listings")
    return 0
