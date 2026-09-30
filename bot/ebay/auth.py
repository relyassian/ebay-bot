"""eBay OAuth (authorization-code grant).

One-time setup: `python -m bot.cli auth-url` → Rafael signs in on eBay's own page and clicks Agree →
eBay redirects to the RuName's accept URL with ?code=... → `python -m bot.cli auth-code <code>` prints
a refresh token (valid ~18 months) to store as EBAY_REFRESH_TOKEN. Access tokens (2 hours) are minted
from the refresh token on every run. The bot never sees Rafael's password.
"""
from __future__ import annotations

import base64
import time
import urllib.parse

import requests

from bot.config import secret

AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SCOPES = [
    "https://api.ebay.com/oauth/api_scope",                       # Trading API
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
]

_cache: dict = {}


def _basic() -> str:
    raw = f"{secret('EBAY_CLIENT_ID')}:{secret('EBAY_CLIENT_SECRET')}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def consent_url() -> str:
    q = {
        "client_id": secret("EBAY_CLIENT_ID"),
        "response_type": "code",
        "redirect_uri": secret("EBAY_RUNAME"),
        "scope": " ".join(SCOPES),
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def exchange_code(code: str) -> dict:
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": _basic(), "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": code, "redirect_uri": secret("EBAY_RUNAME")},
        timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"eBay rejected the code ({r.status_code}): {r.text[:300]} — codes work once and "
                           "expire in ~5 minutes; approve again and paste the NEW code.")
    return r.json()  # contains refresh_token + refresh_token_expires_in


def access_token() -> str:
    if _cache.get("exp", 0) > time.time() + 60:
        return _cache["token"]
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": _basic(), "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": secret("EBAY_REFRESH_TOKEN"),
              "scope": " ".join(SCOPES)},
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    _cache.update(token=body["access_token"], exp=time.time() + int(body.get("expires_in", 7200)))
    return _cache["token"]
