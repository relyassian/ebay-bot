"""Runs the new-listing pipeline and Rafael's Telegram commands.

- drafts(): every new candidate → checked against the rules → checked by eBay (Verify, nothing is listed)
            → sent to Rafael on Telegram with per-size prices and profit.
- inbox():  reads Rafael's Telegram replies: APPROVE <id>, SKIP <id>, PAUSE, RESUME, STATUS.
- publish(): approved drafts are rebuilt with fresh numbers and listed (only when LIVE and not paused).
"""
from __future__ import annotations

import re

import requests

from bot.alerts import send
from bot.alerts.telegram import _chat_id
from bot.config import ROOT, load_config, secret
from bot.listing import (PAUSE_FLAG, SIZE_NAME, build_add_xml, draft_message, load_candidates, load_state, make_draft,
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
    todo = {k: c for k, c in load_candidates().items() if k not in state or k.startswith("test-")}
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
        ok, msgs = verify_add(build_add_xml(d, profiles, postal, SIZE_NAME.get(c["category"], "US Shoe Size")), token)
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
        out.append(draft_message(d))
    save_state(state)
    return out


def apply_decision(code: str, approve: bool, live: bool) -> list[str]:
    """Yes/no on a waiting item: a price-raise code (R1 / ALL) or a new-listing draft id."""
    if code.upper() == "ALL":                     # every waiting raise AND every waiting new listing
        from bot.raises import answer, pending
        out = answer("ALL", approve, live) if pending() else []
        state = load_state()
        drafts = [k for k, v in state.items() if v.get("status") == "sent"]
        for k in drafts:
            state[k]["status"] = "approved" if approve else "skipped"
        save_state(state)
        if drafts:
            out.append(f"👍 Approved {len(drafts)} new listing(s); they go live within a few minutes."
                       if approve else f"OK, skipped {len(drafts)} new listing(s).")
        return out or ["Nothing is waiting for an answer right now."]
    if re.fullmatch(r"[Rr]\d+", code):
        from bot.raises import answer
        return answer(code, approve, live)
    state = load_state()
    if state.get(code, {}).get("status") != "sent":
        return [f"Nothing waiting called '{code}'. Send STATUS to see what's waiting."]
    state[code]["status"] = "approved" if approve else "skipped"
    save_state(state)
    return [f"👍 {code} approved. It goes live within a few minutes." if approve else f"OK, skipped {code}."]


def status_text() -> str:
    from bot.raises import pending
    state = load_state()
    waiting = [k for k, v in state.items() if v.get("status") == "sent"]
    raises = pending()
    lines = ["⏸ Bot is PAUSED (send RESUME)" if PAUSE_FLAG.exists() else "▶️ Bot is running"]
    lines.append("New listings waiting for you: " + ", ".join(waiting) if waiting else "No new listings waiting for you.")
    if raises:
        lines.append("Price raises waiting for you:")
        lines += [f"{c} · {r['name']} US {r['size']}: ${r['old']:.2f} → ${r['new']:.2f} {r.get('url', '')}"
                  for c, r in sorted(raises.items(), key=lambda kv: int(kv[0][1:]))]
    else:
        lines.append("No price raises waiting.")
    return "\n".join(lines)


def inbox(live: bool = False, wait: int = 0) -> list[str]:
    """Apply Rafael's Telegram messages. Exact commands are handled directly; anything else goes to the chat
    assistant (bot/chat.py). Only messages from his own chat are accepted. wait = long-poll seconds."""
    token = secret("TELEGRAM_BOT_TOKEN")
    me = _chat_id(token)
    offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates",
                     params={"offset": offset, "timeout": wait, "allowed_updates": '["message"]'}, timeout=wait + 30)
    r.raise_for_status()
    replies, last = [], offset - 1
    for upd in r.json().get("result", []):
        last = max(last, upd["update_id"])
        OFFSET.parent.mkdir(exist_ok=True)
        OFFSET.write_text(str(last + 1))            # saved per message: a crash never re-runs an approval
        msg = upd.get("message") or {}
        if str(msg.get("chat", {}).get("id")) != me:
            continue
        text = (msg.get("text") or "").strip()
        words = text.split()
        if not words:
            continue
        cmd, arg = words[0].upper().strip(".!,"), (words[1].strip(".!,") if len(words) > 1 else "")
        if cmd == "ADS" and arg.upper() == "ON":
            try:
                from bot.ads import setup
                replies += setup(live)
            except Exception as e:
                replies.append(f"⚠️ Couldn't switch ads on: {str(e)[:200]}. If it mentions scope or permissions, "
                               "eBay needs to be reconnected first (connect-ebay in GitHub).")
            continue
        low = text.lower().strip(" .!?")
        yes_words = {"yes", "y", "ok", "okay", "yep", "sure", "go", "do it", "approve", "approved", "yes please"}
        no_words = {"no", "n", "nope", "skip", "don't", "dont", "no thanks"}
        lw = set(re.findall(r"[a-z]+", low))
        if "all" in lw and lw & {"yes", "approve", "approved", "ok", "okay", "accept", "do"} and not lw & {"no", "skip", "dont", "don"}:
            replies += apply_decision("ALL", True, live)  # "yes to all", "approve all of them", "ok all"
            continue
        if "all" in lw and lw & {"no", "skip"} and not lw & {"yes", "approve"}:
            replies += apply_decision("ALL", False, live)
            continue
        if low in yes_words | no_words:                 # bare yes/no: fine when exactly one thing is waiting
            from bot.raises import pending
            waiting = list(pending()) + [k for k, v in load_state().items() if v.get("status") == "sent"]
            if len(waiting) == 1:
                replies += apply_decision(waiting[0], low in yes_words, live)
            else:
                replies.append("Nothing is waiting for an answer right now." if not waiting else
                               "Which one? " + ", ".join(waiting) + " (e.g. \"yes " + waiting[0] + "\").")
            continue
        if any(k in low for k in ("status", "what's going on", "whats going on", "what's waiting", "whats waiting",
                                  "update", "what's up", "whats up")) and "API" not in text:
            replies.append(status_text())
            continue
        if cmd in ("APPROVE", "YES", "SKIP", "NO") and len(words) == 2:
            replies += apply_decision(arg, cmd in ("APPROVE", "YES"), live)
        elif cmd == "PAUSE" and len(words) == 1:
            PAUSE_FLAG.write_text("paused by Rafael\n")
            replies.append("⏸ Paused. No listing changes and no new listings until you send RESUME. "
                           "You'll still get sale alerts.")
        elif cmd == "RESUME" and len(words) == 1:
            PAUSE_FLAG.unlink(missing_ok=True)
            replies.append("▶️ Back on. Changes resume at the next check.")
        elif cmd == "STATUS" and len(words) == 1:
            replies.append(status_text())
        else:
            from bot.chat import reply
            try:
                replies.append(reply(text, live))
            except Exception as e:
                replies.append(f"Sorry, I couldn't answer that just now ({str(e)[:120]}). Try again in a minute.")
    OFFSET.parent.mkdir(exist_ok=True)
    OFFSET.write_text(str(last + 1))
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
        item_id, msgs = add_item(build_add_xml(d, profiles, postal,
                                               SIZE_NAME.get(cands[cid]["category"], "US Shoe Size")), token)
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
    for text in inbox(live) + publish(live):
        send(text)
