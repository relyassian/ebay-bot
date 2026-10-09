# eBay Arbitrage — STATUS
_Last updated: Fri Oct 9, 2026, 1:20am ET (rebuilt in the new chat after the old chat lost its Mac connection)._
_Canonical copy: Mac `~/Desktop/eBay Arbitrage/STATUS.md`; mirrored to the repo at `docs/STATUS.md`. Update both at the end of every work session._

## What we've built
- **ebay-bot** (GitHub `relyassian/ebay-bot`, public so GitHub Actions minutes stay free). Python, runs entirely on GitHub Actions, live on eBay (`LIVE=true` repo variable).
  - **sale-alerts** (`sales.yml`, `bot/listen.py`): always-on self-chaining runs (~25 min each). Answers Telegram, checks orders every 10 min, lists approved drafts, saves state. Confirmed running every 25 min as of Oct 9 05:00 UTC.
  - **daily-sync** (`daily.yml`, `bot/sync.py`): runs after each research push. Hides sizes with no profitable store (or no data in 36h), relists sold sizes, raises up to +15% automatically, 3%/7-day decay, matches market price down to 1.5× the required profit, eBay sale badges (20/15/10/5%).
  - **New listings**: research writes `data/candidates/*.yaml` → bot drafts → auto-publishes when every size clears the floor, has an eBay catalog photo and a verified style code.
  - **Promoted Listings** 8% on all shoe listings (`ads.yml`, `data/ads_state.json`).
  - **Telegram**: one morning digest (`bot/digest.py`), instant bold sale alerts, plain-English replies via Claude Haiku (`bot/chat.py`). Commands: `STATUS`, `PAUSE`, `RESUME`, `yes R1`, `no <draft>`.
- **Daily research** (Claude scheduled task, fresh session each morning): reads store prices/stock in the Mac's built-in browser (StockX, GOAT, Cettire; Farfetch/Italist/Nugnes1920/END as available), rewrites `data/source_prices.csv`, adds up to 8 new candidates, promo codes. Instructions: `docs/research_routine.md`.

## Current state (read from the repo, Oct 9 ~05:10 UTC)
- **Listings:** 66 listings compared in the last price check (≈47 bot-created + ≈19–20 legacy). Drafts: 47 live, 25 blocked, 8 waiting for selling-limit room. 80 candidate files.
- **eBay selling limit (binding constraint):** $4,183.89 of listed value left this month (7,135 qty). Resets ~Nov 1. eBay refused a limit increase (no sales history yet); sales are what raise it.
- **Sales this month (per eBay limit data):** 1 sale, $899.99.
- **Last daily check (Oct 8):** raised 5 listings (store got pricier), dropped 4 by 3%. 446 source-price rows, last research read Oct 8 ~10:52 UTC.
- **Engagement (Oct 8):** new listings 279 views/7d, 6 watchers; legacy listings 98 views/7d, 232 watchers.
- **Telegram "Needs you" queue:** empty.

## In progress
- **Floor-100 test** (started Oct 8, `config.yaml → pricing.floor100_items`): 5 low-margin Gucci listings (Rhyton Ivory 820204075737, MAC80 White/Blue 820207186615, Ace GG Embossed Black 820205698211, MAC80 Black/Off-White 820205221669, Run Black knit 820207186774) may match market down to $100 profit instead of $150. **Review Oct 15.**
- **Ads + ~10% price bump** (since Oct 2). **Review Oct 16.**

## Open decisions (Rafael)
1. **eBay drop-shipping policy risk (most important).** eBay's policy bans buying from another retailer/marketplace to fulfill an order — which is the current model. Recommended fix: "ship through Rafael" (store ships to him, he inspects, he ships to the authenticator): ~$15–20 extra and 2–4 extra days per sale. Rafael said "don't make any changes yet."
2. **Bally blue loafers:** buy one pair ($204, Farfetch, free 30-day returns) to photograph, so uncatalogued shoes can be listed. Not decided.
3. **Floor-100 test:** expand / keep / revert after Oct 15 review.
4. **Other marketplaces:** none allow list-before-owning (Mercari bans it; Whatnot needs 2-day shipping). Only viable once he owns stock. Grailed/Poshmark not yet checked.

## Next steps
1. Oct 15: floor-100 review → recommendation with profit math.
2. Oct 16: ads review → keep / lower prices / change rate.
3. Get sales to raise the eBay limit; prioritize listings most likely to sell over adding more.
4. Decide the compliance switch (#1 above) before volume grows.
5. Nov 1: limit resets → 8 waiting drafts publish; check research backup timing after the DST change.
6. M5 backlog: more store adapters, promo inbox, tracking ingest from store emails.

## Rules (summary — full spec in repo `CLAUDE.md`)
$100 net floor (target $250; LV $200; $300+ when price > $1,500) · new with box only · qty 1 per size · match by style code, never show it on eBay · no returns, free shipping, ≥3-day handling · catalog photos only · never auto-buy (Rafael buys from the link) · cash cap $5,000 in bought-but-unpaid orders · excluded brands: Dior, Hermès, Christian Louboutin, Versace, Nike, Saint Laurent, Valentino + religious/mythological imagery (ask Rafael before adding any brand) · NJ sales tax doesn't apply to shoes/clothing · StockX/GOAT checkout shipping $14.95.

## Key file paths (repo `relyassian/ebay-bot`)
`CLAUDE.md` spec · `config.yaml` all numbers/switches · `docs/research_routine.md` research instructions · `data/source_prices.csv` store prices · `data/candidates/` new products · `data/drafts_state.json` draft status · `data/stats.json` views/watchers · `data/selling_limits.json` · `data/notices.json` "Needs you" · `data/sales_log.csv` · `data/price_log.json` · `data/rafael_requests.txt` · `bot/` code · `.github/workflows/` (sales, daily, ads, catalog, market, snapshot, dump, connect-ebay, demo).

## Accounts & tools
eBay seller `rafaelelyassian` (Trading API, OAuth refresh token in GitHub secrets) · GitHub `relyassian` · Telegram bot · Anthropic API key (Haiku for chat replies) · Claude desktop app on Rafael's Mac (built-in browser signed in to eBay/StockX/GOAT — must stay open and awake for research) · stores: StockX, GOAT, Cettire, Farfetch, Italist, Nugnes1920, END.

## Scheduled tasks
| Task | When (ET) | Where it runs | What |
|---|---|---|---|
| eBay Research v2 (StockX/GOAT) | daily 6:37am | fresh session (not tied to any chat) | full research + push |
| eBay Research (backup) | daily 7:07am EDT (UTC cron — becomes 6:07am after Nov 1, BEFORE the 6:37 run; Rafael must change it to 10:07am ET) | fresh session | skips itself if the 6:37 run already succeeded |
| eBay daily check-in | Sun–Fri 7:20am | **this chat** | reads STATUS.md, confirms research + bot ran, posts a short summary here |
| Floor-100 review | Oct 15, 11:00am | **this chat** | review + recommendation |
| Ads review | Oct 16, 10:00am | **this chat** | review + recommendation |
