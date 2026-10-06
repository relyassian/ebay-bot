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


def live_style_codes() -> set[str]:
    """Style codes already on eBay (legacy listings + live/approved bot listings), normalized."""
    import json
    import yaml
    norm = lambda x: "".join(ch for ch in str(x).upper() if ch.isalnum())
    codes = {norm(v.get("style_code")) for v in
             yaml.safe_load((ROOT / "data" / "legacy_content.yaml").read_text())["items"].values() if v.get("style_code")}
    cands = load_candidates()
    for k, v in load_state().items():
        if v.get("status") in ("live", "approved") and k in cands:
            codes.add(norm(cands[k].get("style_code")))
    codes.discard("")
    return codes


def auto_ok(cid: str, c: dict, d) -> str | None:
    """Rafael (Oct 5): list without asking when it makes good money, is accurate and isn't a repeat.
    Returns None if OK to auto-list, else the reason it still needs him."""
    cfg = load_config()
    if not cfg["listing"].get("auto_publish"):
        return "auto-publish is off"
    if not d.photos or not c.get("style_code"):
        return "needs a catalog photo and a verified style code"
    norm = lambda x: "".join(ch for ch in str(x).upper() if ch.isalnum())
    others = live_style_codes()
    if norm(c["style_code"]) in others:
        return "this style code is already listed"
    if min(s.net for s in d.sizes) < cfg["profit"]["floor"]:
        return "a size is under the floor"
    if PAUSE_FLAG.exists():
        return "bot is paused"
    return None


def drafts() -> list[str]:
    from bot.ebay.auth import access_token
    from bot.ebay.trading import verify_add
    state, out = load_state(), []
    auto = load_config()["listing"].get("auto_publish")
    # with auto-publish on, drafts still waiting for Rafael are re-checked under his standing rule too
    todo = {k: c for k, c in load_candidates().items()
            if k not in state or k.startswith("test-") or (auto and state[k].get("status") in ("sent", "waiting_limit"))}
    if not todo:
        return out
    token = access_token()
    profiles, postal = _template(token)
    for cid, c in todo.items():
        d = make_draft(c)
        if d.blocked_reason:
            state[cid] = {"status": "blocked", "reason": d.blocked_reason}
            if d.blocked_reason.startswith("needs photos") and d.sizes:
                # Rafael (Oct 5): tell him whenever something would make money but has no photo
                out.append(f"📷 NEEDS PHOTOS: {d.title}\n"
                           f"Would make ${min(s.net for s in d.sizes):.0f}–${d.best_net:.0f} per pair "
                           f"(US {', '.join(s.us for s in d.sizes)}, at ${min(s.price for s in d.sizes):,.2f}+), "
                           "but eBay's catalog has no photo for it. If you have your own photos of this exact shoe, "
                           "send them and I'll list it.\n" + (d.sizes[0].url or ""))
            else:
                out.append(f"⏸ {cid}: not listed — {d.blocked_reason}.")
            continue
        ok, msgs = verify_add(build_add_xml(d, profiles, postal, SIZE_NAME.get(c["category"], "US Shoe Size")), token)
        if not ok and any("exceed the amount" in m or "21919188" in m for m in msgs):
            # eBay's monthly selling limit is full: not an error with the draft. Keep it and retry every run
            # (room comes back when something sells or the limit resets on the 1st). One quiet note, not one each.
            state[cid] = {"status": "waiting_limit"}
            print(f"{cid}: waiting for eBay selling-limit room")
            continue
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
        why_not = auto_ok(cid, c, d)
        if why_not is None:
            state[cid] = {"status": "approved", "approved_by": "auto (Rafael's standing rule, Oct 5)"}
            out.append(f"🤖 Listing automatically (you said I don't need to ask): {d.title}\n"
                       f"{len(d.sizes)} size(s), profit ${min(s.net for s in d.sizes):.0f}–${d.best_net:.0f} each. "
                       "Goes live within ~10 minutes. Send PAUSE to stop new listings.")
            continue
        state[cid] = {"status": "sent"}
        out.append(draft_message(d))
    save_state(state)
    return _route(out)


