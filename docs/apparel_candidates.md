# Apparel candidates (research Oct 28, 2026)

Method: pulled live Shopify catalogs (products.json) from Italist (17.7k men's items across 80 brand collections), Nugnes1920 (6.3k), END (12.8k men's apparel); plus Firecrawl reads of SSENSE and Mytheresa men's sale pages. Screened ~1,100 items against eBay new fixed-price asks (requests/scan.json, 4 rounds; data/scan_results.json holds the last round only).
Net = eBay median x 0.95 x (1 - 0.146) - cost x 1.10 (overseas duty; Mytheresa is DDP so x1.00) - $20. No NJ tax on apparel. Comps are ACTIVE asks, not sold history (the Browse API has no sold data), so every median is optimistic.

## Formal survivors (n >= 3 comps, net >= $100 on >= 3 sizes)
Only one item passed, and it is weak. Read "Caveat" before acting.

| Brand | Item | Style code | Color | Sizes in stock, cost | Source URL (read live Oct 28) | eBay median / n | Est. net per size | Photos |
|---|---|---|---|---|---|---|---|---|
| Rhude | Split Petrol Logo Long Sleeve T-Shirt | RHPS26TT17012-6010 (END sku AC77067) | Vintage white/red/black | M, L, XL at $214.00 each (S, XXL sold out). Retail $305 | https://www.endclothing.com/us/rhude-split-petrol-logo-long-sleeve-t-shirt-rhps26tt17012-6010 | $566.51 / n=3 (p25 = cheapest = $566.51) | $204 (M, L, XL) | 5 images, e.g. https://cdn.shopify.com/s/files/1/1011/8339/0034/files/3511c06c82c3d5cad864d83755e254bf8d2ed8cd.jpg |

