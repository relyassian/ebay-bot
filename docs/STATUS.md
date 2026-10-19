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
- **25 blocked drafts = all "needs photos"** (no eBay catalog photo; the 8 low-competition Oct 7 finds are among them: Bally blue + grey loafers, Margiela Sprinters, 2 Givenchy, Lanvin Curb pink, D&G Portofino off-white, Brunello Cucinelli beige, plus Ferragamo/Gucci/Prada/McQueen/Bottega ones). Rule (changed Oct 11, see below): eBay catalog photo, else store/marketplace photo.
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

## Research run 2026-10-10 (in-chat, 6:41am ET)
- Done: StockX 88 rows (25 pages) + GOAT 270 rows (50 pages) refreshed and pushed (`b281efe`). GOAT now read from GOAT's own per-size data feed (method in docs/research_routine.md), no clicking. 260 of 270 GOAT prices matched yesterday's old rows, so yesterday's old GOAT data was right and yesterday's flat-price reads were the bad ones.
- Not done: END, Farfetch, Italist, Nugnes, Cettire rechecks; Part C (Gmail promos); Part B skipped (selling limit $4,183.89).
- Guard: v2 disabled; backup task not visible in my list; newest data before this run was Oct 9 10:48Z.

## Research run 2026-10-11 (in-chat, 6:41am ET)
- Done: StockX 88 rows + GOAT 270 rows refreshed and pushed (`6d7c80b`). GOAT via buy_bar_data feed (docs/research_routine.md). StockX still needs page-by-page DOM reads (about 2-3 pages per browser batch, ~9 batches).
- Gap: one GOAT URL in source_prices.csv, `goat.com/sneakers/gucci-mac80-sneaker-blue-778301-aab79-4542`, is not in my GOAT page list, so its rows were not refreshed. One Gucci Run monogram size (US 13) has no GOAT size.
- Not done: END/Farfetch/Italist/Nugnes/Cettire rechecks; Part C Gmail; Part B skipped (limit $4,183.89).
- Waiting on Rafael: non-catalog photos for the 25 photo-blocked drafts (my Oct 10 recommendation).

## Check-in 2026-10-11 7:21am ET
- Research ran 6:50am ET (StockX + GOAT). daily-sync success 6:50am; sale-alerts chain healthy (last 8 runs ok, one in progress).
- Sales: none new (TotalSoldCount 1, $899.99). Selling-limit room $4,183.89. notices.json empty. Drafts: 49 live, 25 blocked (photos), 6 invalid.

