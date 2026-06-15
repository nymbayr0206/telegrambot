---
name: mongolian-web-scraping
description: "Extract structured data from Mongolian websites with no public API — covers SSR (server-rendered HTML) and React SPA sites. Includes field-proven patterns for unegui.mn (real estate classifieds) and remax.mn (RE/MAX Mongolia)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [scraping, mongolia, real-estate, unegui, remax]
    related_skills: [zangia-lead-generation, mongolian-real-estate-leads, maps]
---

# Mongolian Web Scraping

Two site architectures found on Mongolian web, each with a different scraping approach.

## 1. Server-Side Rendered (SSR) Sites

Content is embedded in the initial HTML response. Use `curl` + regex/Python — no browser needed.

### unegui.mn

**Listing page:** SSR — all 60 ads in HTML inside `<div class="advert js-item-listing" data-id="...">`.

**Key HTML extraction patterns:**
- Price: `<span>[\d\.]+ (сая|тэрбум) <b>₮</b></span>` inside `advert__content-price`
- Title: `class="advert__content-title"` → `a` text
- Date: `class="advert__content-date"`
- Location: `class="advert__content-place"`
- Ad URL: `href="/adv/(\d+)_..."` — full URL: `https://www.unegui.mn/adv/{id}/`

**Individual ad page** (`https://www.unegui.mn/adv/{id}/`):
- Author: `<div class="author-name" itemprop="name">` — text content
- User ID: `data-user="(\d+)"`
- Registration: `<p class="date-registration">Элссэн огноо (.*?)</p>`
- Views: `<span class="counter-views">Үзсэн : (\d+)</span>`
- Price meta: `<meta itemprop="price" content="(\d+\.?\d*)">`
- Author total listings: GET `/items/author/{user_id}/` → regex `(\d+)\s*зар`

**Phone numbers:** Hidden behind JS click-to-reveal (requires auth + click). Not scrapable via curl.

**Classification:** Realtor if total_listings ≥ 5, Individual if < 5.

**Pagination:** `<link rel="next">` / `<link rel="last" href="...&page=N">`

**Pitfalls:** POST endpoints (`/ajax-items-list/`) require CSRF token + Referer — use GET/SSR instead.

### Reference: `references/unegui-parsing.md`

## 2. React SPA Sites

Initial HTML is a ~2.5KB shell. All content loads via JS API calls.

### Discovery Process

1. Fetch the HTML → note `<script src="/static/js/main~*.js">` bundles
2. Download main JS bundle(s) and search for API patterns:
   - `grep -oP '"[a-z]+/[a-z]+/[a-z0-9_-]+"'` for REST paths
   - Search for `fetch(`, `axios`, `POST`
3. Look for `/ConfigRegion`, `/search/`, `/api/`, `listing` patterns
4. Test discovered endpoints with JSON

### remax.mn (RE/MAX Mongolia)

**Infrastructure:** React SPA + ApostropheCMS backend + Azure Cognitive Search.

**Config:** `GET https://www.remax.mn/ConfigRegion` → `{tenantid, regionid, macroregionid, defaultlanguage}`

**Search API:** `POST https://www.remax.mn/search/listing-search/docs/search`
- Content-Type: `application/json`
- Azure OData filter syntax

**Key filter fields:**
- `content/TransactionTypeUID eq 261` — for sale (худалдах); 260 = rent
- `content/PropertyTypeUID eq 18` — land (газар)
- `content/City eq 'Хан-Уул'` — city name (Mongolian Cyrillic)
- `content/LocalZone eq '14-р хороо'` — district/khoroo
- `content/OnHoldListing eq false`, `content/IsViewable eq true`

**Search body example:**
```json
{
  "count": true, "skip": 0, "top": 71,
  "searchMode": "any", "queryType": "simple", "search": "*",
  "filter": "content/TenantId eq 6 and content/MacroRegionId eq 119 and content/OnHoldListing eq false and content/IsViewable eq true and content/TransactionTypeUID eq 261 and content/PropertyTypeUID eq 18 and content/City eq 'Хан-Уул' and content/LocalZone eq '14-р хороо'"
}
```

**Response:**
- `@odata.count` — total count
- `value[].content` fields: `ListingPrice`, `ListingId`, `City`, `LocalZone`, `TotalArea`, `MLSID`, `FullTextSearch`, `ShortLinks[]` (for listing URLs), `ListingDescriptions[]`, `ListingImages[]`, `GeoDatas[]`, `AgentId`, `OfficeId`

**Listing URL:** `https://www.remax.mn/{shortlink}` — pick the Mongolian-language `ShortLink`.

**Pagination:** `skip` (offset) + `top` (page size).

### Other remax.mn endpoints:
- `POST /sendServiceBusMessage` — logging
- `POST /openai` — AI search
- `POST /logservice/InsertLog` — error logging
- `GET /api/v1/@apostrophecms/global/footer?aposLocale={lang}` — CMS footer

## 3. General Pitfalls

- **Phone obfuscation:** Mongolian classifieds (unegui.mn, zangia.mn) hide numbers behind JS click-to-reveal.
- **CSRF:** POST endpoints may require `X-CSRFToken` + cookies + Referer. Prefer GET/SSR.
- **OData escaping:** In JSON, Azure Search string filters need `'\''value'\''` single-quote escaping.
- **User-Agent:** Always set a realistic Chrome UA header.
- **Rate limiting:** Batch 10-15 requests at a time for individual pages; remax search API handles 70+ in one call.

## References

- `references/unegui-parsing.md` — detailed unegui.mn data extraction patterns
- `references/remax-api.md` — complete remax.mn API reference

## Related Skills

- `zangia-lead-generation` — lead scraping from Zangia.mn (job/company data)
- `maps` — geocoding Mongolian addresses
