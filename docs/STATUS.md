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

## Research run 2026-10-20 (scheduled 6:40am ET run, Mac browser linked)
- Guard passed (newest checked_at was Oct 19 10:52Z). Refreshed 462 rows: GOAT 60 pages (15 price changes; Run beige-ebony US 13 and Bottega Eliot US 12 have no GOAT size now: left unchanged and expire), StockX 26 pages (9 changes; BID-only sizes left unchanged: Ayrton black US 12, Ayrton brown US 7.5), Italist Grandioso ($621.73; US 6/6.5/7/8/5.5 in stock, US 5 sold out), Nugnes Ace beige ($625, US 7 and 8 in stock), Farfetch Gancini and D&G Saint Tropez (unchanged), the 8 Farfetch-only rows behind live listings (Bally x2, Cucinelli, D&G Portofino, Givenchy trainer + derby, Lanvin, Margiela) and Cettire cufflinks ($241.06, Add to bag).
- Farfetch changes: Margiela Sprinters EU 41/42/43 now $508 (was 569/569/695); Givenchy padded trainer FR 41 (US 8) sold out, row blanked (off sale); Lanvin Curb FR 43 (US 10) is $754, not $533 (the Oct 18 figure looks like a misread; +41% so the bot keeps that size off sale).
- Part B skipped (time; room is ample, ~$173k in the file). Part C: Gmail promo search (21 days, 12 stores) empty; promos.yaml unchanged (Farfetch GET10 to Oct 28, Cettire FIRST10 app-only).
- Part D (first run): scanned Nugnes1920 sneakers/shoes/loafers/belts/accessories-man via products.json: ~46 in-stock items at 35-51% off. 0 candidates written. Best discount: Givenchy Nabuk sneaker $438 (51% off $895, US 8/10/11 area sizes 41/43/44) and McQueen loafer $458, but ships from Italy (duty) and needs a list price near or above typical eBay resale to clear $100; eBay comps NOT checked (eBay bot check). Valentino items skipped (excluded brand). Needs a market check before listing.

## Oct 20 check-in (7:20am ET)
- Research ran today (534 source rows, newest checked_at Oct 20; Part D scan included). daily-sync latest run success (11:01Z); sale-alerts chain running. One daily-sync failure Oct 19 23:14Z was superseded by a success.
- Sales: still 1 total ($899.99). Selling-limit room: 13,673 items / $173,587. No notices waiting.

## Oct 20 afternoon: Part D scan by hand
- Scanned Nugnes1920 (672 discounted items) and Italist (men, >=20% off, >=$200): 85 screened against live eBay comps (27 had >=2 comps).
- Result: 0 viable. Store sale prices sit at or above the eBay median (e.g. Givenchy leather sneaker $420 vs eBay median $455; D&G belt $357 vs $297; Gucci loafers $588 vs $490). Best was a Moncler sneaker at ~$46 net, 1 size.
- Lesson: only deeper-than-retail-sale sources (Farfetch/SSENSE/Cettire 50%+ off, browser needed) clear $100. New tool: `requests/scan.json` + `requests/market` push -> `data/scan_results.json` (see docs/research_routine.md Part D).
- Selling room is not the limit (13,673 items); candidates are.

## Oct 20 evening: wider scan (Rafael: "go for the best opportunities")
- Screened 469 more men's luxury shoes/belts from Slam Jam, Antonioli (US page = USD, duties included), Biffi, Baseblu against live eBay comps. 129 had >=3 comps.
- Only hit: Margiela Sprinters white/grey (S97WS0092H0966), Antonioli US $530, eBay comps ~$800 (n=2, other colorways). Listed as item 820259478300, price $799.99, source rows added to data/source_prices.csv (bot had hidden it for lack of rows). Thin comps: watch it.
- Near-misses: MM6 sneaker SH3WS0012P6435T1003 at Biffi $192 (~$93-110 net, duty at checkout unknown, cheap competition from $220); Givenchy New City 1 size.
- Blocked: SSENSE (Cloudflare), Farfetch (blank page in Mac browser), Mytheresa sale (JS). Do not bypass.
- Takeaway: discount boutiques are priced at or above eBay. Better leverage may be price/market side (listing items we already source) or new categories, not more boutique scanning.

