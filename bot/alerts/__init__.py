"""Pluggable alert channel. send(text) picks the channel from config.yaml."""
from __future__ import annotations

from bot.config import load_config


def send(text: "str | dict") -> None:
    """text: a string, or {"text": ..., "photo": url} for a picture card."""
    channel = load_config()["alerts"]["channel"]
    if isinstance(text, dict) and channel == "whatsapp":
        text = text["text"]
    if channel == "whatsapp":
        from bot.alerts.whatsapp import send as _send
    else:
        from bot.alerts.telegram import send as _send
    _send(text)
