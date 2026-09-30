"""Telegram alerts. Needs TELEGRAM_BOT_TOKEN (from @BotFather).
TELEGRAM_CHAT_ID is optional: if missing, the chat is found automatically from the latest
message sent to the bot (Rafael just has to send the bot any message once)."""
from __future__ import annotations

import os

import requests

from bot.config import secret


def _chat_id(token: str) -> str:
    cid = os.environ.get("TELEGRAM_CHAT_ID")
    if cid:
        return cid
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    r.raise_for_status()
    for upd in reversed(r.json().get("result", [])):
        msg = upd.get("message") or upd.get("edited_message") or {}
        if msg.get("chat", {}).get("id"):
            return str(msg["chat"]["id"])
    raise RuntimeError("Telegram: send your bot any message first so it knows where to reach you.")


def send(text: str) -> None:
    token = secret("TELEGRAM_BOT_TOKEN")
    for chunk in [text[i:i + 3900] for i in range(0, len(text), 3900)] or [""]:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": _chat_id(token), "text": chunk, "disable_web_page_preview": True},
            timeout=20,
        )
        r.raise_for_status()
