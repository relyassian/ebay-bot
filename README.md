# ebay-bot

Automates Rafael's eBay luxury-shoe store. Rules and roadmap: **CLAUDE.md**.

## One-time setup (≈20 minutes)

1. **eBay developer keys** — developer.ebay.com → My Account → Application Keys → **Production** keyset.
   Copy *App ID (Client ID)* and *Cert ID (Client Secret)*.
2. **RuName** — same site → User Tokens → *Get a Token from eBay via Your Application* → add eBay Redirect URL.
   Use eBay's default accept/decline pages. Copy the **RuName** (looks like `Rafael_Elyas-...-abcde`).
3. `cp .env.example .env` and fill in `EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `EBAY_RUNAME`.
4. `pip install -r requirements.txt`
5. `python -m bot.cli auth-url` → open the link, sign in to eBay, click **Agree**.
   The page you land on has `code=...` in its address. Copy everything after `code=` up to `&`.
6. `python -m bot.cli auth-code "<that code>"` → paste the printed `EBAY_REFRESH_TOKEN=...` into `.env`.
   (Codes expire in ~5 minutes; if it fails, repeat step 5.)
7. Telegram: message **@BotFather** → `/newbot` → copy the token into `TELEGRAM_BOT_TOKEN`.
   Send your new bot any message, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id` into `TELEGRAM_CHAT_ID`.
   Test: `python -m bot.cli alert-test`.

## Daily use (M1)

```bash
python -m bot.cli show 355429340181                      # live sizes / prices / available
python -m bot.cli apply plans/2026-09-30_raise_to_floor.csv          # dry run — shows every change
# set dry_run: false in config.yaml, then:
python -m bot.cli apply plans/2026-09-30_raise_to_floor.csv --live   # writes to eBay, reads back to confirm
```

Plan files: `item_id,size,new_price,new_available` (blank = unchanged; size blank for items without sizes).
Safety: quantity is capped at 1 per size; a price cut over 40% needs `--force`; every run is logged in `logs/`.

## Tests
`python -m pytest -q`
