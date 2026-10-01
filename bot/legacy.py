"""Rewrite existing (website-created) listings in the new style: title with style code, professional description,
extra verified item specifics. Photos, prices, sizes, quantities, watchers and sales history are untouched.

  python -m bot.cli legacy-plan   → plans/approved/<date>_legacy_content.json (raw ReviseFixedPriceItem bodies)
The daily sync applies approved JSON plans (see sync.apply_raw_plan)."""
from __future__ import annotations

import json
from datetime import date
from xml.sax.saxutils import escape

import yaml

from bot.config import ROOT
from bot.listing import SizeLine, build_description, build_title

CONTENT = ROOT / "data" / "legacy_content.yaml"
SNAPSHOT = ROOT / "data" / "snapshot.json"


def native(us: str, system: str) -> str:
    x = float(us)
    n = {"UK": x - 0.5, "IT": x + 33, "EU": x + 33}.get(system, x)
    return str(int(n)) if n == int(n) else str(n)


def item_xml(snap: dict, c: dict) -> str:
    sizes = [next(iter(s.values())) for s in snap["sizes"] if s]
    sizes.sort(key=float)
    lines = [SizeLine(u, native(u, c["size_system"]), 0, 0, "", "", 0, "") for u in sizes]
    c = dict(c, handling_days=int(snap.get("dispatch_days") or c.get("handling_days", 3)))
    specifics = {k: list(v) for k, v in snap["specifics"].items()}
    specifics.pop("Style Code", None)          # never shown on eBay
    for name, val in (("Model", c["model"]),
                      ("Product Line", c.get("product_line"))):
        if val:
            specifics[name] = [val]
    spec_xml = "".join("<NameValueList><Name>" + escape(k) + "</Name>"
                       + "".join(f"<Value>{escape(v)}</Value>" for v in vals if v) + "</NameValueList>"
                       for k, vals in specifics.items())
    return (f"<Item><ItemID>{snap['item_id']}</ItemID><Title>{escape(build_title(c))}</Title>"
            f"<Description><![CDATA[{build_description(c, lines)}]]></Description>"
            f"<ItemSpecifics>{spec_xml}</ItemSpecifics></Item>")


def make_plan() -> str:
    cfg = yaml.safe_load(CONTENT.read_text())
    snaps = {s["item_id"]: s for s in json.loads(SNAPSHOT.read_text())}
    plan = []
    for item_id, c in cfg["items"].items():
        if item_id not in snaps:
            continue
        c = {**cfg["defaults"], **c}
        plan.append({"item_id": item_id, "old_title": snaps[item_id]["title"], "new_title": build_title(c),
                     "item_xml": item_xml(snaps[item_id], c)})
    out = ROOT / "plans" / "approved" / f"{date.today()}_legacy_content.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=1))
    return str(out)
