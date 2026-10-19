"""Photo upgrades for live listings (Rafael, Oct 19: more photos, best angle first, online photos are fine).

data/photo_results.json {item_id: {photos: [best first, ...], source, page, notes}} (written by the research run)
→ plans/approved/<date>_photos.json, applied by the daily sync with ReviseFixedPriceItem (PictureDetails replaces the
whole gallery, so every photo we want to keep is listed).
Rules: never another eBay seller's photo (an i.ebayimg.com URL is allowed only if the listing already uses it);
at least 3 photos, otherwise there is nothing to gain; max 12; https only; no duplicates.
"""
from __future__ import annotations

import json
from datetime import date
from xml.sax.saxutils import escape

from bot.config import ROOT

RESULTS = ROOT / "data" / "photo_results.json"
SNAPSHOT = ROOT / "data" / "snapshot.json"
MIN_PHOTOS, MAX_PHOTOS = 3, 12


def clean(urls: list[str], current: list[str]) -> list[str]:
    keep = {u.split("?")[0] for u in current}
    out, seen = [], set()
    for u in urls:
        key = u.split("?")[0]
        if not u.startswith("https://") or key in seen:
            continue
        if "ebayimg.com" in u and key not in keep:
            continue                                  # another eBay seller's photo: never
        seen.add(key)
        out.append(u)
    return out[:MAX_PHOTOS]


def make_plan() -> tuple[str | None, list[str]]:
    res = json.loads(RESULTS.read_text())
    snaps = {s["item_id"]: s for s in json.loads(SNAPSHOT.read_text())}
    plan, notes = [], []
    for item_id, r in res.items():
        snap = snaps.get(item_id)
        if not snap:
            notes.append(f"{item_id}: not in snapshot"); continue
        urls = clean(r.get("photos") or [], snap.get("photos") or [])
        if len(urls) < MIN_PHOTOS:
            notes.append(f"{item_id}: only {len(urls)} usable photos, skipped"); continue
        pics = "".join(f"<PictureURL>{escape(u)}</PictureURL>" for u in urls)
        plan.append({"item_id": item_id, "old_title": snap["title"], "new_title": None,
                     "item_xml": f"<Item><ItemID>{item_id}</ItemID><PictureDetails>{pics}</PictureDetails></Item>"})
        notes.append(f"{item_id}: {len(snap.get('photos') or [])} -> {len(urls)} photos")
    if not plan:
        return None, notes
    out = ROOT / "plans" / "approved" / f"{date.today()}_photos.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=1))
    return str(out), notes


if __name__ == "__main__":
    path, notes = make_plan()
    print("\n".join(notes)); print(path or "nothing to apply")
