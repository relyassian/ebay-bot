"""Things Rafael should know about but that can wait for the morning update (Rafael, Oct 5: few messages).
Stored in data/notices.json; the morning digest shows them once and clears them."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from bot.config import ROOT

FILE = ROOT / "data" / "notices.json"


def add(kind: str, text: str) -> None:
    """kind: photos (profitable but no photo) | approve (needs his OK) | problem (something failed)."""
    items = json.loads(FILE.read_text()) if FILE.exists() else []
    if any(i["kind"] == kind and i["text"] == text for i in items):
        return
    items.append({"kind": kind, "text": text, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(items, indent=1))


def pop_all() -> list[dict]:
    items = json.loads(FILE.read_text()) if FILE.exists() else []
    FILE.write_text("[]")
    return items