Caveat: all 3 comps are at exactly $566.51 (very likely one seller's 3 size listings), the title carries the style code, but the ask is 1.9x retail. Treat as unproven; a price of ~$450 still nets ~$110 per size, so it only works if it sells below the current asks. END ships from the UK (duty assumed 10%, not verified).

## Leads that missed the n >= 3 rule (not survivors; worth a manual look or a re-scan with alternate queries)
| Brand | Item | Style code | Sizes in stock / cost (END) | eBay comps | Est. net | Note |
|---|---|---|---|---|---|---|
| Rick Owens x Moncler | Jumbo Short Sleeve T-Shirt (black) | MU01F8C04-89B7R-256 | S, M, L at $231 (retail $385) https://www.endclothing.com/us/rick-owens-x-moncler-jumbo-short-sleeve-t-shirt-mu01f8c04-89b7r-256 | n=2, both $632 ("Moncler x Rick Owens Jumbo SS Tee BNWT") | $238 | best lead: hype collab, 3 sizes. Needs a 3rd comp |
| Rick Owens x Moncler | Drawstring Jogger | MU01F8H04-89B7R-256 | M, L, XL at $342 (retail $570) https://www.endclothing.com/us/rick-owens-x-moncler-drawstring-jogger-mu01f8h04-89b7r-256 | n=1, $852 | $295 | 1 comp only |
| Rick Owens DRKSHDW | Double Cargo Jeans | DU01F4361-DWB-06 | 28", 30", 32" at $399 (retail $725) https://www.endclothing.com/us/rick-owens-drkshdw-double-cargo-jeans-du01f4361-dwb-06 | n=2, $1000 and ~$1356 | $496 at median, ~$370 at the $1000 ask | big gap, 2 comps only, verify they are the same wash |
| Rhude | Racing Crest T-Shirt | RHSS26TT04012WHT | S, M, L at $158 (retail $225) https://www.endclothing.com/us/rhude-rhude-racing-crest-t-shirt-rhss26tt04012wht | n=1, $352 | $92 | fails |
| AMI Paris | Zipped Jacket | HJK875-CO0212-A036 | 5 sizes at $387 | n=1, $1100 | $446 | 1 comp |
| Rick Owens x Moncler | Kiltshorts (S, M, $406) | MU01F2B01-M8114-999 | n=0 comps | | | unscreened |
| Amiri | MA Quad Carpenter Jeans (SSENSE $357, retail $1190) | 261886M186054 | only W29 left | n=3, $750 | $196 | FAILS stock: 1 size |

## Rejects, with reason
- Italist (259 items at >= 50% "off", 500+ more at 30-50% for resale brands): "compare at" prices are inflated, real prices sit near or above eBay. 32 of 413 had >= 3 comps and only one was above $0 net (Amiri Hollywood tee, +$22). Typical misses: Burberry (-$376 to -$799), Canada Goose (-$1,024), Moncler Maya (-$521), Off-White tees (-$208 to -$283; n up to 73, median $112-186), Brioni (-$357), Gucci sweatshirt (-$392).
- Nugnes1920 (37 men's apparel items >= 40% off, 3+ sizes): no item with 3+ comps cleared $0. Fendi/Tagliatore/Givenchy/D&G halves-off are still at or above eBay.
- Mytheresa (60 items at >= 50% off, mostly Final Sale): only 4 had 3+ comps and all lose $319-$1,319 (Herno coat, D&G pants, Burberry blazer, Jil Sander jacket). A note on the pages said "20% off over $350" per product; I did not confirm if it is applied automatically or needs a code, and even at -20% those four still lose money.
- SSENSE 70% off (480 items read, ~200 scanned): deep discounts are real, but the live stock is mostly ONE size left. Checked two product pages: Amiri MA Quad Carpenter Jeans 1 of 10 sizes left; MM6 Denim Trucker Jacket 1 of 6. They fail the 3-size (2 for jackets) rule. Casablanca crochet polo, Casablanca jacquard shirt, Amiri crewneck, Dries Van Noten tee: net -$44 to +$91 and the comps did not match the exact item.
- END other: Casablanca Monogram Shirt (net $136 at median but $16 at p25, and the END item is 100% polyamide while the comps are silk-satin shirts), Rick Owens Jumbo Tee ($86), Rick Owens DRKSHDW Geth Jeans ($21), MM6 Denim Shirt ($71), Gallery Dept, Diesel, Polo Ralph Lauren, C.P. Company (-$367 and worse), A Bathing Ape.
- Excluded by rule and not scanned: Dior, Versace, Valentino, Saint Laurent, Nike, Louboutin, Hermes. Religious or mythological graphics (cross, saint, angel, Medusa, Madonna, etc.) were filtered out of every list by keyword. Palm Angels, Casablanca and Vetements graphics still need a visual check before any listing.

## Most promising brand/store combos (given the numbers)
1. END (UK) for hype brands near 35-45% off: Rick Owens / Rick Owens x Moncler / DRKSHDW, Rhude, Amiri, AMI Paris. eBay asks run well above END's sale price, but comps are thin (n of 1-3). Highest upside: Rick Owens x Moncler tee and jogger, DRKSHDW double cargo jeans.
2. SSENSE 70% off Amiri / Rick Owens / Casablanca: profit exists on paper (cost 25-35% of retail) but only 1 size is usually left. Check size menus on new arrivals to sale (sort=position-desc), not the discount-sorted page.
3. Dead ends for now: Italist, Nugnes1920 and Mytheresa at the 50% mark (prices are not low enough), Burberry, Canada Goose, Polo Ralph Lauren, Off-White tees, Stone Island, C.P. Company, Moncler core (eBay is saturated and sells near or below the sale price).

## Could not reach / not done
- Farfetch (403 Access Denied), Mr Porter (403), Luisaviaroma (403), Cettire (HTTP 500 on products.json; JS site), Nordstrom Rack / Neiman Last Call / outlet sites (Burberry, Ralph Lauren, Moncler): not attempted (bot checks / login-style flows; no products.json).
- Slam Jam and Baseblu (Shopify) were listed but their discounted men's lines are niche (Undercover, Junya, Kiko Kostadinov) with little eBay depth; not scanned.
- Sold-price history is unavailable (Browse API only shows active asks), so no median here is a confirmed selling price.
- SSENSE size availability was read for only 2 products; Italist and Nugnes stock came from products.json availability flags (not per-unit quantities).