## Oct 20 3pm: state of the store + why no sales (Rafael asked)
- 87 listings on eBay: 86 bot-managed + AirPods Max ($375, Rafael's own, bot ignores). 75 have >=1 size live, 11 fully hidden (out of stock at stores). 326 live sizes. 7-day views 426, watchers 252, 1 sale total.
- Cufflinks live at $599.99 (cost ~$241). Selling limit room 13,673 items / $173,587; $5,000 cash cap untouched.
- Root cause of no sales: market.json shows 34 of 74 priced listings are >5% above the cheapest competitor and 22 of 24 with comps are above the eBay median (many Gucci $100-300 over). Only 5 of 24 would net >=$100 at 95% of median, 11 net >=$0.
- Proposal to Rafael pending his go: lower floor for sales (e.g. $50), reprice the items that net >=$50 at ~95% of median, delist the underwater ones, then fill to 100 only with at-market items.

## Oct 20 evening: real fee on the Gucci sale + demand scan status
- Order 11-15213-78941 (Gucci Ace GG Crystal green, Casual Shoes cat 24087): eBay fee $132.90 on $899.99 price / $974.24 total incl. buyer tax = 13.6% of the TOTAL (tax included) + $0.40 per order = 14.8% of price. Seller received $767.09 (held to Oct 27). Bot model (13.6% + 1% buffer) is within ~$5 of this; buffer covers the tax-on-fee effect but not the $0.40.
- eBay fee page: 8% (no per-order fee) only for Athletic Shoes category at >= $150; 52 listings are in Athletic Shoes (not verified against a sale); Ace Crystal listings are Casual Shoes so they pay 13.6%. Do not move categories just for fees.
- Older cancelled order 13-15032-44930 (Ferragamo Rolo, Aug 16, refunded Aug 25): the cancellation history Rafael wanted to avoid.
- Demand scan (competitor sold quantities via Browse API) failed with HTTP 429: eBay daily Browse quota used up by today's scans. It reruns automatically in tomorrow's daily-sync (after reset ~3am ET); results -> data/demand_results.json. requests/scan.json cleared to save quota.

## Oct 20 night: $80 market floor applied
- Rafael: "willing to bring it down to $80". Config `pricing.market_floor_net: 80` (bot/sync.py market_drops): market matching may go to $80 net on every listing; new listings and weekly decay keep their old floors ($100 / 1.5x).
- Daily-sync applied it: 30 listings / ~125 sizes repriced (most Gucci Basket, MAC80, Tennis 1977, Run, Horsebit; typically $20-100 lower). No listing delisted (underwater ones stay at their floor, above market).
- Incident: my scans exhausted eBay's daily Browse quota, so market.json was overwritten with 0 items twice; restored from commit 1c73a09 and added guards (bot/market.py keeps last good data if all lookups fail; demand/scan skip when fresh). If market.json shows 0 items, restore it.
- Pending: demand scan (data/demand_results.json) reruns in tomorrow's daily-sync; review which products/categories actually sell, then decide keep/delist/add. Store name still open (pick: Corso Luxe). First proper Part D run Oct 21 6:40am ET.

## Oct 21 research run (6:40am ET, scheduled)
- Guard passed (newest checked_at Oct 20 18:58Z). Mac reachable. Refreshed: GOAT 60 pages (305 rows re-read, 23 price changes; Run beige-ebony US 13 has no GOAT size, left unchanged), StockX 26 pages (19 price changes; BID-only left unchanged: Ayrton black US 12, Ayrton brown US 7.5, Indigo driver US 9.5), Italist Grandioso ($620.85 page price; kept $621.73; US 5.5/6/6.5/7/8 in stock, 5 sold out), Nugnes Ace beige (UK 7.5 / US 8 now sold out there; US 8 row switched to GOAT $740; US 7 still $625), Antonioli Margiela (all EU 40-45 in stock, $530; removed 6 duplicate rows), Cettire cufflinks ($241.06, Add to bag).
- NOT refreshed: Farfetch (10 products: Gancini, D&G x2, Bally x2, Cucinelli, Givenchy x2, Lanvin, Margiela). Page renders blank in the Mac browser; not bypassed. Their rows (checked Oct 20 ~11:00Z) expire ~Oct 21 23:00Z and those sizes go off sale unless a later run reads them.
- Part C: Gmail promo search (21 days, 12 stores) empty; promos.yaml unchanged.
- Part B and Part D: NOT run this time (the full price refresh used the session; prior Part D runs found 0 viable at boutique prices). Next run should do Part D first if time is short.

## Oct 21 check-in (7:20am ET)
- Research ran (Oct 21 6:40 run; 540 source rows, newest checked_at 11:35Z). Farfetch not refreshed (blank page); its 10 products' rows expire ~Oct 21 23:00Z and those sizes will hide. Part B/D skipped.
- Bot healthy: daily-sync success 10:56Z; sale-alerts chain running (last 10 runs success).
- Sales: still 1 total ($899.99). Selling-limit room 13,667 items / $177,134. No notices.
- Demand scan: data/demand_results.json has only 2 entries (1 ok) after 11:12Z sync; Browse quota/limit likely still short. Re-dispatch market workflow later today and check.
- Cufflinks (356084785661): left at $599.99; floor for $80 net is ~$480; no comps. No change made.

- Rule (Rafael, Oct 21): never tell GOAT or any store/third party an order is for resale. Added to CLAUDE.md Fulfillment.

## Oct 21 evening: demand ranking + sunglasses scan (Rafael: "scan for whatever works, we need sales")
- Demand (competitor sold/30d, top-10 listings): Gucci sunglasses ~43, Prada sunglasses ~21, Ferragamo belts ~17, Ferragamo ties ~7, Prada wallets ~3; nearly every shoe model 0-1.3/30d (48 of 70 products with competitors show 0 sold). (Earlier note "demand has only 2 entries" was my parsing error; file has 117 entries.)
- But volume is cheap gray-market: Gucci sunglasses sell ~$140-210, Ferragamo belts ~$95, Prada sunglasses ~$160.
- Scanned 94 in-stock sunglasses models (Italist, Slam Jam, Browns; Gucci, Prada, Ferragamo, Tom Ford, Ray-Ban, Oakley, Burberry) vs live eBay comps (74 had comps): 0 clear $80 net at 95% of median (assumes $20 ship, 10% duty on Italist, 5% ad rate). Best was Ferragamo SF1061S at about -$16.
- Conclusion: boutique prices >= eBay for everything scanned. Sales need either cheaper sources (Farfetch/SSENSE sale, not reachable from shell) or accepting lower margin.

## Oct 21 night: $75 floor, higher ad rates, bigger sale badges (Rafael: "anything at 75 now just to make sales")
- Config: pricing.market_floor_net 75 (was 80); ads.boost_floor_net 75 + boost_steps up to 20% (each listing gets the highest ad step that keeps net >= $75 at its current price); markdown.floor_net 75 and steps [25,20,15,10,5] (sale badges where every live size nets >= $75 after the discount).
- Bug found and fixed: sync's raise check (bot/sync.py) still used the $100 floor, so the Oct 21 daily-sync raised ~25 listings back up and undid last night's market drops. It now uses min(base, market_floor_net). Not covered by a new test (53 existing pass).
- After fix: 2 more daily-sync runs; no further market drops fired, so the remaining above-market listings are at their $75 cost floor (cost too high to compete). Ad rates now: 44 listings at 12%, 13 at 20%, 8 at 15%, 3 at 18%, 1 at 10%.
- Sunglasses: even at the cheapest eBay comp, best model nets about -$22. Nothing viable at $50 either.
- New listings still use the $100 floor (listing.py); not changed.

## Oct 21 late: category research (Rafael: "anything else we can sell with high profit that is popular?")
- Built `explore_requests()` in bot/market.py (requests/explore.json -> data/explore_results.json): median new-listing price + sold quantity for any search. Ran 123 queries (TCG, toys, electronics, fragrance, watches, other shoe brands, women's luxury, jewelry). Results in data/explore_results.json (last run = women's/jewelry round; first round numbers are in the Oct 21 chat and git history).
- CAVEAT (my earlier claim was too strong): eBay's estimatedSoldQuantity is only meaningful for multi-quantity listings. Single-quantity luxury listings show 0, so "48 of 70 shoe models sold zero" and all luxury 0s are NOT proof of no demand. Real sold data = Seller Hub Research (Terapeak), login-gated; Rafael would need to check or export it.
- Volume + markup is real only for scarce sealed collectibles: Pokemon ETB ~5,500 sold/30d across top-10 listings (median $140), booster boxes ~4,000, bundles ~2,000; older-set ETBs trade +100% to +500% over MSRP (tcgdropradar, lowest asks Oct 8, not sold prices). Current-set ETBs only +17-36%; booster boxes are BELOW MSRP (-7% to -30%).
- Not source-on-demand: Target's online ETB listings are third-party marketplace prices ($99-190); MSRP stock appears only in short restock drops. Pokemon Center/Target/Walmart limit quantities and cancel resale-looking orders -> cancellation risk = Rafael's worst case. Only workable as a manual stock-first side line.
- Everything else: eBay median is at or below retail (fragrance Chanel Bleu ~$112, AirPods Pro 2 ~$170, Dyson Airwrap ~$402 - retail figures from memory, unchecked). Women's luxury (Alaia/Prada/Miu Miu flats) at boutique prices loses money vs eBay medians, same pattern as men's.
- Ideas ranked: (1) Black Friday/Cyber Monday designer sales (Nov 27) with promo codes, needs Farfetch/SSENSE access; (2) verify real shoe demand with Terapeak before concluding; (3) optional manual Pokemon stock-first test with a small budget.

## Oct 22 early: real eBay SOLD data (Seller Hub Research, Rafael signed in the built-in browser) + Farfetch
- Seller Hub Research works in the Mac built-in browser: URL pattern `https://www.ebay.com/sh/research?marketplace=EBAY-US&keywords=<q>&dayRange=90&conditionId=1000&minPrice=<n>&limit=50&tabName=SOLD` (startDate/endDate ms params as in the page URL). JS can read the stats line and table rows. Do not use scripts to hammer it.
- Shoes DO sell (New, 90 days): Gucci Ace >=$450: 50+ sold, avg $578, 43 sellers. Gucci Horsebit loafer >=$300: 50+ sold, avg $539, 142 sellers. Ferragamo loafer >=$250: 50+ sold, avg $450, 108 sellers. Gucci MAC80 >=$300: 12 sold, avg $466. Margiela Sprinters >=$250: 2 sold, avg $400. Lanvin Curb: 12 sold, avg $334. Givenchy sneakers: 26 sold, avg $330. Unfiltered Gucci Ace: lots at $235-290 (low-priced listings, many already removed by eBay).
- Our asking prices are well above those sold averages (Ferragamo loafers ~$1,090, Gucci Horsebit ~$790, Margiela $799.99) -> no sales. At sold averages we LOSE money because costs are $650+ (Gucci), $500+ (Farfetch sale Givenchy/Lanvin/Margiela), Jomashop Ferragamo loafers $450-680.
- Farfetch men's sale now loads in the built-in browser (up to 70% off; search with discount shows Final price). Gucci/Ferragamo/Tod's/Bally not on sale there. Final Sale items are non-returnable (avoid as a source). Margiela Sprinters Farfetch $508 vs Antonioli $530.
- Conclusion: eBay sold prices for new luxury shoes sit near 40-60% of retail = what off-price/outlet buyers pay. Boutique/sale prices don't beat that. Real fix = off-price sources (Saks Off 5th liquidation, Nordstrom Rack, outlets) or accept small loss-leaders for feedback. Decision pending with Rafael.

## Oct 22 early: Yoox check (no-loss source hunt)
- Yoox US men's shoes are 30–70% off its "reference" price (Tod's loafers $398 vs $795, Santoni loafers $364, Bally loafers $282, Ferragamo loafers $566, Gucci not carried in that search). Read from the live page in the Mac browser; sizes are thin (2–4 sizes per item).
- eBay NEW Tod's Gommino loafers, last 90 days (Seller Hub, 22 sold): avg $186, range $76–$399. Yoox's $398 would lose about $200 per pair. The "discount" is against an inflated list price, so Yoox is NOT a source for Tod's.
- Not checked (assumed same pattern, unverified): Bally, Santoni, Doucal's, Thom Browne. eBay Browse API was rate-limited (429) until ~3am ET, so the explore run returned errors; requests/explore.json is cleared.
- Conclusion: no off-price store found that beats eBay sold prices. No listings changed.

