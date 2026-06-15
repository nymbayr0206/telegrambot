# remax.mn API Reference

## Infrastructure

- **Stack:** React SPA + ApostropheCMS + Azure Cognitive Search
- **Config:** `GET https://www.remax.mn/ConfigRegion`
- **Search:** `POST https://www.remax.mn/search/listing-search/docs/search`

## Config Endpoint

```bash
curl -s 'https://www.remax.mn/ConfigRegion'
```

Response (June 2026):
```json
{
  "regionDomain": "www.remax.mn",
  "regionid": 119,
  "macroregionid": 119,
  "tenantid": 6,
  "theme": "remax",
  "defaultlanguage": "mn-MN",
  "supportedlanguages": "mn-MN,en-US"
}
```

## Search API

### Request
`POST https://www.remax.mn/search/listing-search/docs/search`
Content-Type: `application/json`

### Common Filter Values

| Field | Value | Meaning |
|-------|-------|---------|
| `TransactionTypeUID` | 261 | Худалдах (for sale) |
| | 260 | Түрээслүүлнэ (for rent) |
| `PropertyTypeUID` | 18 | Газар (land) |
| | 20 | Оффис (office) |
| | 15 | Орон сууц (apartment) |
| | 16 | Хаус (house) |
| `TenantId` | 6 | Mongolia tenant |
| `MacroRegionId` | 119 | Mongolia region |

### City Names (Mongolian Cyrillic)

- Хан-Уул
- Баянзүрх
- Сүхбаатар
- Баянгол
- Сонгинохайрхан
- Чингэлтэй
- Налайх
- Багануур
- and provincial names

### Example: Land for sale in Khan-Uul 14th khoroo

```bash
curl -s 'https://www.remax.mn/search/listing-search/docs/search' \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "count": true,
    "skip": 0,
    "top": 71,
    "searchMode": "any",
    "queryType": "simple",
    "search": "*",
    "filter": "content/TenantId eq 6 and content/MacroRegionId eq 119 and content/OnHoldListing eq false and content/IsViewable eq true and content/TransactionTypeUID eq 261 and content/PropertyTypeUID eq 18 and content/City eq '\''Хан-Уул'\'' and content/LocalZone eq '\''14-р хороо'\''"
  }'
```

### Response Structure

```json
{
  "@odata.context": "...",
  "@odata.count": 71,
  "value": [
    {
      "@search.score": 1,
      "metadata_storage_path": "...",
      "content": {
        "TenantId": 6,
        "RegionId": 119,
        "MacroRegionId": 119,
        "AgentId": 119005080,
        "OfficeId": 119005,
        "ListingId": 26,
        "MLSID": "119005080-64",
        "ListingClass": 1,
        "TransactionTypeUID": 261,
        "PropertyTypeUID": 18,
        "TitleAddress": "Хан-Уул, Монгол",
        "FullAddress": "Хан-Уул, Монгол",
        "City": "Хан-Уул",
        "LocalZone": "14-р хороо",
        "Province": "Улаанбаатар",
        "CountryID": 119,
        "ListingPrice": 25000000,
        "ListingCurrency": "MNT",
        "TotalArea": 235.5,
        "ListingId": 26,
        "OrigListingDate": 1762257600,
        "LastUpdatedOnWeb": 1762231044,
        "FullTextSearch": "Худалдах ... Газар ...",
        "ShortLinks": [
          {
            "ShortLink": "mn-mn/листингүүд/газар/худалдах/хан-уул/119048298-26",
            "LanguageCode": "mn-MN"
          }
        ],
        "ListingDescriptions": [{"Description": "..."}],
        "ListingImages": [{"FileName": "L_....jpg", "Order": "1"}],
        "ListingFeatures": [{"GroupingName": "...", "FeatureName": "..."}],
        "GeoDatas": [{
          "LanguageCode": "mn-MN",
          "CountryName": "Монгол улс",
          "RegionalZone": "Монгол"
        }],
        "Location": {
          "type": "Point",
          "coordinates": [106.83028827, 47.87033035]
        }
      }
    }
  ]
}
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ListingPrice` | int | Price in MNT |
| `ListingId` | int | Internal ID |
| `City` | string | Mongolian Cyrillic city name |
| `LocalZone` | string | District/khoroo name |
| `TotalArea` | float | Area in m² |
| `MLSID` | string | MLS reference |
| `FullTextSearch` | string | Concatenated title + description |
| `ShortLinks[]` | array | Listing URLs per language |
| `ListingDescriptions[]` | array | `{Description}` objects |
| `ListingImages[]` | array | `{FileName, Order}` — image filenames |
| `ListingFeatures[]` | array | `{GroupingName, FeatureName}` |
| `Location` | GeoJSON Point | `{type, coordinates: [lng, lat]}` |
| `AgentId` | int | Listing agent ID |
| `OfficeId` | int | Office ID |
| `OrigListingDate` | unix timestamp | Original listing date |
| `LastUpdatedOnWeb` | unix timestamp | Last update |

### Listing URL Construction

Pick the Mongolian `ShortLink`:
```
https://www.remax.mn/{ShortLink}
# Example:
https://www.remax.mn/mn-mn/листингүд/газар/худалдах/хан-уул/119048298-26
```

### Pagination

Use `skip` (offset) and `top` (page size):
```json
{"skip": 0, "top": 50}   // page 1
{"skip": 50, "top": 50}  // page 2
```

## Results from June 2026 Session

Khan-Uul 14th khoroo, land for sale on remax.mn:

| Metric | Value |
|--------|-------|
| Total listings | **71** |
| Cheapest | 12M MNT |
| Most expensive | 4,175M MNT |
| Median | 28M MNT |
| Average | 289M MNT |

### Price Distribution

| Range | Count |
|-------|:-----:|
| < 15M | 5 |
| **15-30M** | **29** (most) |
| 30-50M | 3 |
| 50-100M | 6 |
| 100-300M | 5 |
| 300-500M | 6 |
| 500-1000M | 3 |
| 1B+ | 7 |

## vs unegui.mn Comparison

| Metric | unegui.mn | remax.mn |
|--------|:---------:|:--------:|
| Total ads | 60 | 71 |
| Cheapest | 10M | 12M |
| Median | 45M | **28M** |
| Max | 900M | **4,175M** |
| 15-30M range | 15 ads | **29 ads** |

remax.mn has cheaper options in the 15-30M range and more ultra-premium (1B+) listings.
