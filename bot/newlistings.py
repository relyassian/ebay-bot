"""Runs the new-listing pipeline and Rafael's Telegram commands.

- drafts(): every new candidate → checked against the rules → checked by eBay (Verify, nothing is listed)
            → sent to Rafael on Telegram with per-size prices and profit.
- inbox():  reads Rafael's Telegram replies: APPROVE <id>, SKIP <id>, PAUSE, RESUME, STATUS.
- publish(): approved drafts are rebuilt with fresh numbers and listed (only when LIVE and not paused).
"""
from __future__ import annotations

import requests

from bot.alerts import send
from bot.alerts.telegram import _chat_id
from bot.config import ROOT, load_config, secret
from bot.listing import (PAUSE_FLAG, build_add_xml, draft_message, load_candidates, load_state, make_draft,
                         save_state)

OFFSET = ROOT / "data" / "telegram_offset.txt"


def _template(token: str):
    from bot.ebay.trading import get_listing_template
    cfg = load_config()
    return get_listing_template(str(cfg["listing"]["template_item_id"]), token)


def drafts() -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import verify_add
    state, out = load_state(), []
    todo = {k: c for k, c in load_candidates().items() if k not in state}
    if not todo:
        return out
    token = access_token()
    profiles, postal = _template(token)
    for cid, c in todo.items():
        d = make_draft(c)
        if d.blocked_reason:
            state[cid] = {"status": "blocked", "reason": d.blocked_reason}
            out.append(f"⏸ {cid}: not listed — {d.blocked_reason}.")
            continue
        ok, msgs = verify_add(build_add_xml(d, profiles, postal), token)
        if not ok:
            state[cid] = {"status": "invalid", "errors": msgs[:5]}
            if cid.startswith("test-"):
                out.append(f"🧪 Test draft {cid}: eBay found problems (nothing was listed):\n" + "\n".join(msgs[:5]))
                continue
            out.append(f"⚠️ {cid}: eBay rejected the draft:\n" + "\n".join(msgs[:5]))
            continue
        if cid.startswith("test-"):              # verification-only drafts: never offered for approval
            state[cid] = {"status": "tested", "ok": True, "notes": msgs[:3]}
            out.append(f"🧪 Test draft {cid}: eBay accepted it (nothing was listed). {len(d.sizes)} sizes. "
                       + ("Notes: " + "; ".join(msgs[:3]) if msgs else ""))
            continue
        state[cid] = {"status": "sent"}
        out.append(draft_message(d) + ("\n\n(eBay notes: " + "; ".join(msgs[:3]) + ")" if msgs else ""))
    save_state(state)
    return out


def inbox() -> list[str]:
    """Apply Rafael's Telegram commands. Only messages from his own chat are accepted."""
    token = secret("TELEGRAM_BOT_TOKEN")
    me = _chat_id(token)
    offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params={"offset": offset, "timeout": 0},
                     timeout=30)
    r.raise_for_status()
    state, replies, last = load_state(), [], offset - 1
    for upd in r.json().get("result", []):
        last = max(last, upd["update_id"])
        msg = upd.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != me:
            continue
        words = (msg.get("text") or "").strip().split()
        if not words:
            continue
        cmd, arg = words[0].upper(), (words[1] if len(words) > 1 else "")
        if cmd in ("APPROVE", "SKIP"):
            if state.get(arg, {}).get("status") != "sent":
                replies.append(f"No draft waiting called '{arg}'.")
                continue
            state[arg]["status"] = "approved" if cmd == "APPROVE" else "skipped"
            replies.append(f"👍 {arg} approved — it goes live within 30 minutes." if cmd == "APPROVE"
                           else f"OK, skipped {arg}.")
        elif cmd == "PAUSE":
            PAUSE_FLAG.write_text("paused by Rafael\n")
            replies.append("⏸ Paused: no listing changes and no new listings until you send RESUME. Sale alerts continue.")
        elif cmd == "RESUME":
            PAUSE_FLAG.unlink(missing_ok=True)
            replies.append("▶️ Resumed.")
        elif cmd == "STATUS":
            waiting = [k for k, v in state.items() if v.get("status") == "sent"]
            replies.append(("⏸ PAUSED\n" if PAUSE_FLAG.exists() else "▶️ Running\n")
                           + (f"Drafts waiting: {', '.join(waiting)}" if waiting else "No drafts waiting."))
    OFFSET.parent.mkdir(exist_ok=True)
    OFFSET.write_text(str(last + 1))
    save_state(state)
    return replies


def publish(live: bool) -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import add_item
    cfg = load_config()
    live = live and not cfg.get("dry_run", True)
    state, cands, out = load_state(), load_candidates(), []
    ready = [k for k, v in state.items() if v.get("status") == "approved" and k in cands]
    if not ready:
        return out
    if PAUSE_FLAG.exists():
        return ["⏸ Paused — approved drafts are waiting. Send RESUME to list them."]
    token = access_token()
    profiles, postal = _template(token)
    for cid in ready:
        d = make_draft(cands[cid])          # fresh numbers: sizes that stopped clearing the rules drop out
        if d.blocked_reason:
            state[cid] = {"status": "blocked", "reason": d.blocked_reason}
            out.append(f"⏸ {cid}: not listed — {d.blocked_reason} (numbers changed since you approved).")
            continue
        if not live:
            out.append(f"(dry run) would list {cid}: {len(d.sizes)} sizes")
            continue
        item_id, msgs = add_item(build_add_xml(d, profiles, postal), token)
        if item_id:
            state[cid] = {"status": "live", "item_id": item_id}
            out.append(f"✅ Listed {d.title}\nhttps://www.ebay.com/itm/{item_id}\n{len(d.sizes)} sizes, "
                       f"best net ${d.best_net:.0f}")
        else:
            state[cid] = {"status": "invalid", "errors": msgs[:5]}
            out.append(f"⚠️ {cid}: eBay refused to list it:\n" + "\n".join(msgs[:5]))
    save_state(state)
    return out


def run_all(live: bool) -> None:
    for text in inbox() + publish(live):
        send(text)
