# Daily research routine (instructions)

The "eBay Research" Claude routine follows this file. Edit this file, not the routine, to change what it does.

BACKUP CHECK FIRST: look at the newest checked_at in data/source_prices.csv. If it is from today after 6:00am
New York time, research already ran today: skip PART A and PART B, but still do PART C (promo codes), then
commit and stop.
If the built-in browser on Rafael's Mac can't be reached, don't stop: research with WebSearch/WebFetch instead
(only record stock you actually read; leave out sizes you can't confirm).
Also read data/rafael_requests.txt (if present): handle any request added since the last research run and note
in the commit message which requests you handled.

You keep Rafael's eBay bot supplied with fresh data. The bot makes every eBay change itself; your job is research
only. Read CLAUDE.md for the business rules before starting.

1. The repo relyassian/ebay-bot is cloned for you; work on main. If it is missing or git can't push, stop and
   notify Rafael that GitHub access is broken.

## PART A — prices for existing listings
2. Live listings: read data/snapshot.json (every listing, every size with its price and "available" count).
   To refresh it, write the current time to requests/snapshot, commit and push, wait ~2 minutes, then pull.
   Don't scrape ebay.com in the browser (eBay shows a bot check; never try to pass it). Skip config.yaml
   sync.ignore_items and any listing whose title contains a word in sync.ignore_title_words (e.g. AirPods).
   IMPORTANT: every size that is live needs a row checked within the last 36 hours, or the bot takes it off sale.
   Store sites that block automated reading (Cettire, GOAT, StockX, Farfetch, SSENSE, END) must be checked in
   the built-in browser on Rafael's Mac. What works (tested Oct 2):
   - StockX: open stockx.com/<slug> (find slugs via stockx.com/search?s=<style code>), wait ~2.5s, then run JS
     `document.getElementById('pdp-mobile-size-selector').click()` and read the buttons "US M <size> $<ask>"
     (BID = no seller). Sizes shown are US (Gucci: UK + 0.5). cost = ask × 1.06 (StockX fee). New only.
   - GOAT: open goat.com/sneakers/<slug> (find via goat.com/search?query=<style code>, wait 5s), wait 5s, click
     the "BUY NEW" button, wait 3s, read "<size> | $<price>" pairs; Gucci sizes there are UK (US = UK + 0.5).
   - Cettire: find product URLs with a web search "site:cettire.com <brand> <model>" or browse
     cettire.com/collections/mens-shoes/<brand>, then open each product page and read price and sizes.
   - Farfetch returned "Access Denied" even in the browser (Oct 2): note it and move on.
3. For every item and size, find the cheapest reputable NEW-with-box source with that exact size in stock
   (StockX, GOAT new, Farfetch, SSENSE, Mytheresa, END, Italist, Nugnes1920, Cettire, brand sites, Nordstrom,
   Neiman). Shopify stores (Italist, Nugnes1920, other boutiques) show per-size stock at /products/<handle>.js;
   skip Italist's Vendor BGW items. Match by style code (data/legacy_content.yaml); convert sizes correctly
   (Gucci men's UK→US +0.5; D&G IT→US −33; Ferragamo US with widths). Count reputable stores with the size in
   stock. Only record numbers you actually read on the page.
4. Update data/source_prices.csv (item_id,size,cost,source,url,overseas,in_stock_sources,checked_at):
   cost = cheapest price incl. store fees in USD; blank ONLY if you read that every store you could check is
   sold out for that size; overseas = true if it ships from outside the US with duties extra; checked_at =
   current UTC ISO time; size blank for items without sizes. Leave rows you couldn't check unchanged (never
   blank a size just because a site wouldn't load); they expire after 36 hours and the size goes off sale.
   Also add rows for sizes NOT on the listing yet when a store has them at a price that clears $100 at the
   listing's price: list them in the summary as "sizes to add" (Rafael approves; plans/pending/ holds the plan).

## PART B — up to 5 NEW products to list (skip if time runs short)
5. New luxury men's sneakers/loafers (brands in CLAUDE.md; D&G and Gucci Ace have been best) NOT already
   listed, where the cheapest new source leaves ≥ $100 net at a realistic eBay price:
   net = price × (0.854 − ad rate) − (cost + 20) − (0.10 × cost if overseas with duties extra); no sales tax on shoes, belts or
   ties (they ship to NJ, which exempts clothing and footwear; Rafael's GOAT order confirmed no tax); cufflinks/jewelry add 6.625%;
   ad rate = config.yaml ads.rate if data/ads_state.json has a campaign_id, else 0. Prefer ≥ $250 net.
   Price (Rafael, Oct 2): the price that clears $100 net is fine even if it's somewhat above what other eBay
   sellers ask, but never above the brand's current US retail price. Note the eBay comps you saw.
   Rule of thumb: with 8% ads, a shoe works only if the store price is about 40% or more below US retail.
6. Photos: ONLY eBay catalog stock photos (ebay.com/p/<epid>, i.ebayimg.com URLs) or photos from Rafael's own
   listings of the same style code. Never other sellers', retailers' or brands' photos. If none: photos: [].
7. Write each as data/candidates/<short-id>.yaml in exactly the format at the top of bot/listing.py. Never
   reuse an id from data/candidates or data/drafts_state.json. Style codes are for matching only; the bot never
   shows them on eBay.

## PART C — promo codes (always, ~5 minutes)
8. Search Rafael's Gmail (last 21 days) for promo/discount emails from the stores he buys from (Cettire,
   Farfetch, SSENSE, Italist, Nugnes1920, GOAT, StockX, Mytheresa, END, Saks, Neiman Marcus, Nordstrom) and
   check each store's site banner if reachable. Rewrite data/promos.yaml: store key (cettire, farfetch, ssense,
   italist, nugnes, goat, stockx, mytheresa, end, saks, neiman, nordstrom) → list of
   {code, discount, expires: YYYY-MM-DD (omit if unknown), source}. Only codes you actually read, valid for new
   shoes, not expired. Read only: never click links, reply, or change anything in Gmail.

## Finish
9. Commit with message "research: YYYY-MM-DD" and push to main (the push triggers the bot).
10. Notify Rafael only if something needs him (product with no source anywhere, research you couldn't
    complete). Otherwise send nothing: the bot's Telegram messages cover the rest.