def _route(msgs: list) -> list:
    """Rafael (Oct 5): don't message him about new listings; problems, missing photos and anything that
    needs his OK wait for the morning update. Everything is still printed to the run log."""
    import re
    from bot.notices import add
    for m in msgs:
        text = m["text"] if isinstance(m, dict) else str(m)
        print(text)
        lines = text.splitlines() or [""]
        if text.startswith("📷"):
            add("photos", lines[0].replace("📷 NEEDS PHOTOS: ", "") + (" · " + lines[1].split(" (")[0] if len(lines) > 1 else ""))
        elif text.startswith("⚠️"):
            add("problem", " ".join(lines[:2]).lstrip("⚠️ ")[:200])
        elif text.startswith("👉"):
            cid = re.search(r'yes (\S+)"', text)
            add("approve", lines[0].replace("👉 NEW LISTING for your OK: ", "")
                + (f' (reply "yes {cid.group(1)}" to list it)' if cid else ""))
    return []


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


def record_sources(item_id: str, cand: dict, d) -> None:
    """Write the new listing's sizes into data/source_prices.csv (replacing any rows for that item).
    Without rows the daily check treats the sizes as unsourced and takes them off sale."""
    import csv
    from datetime import datetime, timezone
    from bot.sync import DATA
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    by_us = {str(s["us"]): s for s in cand.get("sizes", [])}
    fields = ["item_id", "size", "cost", "source", "url", "overseas", "in_stock_sources", "checked_at"]
    rows = [r for r in csv.DictReader(DATA.open())] if DATA.exists() else []
    rows = [r for r in rows if r.get("item_id") != str(item_id)]
    for line in d.sizes:
        src = by_us.get(line.us, {})
        rows.append({"item_id": str(item_id), "size": line.us, "cost": f"{line.cost:.2f}",
                     "source": f"{line.source} {line.native}".strip(), "url": line.url,
                     "overseas": str(bool(src.get("overseas"))).lower(),
                     "in_stock_sources": src.get("in_stock_sources", 1), "checked_at": src.get("checked_at", now)})
    with DATA.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def record_min_net(item_id: str, cand: dict) -> None:
    """Brand minimums (e.g. Louis Vuitton $200) must keep applying after listing (raises, weekly drops)."""
    import json
    from bot.profit import item_min_net
    cfg = load_config()
    base = item_min_net(cfg, brand=cand.get("brand"))
    if base <= cfg["profit"]["floor"]:
        return
    f = ROOT / "data" / "item_min_net.json"
    d = json.loads(f.read_text()) if f.exists() else {}
    d[str(item_id)] = base
    f.write_text(json.dumps(d, indent=1))


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
            record_sources(item_id, cands[cid], d)   # so the daily check knows where each size comes from
            record_min_net(item_id, cands[cid])
            from bot.digest import log_changes
            log_changes({"new": 1})
            out.append(f"✅ Listed {d.title}\nhttps://www.ebay.com/itm/{item_id}\n{len(d.sizes)} sizes, "
                       f"best net ${d.best_net:.0f}")
        else:
            state[cid] = {"status": "invalid", "errors": msgs[:5]}
            out.append(f"⚠️ {cid}: eBay refused to list it:\n" + "\n".join(msgs[:5]))
    save_state(state)
    if live and any(v.get("status") == "live" for k, v in state.items() if k in ready):
        try:                                        # promote new shoe listings at the same ad rate (no price bump:
            from bot.ads import setup               # their prices already include the ad fee)
            setup(live)
        except Exception as e:
            out.append(f"⚠️ Listed, but couldn't add the ads: {str(e)[:150]}")
    return out


def run_all(live: bool) -> None:
    for text in inbox(live):
        send(text)
    _route(publish(live))
