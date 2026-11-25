"""Open listings to buyers outside the US (Rafael, Nov 25: "open it to as many countries as possible").

Shipping to other countries goes through eBay International Shipping (EIS): we ship the sold item to a US hub, the
buyer pays international shipping + import fees, eBay does customs. So the stores only ever ship inside the US.
Authenticity Guarantee still applies by itself to US / PR / Canada / Australia buyers (eBay decides by address).

Config (config.yaml -> shipping.international): enabled, items ("all" or a list of item ids), exclude (country codes).
State: data/shipto_done.json (item ids already revised, so we only call eBay once per listing).
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "data" / "shipto_done.json"


def _load() -> dict:
    try:
        return json.loads(DONE.read_text())
    except Exception:
        return {}


def wanted(cfg: dict, item_id: str) -> bool:
    c = (cfg.get("shipping") or {}).get("international") or {}
    if not c.get("enabled"):
        return False
    items = c.get("items", [])
    return items == "all" or str(item_id) in {str(i) for i in items}


def build_xml(item_id: str, exclude: list[str]) -> str:
    ex = "".join(f"<ExcludeShipToLocation>{escape(x)}</ExcludeShipToLocation>" for x in exclude)
    return (f"<Item><ItemID>{escape(str(item_id))}</ItemID><ShipToLocations>Worldwide</ShipToLocations>"
            f"<ShippingDetails>{ex}</ShippingDetails></Item>")


def apply(cfg: dict, item_id: str, token: str, live: bool) -> str | None:
    """Revise one listing to ship worldwide. Returns a note, or None when nothing to do."""
    if not wanted(cfg, item_id):
        return None
    done = _load()
    if str(item_id) in done:
        return None
    exclude = (cfg["shipping"]["international"].get("exclude") or [])
    if not live:
        return f"{item_id}: would open to Worldwide (excluding {', '.join(exclude) or 'none'})"
    from bot.ebay.trading import _call
    _call("ReviseFixedPriceItem", build_xml(item_id, exclude), token)
    done[str(item_id)] = "Worldwide"
    DONE.write_text(json.dumps(done, indent=1))
    return f"{item_id}: opened to Worldwide"
