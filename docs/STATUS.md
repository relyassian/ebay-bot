# eBay Arbitrage — STATUS
_Last updated: Fri Oct 9, 2026, 1:40am ET. Rebuilt in the new chat after the old chat lost its Mac connection, then audited against the old chat (v2)._
_Copies: Mac `~/Claude Code/STATUS.md` (the only folder this chat can reach now; an older v1 copy sits in `~/Desktop/eBay Arbitrage/` and is stale: delete it) and repo `docs/STATUS.md` (same content). Update both at the end of every work session._
_Old chat = claude.ai chat `9ad43b66-8fb8-4bc1-99c9-04cade988b93` ("eBay Arbitrage", 550 turns, last message Oct 8 ~2:50pm ET). Its container (scratch files) is gone; everything committed is in the repo._

## 1. What we've built
- **ebay-bot** (GitHub `relyassian/ebay-bot`, public so Actions minutes stay free). Python on GitHub Actions, live on eBay (`LIVE=true` repo variable).
  - **sale-alerts** (`sales.yml`, `bot/listen.py`): self-chaining runs (~25 min each): Telegram replies, new-order check every 10 min, lists approved drafts, saves state. Verified running back-to-back at Oct 9 05:00 UTC.
  - **daily-sync** (`daily.yml`, `bot/sync.py`): runs on each research push. Hides sizes with no profitable store (or no price row in 36h), relists sold sizes, raises up to +15% automatically, decays unsold prices 3%/7 days, matches the market (see rules), eBay sale badges (20/15/10/5%), per-listing ad rates.
  - **Price check vs other eBay sellers** (`bot/market.py`, runs before each sync) → `data/market.json`. 21 of ~66 listings have ≥3 comparable sellers; the rest have little competition.
  - **New listings**: research writes `data/candidates/*.yaml` → bot drafts → vets against the eBay market → auto-publishes if every size clears the floor, has an eBay catalog photo and a verified style code.
  - **Promoted Listings** 8% base on all shoe listings; the daily tune raises 7 listings to 10–15% only while every live size keeps 1.5× required profit (`bot/ads.py`).
  - **Telegram**: one morning digest, instant bold sale alerts, plain-English replies via Claude Haiku. Commands: `STATUS`, `PAUSE`, `RESUME`, `yes R1`, `no <draft>`. Duplicate-digest bug fixed Oct 7.
- **Daily research**: reads StockX/GOAT/Cettire/Farfetch in the Mac's built-in browser, rewrites `data/source_prices.csv`, adds up to 8 candidates (Oct 7 change: "competitive first": sale sections and low-competition brands), promo codes. Instructions: `docs/research_routine.md`. **From Oct 9 it runs inside this chat** (see section 11).

## 2. Standing decisions and instructions from Rafael (all still in force)
- **Oct 9: every scheduled-task result for the eBay project must appear in THIS chat, not in the Scheduled section and not in any other chat, unless Rafael says otherwise. eBay tasks only** (not Marketing, Price AI, Shieldr or trading-bot tasks).
- **Update STATUS.md (Mac + repo) at the end of every work session; every scheduled run starts by reading it.**
- Oct 1: one in-stock store is enough to list/relist (accepts cancellation risk). Style codes are never shown on eBay.
- Oct 2: Promoted Listings 8%; prices raised ~10% once to cover it.
- Oct 4: no idol-worship brands/imagery: Dior, Hermès, Christian Louboutin, Versace, Nike, Saint Laurent, Valentino, Medusa/Buddha/crosses/angels/saints. **Ask before adding any brand.**
- Oct 5: new listings auto-publish; raises ≤15% and drops ≥ floor are automatic; ≥$300 profit above $1,500 price (+$100 per $500); Louis Vuitton ≥$200; drops never below 1.5× required profit; sale badges; fuller titles; Telegram = one morning digest, sales instant.
- Oct 7: **"Relisting: you don't have to ask me."** **"Match market wherever you can."** **"Put more products that have no competition, or match or are lower than the market."**
- Oct 7: **Return policy: do all the other changes, but tell Rafael before touching returns.** eBay allows only 30 or 60 days (14 is not possible); buyer-paid return shipping is allowed. Returns are still **none**. No decision yet.
- Oct 8: **Floor-100 test** on 5 Gucci listings (market matching may go to $100 profit instead of $150).
- Older: Sun–Fri monitoring at 7am (see gaps), quantity 1 per size, $5,000 cap on bought-but-unpaid orders, new with box only, Rafael buys the pair himself (the bot never auto-buys), approves any cufflink/Best Offer in-between cases.