## Oct 11 (evening): photo rule changed by Rafael
- Rafael: "just take photos from online somewhere" (after I warned about copyright takedown risk and that I had not verified Authenticity Guarantee behavior with non-catalog photos). CLAUDE.md rule 8 updated: catalog photo first, else store/marketplace photo of the exact style code; never other eBay sellers' photos.
- **17 of the 25 blocked drafts unblocked**: photo URL added to `data/candidates/<id>.yaml` (`photos:` + `photo_source:`), state reset so the next daily-sync/sale-alerts run re-drafts and eBay-verifies them. 14 photos from GOAT page `og:image` (one image per product; the page's other images are different colorways, so not used), 3 from StockX (`images.stockx.com`, white background). Two GOAT images were viewed and match the product.
- **7 still blocked (Farfetch-only, Farfetch blocks the browser, none on GOAT/StockX):** Bally blue + grey loafers, Brunello Cucinelli beige, D&G Portofino off-white, 2 Givenchy, Lanvin Curb pink, Margiela Sprinters. Need another source (brand site, other retailer) or the Bally buy-one-and-photograph idea.
- Watch: eBay Verify may reject a photo URL (hotlink or size); drafts then show "invalid" in `drafts_state.json`. Most new drafts will queue as `waiting_limit` (limit room $4,183.89, 8 already waiting).
- Not verified: whether Authenticity Guarantee accepts these listings without catalog photos; check the first one that lists.


## Oct 11, 21:15Z: result of the photo unblock
- 17 drafts re-processed: **4 listed live** (Bottega Eliot Mid, Ferragamo Cassini, Ferragamo Cosma, Prada Monolith) so eBay accepted the GOAT photo links; **no photo errors**. 4 skipped as uncompetitive (other sellers ask less: Gucci Driver Horsebit black + green, Gucci Horsebit Loafer black, Gucci Tennis 1977). 8 hit eBay's monthly listing limit (now $1,922.94 room) and were moved to waiting_limit so they retry. 1 real error: Gucci Cordovan Lux needs the item specific "Style" (to fix).
- Bottega, Cassini, Cosma and one Prada size were taken off sale by the sync right after listing: their store rows are from Oct 7 (older than 36h). They come back when the research run refreshes those GOAT rows (these 4 GOAT URLs are not yet in the daily path list: add them).
- Still unverified: Authenticity Guarantee with non-catalog photos (check first sale/AG status on the 4 live items).

## Oct 11 (night): near-market first
- Rafael: prioritize near-market listings to build sales/account history now; above-market products still wanted later. Code: `bot/newlistings.py` drafts() sorts by price/market median (closest first) and retries "uncompetitive" drafts once `pricing.match_market` is false. Until then they stay parked (4 so far: Gucci Driver Horsebit black/green, Horsebit Loafer black, Tennis 1977 white-green-red).
- Market comparison Oct 8-11: 7 of 26 measurable listings within ~1.25x of the eBay median (Rhyton Ivory, MAC80 White/Blue, Ace GG Embossed, MAC80 Blue...); 15 are 1.45-1.86x. Sale badges: one 14-day sale (Oct 5-19) on 12 listings; not verified on eBay itself.
- Next: put near-market listings first in daily price refresh; decide Oct 15 floor-100 test from sales.

## Oct 12: daily research (10:40Z run)
- Part A done: GOAT refreshed 329 rows, StockX 57 rows (26 pages); 390 rows now dated Oct 12. Sizes with only BID (no seller) left unchanged (38 skipped); they age out via the 36h freshness rule.
- New StockX reader (old mobile selector is dead): load page, wait 2.5s, click the button matching /^Size:/, wait 1.5s, collect unique button/li/[role=option] texts matching /^US M \d/. "BID" = no ask. Max 2 pages per browser_batch (50s limit). Cost = ask x 1.06.
- Part B skipped (listing limit remaining ~$1,923, under $5,000). Part C (Gmail promos) and END/Farfetch/Italist/Nugnes/Cettire rechecks NOT done. Farfetch still blocks the browser.
- Open: 7 Farfetch-only drafts have no photo source; Gucci Cordovan Lux needs "Style" item specific; check-in is 7:20am ET vs Rafael's 7:00 ask; backup research task trig_01QV4pywhVAgf7BvHcDb4Q8k not confirmed paused; "item from goat" question unanswered.
- Mac copy of STATUS.md still stale (Oct 9).

## Oct 12 check-in (11:28Z)
- Research ran today (newest checked_at 10:53Z). daily-sync success 10:55Z; sale-alerts chain healthy (runs every ~25 min, all success). No sales logged (1 sold total, $899.99). notices.json empty. data/selling_limits.json shows $4,183.89 but is stale; real remaining after 4 new listings ~ $1,923.

## Oct 12 evening: GOAT order checked (Rafael logged in; read-only)
- GOAT order #200219919: Gucci Ace 'GG Crystal Canvas - Green', UK 10 (US 10.5), ordered 9/29, total $560.95 ($546 + $14.95 shipping). Status "Verified" by GOAT ("will be shipped shortly"). Tracking number shown: 878356372280 (carrier not stated on page). Ships to the NJ authenticator address; line 2 reads `evtn:l227ktv SKC3` (eVTN intact, not truncated this time). Not yet confirmed as delivered. Whether it matches the $899.99 eBay sale is still unverified.

## Oct 12 night: tracking added to eBay
- eBay order 11-15213-78941 (Gucci Green Ace GG Crystal Canvas, US 10.5, $899.99, created Sep 26) = the $899.99 sale = GOAT order 200219919 (cost $560.95, est. net before fees about $340 minus eBay ~14%).
- FedEx 878356372280 added to the order via new `add-tracking` command/workflow (CompleteSale, workflow id 382671516, inputs order/tracking/carrier). FedEx status at the time: Label Created Oct 7 (Shatin, HK), not yet picked up.
- Watch: eBay ship-by / late-shipment risk if FedEx doesn't scan soon; GOAT support if still unscanned in a few days.
- Not yet automated: parsing store emails for tracking (bot still needs this).

## Oct 13: daily research NOT run (Mac browser unreachable)
- 10:40Z scheduled research fired, but the linked-computer tools (built-in browser) are gone from this session. WebFetch fallback was refused (permission not answered) and GOAT/StockX sizes need JS anyway. No prices changed; newest checked_at is still Oct 12 10:53Z.
- Guard: no other research task fired today (checked page 1 of enabled tasks; research tasks not listed there).
- IMPACT: rows older than 36h expire at about 22:53Z Oct 13 (6:53pm ET). Without a refresh the sync takes live sizes off sale after that.
- Fix: reopen this chat in the Claude desktop app on the Mac (Link to this computer), then re-run research. Tracking added to eBay order 11-15213-78941 Oct 12 (see above).

## Oct 13 check-in (11:22Z)
- Research did NOT run today (Mac unreachable); newest checked_at Oct 12 10:53Z; rows expire ~22:53Z tonight. sale-alerts chain healthy (all recent runs success); daily-sync last success Oct 12 10:55Z. No new sales. Limit room ~$1,923 (file stale at $4,184). 4 notices: listing-limit refusals (Gucci Interlocking G loafer, MAC80 blue, Bottega Eliot, Ferragamo Cosma).

## Oct 13 (12:30pm ET): research re-run after Mac relink
- GOAT 328 rows + StockX 95 rows refreshed (423 rows dated Oct 13). Rows from other stores (Sept 30 / Oct 8) not rechecked: Part B skipped (limit ~$1,923), Part C and other-store rechecks not done. Browser was run 1 page per call when pages timed out (2 in parallel batches interleave: use one browser_batch at a time).

## Oct 13 (≈1:30pm ET): "recheck" of non-GOAT/StockX rows
- Italist Ferragamo Grandioso black (355066429434): read Shopify .js. 6 rows refreshed at $619.26; US 8.5 is out of stock, row removed (size goes off sale).
- Nugnes1920 Gucci Ace GG Supreme beige (355429385763): US 7 and US 8 both in stock at $625, rows refreshed.
- NOT refreshed (blocked): Farfetch Ferragamo Gancini moccasins (8 rows) and D&G Saint Tropez (2 rows) show a bot check; Cettire cufflinks page renders blank. These rows expire 36h after their Oct 8 check and those sizes/listings go off sale unless Rafael loads them in the browser (Farfetch worked after sign-in on Oct 5).
- Stale GOAT single sizes (Run beige-ebony US 13, Bottega US 12, Nima US 12) not refreshed (no size match in today's GOAT run).
- Update (≈1:20pm ET, after Rafael signed in): Farfetch Ferragamo Gancini (8 rows) and D&G Saint Tropez (US 7 $465, US 8.5 $452) read in browser; stock and prices unchanged, rows refreshed. Cettire cufflinks (blank page) and 3 single GOAT sizes still not refreshed.
- Cettire cufflinks (356084785661) read in browser ≈1:20pm ET: in stock, $241.06 duties included (was $246.48); row refreshed. Only the 3 single GOAT sizes remain unrefreshed.

## Oct 14: daily research (10:41Z run, Mac browser linked)
- Part A done: GOAT 327 rows + StockX 95 rows (26 pages, one page per call; 2 per batch times out) refreshed; Italist Grandioso (6 rows, now $620.57), Nugnes Gucci Ace beige (2), Farfetch Gancini (8) and D&G Saint Tropez (4 rows incl. US 6/8 not read on page; US 7 $465, US 8.5 $452 confirmed), Cettire cufflinks ($241.06) re-read, all unchanged except Italist FX. 422+ rows dated Oct 14. 4 GOAT sizes had no listing at GOAT today (Kaveh 12.5, Run beige-ebony 13, Bottega 45/US 12, Nima US 12): left stale, they go off sale after 36h.
- Part B skipped (limit ~$1,923). Part C: Gmail had only a StockX seller-fee promo; promos.yaml now has Cettire FIRST10 and Farfetch GET10 (to Oct 28, selected styles, $300 min basket).
- No rafael_requests.txt. Guard: newest checked_at was Oct 13 before this run; research tasks 'eBay Research v2'/'eBay Research' not seen on page 1 of list_triggers (has_more), not confirmed paused.
- Browser notes: Farfetch/Cettire sometimes redirect once (interstitial) then load; re-navigate, then read with separate JS calls (timers stall when the pane is hidden). Mac STATUS.md still stale.

## Oct 14 check-in (11:20Z)
- Research ran today (441 rows dated Oct 14, newest 11:20Z). daily-sync success 10:57Z and 11:01Z; sale-alerts chain healthy (all recent runs success). No sales logged since Oct 13 (1 sold total). Limit file still stale at $4,183.89 (real ~ $1,923). notices.json: listing-limit refusals (cufflinks 356084785661, Ferragamo Grandioso 355066429434, Ferragamo Gancini moccasin 355420832785, plus others earlier): their price/qty changes won't apply until the limit resets ~Nov 1. Watch FedEx 878356372280.

## Oct 15 research (scheduled run, ~11:00-11:20Z)
- Refreshed: GOAT 327 rows, StockX 26 pages / 95 rows, Italist (Ferragamo black loafer), Nugnes (Ace GG Supreme), Farfetch (Gancini moccasin, D&G Saint Tropez), Cettire cufflinks. All other-store prices/stock unchanged vs Oct 14. Rows dated Oct 15, good until ~Oct 16 23:00Z.
- Part B skipped (selling limit remaining ~$1,923, resets ~Nov 1). Part C: Gmail promo search returned nothing new; promos.yaml unchanged (Farfetch GET10 still shown on site, expires Oct 28).
- Still stale (go off sale after 36h, safe): Kaveh 12.5, Run beige-ebony 13, Bottega US 12, Nima US 12 (no GOAT listing).
- Open for Rafael: FedEx 878356372280 (Gucci order 11-15213-78941) - confirm it's been scanned, else contact GOAT support. Floor-100 review today; ads review Oct 16.

## Oct 15 check-in (11:20Z)
- Research ran (newest checked_at 11:03Z today). daily-sync success 11:04Z; sale-alerts running every ~25 min, all success. No notices. No new sales logged (TotalSoldCount 1 / $899.99).
- Selling-limit file still shows stale $4,183.89; real remaining ~$1,923, resets ~Nov 1.
- Rafael: check FedEx 878356372280; floor-100 review today.

## Oct 15 floor-100 review (15:00Z)
- Result: inconclusive on sales. 0 sales on the 5 test listings and 0 on every other listing since Oct 8 (account total still 1 sold, the $899.99 Green Ace).
- Interest (stats.json, Oct 15, 7-day views per live size): test listings 50 views / 9 live sizes = 5.6; other 56 listings 422 / 267 = 1.6. Watchers 4 vs 131 (0.4 vs 0.5 per size). Test items get ~3.5x views per size; no watcher lift.
- Cost of the test: each pair gives up ~$50 of margin vs the 1.5x floor ($100 vs $150). Prices dropped 1-5 steps since Oct 8 (e.g. Embossed Black from $929.99 to $683-821; MAC80 B/OW from $1,044.99 to $678-860).
- Recommendation: KEEP as is (do not expand, do not revert) and re-review ~Nov 1 when the selling limit resets and more listings are live. Rhyton Ivory now has 0 live sizes (unsourceable).
- No config changed.

## Oct 15 night: ad boost change (Rafael: "just do something to get sales")
- Why no sales: traffic is thin (55 views/day across 60 listings, falling; new account, 1 sale). Not a price problem.
- Found: ads already ON at 8%; the bot already auto-boosts to 10-15% where every size keeps 1.5x profit (12 listings on Oct 14).
- Change (commit 9f2f5d0, config `ads.top_viewed_n: 10`, `top_viewed_mult: 1.0`): the 10 most-viewed listings (7-day views) may take 10/12/15% down to the $100 profit floor. Ad fee is only charged on an ad-driven sale.
- Triggered the market workflow (id 377802242) at 03:14Z Oct 16 to apply it; result to be posted in this chat. Daily run re-tunes automatically.
- Rafael to do: request a higher selling limit in Seller Hub (Performance > Selling limits). Limit room ~$1,923 until ~Nov 1.
- Ads review (trig_019JtJ…) is Oct 16 10am.

## Oct 17/18 catch-up research (run late night Oct 17 ET)
- Gap: no research Oct 16 or Oct 17 (chained one-shots lapsed). Prices were >36h stale, so sizes were heading off sale. Manual refresh done: GOAT 60 pages (327 rows), StockX 26 pages (95 rows), Italist, Nugnes, Farfetch (Gancini, D&G Saint Tropez), Cettire cufflinks ($241.06, Add to bag). Committed "research: 2026-10-17".
- Changes seen: Farfetch Gancini sizes 6-7.5 now $725 (was $731); D&G Saint Tropez US 7 $460, US 8.5 $452; Italist Ferragamo loafer $610.50.
- Not refreshed: GOAT US 13 on 820207186222 (no GOAT listing) stays stale, goes off sale after 36h (safe). Promo Gmail scan and the Oct 16 check-in / ads review still to do.
- Recurring prevention: scheduled task "eBay daily research (recurring)" trig_01KccF1saAhBjHmECjbhgdVJ, cron CRON_TZ=America/New_York 40 6 * * *, needs the Mac, auto-approve. Uses America/New_York so it follows the Nov 1 clock change. Old backup triggers trig_01AG46TxH4X9tRdmeGVZN5Gi and trig_01QV4pywhVAgf7BvHcDb4Q8k not confirmed paused.
- Ad boost: market workflow ran; 16 listings boosted (6 at 10%, 6 at 12%, 4 at 15%), up from 12.
- Risk: on Oct 16 eBay refused hide-size changes on 13 listings (selling limit), so some stale sizes may still be live. See data/notices.json.
- Rafael to do: check FedEx 878356372280 (Gucci order 11-15213-78941, unscanned as of Oct 13; contact GOAT support if still unscanned); request higher selling limit; photos for 7 Farfetch-only drafts. Re-review floor-100 test ~Nov 1.
- Mac copy of STATUS.md (~/Desktop/eBay Arbitrage/) still stale since Oct 9; repo copy is current.

## Research run 2026-10-18 (scheduled 6:40am ET run, Mac browser linked)
- Guard passed (newest checked_at was Oct 18 03:47Z = 11:47pm ET Oct 17). Refreshed: GOAT 60 pages (328 rows, 11 price changes; Gucci Ace Embossed White US 13 now $2,235 = effectively unsourceable, Rhyton Maxi 8.5 $874), StockX 26 pages (94 rows, 11 changes; Tennis 1977 GG Canvas US 6 down to $437, US 11.5 up to $1,027), Italist Grandioso (unchanged $610.50, 6 sizes in stock), Nugnes Ace beige (unchanged $625, US 7/8), Farfetch Gancini (unchanged, 8 sizes) and D&G Saint Tropez (EU 39/40 $460, EU 41.5 $452; US 6 row now Farfetch $460 instead of GOAT $483), Cettire cufflinks ($241.06, Add to bag).
- Stale on purpose (go off sale after 36h, safe): Run beige-ebony US 13 (no GOAT size 12.5), Bottega Eliot US 12 (GOAT has no EU 45), Nima US 12 (no GOAT listing), Rhyton/Ace Crystal Black etc. StockX BID-only sizes left unchanged (820204075517 US 12).
- Part B skipped: real selling-limit room ~$1,923 (selling_limits.json is stale at $187k/$4k). Part C: Gmail promo search (21 days, 12 stores) empty; promos.yaml unchanged (Cettire FIRST10 app-only, Farfetch GET10 to Oct 28).
- Farfetch needed two navigations (blank interstitial first); size menu opens via synthetic mouse events on the DropdownLabelWrapper div (no real click needed).

## Oct 18 check-in (11:20Z)
- Research ran Oct 18 (commit ff30549, 441 rows; some checked_at stamps read up to 11:40Z, i.e. slightly in the future: harmless for the 36h rule). daily-sync and market succeeded; sale-alerts chain is running.
- Sales: still 1 total ($899.99, Oct 2). 7-day views 377 (down from 610 Oct 12), watchers 252.
- Selling limit raised by Rafael Oct 18: room $187,487 (was ~$4.2k). Notices: none.
- Ads: 28 shoe listings on 8%, 17 boosted 10-15%.
- Open: 8 drafts blocked "needs photos" (none on GOAT/StockX by exact code; Farfetch photos need Rafael's OK because of takedown risk). 4 drafts parked "uncompetitive". 33 of 77 listings >5% above another seller.
- Proposed (awaiting Rafael): new-product research now the cap is lifted; $100 floor for the top-viewed listings only.

## Oct 18 afternoon: new-product research pass (Rafael: "go, do the job")
- Scanned Nugnes1920 men's shoe collections (Shopify products.json, compare_at vs price, in-stock sizes): 11 items at 36-51% off, but 1-3 sizes each. Italist products.json is mostly BGW/non-shoes: not scanned. Farfetch search shows no sale %, not scanned further.
- Estimated nets ($100-160 at ~3% under retail, 8% ads, unverified US retail, duties unknown). Catalog photo check (requests/catalog.txt): only Gucci Lace-Up 865172AAGBV1000 has an eBay catalog match with images (UK 6 only, $680). Enki/Screener matches have no images. No candidates written: thin sizes, thin margins.
- Conclusion: store-sale arbitrage on these brands is near the margin floor; more listings are not the lever by themselves. Options to Rafael: Farfetch photos for the 8 blocked drafts (takedown risk), $100 floor on top-viewed only, wait for ads (review ~Oct 25).

## Research run 2026-10-19 (scheduled 6:40am ET run, Mac browser linked)
- Guard passed (newest checked_at was Oct 18 20:14Z). Refreshed: GOAT 60 pages (327 rows, 22 price changes; e.g. Ace Embossed Black US 12.5 down to $513, Ace Crystal Green US 12.5 up to $2,435 = effectively unsourceable), StockX 26 pages (91 rows, 25 changes; BID-only sizes left unchanged: Ayrton black US 12, Ace Supreme Bees US 14/14.5, Ayrton brown US 7.5), Italist Grandioso ($622.07, was $610.50; US 5 now sold out so its row is blank = off sale; 5.5/6/6.5/7/8 in stock), Nugnes Ace beige (unchanged $625, US 7/8), Farfetch Gancini (unchanged; US 11.5 $950 now exists but is not on the listing), Farfetch D&G Saint Tropez (EU 39/40 $460, EU 41.5 $452, unchanged), Cettire cufflinks ($241.06, Add to bag). 438 rows dated Oct 19.
- Method: GOAT via buy_bar_data in one JS call (all 60 in ~20s); StockX 3 pages per browser_batch works (iframe approach returns empty, do not use).
- Stale on purpose (go off sale after 36h): Run beige-ebony US 13 (no GOAT 12.5), Bottega Eliot US 12 (no GOAT EU 45), Nima US 12. The 8 Farfetch-only draft rows (Bally, Cucinelli, D&G Portofino, Givenchy, Lanvin, Margiela) were NOT re-read; they expire about Oct 20 08:00Z (drafts only, no live listing).
- Part B (new products) NOT done today. Correction: selling-limit room was ~$187k on Oct 18 (Rafael raised it), so the under-$5,000 skip rule no longer applies; I did not verify room today and ran out of the run on Part A. Next run should do Part B. Part C: Gmail promo search empty; promos.yaml unchanged (Farfetch GET10 to Oct 28, Cettire FIRST10 app-only).

## Oct 19 check-in (11:23Z) + Oct 18 evening changes
- Oct 18 ~16:20 ET: Rafael OK'd "use any photos you can". 8 blocked drafts got Farfetch product photos + re-read sizes/costs; 7 went live (Bally blue + grey loafers, Brunello Cucinelli suede sneaker, D&G Portofino off-white, Givenchy padded nylon trainer, Lanvin Curb pink, Margiela Sprinters). Givenchy Gent derby invalid: eBay needs the "Style" item specific (TODO). Takedown risk: Farfetch photos.
- Oct 18 selling limit raised: room $187,487. New-product scan (Nugnes 36-51% off) found nothing worth listing.
- Today: research ran (f00244d, newest checked_at 10:52Z), daily-sync + sale-alerts OK. Drafts: 65 live, 11 invalid, 4 uncompetitive. 7-day views 375, watchers 252. No sale alerts; total sold still 1 (last limits read Oct 18).
- eBay sale started on 5 listings. Notices: none.
- Open: Givenchy derby Style field; ads review ~Oct 25; $100 floor on top-viewed (awaiting Rafael); FedEx 878356372280 check; Mac STATUS.md copy not reachable this session. Note: two "eBay daily check-in" triggers exist (trig_01PiTdw4wssvNMrEMNMa3QPJ and trig_01MGrTqxmq39kn4SdXKPrXRc) - possible duplicate.

## Oct 19 afternoon: floor 100 + new-listing push (Rafael: "take it down to 100 but not less", "make new listings", "use other websites' photos", "belts/ties too", "prioritize items below market")
- config.yaml pricing.floor100_items now has the 10 most-viewed listings (+5 from the Oct 8 test): market matching may go to exactly $100 net. Net math (bot/profit.py) = price x (1 - 13.6% fee - the listing's own ad rate [cfg_for] - 1% buffer) - landed (cost + shipping + duty if overseas + tax if taxable). Checked all 9 new IDs: min net at the floor is $100.05 at the base 8% ad rate; ads.tune only boosts a rate when every live size keeps >= $100 at that rate, so price and rate never undercut $100. Weekly 3% decay for these items still stops at 1.5x (pricing.decay_price has no item id): not changed.
- Real risk to "exactly $100": store prices move after the check (Margiela rose $512 -> $569 overnight). Bot re-reads prices daily, raises up to 15% or hides the size.
- Givenchy derby: added Style=Derby, re-approved (verify pending). Gucci Cordovan Lux still needs a verified Style.
- 9 old Gucci drafts (MAC80 x4, Re-Web x2, Run, Screener, Horsebit ivory) were "invalid" only because of the old limit; at their $1,045-1,265 prices vs eBay median $400-610 they are uncompetitive, so NOT re-approved.
- Accessories scan (Nugnes man belts/wallets/ties/Gucci/Fendi/Bottega/Loro Piana, 42 products fetched): only D&G leather belt $375 (40% off) - above the belt buy-price ceilings. Nothing listed. Footwear scan earlier: nothing worth listing.
- Rafael OK'd photos from other websites (Oct 19); still never another eBay seller's photos.

## Oct 19 evening (Rafael: "daily", store question)
- Daily below-market scan added as Part D in docs/research_routine.md; recurring task trig_01KccF1saAhBjHmECjbhgdVJ (6:40am ET, needs the Mac) prompt now runs Parts A-D. First Part D run: Oct 20.
- Givenchy derby (givenchy-gent-derby-black) is live.
- eBay Store question: fee savings per third-party source (edesk, unverified against eBay) ~0.9% Basic / ~1.5% Premium vs $21.95-$27.95 / $59.95-$74.95 per month; break-even roughly $2.4k/mo (Basic) to $4k+/mo (Premium) in sales. Recommendation: rename the username (free, once per 30 days, feedback moves with it) but skip the store subscription until sales volume justifies it. Not done yet: the rename itself (Rafael's call). Check the bot's eBay token still works after any rename.

## Oct 19 night: price endings + photo upgrade
- Prices now end in 4.99 / 9.99 (bot/profit.py charm_up / charm_near; floors round UP so the $100 net is never breached; weekly drops and market matching round at/under the target). Applies only when the bot sets a price (no mass re-price, so eBay sale badges stay). 52 tests pass.
- Photos: 58 of 79 listings had 1-2 photos (data/photo_worklist.json). StockX/GOAT pages have one studio image only; eBay catalog has no extra angles for these codes. A research agent found multi-angle sets for only 3 of the first 30 (Stadium Goods for the 2 Gucci x adidas Gazelles, Italist for the Re-Web); Farfetch rate-limited the browser (429) and doesn't index Gucci style codes. The 3 sets were flattened to white JPGs, committed to data/photos/<item>/ (repo is public, so eBay reads raw.githubusercontent.com URLs) and applied via plans/approved/2026-10-19_photos.json (bot/photos.py builds it from data/photo_results.json).
- Not found (27 of the first 30; items 31-58 not tried): see data/photo_results.json history / worklist. Next: END product pages (slug contains the style code), Farfetch after the 429 clears (~1 request per 2 s), Mytheresa/Nordstrom by model name, brand sites.
- TODO: new-listing pipeline should require/collect several photos (candidate photos list) instead of 1.
- Result (Oct 19 night): both Gucci x adidas Gazelle listings now show 7 photos on eBay (verified in the fresh snapshot). The Re-Web (820204075633) still shows 1 photo: the revise did not take and the error wasn't logged (the listing has no live sizes right now). Re-try with a new plan after the next research run.

## Oct 19 night (2): photo fix
- GOAT product pages carry 8 extra studio photos in __NEXT_DATA__ (productTemplateExternalPictures; fetch the page from inside a goat.com tab and read `additional_pictures/.../medium/` URLs, swap to /original/ and download from image.goat.com). Standard order: 1 side, 2 side close-up, 3 medial, 4 sole, 5 sole close-up, 6 heel pair, 7 heel close-up, 8 pair 3/4 front. We use [8,1,3,2,6,4,7], padded square on white, hosted in data/photos/<item>/ (public repo, raw.githubusercontent.com).
- Applied Oct 19 22:46Z: 26 GOAT sets + the 2 Gazelles (Stadium Goods) + Re-Web. Verified in snapshot: 31 listings now have 7 photos; 29 still have 1 (listed in data/photo_worklist2.json; GOAT has no extra pictures for those, e.g. brown Interlocking G loafer, Horsebit drivers, Ferragamo Lunar/Cassini/Cosma/Nima, McQueen, LV, Bottega Eliot).
- A second research agent is looking for those 29 elsewhere (Cettire, Luisaviaroma, Mytheresa, END, Saks, resale sites); results go to data/photo_results2.json (not yet applied; merge into photo_results.json and run `python -m bot.photos`).

## Oct 19 late night: photo batch 2 done
- 27 more listings got retailer galleries (3–6 photos, best 3/4 angle first; hosted in `data/photos/<id>/`, results in `data/photo_results.json`). Verified in snapshot: 87 listings now have ≥3 photos.
- Still 1 photo (skipped on purpose): 820229265137 (McQueen, no good source) and 820207186315 (only watermarked shots found).
- Weak sets to upgrade later: 820207186550 (green Driver, mixed shots), 820204075737 Rhyton, 820207186615 MAC80.
- New-listing pipeline should collect several photos per candidate (todo).
- Still pending: Rafael's store-name choice (my pick: Corso Luxe); first Part D scan runs Oct 20 6:40am ET (needs the Mac on).
