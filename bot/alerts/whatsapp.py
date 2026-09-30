"""WhatsApp alerts via Meta's WhatsApp Business Cloud API.

Outside a 24-hour reply window, Meta only delivers pre-approved *template* messages,
so business-initiated alerts must use a template (created and approved in Meta Business Manager).
Needs WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_TO (Rafael's number, digits only),
and WHATSAPP_TEMPLATE (an approved template with one {{1}} body variable).
Verify current Meta requirements before relying on this; Telegram is the fallback.
"""
from __future__ import annotations

import requests

from bot.config import secret

GRAPH = "https://graph.facebook.com/v21.0"


def send(text: str) -> None:
    token = secret("WHATSAPP_TOKEN")
    phone_id = secret("WHATSAPP_PHONE_NUMBER_ID")
    to = secret("WHATSAPP_TO")
    template = secret("WHATSAPP_TEMPLATE")
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template,
            "language": {"code": "en_US"},
            "components": [{"type": "body", "parameters": [{"type": "text", "text": text[:1000]}]}],
        },
    }
    r = requests.post(f"{GRAPH}/{phone_id}/messages", json=body,
                      headers={"Authorization": f"Bearer {token}"}, timeout=20)
    r.raise_for_status()