## 3. Current state (read from the repo, Oct 9 ~05:30 UTC)
- **Listings:** 47 bot-created live + about 20 older = about 67; the last price check compared 66. Drafts: 47 live, 25 blocked, 8 waiting for selling-limit room.
- **25 blocked drafts = all "needs photos"** (no eBay catalog photo; the 8 low-competition Oct 7 finds are among them: Bally blue + grey loafers, Margiela Sprinters, 2 Givenchy, Lanvin Curb pink, D&G Portofino off-white, Brunello Cucinelli beige, plus Ferragamo/Gucci/Prada/McQueen/Bottega ones). Rule: eBay catalog photos or Rafael's own photos only.
- **8 waiting on selling limit:** Gucci loafer Interlocking G brown, MAC80 blue / dune / high black-off-white / off-white-black, Re-Web leather black / white, Run light-grey-brown.
- **eBay selling limit (the binding constraint):** $4,183.89 listing value and 7,135 items left this month; resets about Nov 1. eBay declined a limit increase (no sales history yet).
- **Sales:** the bot's own sales log is empty and the old chat said "no sales yet" on bot listings. eBay's limits endpoint reports 1 sold item worth $899.99 this period. **Not reconciled**: treat as "0 bot sales, 1 sale of unknown origin".
- **Last daily check (Oct 8):** 5 listings raised (store got pricier), 4 lowered 3%. Store prices last refreshed Oct 8 11:12 UTC; sizes with no row newer than 36h go off sale, so rows expire about Oct 9 23:12 UTC if today's research fails.
- **Traffic (Oct 8):** new listings 279 views/7d, 6 watchers; older listings 98 views/7d, 232 watchers. Price check found most Gucci listings 1.3–1.9× what other sellers ask (asking prices, rough matching); about 39 of 43 compared can't reach the market even at the $100 floor.
- **10 older listings that were off sale (about 120 watchers):** 2 relisted Oct 7 (Ferragamo reversible-bit moccasin as Wide EE; D&G Saint Tropez white, US 6/7/8.5 from Farfetch). The other 8 have no store with stock or no confirmed style code.
- **Telegram "Needs you" queue:** empty.

## 4. In progress
- **Floor-100 test** (started Oct 8): Rhyton Ivory 820204075737, MAC80 White/Blue 820207186615, Ace GG Embossed Black 820205698211, MAC80 Black/Off-White 820205221669, Run Black knit 820207186774. Review Oct 15.
- **Ads + ~10% price bump** since Oct 2. Review Oct 16.
- **Pending size-add plans** in `plans/pending/`: Oct 6 (91 sizes, 32 listings) and Oct 7 (78 sizes, 29 listings). Prices are from Oct 6–7 (stale) and would add far more listed value than the $4.2k of limit left, so **do not apply before Nov 1 and re-verify prices first**. Rafael has not approved them.