## Oct 22: daily research (11:07Z run, Mac browser linked)
- Part A: refreshed all GOAT (60 pages), StockX (26), Farfetch (10 products), Italist, Nugnes1920, Antonioli and the Cettire cufflinks (all read live Oct 22 ~10:40-11:07Z). 513 of 540 rows rewritten with checked_at 11:07Z (46 legacy no-source rows left as is). 5 sizes went out of stock (e.g. D&G Saint Tropez EU 40, Givenchy FR 41); 63 prices changed, 16 by more than 10% (mostly StockX/GOAT asks moving). Sizes in the CSV only; no "sizes to add" proposed. Prices go stale at ~23:00Z Oct 23 if not refreshed.
- Part B skipped (no confirmed selling-limit room check; file says 177k remaining, stale Oct 20).
- Part C: Gmail (21 days, 12 stores) empty again; promos.yaml unchanged (header note added).
- Part D: scanned Nugnes1920 men's sneakers (58 in stock, 11 at >=35% off). Best: Givenchy black $426, Margiela Replica red $537, Moncler Trailgrip $330, Rick Owens Minimal $417. Requested eBay comps for 4 of them via requests/scan.json; the `market` workflow was still queued when this run ended (data/scan_results.json not updated). 0 candidates written. Earlier days' finding stands: boutique sale prices are mostly above eBay sold prices. Check data/scan_results.json next run before writing any candidate.
- Scheduled task this chat owns: "eBay daily research" (daily, ~6-7am ET): follows docs/research_routine.md Parts A-D, commits `research: YYYY-MM-DD`, pushes, updates this file.

## Oct 22 7:24am ET: daily check-in
- Research ran today (newest checked_at 11:07Z). daily-sync success 11:08Z; sale-alerts chain running (last completed success 10:56Z). market workflow was still in progress. No notices (data/notices.json empty). Selling limit room: 13,667 items / $177,134.
- Sales this month per eBay limits: 1 sold, $899.99 (no new sale detected since the last check).
- Scheduled: 12 more check-ins queued (this chat), 7:20am ET Sun–Fri Oct 23 to Nov 5 (Oct 23, 25-30, Nov 1-5). The Nov 5 one re-queues the next two weeks. Oct 28 check-in also reviews the $75 floor / ad rates / sale badges.
- Mac STATUS.md not updated (copy is stale; repo docs/STATUS.md is the source of truth).

