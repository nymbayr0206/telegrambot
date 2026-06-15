# unegui.mn Data Extraction Reference

## Listing Page (SSR)

URL pattern: `https://www.unegui.mn/l-hdlh/l-hdlh-zarna/gazar/han-uul-horoo-14/`

Sample from June 2026 — 60 land-for-sale ads in Khan-Uul 14th khoroo:

### HTML Structure

Each listing is inside:
```html
<div class="advert js-item-listing js-advert-click" data-event-name="advert_click" data-id="10406421" id="10406421">
  <div class="advert__body">
    ...swiper image slider...
  </div>
  <div class="advert__section">
    <div class="advert__content">
      <!-- PRICE -->
      <div class="advert__content-header">
        <a class="advert__content-price _not-title" href="/adv/10406421_.../">
          <span>16 сая <b>₮</b></span>
        </a>
      </div>
      <!-- TITLE -->
      <a class="advert__content-title" href="/adv/10406421_.../">
        Худ, гавьжийн шандад 2 айлын хоосон газар
      </a>
      <!-- DATE & LOCATION -->
      <div class="advert__content-hint">
        <div class="advert__content-date">1 цагийн өмнө</div>
        <div class="advert__content-place">Хан-Уул, Хан-Уул, Хороо 14</div>
      </div>
    </div>
  </div>
</div>
```

### Python Extraction (60 ads, ~357KB HTML)

```python
import subprocess, re

html = subprocess.run(['curl', '-s', '-L', URL,
    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'],
    capture_output=True, text=True, timeout=30).stdout

# Get all ad IDs and extract surrounding blocks
ad_starts = [m.start() for m in re.finditer(r'<div class="advert js-item-listing', html)]

for i, start in enumerate(ad_starts):
    end = ad_starts[i+1] if i+1 < len(ad_starts) else start + 5000
    block = html[start:end]
    
    ad_id = re.search(r'data-id="(\d+)"', block).group(1)
    price_match = re.search(r'<span>([\d\.\,]+)\s*(сая|тэрбум)\s*<b>₮</b>', block)
    title = re.search(r'class="advert__content-title"[^>]*>\s*([^<]+)', block)
    date = re.search(r'class="advert__content-date">([^<]+)', block)
    place = re.search(r'class="advert__content-place">([^<]+)', block)
```

## Individual Ad Page

URL: `https://www.unegui.mn/adv/{id}/` (or `https://www.unegui.mn/adv/{id}_{slug}/`)

### Extraction

```python
html = subprocess.run(['curl', '-s', '-L', url, ...], capture_output=True, text=True).stdout

# Author
author = re.search(r'<div class="author-name[^>]*itemprop="name"[^>]*>\s*([^<]+)', html)

# User ID
user_id = re.search(r'data-user="(\d+)"', html)

# Registration date
reg = re.search(r'Элссэн огноо\s*(.*?)(?:<|$)', html)

# Price from meta
price = re.search(r'<meta itemprop="price" content="(\d+\.?\d*)">', html)

# View count
views = re.search(r'<span class="counter-views">[^:]*:\s*(\d+)', html)
```

### Total Listings by Author

```python
author_html = subprocess.run(['curl', '-s', '-L',
    f'https://www.unegui.mn/items/author/{user_id}/', ...], capture_output=True, text=True).stdout
total = re.search(r'(\d+)\s*зар', author_html)
```

## Results from June 2026 Session

Khan-Uul 14th khoroo, land for sale:

| Metric | Value |
|--------|-------|
| Total ads | 60 |
| Realtors (≥5 listings) | 40 (67%) |
| Individuals (<5 listings) | 20 (33%) |
| Cheapest | 10M MNT |
| Most expensive | 900M MNT |
| Median price | 45M MNT |
| Avg views (sample 15) | 43 |

### Active realtor accounts:
- Галбадрах (ID 367338): 201 total listings
- ГАЗАР НАБА (ID 168331): 136 listings
- Remax HUB Mj (ID 5037114): 82 listings
- munkhjargal (ID 6799494): 68 listings
- Төгсжаргал (ID 6228197): 16 listings
- Barbara (ID 850348): 15 listings
- Энхмандах (ID 6982078): 13 listings
- Булган (ID 80029): 9 listings

## Price Ranges (Khan-Uul 14th khoroo, unegui.mn)

| Range | Count | Avg Price |
|-------|:-----:|:---------:|
| 10-50M | 30 | 25M |
| 50-100M | 11 | 70M |
| 100-200M | 2 | 142M |
| 200-500M | 7 | 329M |
| 500-900M | 5 | 730M |