## 5. Open decisions (Rafael)
1. **eBay drop-shipping policy (biggest risk).** eBay bans buying from another retailer to fulfill an order; the authenticator hides the store box but doesn't make it allowed. Recommended: "ship through me" (store ships to Rafael, he inspects and ships to the authenticator): about $15–20 and 2–4 days more per sale, ~10–20% of thin sizes drop off. Rafael (old chat, before Oct 6): "you think from now on we should do ship through me? … don't make any changes yet." Claude recommended yes; he has not replied "ship through me" in anything I read (through Oct 9 1:59am). **Not decided; no changes made.**
2. **Wholesale supplier route** (e.g. BrandsGateway, seen as "Vendor::BGW" on Italist): eBay allows drop shipping from a true wholesale supplier. Offered as "reply research wholesalers"; no reply found in turns 521–552. **Not started.**
3. **Facebook Marketplace / Grailed test.** Rafael's words (Oct 6, not Oct 7): "mercari and depop will never know, you should be able to post if i log you in right?", "do more research into all platforms", "isnt it worth it just to try the other platforms a little", "can we make a major facebook marketplace push now, i want to list in as many places for free as possible", "what account am i posting on on fb?". Claude then proposed the test: 10 pairs, Rafael lists by hand, "SOLD F12" Telegram command to pull sizes from eBay, 2-week test. "Build the FB pack" step was blocked by a tool permission and awaits his confirmation. **Nothing was posted. His next messages (Oct 7 12:17 onward) moved to sales ideas, price matching and floor-100; he never confirmed the FB test.** Note he wants Mercari/Depop too ("they will never know"); Claude's research says their rules forbid listing unowned items, so I would not do that without telling him the account risk. Mercari/Depop/Poshmark/Whatnot ruled out (they forbid listing unowned items).
4. **Bally pair:** buy one blue loafer ($204, Farfetch, free 30-day returns), photograph it, unlocks photo-less low-competition shoes. **Not decided: when Claude offered "floor 100" or "Bally" (Oct 7 night) he chose floor-100 (Oct 8 2:49pm) and did not answer on Bally.**
5. **Floor-100:** expand / keep / revert after Oct 15.
6. **Returns:** Oct 7 4:01pm he said "do all of them but tell me before doing return policy; what is the lowest days of return possible?" Answer given: 30 (30 or 60 only). Claude suggested 30 days, buyer pays return shipping, as a way to lift sales. No decision yet. Must be told before any change.
7. **Offers to watchers on relisted items:** idea only; nothing sent without his OK.
8. **StockX developer API access:** requested around Sept 30 ("tell me when StockX approves you"). Status unknown; research currently reads StockX in the browser.
9. **Saturday research and check-in time:** see section 12.

## 6. Side venture: TikTok Shop / Amazon (separate from eBay; project files `claude/product-criteria.md`, `claude/tiktok-pet-roller.md`)
- Own-brand, creator-driven. Criteria agreed Oct 6 (≥$8–10 net/order, evergreen, multi-channel, no patent traps, one niche).
- Current pick (Oct 7): pet shedding kit (self-cleaning deshedding brush + electrostatic glove) at $29.99; product #2 poop-bag dispenser + refills; roller dropped (active utility patent to 2030). Test budget ≤ $800 (100 kits, 15 to creators).
- **Not started.** Rafael still needs to: open a TikTok Shop seller account, log in to Kalodata/FastMoss/Helium 10/Jungle Scout (so I can verify velocity), get supplier quotes. No scheduled tasks for it.

## 7. Next steps
1. **Rafael: pause "eBay Research v2" now; pause the backup "eBay Research" after today's in-chat run succeeds** (section 11), so research results only appear in this chat.
2. Today 6:40am ET: first in-chat research run; 7:20am: first daily check-in.
3. Oct 15 floor-100 review; Oct 16 ads review.
4. Decide #1 (compliance) before volume grows; #3/#4 if he wants more sales channels or photos.
5. Nov 1: limit resets → 8 waiting drafts publish; clocks change (in-chat tasks use fixed UTC times: reschedule to 11:40Z research / 12:20Z check-in).
6. M5 backlog: more store adapters, promo inbox, tracking ingest from store emails, Google Sheet dashboard, bookkeeping CSV.

