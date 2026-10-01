"""Talk to the bot like a person on Telegram.

Exact commands (yes R1, no R1, APPROVE <id>, PAUSE, ...) are handled directly in newlistings.inbox().
Anything else goes here: Claude reads the bot's current state and answers in plain English, and can take
only the same safe actions the commands allow (approve/skip a waiting item, pause, resume) or save a request
for the daily research run (e.g. "look for Gucci Horsebit loafers in size 10").
Needs the ANTHROPIC_API_KEY secret; without it the bot replies with the command list.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import requests

from bot.config import ROOT, secret

MODEL = "claude-haiku-4-5-20251001"   # cheapest Claude model: about half a cent per reply with this compact state
REQUESTS = ROOT / "data" / "rafael_requests.txt"   # read by the daily research task
HISTORY = ROOT / "data" / "chat_history.json"

SYSTEM = """You are Rafael's eBay reselling bot, chatting with him on Telegram. He resells new luxury shoes
(Gucci, Dolce & Gabbana, Ferragamo) on eBay and buys each pair from a store only after it sells.
How the business works: every listing must make at least $100 profit (target $250); a size stays on sale only if
2+ stores have it in stock (so a sale never turns into a cancellation); quantity 1 per size; no returns;
the bot checks everything daily at 7:37am and sale alerts every ~30 minutes; Rafael approves new listings and
price raises.
Write like a sharp, friendly assistant texting: short, plain words, no jargon, no markdown headers or bold
(Telegram shows plain text). Lead with the answer. Include the eBay link when you talk about a listing.
Only state facts from the STATE below or from a tool result; if you don't know, say so and offer to have the
daily research check it (save_request). Never invent prices, stock or sales. You cannot buy anything, change
prices directly, or edit listings: for those, use the tools you have or save_request so it's handled on the next run.
Before approve/skip, be sure he clearly meant that specific item; if ambiguous, ask."""

TOOLS = [
    {"name": "approve", "description": "Approve a waiting item: a price raise code like R1, a new-listing draft id, or ALL raises.",
     "input_schema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "skip", "description": "Say no to a waiting item (raise code or draft id).",
     "input_schema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "pause", "description": "Stop all listing changes and new listings (sale alerts continue).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "resume", "description": "Turn listing changes back on.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "save_request", "description": "Save something Rafael wants done that needs research or a listing change "
     "(find an item, change a listing, check a store). It is picked up by the next daily run.",
     "input_schema": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]}},
]


def _state() -> str:
    """Compact on purpose (cost scales with size): one line per listing + what's waiting."""
    import csv
    from bot.listing import PAUSE_FLAG, load_state
    from bot.raises import pending
    from bot.report import short_name
    stock: dict[str, list] = {}
    p = ROOT / "data" / "source_prices.csv"
    if p.exists():
        for r in csv.DictReader(p.open()):
            stock.setdefault(r["item_id"], []).append(r)
    lines = []
    snap = ROOT / "data" / "snapshot.json"
    for x in (json.loads(snap.read_text()) if snap.exists() else []):
        rows = stock.get(x["item_id"], [])
        buyable = [r["size"] or "one size" for r in rows if (r.get("cost") or "").strip()]
        src = (f"buyable sizes: {', '.join(buyable)}" if buyable
               else "no store has it (off sale)" if rows else "no store data yet")
        lines.append(f"{short_name(x['title'], 60)} | ${x.get('price') or '?'} | {src} | https://www.ebay.com/itm/{x['item_id']}")
    drafts = {k: v.get("status") for k, v in load_state().items()}
    return "\n".join([f"now (UTC): {datetime.now(timezone.utc):%Y-%m-%d %H:%M}",
                      f"paused: {PAUSE_FLAG.exists()}",
                      f"price raises waiting: {json.dumps({c: {k: r[k] for k in ('name', 'size', 'old', 'new')} for c, r in pending().items()})}",
                      f"new listing drafts: {json.dumps(drafts)}",
                      "listings (title | price | store stock | link):"] + lines)


def _run_tool(name: str, args: dict, live: bool) -> str:
    from bot.listing import PAUSE_FLAG
    if name == "pause":
        PAUSE_FLAG.write_text("paused by Rafael\n")
        return "paused"
    if name == "resume":
        PAUSE_FLAG.unlink(missing_ok=True)
        return "resumed"
    if name == "save_request":
        REQUESTS.parent.mkdir(exist_ok=True)
        with REQUESTS.open("a") as f:
            f.write(f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M}Z  {args['request']}\n")
        return "saved for the next daily run"
    if name in ("approve", "skip"):
        from bot.newlistings import apply_decision
        return "\n".join(apply_decision(args["code"], name == "approve", live))
    return "unknown tool"


def reply(text: str, live: bool) -> str:
    key = secret("ANTHROPIC_API_KEY", required=False)
    if not key:
        return ("I only understand commands right now: yes R1 / no R1, yes <draft>, STATUS, PAUSE, RESUME. "
                "(Free-text chat turns on once the ANTHROPIC_API_KEY secret is added.)")
    history = json.loads(HISTORY.read_text())[-6:] if HISTORY.exists() else []
    messages = history + [{"role": "user", "content": text}]
    system = SYSTEM + "\n\nSTATE:\n" + _state()
    for _ in range(4):                                # a few tool rounds at most
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=90, headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 400, "system": system, "tools": TOOLS, "messages": messages})
        r.raise_for_status()
        body = r.json()
        messages.append({"role": "assistant", "content": body["content"]})
        calls = [b for b in body["content"] if b["type"] == "tool_use"]
        if not calls:
            answer = "".join(b.get("text", "") for b in body["content"] if b["type"] == "text").strip()
            HISTORY.write_text(json.dumps((history + [{"role": "user", "content": text},
                                                      {"role": "assistant", "content": answer}])[-10:]))
            return answer or "OK."
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": c["id"], "content": _run_tool(c["name"], c["input"], live)}
            for c in calls]})
    return "Done."