## Oct 22 afternoon: 97-query eBay sweep (Rafael: "another item that sells very well with decent profit")
- Ran explore on 97 brands/products (shoes: Hoka, On, Salomon, NB, Asics, Adidas, UGG, Birkenstock; outerwear: Patagonia, Arc'teryx, North Face, Canada Goose, Carhartt; electronics: AirPods, Sony, Bose, DJI, GoPro, Dyson, Garmin; cologne; watches; kitchen; TCG; Lego; Funko; bags). Results in data/explore_results.json (live listing medians + sold counts; single-qty sold counts unreliable).
- Almost everything has an eBay median at or below retail (cologne Creed Aventus $300 vs ~$365 retail, Dyson, AirPods, Oakley, Ray-Ban, UGG, Hoka, Salomon, North Face, Lululemon, Le Creuset). No source-on-demand category shows a >$75 margin from this data alone.
- Only real markups: sealed TCG. Pokemon ETB median $130 (MSRP ~$55-60, but stock only at restocks), One Piece boxes median $197, MTG collector boxes median $445, Lorcana $202. All stock-first (buy before listing) and retailers cancel resale-looking orders. Retail/MSRP figures not verified this run (web search only returned snippets).
- Watches (Tissot PRX $421, Hamilton Khaki $715, Seiko 5 $319 medians) are the one source-on-demand candidate: Jomashop/Ashford price below MSRP. NOT verified; needs a Jomashop vs eBay-sold check per model (Seller Hub Research).
- Arc'teryx (median $320, ~83 sold/30d) worth a sale-price check at Arc'teryx outlet/REI/Backcountry. Unverified.

## Oct 22 afternoon: watch check (Jomashop vs eBay SOLD) + "no holding stock" (Rafael)
- Rafael: no holding stock -> trading-card test is OFF. Only buy-after-sale ideas qualify.
- Jomashop prices (search snippets, Oct 22): Tissot PRX quartz 40mm $324-333 (retail $450); PRX Powermatic 80 $612-620 (retail $850); Hamilton Khaki Field H69439931 $526.50; Seiko 5 SRPD51 $219; Casio GA-2100-1A1 $84.99 (out of stock).
- eBay NEW sold, 90 days (Seller Hub): Tissot PRX quartz T137.410.11.041.00 avg $206 (range $70-382; keyword may include other items); Seiko SRPD51 avg $198; Hamilton H69439931 avg $553 (9 sellers). Powermatic query returned nothing.
- Result: Jomashop >= eBay sold on all three, so watches lose money after fees. Dead end.
- Also: cologne (YSL Y EDP Jomashop $99.99 vs eBay ~$106) loses. Conclusion across 100+ products: no buy-after-sale category beats eBay sold prices at boutique/discount-site prices. Remaining plan: Oct 28 review, Black Friday re-scan.

## Oct 22 night: policy check + wholesale/dropship supplier research (Rafael: "no inventory test, there's gotta be something")
- eBay US dropshipping policy (ebay.com/help/selling/posting-items/setting-postage-options/drop-shipping?id=4176, read Oct 22): dropshipping from a WHOLESALE supplier is allowed; "listing an item on eBay and then purchasing the item from another retailer or marketplace that ships directly to your customer is not allowed". Our shoe model (list, then buy from Farfetch/GOAT/etc after a sale) is the second pattern. Authenticity Guarantee routing (ships to eBay's authenticator) may not change that. Account has had no flags so far; risk is policy/enforcement, not seen. Rafael informed.
- Only policy-compliant no-inventory route: a real wholesale/dropship supplier. Candidates: BrandsGateway (free account to browse, no card; dropship subscription from ~$209/mo Shopify, wholesale from EUR 1,000 min order; reviewers: mostly overstock, often 1-2 units/product, items sell out after payment, prices near retail, sometimes cheaper on eBay) and Luxury Distribution (from $125/mo; current-season Milan stock; its own comparison page, so biased; claims 10-60% est. margin). Neither verified against eBay sold prices. Stock-out after sale = cancellation risk (Rafael's worst problem).
- Next step if Rafael agrees: he creates a free BrandsGateway account (I cannot create accounts), I read its catalog prices in the Mac browser and compare to Seller Hub sold averages for the same styles. No subscription until a margin is proven.

## Oct 23: daily research (~10:45-11:20Z, Mac browser linked)
- Part A: refreshed 466 rows (checked_at Oct 23): all 60 GOAT pages (337 rows), 25 StockX pages (83 rows), Farfetch 10 products (size menus), Antonioli, Cettire cufflinks ($241.06, in stock). Changes: Italist Ferragamo loafer fully sold out (5 sizes now blank); Nugnes1920 Gucci Ace beige page is 404, so US 7/8 moved to GOAT ($763/$740); Lanvin Curb pink dropped (US 10/11 $754 -> $653); Margiela Sprinters US 7/8/9 dropped (569/508/508 -> 501/474/490); StockX Gucci Ace Web beige US 13 jumped $339 -> $1,052. One GOAT size (820207186346 US 13.5) not on GOAT now, row left unchanged (expires). StockX/GOAT rows were not re-ranked against other stores. Next refresh must land before ~23:00Z Oct 24.
- Part B skipped: selling_limits.json still stale (Oct 20, shows $177k room); snapshot refresh requested (requests/snapshot) but file had not updated when this run ended.
- Part C: Gmail (21 days, 12 stores) empty again. promos.yaml: added Cettire OCT5 (extra 5%, ends Oct 23 ~19:07Z, seen on banner).
- Part D: no new scan (reviewed Oct 22 scan_results: Givenchy slip-on median $447, Moncler 1 comp $499; Nugnes prices lose money after fees/duty). 0 candidates written.

## Oct 23 7:22am ET: daily check-in
- Research ran (newest checked_at 10:52Z today). daily-sync and snapshot succeeded 10:52Z; sale-alerts chain healthy (all recent runs success). notices.json empty. Selling-limit room: 13,666 items / $170,146.
- Sales: eBay limits still show 1 sold ($899.99); no new sale detected. No listing changes made by me.
- Rafael's open question: BrandsGateway free-account catalog check (needs him to create account). No reply yet.

## Oct 25 (UTC 01:06-01:40): daily research (scheduled run for Oct 24 10:40Z fired ~14h late)
- Prices were already >36h old at start (last refresh Oct 23 10:52Z), so every GOAT/StockX/Farfetch size had likely come off sale before this run.
- Mac linked, but the built-in browser pane's JS tool returns nothing and its StockX page has no viewport; I read GOAT through the Mac's Puppeteer browser instead (works, not signed in). StockX shows a Cloudflare check there (not bypassed); Farfetch/Cettire/Antonioli not readable this run.
- Part A: refreshed 339 GOAT rows (all 60 pages, buy_bar_data, new/good box only); 12 prices changed. NOT refreshed (expire): 83 StockX rows, Farfetch (32 rows), Antonioli (6), Cettire cufflinks (1). GOAT rows not re-ranked against other stores.
- Part B skipped (selling_limits.json stale). Part C: Gmail empty; removed expired Cettire OCT5. Part D: not run (no usable browser); no candidates written.
- Next: fix the built-in browser JS tool / sign-in so StockX and Farfetch can be read; next refresh needed before ~13:00Z Oct 26.

## Oct 25 (10:40-11:35Z): daily research, Mac browser linked (JS tool works again)
- Part A: refreshed 339 GOAT rows (all 60 pages, buy_bar_data), 83 StockX rows (25 pages, size-menu read; iframes do not work, one page per navigation), Farfetch Ferragamo Gancini (8 rows, all unchanged) and D&G Saint Tropez (EU 39 only left; US 8.5 row switched to GOAT $650). Farfetch Bally blue loafer is now Sold Out (2 rows blanked). Prices moved on ~25 rows (e.g. 355428079713 size 11 StockX $659 -> $1,013; 820205221528 sizes 5.5/6 up ~$70). Not re-ranked across stores (a cheaper other store is not checked).
- NOT refreshed (expire ~Oct 26 23:00Z): 8 other Farfetch products (22 rows; the size menu needs a real click, JS click does not open it: use Browser find + computer left_click on the "Select size" ref), Antonioli (6), Cettire cufflinks (1), END (26 rows have no URL). One GOAT size sold out: 820207186346 US 13.5 (left as is, expires).
- Part B skipped: selling_limits.json is stale (snapshot refresh requested via requests/snapshot at 11:30Z, not yet landed when this run ended). Part C: Gmail only a StockX marketing email, no code; Farfetch GET10 ends ~Oct 28. Part D: not run this time (time spent on StockX page-by-page reads); 0 candidates.
- Tip: Farfetch "Bally logo-plaque grey" page says "Non-returnable".

## Oct 25 7:21am ET: daily check-in
- Research ran (newest checked_at 11:25Z today). daily-sync success 10:49Z; sale-alerts healthy; no failures in the last 40 runs. notices.json empty. Selling-limit room: 13,776 items / $274,347.
- Sales: still 1 sold ($899.99) per eBay limits; no new sale. Watchers 260, 7-day views 471 (up from 428 on Oct 23). No listing changes by me.
- Open: BrandsGateway free-account catalog check waiting on Rafael. Oct 28 = one-week review of $75 floor / ads / badges.

## Oct 25 (evening): 9 stuck Gucci drafts released
- The 9 drafts that failed on Error 21919188 (old selling limit, now ~$274k) had their "invalid" state cleared; daily-sync rebuilt them and all 9 passed the rules (incl. match_market) -> status "approved"; sale-alerts lists them on its next pass (≤30 min).
- Still parked: 4 "uncompetitive" Gucci (horsebit drivers x2, horsebit loafer black, tennis 1977; market $395-612 below our floor math). 1 invalid: Gucci Cordovan Lux (missing Style item specific).
- Photos: eBay catalog gives 1 image per product; extra photos need GOAT/StockX shots of the exact style code (rule 8). Not yet automated.

## Oct 26: BrandsGateway test + scraper review
- Rafael created a free BrandsGateway (BG) account (type: wholesale). Prices visible immediately, no approval wall. BG blocks the Mac built-in browser at login (bot detection) -> we do NOT work around it; Rafael sends phone screenshots or a CSV from BG chat.
- Gucci Ace white (Bos Taurus) at BG: $514.88 (38% off MSRP $839.48), sizes US 5/6/6.5/9.5 only, 1-2 in stock each. Est. landed ~$590 (assumes $20 ship + 10% duty, unverified). eBay cheapest comp for that style ~$565 -> loses ~$90. Other BG items shown (Aries $615, flip-flops $537, beige GG $470) are all 38-40% off, i.e. same as Cettire sale pricing. Verdict: BG not cheaper unless discounts >=55%.
- Asked Rafael to: sort BG by discount (top 5 screenshots), ask BG chat for a CSV price list.
- Ultimate Web Scraper (ultimatewebscraper.com/mcp): paid cloud scraper for Shopify/Woo/Magento/SFCC catalogs; image download is extension-only; not covering Farfetch/SSENSE/GOAT/Cettire. Decision: skip for now; Firecrawl covers needs.
- Rafael: "keep working the same way and try to find new ways" -> continue autonomous research; next: photo upgrades (GOAT/StockX, exact style code), Cordovan Lux Style fix, Black Friday re-scan.

## Oct 26 (10:41-11:45Z): daily research (scheduled, Mac browser linked)
- Part A: refreshed 397 GOAT rows (68 pages, buy_bar_data), 70 StockX rows (29 pages; sizes 5.5-11 via iframe reader, larger sizes left unchanged), Farfetch Ferragamo Gancini moccasin (8 rows; size 7.5 sold out -> blanked) and D&G Saint Tropez (EU 39 only). 2 GOAT rows blanked (size no longer offered). Biggest moves: Gucci Basket black-red US 7.5 $546->$1,382, Re-Web white US 10 +18%.
- NOT refreshed (expire): 8 non-live Farfetch candidates (22 rows), Antonioli (6), END (26, no URL), Cettire cufflinks (1, last read Oct 23 -> already stale, so that listing is likely off sale). Farfetch size menu: JS click on [data-component=DropdownPlaceholder] opens it (works now).
- Part B: selling_limits.json shows $274k room but I did not write new candidates this run (time went to Part A). Part C: Gmail empty again, promos.yaml note updated.
- Part D (light): Nugnes1920 *-man collections via products.json, items >=38% off: Gucci GG Bicolor sneaker 857889 $526 (retail $850), Gucci black leather loafer 851396 $588 ($950), Ferragamo Nima 021285 $477 (GOAT is cheaper at $373). 54 hits scanned, 0 candidates written (no comp check / photos yet). Valentino, Saint Laurent hits ignored (excluded brands).

## Oct 26 check-in (7:25am ET)
- Research ran today (newest source_prices checked_at 2026-10-26 11:25Z). daily-sync + sale-alerts all green. 76 live, 4 uncompetitive, 1 invalid (Cordovan Lux Style). No new sales (total 1, $899.99). Room: 13,776 items / $274k. notices.json empty. No listing changes made.
- eBay "PHP2Shell" developer email: not applicable (bot is Python/GH Actions); no token rotation.

## Oct 26-27: use all the room
- New config `pricing.list_uncompetitive: true` (match_market stays ON so live-listing market drops continue): above-market new products list at planned prices (>= floor) instead of being parked. The 4 parked Gucci (Horsebit drivers x2, Horsebit loafer black, Tennis 1977) + Cordovan Lux (Style=Oxford, set via candidate `style:`) are now "approved"; sale-alerts lists them on its next pass. Test pinned (tests/test_ads_market.py).
- Research sweep (subagent, 12 brands at Italist, Nugnes1920 371 products, Mytheresa; 37 eBay comps): 0 new candidates clear $100 net. Need cost <= ~50% of eBay median. Italist "-50..-69%" reference prices are inflated. Not reached: Farfetch, END, SSENSE, Cettire, GOAT/StockX small goods.
- GOAT closed the ticket (canned reply). Rafael may open a NEW ticket asking for replacement pair/credit (draft given).
- BrandsGateway: Gucci Ace white $514.88 vs eBay ~$565 -> no. Awaiting CSV / discount screenshots.

## Oct 27 check-in (7:23am ET)
- 81 live (the 5 released drafts are live). Sales still 1 ($899.99). Room 13,776 items / $274k. notices.json empty. Bots green.
- WARNING: today's research has NOT run (newest source_prices checked_at = 2026-10-26 11:25Z). Rows expire 36h after that (~Oct 27 23:25Z UTC); without a fresh run the bot takes sizes off sale tonight.

## Oct 28 (00:20 ET) — research outage
- Root cause: "eBay daily research (recurring)" (trig_01KccF1saAhBjHmECjbhgdVJ) last run Oct 27 10:41Z FAILED: USAGE_LIMIT_REACHED. The backup "eBay Research" (trig_01QV4pywhVAgf7BvHcDb4Q8k, 11:09Z) ran 43s and wrote nothing. Newest source_prices checked_at = 2026-10-26T11:25Z (>36h).
- Effect: bot/sync.py decide() hides every live size with no row <36h old at the next daily-sync. Not yet seen to fire (last daily-sync 2026-10-27 16:49Z). Next scheduled research: 10:40Z (6:40 ET) Oct 28.
- I tried to fire the research task now; the permission classifier denied it. Left for Rafael to run it / approve. No config loosened (max_source_age_hours stays 36).
- 81 live, 1 sale total, watchers 262, views_7d 599. Room 13,776 items / $274k unused (limit is profitable candidates, not eBay room).

## Oct 28: daily research (scheduled, 10:41-11:20Z, Mac browser linked)
- Guard: newest checked_at was Oct 26 11:25Z (rows already >36h stale at start; outage Oct 27 = USAGE_LIMIT on the recurring task). Ran Part A in full.
- Part A: GOAT 398 rows (69 of 73 pages' needed sizes via buy_bar_data; ~4 sizes with no ask left unchanged), StockX 105 rows (28 pages, top-level reader one page per call; iframe reader is UNRELIABLE: showed all-BID on pages that have asks, do not use), Farfetch Ferragamo Gancini moccasin 355420832785 (6 rows refreshed, US 9.5 sold out -> blanked, new size 11.5 $950 seen but not on listing), Farfetch D&G Saint Tropez 355422763143 (US 6 $460, US 7 $460 now cheaper than GOAT, US 8.5 $452), Cettire cufflinks $241.06 in stock. Pushed in 3 commits (0ebd901, 394794d, 36d9bbb); the daily-sync for 36d9bbb was cancelled by a newer push, so check that a sync ran after it.
- Not refreshed: 8 non-live Farfetch candidates, Antonioli, END (expire; non-live). 4 StockX sizes with only BID left unchanged.
- Part B: selling limit room is $274k so it is NOT skipped by rule, but I did not write new candidates (time went to Part A after the outage recovery).
- Part C: Gmail (21 days, 12 stores) empty; promos.yaml note updated (Farfetch GET10 expires today).
- Part D (light): Nugnes1920 sneakers/loafers/shoes/belts/accessories-man collections, >=45% off and in stock: Alexander McQueen leather loafer 778158 $445 (retail $890), Givenchy BH009 nabuk sneakers black/beige $425 ($850), Doucal's loafer $237.50, Moncler/Y-3 (brands not approved: not scanned). Scanned ~4 collections x up to 4 pages; 4 sent to the eBay comp check (requests/scan.json); results pending when this was written, no candidates written yet.
- Browser tool notes: javascript_tool params are `action: javascript_exec` + `text` (REPL, no `return`); one StockX page per call (2 per batch times out at 50s).
- Follow-up 11:20Z: triggered daily-sync by workflow_dispatch so the Farfetch/Cettire rows (36d9bbb, its sync was cancelled) are applied. The McQueen/Givenchy comp scan (market workflow) was still queued/running; read data/scan_results.json keys mcq-loafer-778158, givenchy-bh009-*, doucals-du3260 next run.

## Oct 28 check-in + one-week review (7:25am ET)
- Research recovered: newest source_prices checked_at 2026-10-28T11:05Z (before the stale-hide). daily-sync/sale-alerts/market green. 81 live, 0 hidden-size notices. Room 13,776 items / $274k. notices.json empty.
- One-week review (Oct 21 -> Oct 28): sales 0 new (total 1, $899.99). Watchers 255 -> 263 (+3%). views_7d 442 -> 597 (+35%), partly the 9-14 newly listed items (87 -> 101 tracked). Ads: 10 listings raised (1@10%, 3@12%, 1@15%, 2@18%, 3@20%), eBay accepted all. Verdict: keep $75 floor, ad rates, 25% sale badges one more week (traffic up, no sales yet; too early/no evidence to roll back). Re-review Nov 4.

## Oct 28: second candidate sweep (Farfetch/Cettire/END/SSENSE/Nordstrom + StockX small goods)
- 0 candidates. Ferragamo Farfetch sale ($377-523) needs eBay ~$750-800; eBay medians $380-450. SSENSE sale: only near-miss Givenchy New City black $299 (eBay median $530, n=21, net ~$111 at the median, <$100 if undercut; duty/shipping from SSENSE unverified). END, Cettire, Nordstrom: nothing. StockX small goods: asks >= retail, no spread (Gucci belt ceiling ~$110 vs asks $162+).
- Not reached: Neiman (403), GOAT direct (403). Tip: eBay comp scans need real manufacturer style codes (SSENSE SKUs return n=0).

## Oct 28 evening: apparel research (docs/apparel_candidates.md) + CLAUDE.md scope updated
- ~1,100 men's apparel items screened (Italist, Nugnes1920, END, SSENSE, Mytheresa) vs eBay active asks (not sold data). 1 formal survivor (Rhude Split Petrol LS tee, END $214 M/L/XL, comps n=3 all $566.51 = likely one seller, weak). Better leads (comps n=1-2): Rick Owens x Moncler Jumbo tee (END $231, comps $632), Rick Owens x Moncler jogger ($342 vs $852), DRKSHDW Double Cargo jeans ($399 vs $1000+), AMI zipped jacket ($387 vs $1100).
- Re-check at 16:xx ET: END page for the Rick Owens x Moncler tee returns 404 (gone/sold out/URL changed) -> leads decay fast; NOT building apparel support in bot/listing.py (only sneaker/loafer/dress_shoe/belt/tie today) until a lead is confirmed live with per-size stock.
- If built later: CATEGORY_IDS tshirt 15687, pants 57989, jeans 11483, jacket 57988, sweater 11484, hoodie 155183; size name "Size"; clothing is NJ tax exempt; eBay Verify will reveal required specifics.

## Oct 28, 5:3x pm ET: Cettire + Farfetch re-check (Rafael: "check cettire and everywhere else")
- Cettire men's shoe sale read in the Mac browser (66 items, prices duties-included). Deepest: Salomon ACS Pro $141 (-56%), CDG Play x Converse $91, Veja $126-154, Axel Arigato Dice $210, Isabel Marant $286, Golden Goose Super-Star $413. None reaches 2x its eBay price, so none clears $100 net. 0 candidates.
- Farfetch men's sale (browser, signed in): deepest loaded -60% (Etudes Studio jacket $189, XS/S only). Typical -10% to -40%. 0 candidates.
- Listing room is not the limit (13.7k items / $274k free). Limit is cost vs eBay price.
- Still open: Givenchy New City black (SSENSE $299, eBay median $530) needs Rafael go-ahead after duty/shipping check; Black Friday (Nov 27) re-scan.

## Oct 29: daily research (scheduled, 10:41-11:50Z, Mac browser linked)
- Guard passed (newest checked_at was Oct 28 11:05Z). Part A: GOAT 397 rows (69 pages, buy_bar_data, all fetched), StockX 88 rows (29 pages, 4 parallel tabs works: seed+3 tabs, one page per browser_batch), Farfetch Ferragamo Gancini moccasin (US 5-9.5 refreshed; 10.5 blanked, not in menu) and D&G Saint Tropez (US 6/7/8.5 unchanged $460/$460/$452), Cettire cufflinks $241.06 in stock.
- NOT refreshed (17 StockX rows): big sizes (about 12+) that the StockX size list does not show; they keep the Oct 28 11:04Z timestamp and expire ~23:04Z Oct 29, so those sizes come off sale tonight until tomorrow's run. Also not refreshed: non-live Farfetch/Antonioli/END rows.
- Part B: skipped for time (room $274k is not the limit); 0 candidates written.
- Part C: Gmail (21 days, 12 stores) empty. Farfetch GET10 expired Oct 28: removed from promos.yaml. Farfetch banner is only a refer-a-friend 10%, not a code.
- Part D (light): Nugnes1920 sneakers/loafers/shoes/belts/accessories-man at >=45% off and in stock: same as Oct 28 (McQueen loafer 778158 $445, Givenchy BH009 black/beige $425, Doucal's loafer $237.50; Y-3 not approved). 4 items sent to the eBay comp scan (keys d-*), results not back yet when written; Nugnes ships from Italy (10% duty) so a median >= ~$750 is needed. 0 candidates.
- Browser notes: StockX list is truncated for large sizes; Farfetch size menu reads via the second "Select size" element click (listbox shows "<size> Wide $<price>", prices differ per size).

## Oct 29 7:30am ET check-in
- Research ran (newest source_prices checked_at 11:35Z). sale-alerts/daily-sync/market all green. 81 live, 0 drafts waiting. No sales (total still 1, $899.99). notices.json empty. Limits free: 13,776 items / $274,347.
- No listing changes made. Open: Givenchy New City go-ahead, BG CSV, Black Friday re-scan.

## Nov 1 7:21am ET check-in (also covers the missed Oct 30 notice)
- PROBLEM: research has not run since Oct 29 (newest source_prices checked_at 2026-10-29T11:35Z, ~49h old). daily-sync last ran Oct 30 17:07Z; nothing Oct 31/Nov 1. sale-alerts chain is healthy (runs every ~25 min).
- Effect: all live source rows are past max_source_age_hours (36h). Next daily-sync will set every live size to qty 0 (by design). Until then listings still show stock that was last verified Oct 29, so a sale now carries cancellation risk. Did NOT dispatch daily-sync or fire the research trigger (no listing changes in check-ins).
- No sales (total 1, $899.99). 81 live, notices empty, limits 13,776 items / $274,347. Interest ~266 watchers / ~698 views_7d (Oct 30).
- Needs Rafael: run/enable "eBay daily research" (trig_01KccF1saAhBjHmECjbhgdVJ) and check why daily-sync stopped.

## Nov 2: daily research (scheduled, ~05:40-06:15Z, Mac browser linked)
- Guard passed (newest checked_at was Oct 29 11:35Z; research had lapsed Oct 30-Nov 1). Part A: GOAT 423 rows (73 pages, buy_bar_data), StockX 96 rows (29 pages, one page per call), Cettire cufflinks $241.06 in stock. All stamped ~06:0xZ Nov 2.
- NOT refreshed: Farfetch Ferragamo Gancini moccasin (10 rows) and D&G Saint Tropez (3 rows): the size menu would not open in the browser this time (page header now shows $725 vs stored $1,032, unverified). 4 StockX rows (big/BID sizes) and 6 GOAT rows with no GOAT size stay stale; they go off sale after 36h (safe). Draft-only Farfetch/Antonioli rows not re-read.
- Part B skipped (no confirmed room check). Part C: Gmail 21 days empty; promos.yaml unchanged. Part D skipped this run (time spent on the 3-day gap).
- Note: the local clone was detached/stale at start; fast-forwarded to origin/main.

## Nov 2 ~11:45Z (6:45am ET): second research pass (scheduled)
- Guard did not match (newest checked_at 06:05Z = 1:05am ET, before 6am ET), so I ran, but Part A prices are only ~5.5h old (GOAT/StockX/Cettire from the 06:05Z run), so I did not re-read them.
- Retried Farfetch (Ferragamo Gancini moccasin, 10 rows; D&G Saint Tropez, 3 rows): the page now shows Farfetch's bot-protection screen, no size menu, nothing read. Left unchanged (not trying to bypass). Those 13 rows are from Oct 22-29, already past 36h, so those sizes stay off sale until Farfetch loads again or another store has them.
- Part B skipped (no change). Part C: Gmail 21 days empty; promos.yaml comment only. Part D skipped (time; same yield as Oct 29).

## Nov 2 7:35am ET check-in
- Recovered: research ran Nov 2 06:05Z and a second pass 11:41Z; daily-sync succeeded 06:05Z; sale-alerts green. Newest source_prices checked_at 06:05Z (1:05am ET, so not "after 6am"; second pass deliberately skipped re-reading 5h-old prices).
- During the gap daily-sync (Nov 1 12:40Z) zeroed stale sizes: stats showed only 6 live sizes on Nov 1 (was 346 on Oct 30). Nov 2 live-size count not yet in stats.json; should be back up after the 06:05Z sync (unverified).
- Farfetch rows (Gancini 10, D&G Saint Tropez 3) unrefreshed (Farfetch bot screen); those sizes stay off sale.
- No sales (total 1, $899.99); 81 listings, 0 drafts waiting, notices empty, limits 13,776 / $274,347. Watchers ~271, views_7d ~688 (Nov 1). No listing changes made by this check-in.

## Nov 3: daily research (scheduled, ~11:40-12:25Z, Mac browser linked)
- Guard passed (newest checked_at was Nov 2 06:05Z). Part A: GOAT 418 rows refreshed from buy_bar_data (73 pages; 7 sizes no longer offered were blanked; 2 rows with >35% jumps left stale: 355423513413 US 5.5, 820207186196 US 12). StockX 49 rows refreshed (28 of 29 pages read, 4 parallel tabs; LV skate skipped). StockX rows are updated from their own source only (no GOAT-vs-StockX cheapest merge). Sizes missing from StockX's truncated list stay stale.
- NOT refreshed: Farfetch (Gancini 10 rows, D&G Saint Tropez 3) - bot screen last time, not retried; ~43 rows older than 36h remain and go off sale.
- Part B skipped (room $274k is not the limit; 0 candidates). Part C: Gmail 21 days empty, promos.yaml unchanged. Part D skipped (time spent on StockX).

## Nov 3 7:21am ET check-in
- Healthy. Research ran today (newest checked_at 11:50Z = 6:50am ET; GOAT 418 rows, StockX refreshed). daily-sync x2 and sale-alerts green. Live sizes back to 378 (was 6 on Nov 1).
- No sales (total 1, $899.99). 81 listings, 0 drafts waiting, notices empty, limits 13,776 / $274,347. Watchers 272, views_7d 590 (down from 688 after the Nov 1 gap).
- Open: Givenchy New City go-ahead, BG CSV, Nov 4 re-review of $75 floor/ad rates/sale badges, Black Friday (Nov 27) re-scan. No listing changes made.

## Nov 3 evening: floor lowered to $50 (Rafael: "make more listings, even if we just make $50")
- `config.yaml` profit.floor 100 -> 50 (commit 95b01e3). Effects: new listings and live sizes now need >= $50 net; decay/market-drop floors (1.5x) become $75; brand_min_net (LV $200) and item_min_net.json overrides unchanged; ads/markdown/market floors were already $75. Tests pinned to the old $100 via tests/_cfg.py (53 pass).
- Checked the known near-misses live: Givenchy New City black (SSENSE $299, style 261278M237014): only IT 40.5 left, "Only 1 remaining" -> NOT listed (one unit = cancellation risk). MM6 SH3WS0012P6435T1003 (Biffi $191.88): page flags Sold Out/Pre-order, per-size stock unreadable -> NOT listed.
- Result: the lower floor mostly widens margins for products we already track; no new candidate files written.
- Revert: set profit.floor back to 100.

## Nov 3 night: apparel built, 4 leads tried (Rafael: "go, find anything to start making sales")
- Code: apparel categories (tshirt, pants, jeans, jacket, sweater, hoodie) in `bot/listing.py`, size variation, specifics, `END US apparel: 40` shipping (ships to Rafael, then reship), sale alerts parse "Size". 54 tests pass.
- END product URLs must end in `.html`. Research task must re-read END apparel rows daily or sizes auto-hide after 36h.
- eBay API returned 0 comps for all four (the Oct 28 asks of $566-$1,356 were single-seller active listings, now not found). Prices below are priced under those old asks, not on proven sales.
- END live prices rose since Oct 28: tee $303, jogger $447, cargo $522, Rhude $279. Landed = price x 1.10 + $40.
- Approved (auto, will list on next sale-alerts run): Rick Owens x Moncler Jumbo Tee Dark Dust S/M/L at $549 (net ~$96); Rhude Split Petrol Long Sleeve M/L/XL at $499 (net ~$79). Stock is "one left" / "few left" per size: cancellation risk is real.
- Blocked: Moncler jogger ($749) and DRKSHDW cargo jeans ($879): eBay requires Inseam and Style; END does not state inseam, so not filled (rule: only verifiable specifics). Candidates stay in data/candidates; add `extra_specifics: {Inseam: ..., Style: ...}` once a measurement is verified.
- Photos are END product photos (exact style code), not eBay catalog.

## Nov 4 check-in (7:20am ET)
- Research did NOT run today: newest source_prices checked_at is Nov 3 22:33Z. Rows (incl. END apparel) auto-hide sizes after 36h (~Nov 5 10:30 ET) unless it runs.
- Bot: sale-alerts chain healthy (success 11:35Z, next run in progress). daily-sync last ran Nov 3 22:35Z (succeeded; a duplicate dispatch was cancelled).
- Live now: Rick Owens x Moncler tee (820312366372, $549) and Rhude long sleeve (820312366345, $499). No sales since the Oct total ($899.99, 1 sale). Selling room 13,776 items / $274,347.
- Needs Rafael: inseam for the Moncler jogger and DRKSHDW cargo jeans (eBay rejects drafts without it; notices.json).
- Apparel comps (Nov 4): Rick Owens Zip Hoodie n=1 at $698 vs END $796 -> fails; Zip Knitted Hoodie and Tommy Tee n=0 (no price evidence). Not listed.
- No listing changes made by this check-in.

## Nov 4: daily research (scheduled run fired 17:06Z, ~5h late; Mac link dropped mid-run)
- Done: GOAT refreshed for all 73 pages (419 rows read, 1 now sold out; buy_bar_data method), pushed 19288c9 ("checked_at" 17:30Z). StockX: 25 of 29 pages (72 rows refreshed, 2 blanked as BID-only), checked_at 17:40Z.
- NOT done: StockX gucci-screener-black-canvas, gucci-screener-gg-supreme-dark-blue-red, gucci-tennis-1977-canvas-high-top-beige-gg-print, gucci-tennis-1977-gg-canvas, louis-vuitton-lv-skate; Farfetch/END/Antonioli/Cettire rows (Nov 2-3 reads, expire ~Nov 5 evening); Part B (selling-limit room is $274k, so it was due), Part C (Gmail promos), Part D scan.
- Cause: Rafael's Mac dropped off the bridge ("device not connected") at ~17:45Z; retried twice. Rows from the unread stores expire 36h after their last read.
- Next: rerun when the Mac is back; the Nov 5 scheduled run should cover the skipped parts.

## Nov 4 night: Italist sneaker screen (Rafael: "there's got to be things online")
- Italist men's sneakers sorted by discount (read live, 40 items): almost all 15-40% off retail; only Michael Kors -78% (not luxury-resale), Comme des Garcons/Reebok x Palm Angels -37-40% at $123-131 (low price, nets under floor after $20 ship + 10% duty). Gucci -21 to -30% ($803-$946), Golden Goose -13 to -19%: above or at current eBay prices for the same models. Saint Laurent is on the exclude list.
- Conclusion: eBay already prices luxury shoes ~25-35% under retail, so only 50%+ off works; no source seen has that outside BrandsGateway and Black Friday (Nov 27).

## Nov 5 — first sale bought (order 23-15364-04589)
- Bought at Jomashop, order **M40FV9XM**, Nov 5 ~4am ET: Ferragamo Logo-Patch Panelled Sneakers (021271 766299), size 11, $163.95 (DM40 = 40% off, free Standard shipping, no tax, card ending 0814). Shipped DIRECT to buyer Cruz Russell, 135 Jewett Ave, Jersey City NJ 07304 (Rafael's choice). Confirmation email went to relyassian@gmail.com.
- eBay: sold $339.99, earnings $300.59 (fees $27.20 + ad $12.20) -> net about $136.64. Ship by Nov 9 11:59pm PST; buyer window Nov 9-16. Funds on hold until Nov 19.
- Open: add tracking to eBay when Jomashop sends it. Standard shipping may be slow (processing 1-3 days + 3-7 days): watch the Nov 9 ship-by.
- Unverified: Jomashop "Size 11" is assumed US (GOAT says US 11). Billing address was left as the buyer's address (payment still went through).
- Jomashop priced invoice/gift receipt: no confirmed way to hide price; "Send gift receipt" checkbox exists at checkout, effect unknown.
- Jomashop returns: 30 days, new items, original packaging, customer pays return shipping; refund method unknown (one review says gift cards).
- Todo: record Jomashop as a source row in data/source_prices.csv; build returns-by-source (needs Rafael OK on CLAUDE.md rule 7); reconcile bookkeeping for this order.

## Nov 5: daily research (scheduled, ~11:42-12:00Z, Mac browser linked)
- Guard passed (newest checked_at was Nov 4 17:40Z). Committed a7cca29 "research: 2026-11-05"; daily-sync run #172 started 11:51Z.
- Part A done: GOAT 421 rows from buy_bar_data (73/73 pages, no errors; 27 prices changed; none blanked, none >35% jump). StockX 28 of 29 pages read, 4 tabs in parallel: 81 rows refreshed (3 blanked BID-only); 17 sizes missing from StockX's truncated size list and 2 rows with >35% jumps (820205389034 US 10 $1,399 -> $901; 820277098563 US 13 $660 -> $1,011) left stale. END apparel (Rick Owens x Moncler tee S/M/L $303, Rhude LS M/L/XL $279) re-read via page JSON-LD: same prices, all those sizes InStock, checked_at refreshed.
- NOT refreshed: Farfetch (blank page in browser, bot block; Gancini, D&G Saint Tropez, Givenchy etc. rows already older than 36h), Cettire cufflinks (HTTP 403, not bypassed), Antonioli. Those sizes stay off sale.
- Part B: not run (room $274k means it was due; time went to Part A and blocked stores). Part C: Gmail 21 days empty (13 stores), promos.yaml comment updated.
- Part D (Nugnes1920 *-man collections, >=45% off, in stock): 18 hits, ~13 unique. Excluded brands dropped (Valentino Vlogo loafer, Saint Laurent). Best leads: Givenchy Nabuk sneaker beige BH009KH1PP-100 $425 (retail $850, EU 41/43/44), Moncler Trailgrip white L109A4M00280 $330 (retail $600, EU 43.5/44/45 only), McQueen loafer black 778158WIES4-1081 $445 (EU 40 only = single size), Moncler Monaco2 $245 (1 size), Y-3 Gazelle/Stan Smith $154 (1 size), Doucal's loafer $237 (1 size). Comps requested via requests/scan.json (commit 29f1bea); `market` run #31 was still queued at 12:00Z, so results land in data/scan_results.json later. No candidates written (no comps yet; Nugnes ships from Italy, add 10% duty + $20). Next run: read scan_results keys givenchy_nabuk_beige / moncler_trailgrip_white / mcqueen_loafer_black and write candidates if net >= floor ($50, 3 sizes rule).
- Scheduled task this chat owns: eBay daily research (this run). Open: Cettire/Farfetch need a manual unblock to refresh.

## Nov 5 7:20am ET check-in
- Research ran (newest checked_at 11:50Z = 6:50am ET). sale-alerts, daily-sync, market scan all green; one sale-alerts run in progress.
- Sales: 1 (order 23-15364-04589), bought at Jomashop M40FV9XM; waiting on tracking (ship by Nov 9). notices.json empty. Selling room: 13,776 items / $274,347.
- Rescheduling the check-in as ~12 one-time send_later tasks was NOT done (Rafael wants one recurring task, not a pile of one-offs). Needs one recurring trigger instead.

## Nov 5 afternoon
- Tracking added to eBay order 23-15364-04589: UniUni UUS6B52571541176201 (Jomashop M40FV9XM), via add-tracking workflow run 42110468394 (live). UniUni shows label created only; Jomashop est. delivery Nov 13. eBay: "ensure carrier has package by Nov 9". Gift receipt box was ticked on Jomashop (email shows "GIFT RECEIPT").
- Green Gucci Ace (order 11-15213-78941, $899.99): buyer opened item-not-received; eBay stepped in, update within 48h, funds on hold. Rafael should NOT refund himself. Tracking 878356372280 (12 digits, possibly FedEx) shows nothing at USPS: find the carrier and claim.
- Rafael asked (Nov 5): check every reliable source, list nonstop. Request saved in data/rafael_requests.txt for the next research run.
- Nov 5 scan (2 agents): no confirmed lead. Comps requested (requests/scan.json): Jomashop Burberry 8052333, Ferragamo Gancini loafers 023610 772477/773004, Montreal 020740 752443; SSENSE Jil Sander Moon 261249M237005/-000 ($362/$348, IT 42-44, FINAL SALE, 1 pair per size), Marni Fussbett 261379M234003, Givenchy New City 261278M237014, RO Stefan jeans, Cargobelas. Mytheresa/END/Mr Porter sales too shallow (20-40%). Cettire/LuisaViaRoma/Farfetch US/NAP/Revolve/BrandsGateway NOT checked (Firecrawl credits out until ~04:35Z Nov 6).
- Nov 5 16:30 Rafael: buyer-pays returns are GOOD; offer them only where the source gives cash refunds and a longer window (not built yet; listings inherit the return policy from the template item via business policies, so it needs a second returns policy + per-listing choice; rule 7 in CLAUDE.md to be updated when built). Also: "just start listing, we need more listings".
- All 83 candidates are live; nothing parked (list_uncompetitive: true). Two blocked on Inseam (RO jogger, RO cargo jeans).
- Jomashop Burberry 8052333: $91.95 is US 16/17 only; US 9 = $284.95 (net about $32 at the $380 ask) -> dropped. Jomashop product pages stopped rendering in the pane for the Gancini loafers, so per-size prices unread.

## Nov 6: daily research (scheduled, fired 16:50Z, Mac browser linked)
- Guard passed (newest checked_at was Nov 5 11:50Z). Part A: GOAT 429 rows (73 pages, buy_bar_data, 25 prices changed; 2 jumps >35%: 355426469262 US 13.5 $359->$533, 355428047951 US 11 $811->$1,095, applied as read), StockX 100 rows (all 29 pages, 40 prices changed, 1 now BID-only), END US apparel (Rick Owens x Moncler tee S/M/L $303, XL sold out; Rhude long sleeve M/L/XL $279, S and XXL out), Farfetch Ferragamo Gancini moccasin (11 sizes, per-size $726-$1,032; US 9.5 and 10.5 not in menu -> blanked) and D&G Saint Tropez (US 6 $461, US 8.5 $452; US 7 gone at Farfetch, switched to GOAT $578). Commits pushed.
- NOT refreshed: Cettire cufflinks (356084785661, page returns HTTP 403, not bypassed; goes off sale after 36h), Farfetch/Antonioli draft-only rows (Bally, Brunello, Givenchy, Lanvin, Margiela, Antonioli).
- Part B skipped (selling room $274k, but no vetted candidates; time went to Part A). Part C: Gmail 21 days empty; promos.yaml unchanged. Part D (partial): Nugnes1920 men's shoes >=50% off: Givenchy nabuk sneakers $438 (retail $895, sizes 41/43/44, one in 44), Alexander McQueen leather loafer $458 (retail $935, EU 40 only). Valentino excluded. Landed ~$502 each needs eBay >= ~$780 to net $100: not written (no comps checked).

## Nov 8: daily research (scheduled, ~11:40-12:30Z, Mac browser linked)
- Guard passed (newest checked_at was Nov 7 11:59Z). Part A: GOAT 73/73 pages via buy_bar_data (no errors); StockX 29/29 pages; 524 GOAT/StockX rows rewritten, 67 prices changed, 4 sizes now sold out; 6 jumps >35% applied as read (355423513413 US 5.5 $2,438->$1,087 and 6.5 $844->$514, 355428047951 US 10 $1,132->$712, 355429355271 US 8 $2,435->$1,061, 820205221528 US 6 $349->$524, 820277097224 US 7.5 $1,969->$956; the big drops are stale GOAT outlier asks now beaten by StockX). Farfetch Ferragamo Gancini moccasin (US 5-9 Wide, $726-$1,032, unchanged; US 9.5/10.5 still not in menu) and D&G Saint Tropez (EU 39 $461, 41.5 $452, last 1 left each) re-read, unchanged. END apparel re-read from page data: Rick Owens x Moncler tee $303 S/M/L in stock (XL out), Rhude LS $279 M/L/XL in stock (S, XXL out).
- NOT refreshed: Cettire cufflinks 356084785661 (Cettire 403 earlier, not retried; row from Nov 2 is stale and the size-less item goes off sale), Farfetch/Antonioli draft-only rows.
- Part B skipped (selling room $274k is fine, but no vetted candidates). Part C: Gmail 21 days empty, promos.yaml comment added.
- Part D: Nugnes1920 men's shoes (113 items, 14 at >=40% off with stock). Comps from the Nov 7 scan: Gucci lace-up black 865172 (only size 6, median $777 vs landed $768), Gucci loafer black 851396 (only size 6, median $539), Givenchy leather sneaker (median $399 vs landed ~$489) all lose money; Fendi/Rick Owns/Margiela/D&G had 0 eBay comps. Zero-comp leads that clear the $50 floor on >=3 sizes at ~3% under retail but are unproven demand and need EU->US size mapping checked: D&G suede pantofola loafer brown A50739 AS70780024 ($464, retail $790, EU 39/40/42/43/45), D&G Ariosto suede black A50734 AT44180999 ($491, retail $835, EU 39/40/42), Margiela Replica red S57WS0517 P7644 T4417 ($537, retail $895, EU 40/41/42). No candidates written. Scanned 14, written 0, best est. net ~$130 at retail-3%.
- Scheduled task this chat owns: eBay daily research (this run). Mac copy of STATUS.md not updated (no folder connected this run).

## Research log
- 2026-11-08 (in-chat scheduled run): refreshed 524 GOAT/StockX rows + Farfetch/END; Gmail empty; Part B skipped; Part D 14 screened, 0 written.
- 2026-11-07 (12:00Z, in-chat run): refreshed 519 GOAT/StockX sizes (5 went out of stock) plus Farfetch Ferragamo/D&G and END apparel (unchanged); Gmail promo scan empty. Part B skipped (limit room $274k is fine but no new candidates written; Part D looked first). Part D: Nugnes1920 men's shoes screened (~20 items at 40-51% off; Valentino excluded); 8 queued in requests/scan.json for the eBay comp check (Gucci lace-up/loafer, Fendi x2, Givenchy leather, D&G Ariosto, Margiela Replica, Rick Owens). Results land in data/scan_results.json; no candidates written yet. Yesterday's scan: Givenchy nabuk/Moncler/McQueen had 0-1 comps.