## 8. Rules (summary; full spec in repo `CLAUDE.md`)
$100 net floor (target $250) · new with box only · qty 1 per size · match by style code, never show it on eBay · no returns, free shipping, ≥3-day handling · eBay catalog photos only · never auto-buy · cash cap $5,000 · NJ sales tax doesn't apply to shoes · StockX/GOAT checkout shipping $14.95 · decay never below 1.5× required profit (floor-100 test items: 1×).

## 9. Key paths (repo `relyassian/ebay-bot`)
`CLAUDE.md` · `config.yaml` · `docs/research_routine.md` · `docs/STATUS.md` · `data/source_prices.csv` · `data/candidates/` · `data/drafts_state.json` · `data/market.json` · `data/stats.json` · `data/selling_limits.json` · `data/notices.json` · `data/sales_log.csv` · `data/price_log.json` · `data/ads_state.json` · `data/rafael_requests.txt` · `plans/pending/` · `bot/` · `.github/workflows/`.

## 10. Accounts and tools
eBay seller `rafaelelyassian` (Trading API, refresh token in GitHub secrets) · GitHub `relyassian` · Telegram bot · Anthropic API key (Haiku replies) · Claude desktop app on Rafael's Mac (built-in browser signed in to eBay/StockX/GOAT; must stay open and awake) · Farfetch (signed in; free 30-day returns) · stores: StockX, GOAT, Cettire, Farfetch, Italist, Nugnes1920, END.

## 11. Scheduled tasks (times ET; all eBay results post in THIS chat)
| Task | Next run | Where | Notes |
|---|---|---|---|
| eBay daily research (in-chat), 8 tasks | 6:40am daily incl. Saturday: Oct 9, 10, 11, 12, 13, 14, 15, 16 | **this chat** | Reads STATUS.md first. Skips itself (and says so) if a separate research task already ran today. The Oct 16 run schedules Oct 17–30. |
| eBay daily check-in, 12 tasks | 7:20am: Fri Oct 9; Sun 11; Mon 12; Tue 13; Wed 14; Thu 15; Fri 16; Sun 18; Mon 19; Tue 20; Wed 21; Thu 22 | **this chat** | Reads STATUS.md first. The Oct 22 run schedules Oct 23–Nov 5. No Saturday check-ins. |
| Review floor-100 test `trig_01Q8gf…` | Thu Oct 15, 11:00am | this chat | Reads STATUS.md first. |
| Review eBay ads results `trig_019JtJ…` | Fri Oct 16, 10:00am | this chat | Reads STATUS.md first. |
| Re-read old chat gaps `trig_01L62x…` | Fri Oct 9, ~2:39am | this chat | One-off: reads Rafael's replies I couldn't reach, updates sections 5 and 12. |
| **eBay Research v2 `trig_01AG46…`** | daily 6:37am | separate session (Scheduled section) | **Rafael: pause this.** I tried to pause it; the permission check blocked me. Until paused, its results show up in the Scheduled section. |
| **eBay Research (backup) `trig_01QV4p…`** | daily 7:07am EDT (UTC cron: 6:07am after Nov 1) | separate session | **Rafael: pause this after today's first in-chat research run succeeds** (it is the safety net until then). Also has its own stale prompt. I can't edit it (created outside a chat). |
| Old chat copies of the two reviews | — | old chat | Already paused (`enabled: false`). Don't delete. |
| eBay listing monitor `trig_01Nf9e…` | — | — | Paused, replaced by the research tasks. |
| Other chats' tasks (Marketing/X/Reddit, Price AI, Shieldr, trading bot) | — | their own chats | Not eBay. Untouched. |

