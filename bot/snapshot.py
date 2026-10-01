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
        sizes = [{nv.findtext("e:Name", namespaces=NS): nv.findtext("e:Value", namespaces=NS)
                  for nv in v.findall("e:VariationSpecifics/e:NameValueList", NS)}
                 for v in it.findall("e:Variations/e:Variation", NS)]
        out.append({
            "item_id": item_id, "title": t("e:Title"), "category": t("e:PrimaryCategory/e:CategoryID"),
            "category_name": t("e:PrimaryCategory/e:CategoryName"), "condition": t("e:ConditionDisplayName"),
            "sku": t("e:SKU"), "price": t("e:StartPrice"), "specifics": specifics, "sizes": sizes,
            "photos": [p.text for p in it.findall("e:PictureDetails/e:PictureURL", NS)],
            "description": (t("e:Description") or "")[:4000],
            "product_ref": t("e:ProductListingDetails/e:ProductReferenceID"),
            "sold_total": sum(int(v.findtext("e:SellingStatus/e:QuantitySold", namespaces=NS) or 0)
                              for v in it.findall("e:Variations/e:Variation", NS))
                          or int(t("e:SellingStatus/e:QuantitySold") or 0),
        })
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"snapshot: {len(out)} listings")
    return 0
