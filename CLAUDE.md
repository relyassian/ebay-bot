# Luxury Footwear Arbitrage Bot — Project Brief

## Goal
**Make as much money as possible** reselling new luxury shoes on eBay without ever cancelling an order. The bot finds items priced low at reputable stores, lists them on eBay at the highest price that still sells, keeps every size's price and stock in sync with the stores, and alerts Rafael when there's money to be made or something sells. Rafael's only routine manual step is buying the pair after a sale.

## Hard rules (never violate)
1. **Profit floor $100 net per item; target $250.** Tier A ≥ $250 (top-priority alert), Tier B $100–249, under $100 = don't list.
2. **Net profit** = eBay price × (1 − 0.136 fees − promoted rate − 0.01 buffer) − landed cost − reship cost.
   **Landed cost** = source price − promo + shipping (default $20) + NJ sales tax 6.625% (items ship to eBay's NJ authenticator) + 10% duty if shipped from overseas. Cashback never counts until proven paid. All numbers live in `config.yaml`.
3. **Never cause a cancellation.** A size is live only if ≥ 2 stores have it in stock at a price that clears the floor (or 1 store marked `reliable`). Out-of-stock cancellations were Rafael's biggest past problem.
4. **New items only**: new with box. No used, worn, B-grade, sample, or damaged box.
5. **Quantity 1 per size, always.** When a size sells, relist it at 1 only if it's still sourceable at a profit.
6. **Accuracy**: size, width, colorway, style code, and condition must match the source exactly. Identify products by **style code**, never by name. Only fill item specifics that are verifiably true.
7. **Listing terms**: no returns, free shipping, handling ≥ 3 business days (longer for slow stores), Best Offer on (auto-accept ≥ Tier A price, auto-decline below floor, anything in between → ask Rafael).
8. **Photos**: eBay catalog photos only. No catalog photo → "needs photos" alert, don't auto-list.
9. **"Discontinued"** in a title only when verified (brand no longer sells it and no retail stock). Save the evidence.
10. **Never auto-buy.** The bot sends buy links; Rafael buys.
11. **Dry-run by default.** Nothing writes to eBay unless `dry_run: false` and `--live` is passed. Log every decision.
12. **Launch mode**: first 2 weeks / 20 listings, every new listing and every price raise needs Rafael's one-tap approval. Price drops (still ≥ floor) and quantity changes are pre-approved.
13. **Cash cap**: stop listing new items when money spent on bought-but-unpaid orders exceeds $5,000.

## Sizing
- Canonical size = US. Store native size + system for every source price.
- Gucci men's = UK (UK 10 = US 10.5 = EU 44). D&G = IT/EU (US = IT − 33; confirm with D&G's own chart). Ferragamo = US with widths D/EE/EEE (EU = US + 34).
- Can't map a size confidently → skip it. Width is part of the size for dress shoes.
- eBay variation label: `US 10.5 (Gucci 10 / UK 10 / EU 44)`, with a conversion table in the description.

## Pricing
1. eBay sold comps for the exact style code + size (active listings as a fallback).
2. Start near the **top** of the recent sold range. With few comps, price at or just above retail. Verified discontinued → up to +15% over last retail, capped at the highest comp.
3. Unsold after 7 days → drop 3% per step, never below the floor price.
4. Log start vs. final sale price per model so starting prices improve.

## Fulfillment
- All luxury shoes on Rafael's account go through **eBay Authenticity Guarantee** (sneakers and loafers). Ship to the authenticator address with the **eVTN on address line 2**. Accessories (e.g. cufflinks) don't.
- GOAT's checkout truncates line 2 (`evtn:l227ktv` → `# L227`). For stores that do this, the sale alert says to ship to Rafael and forward.
- Sale alert: order #, US + native size to buy, cheapest in-stock store + link, best promo code, exact address to paste, eVTN warning if needed.
- Add tracking to eBay only when a real tracking number exists. Parse store shipping emails for tracking automatically.

## Source notes
- END US, Farfetch, SSENSE, Cettire, GOAT load sizes/stock with JavaScript: check them in a real browser and treat "SOLD OUT" on the page as out of stock. END sale items sell out within days.
- Italist is Shopify: `/products/<handle>.js` gives per-size availability; skip its `Vendor::BGW` (BrandsGateway) items.
- Mytheresa product pages show stock per size in plain HTML.