## 12. Known gaps and unverified items
- **Old-chat re-read done (Oct 9 ~2:40am ET):** read Rafael's own messages in turns 521–550 (Oct 6 10:52am to Oct 9 1:59am). Everything he said is now in sections 2 and 5. Turns before 521 were only searched, not read in full.
- **Sun–Fri preference vs daily research:** Rafael asked for Sunday–Friday monitoring (the old monitor ran Sun–Fri), but the research ran **every day including Saturday**, and I kept that for the in-chat research. Reason: store prices older than 36h take sizes off sale, and Friday 6:40am → Sunday 6:40am is 48h, so skipping Saturday would hide sizes for most of Saturday night and Sunday morning. Needs his call (alternatives: skip Saturday and accept the gap, or run Friday afternoon too). **Related, found in the old chat:** Rafael said "make the check everyday sunday through friday at 7 am sharp, not a few minutes before or after" (old chat, ~Oct 3–4). The old monitor was set to 7:00 Sun–Fri (scheduler still ran it ~7:04). The in-chat check-ins are at 7:20am and the old Research v2/backup at 6:37/7:07, so they do **not** match his 7:00 request. Needs his call.
- **In-chat research is unproven:** it relies on this chat receiving the scheduled message and still having the Mac link. First run is Oct 9 6:40am; if it fails the 7:07am backup is the safety net, so keep the backup unpaused until one in-chat run has succeeded.
- **Mac folder choice:** the Desktop folder is no longer reachable from this chat (only `~/Claude Code` is). The current STATUS.md is in `~/Claude Code/`; the old v1 in `~/Desktop/eBay Arbitrage/` is stale. If you keep a different project folder, tell me and I'll move it.
- **Lost with the old container:** scratch files (`goat_batch.json`, `log.txt`, `fb_rows.json` with the Facebook candidate picks). Their results that mattered are in `source_prices.csv`; the Facebook pick list is not and can be regenerated.
- **Inferred, not found:** about 20 older listings (47 live drafts + 66 compared ≈ 67 listings); "1 sale / $899.99" origin; whether the "1 sale / $899.99" is the pre-bot order that led to his GOAT order 200219919 (old chat said "either this order is from before the bot or sale alerts aren't working"; never confirmed). Whether he answered the FB/wholesale/ship-through-me offers in turns before 521 is unknown.

## Research run 2026-10-09 (in-chat, ~7am ET)
- Done: StockX refresh, 88 rows (25 pages), pushed. Selling limit $4,183.89 < $5,000, so Part B skipped.
- NOT applied: GOAT. 48 pages read, but ~200 of 270 sizes showed one flat price per page (e.g. $950 on Basket Green Demetra, whose page shows Buy New $269). Looks like a size-picker fallback, not real per-size asks. Old GOAT rows kept, so they expire after 36h and go off sale (safe). Needs a fixed extractor before GOAT is trusted. The assistant's click on "Buy New" was blocked (purchase flow), so it could not check the size picker.
- NOT done: END/Farfetch/Italist/Nugnes/Cettire rechecks; Part C (Gmail promos). Redo tomorrow.
- Backup research task (7:07am) still enabled; v2 paused.

## Check-in 2026-10-09 7:21am ET
- Research ran 6:48am ET (StockX only; GOAT not applied, see above). daily-sync success 7:02am; sale-alerts chain healthy (last 12 runs ok).
- Sales: none new (TotalSoldCount 1, $899.99). Selling-limit room $4,183.89. notices.json empty.

## 2026-10-09 2:50pm ET
- Backup research task (trig_01QV4pywhVAgf7BvHcDb4Q8k) was created via http_api; I can't edit it and it does not appear in my task list or (per Rafael) his. Its 7:07am run already fired. Check claude.ai/code/routines for it.
- GOAT extractor: Rafael approved opening the size picker (view only), but the auto-mode classifier still blocks the "Buy New" click. GOAT stays on old rows (expire after 36h). Fix needs a different route (e.g. GOAT's page JSON/network data via read_network_requests, no click).