## Sources (one adapter per store in `bot/sources/`, status in `sources.yaml`)
StockX (official API, M2) → Cettire (needs a headless browser: prices load via JavaScript) → GOAT (new only) → Farfetch, SSENSE, END US, Italist, Mytheresa. Saks Off 5th excluded (shutting down). Ranking: lowest landed cost, unless another store is within $15 with better returns or faster shipping. An adapter failing 3 runs in a row is disabled and Rafael is alerted.

## eBay integration (decided)
- Rafael's 21 existing listings were created on the website, so they are revised with the **Trading API** (`GetItem`, `ReviseFixedPriceItem`) using an OAuth user token. The Inventory API can only manage listings it created.
- `GetItem` returns variation `Quantity` including units already sold (available = Quantity − QuantitySold), but `ReviseFixedPriceItem` takes the AVAILABLE quantity and eBay adds the sold units itself: to show N available, send `Quantity = N`. Sending sold + N once put sold-out sizes back on sale.
- New listings (M3) may use the Inventory API or the Trading API; decide in M3.
- The browser-driving assistant can't press Save on eBay, so everything goes through the API or a Seller Hub upload CSV.

## Existing store
The bot adopts listings that already exist on the seller account (keeping watchers and sales history) instead of recreating them, and ignores items listed in `config.yaml` → `sync.ignore_items`. Legacy listings get the same checks as new ones.

## Alerts
Telegram first (instant setup), WhatsApp Business Cloud API later (needs Meta-approved templates). Alert on every Tier A/B opportunity, sales, offers needing a decision, paused listings, and adapter failures. Daily summary. "PAUSE" / "RESUME" kill switch.

## Also required
Google Sheet dashboard (read-only) each run · bookkeeping per order (sale, fees, cost, tax, promo, net) with a monthly CSV export · read eBay selling limits each run · per-store authentication pass/fail tracking · AI-drafted buyer replies, Rafael approves before sending.

## Product scope
- Now: luxury men's shoes (sneakers, loafers, dress shoes). Belts and ties are supported but only listed when a deep discount clears the floor: new luxury belts/ties resell on eBay below retail (checked Sept 30), so typical buy-price ceilings are ~65–80% off retail (e.g. Gucci GG Supreme belt ≤ ~$199, Ferragamo Gancini ≤ ~$128); ties almost never qualify.
- Later, only if the numbers prove out: wallets, cardholders, sunglasses, bags, then high-ticket apparel (≥ ~$800 retail). Skip cheap apparel.
- Belts are sized as the brand marks them (usually cm); ties are one-size single listings. Neither goes through Authenticity Guarantee.

## Architecture
Python, single repo · GitHub Actions cron (no server) · Supabase Postgres (`db/schema.sql`) · secrets in `.env` / GitHub secrets, never committed.

## Milestones (each: tests pass → commit → next)
- **M1**: config, schema, alerts, eBay Trading API client (read + revise price/qty per size), plan-apply CLI, GitHub Actions dry run.
- **M2**: StockX adapter + size mapping + comps + profit calc + opportunity alerts + dashboard. Re-verify all legacy listings first.
- **M3**: new listings with catalog photos and full item specifics; improve legacy titles. Launch mode.
- **M4**: automatic sync (reprice, decay, zero out, relist sold sizes) + sale alerts.

## How the pieces run
- `daily-sync` workflow: applies `plans/approved/*.csv`, then fixes every listing against `data/source_prices.csv` (hide unsourceable sizes, relist sold sizes that are sourceable again, propose raises for underwater sizes).
- `sale-alerts` workflow (every 30 min): new order → Telegram message with what to buy, where, and the exact ship-to address.
- New listings: `data/candidates/<id>.yaml` (format in `bot/listing.py`) → `daily-sync` builds a draft, applies the rules, has eBay verify it (nothing listed), and sends it to Telegram. Rafael replies `APPROVE <id>` / `SKIP <id>`; `sale-alerts` (every 30 min) lists approved drafts with fresh numbers. Price raises the sync proposes get codes (`R1`, `R2`…, state in `data/raises.json`); `APPROVE R1` / `APPROVE ALL` / `SKIP R1` applies them right away and relists the size if the rules allow. `PAUSE` / `RESUME` / `STATUS` also work on Telegram. Telegram messages are plain English (`bot/report.py`): what Rafael must do first, then changes grouped per product with sizes collapsed. Business policies are copied from `listing.template_item_id`.
- `connect-ebay` workflow: one-time eBay approval; stores the refresh token as a repo secret.
- The repo variable `LIVE=true` is the on/off switch for writing to eBay.
- Until source adapters exist, `data/source_prices.csv` is maintained by a daily research task.
- **M5**: Cettire, GOAT, other stores; promo inbox; tracking ingest.
