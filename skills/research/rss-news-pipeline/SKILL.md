---
name: rss-news-pipeline
description: "Monitor RSS news feeds, extract articles with images, and pipe into content creation workflows (carousel posters, summaries, training materials)."
version: 1.1.0
author: Hermes
platforms: [linux, macos]
metadata:
  hermes:
    tags: [RSS, News, Content-Creation, Carousel, Web-Scraping]
prerequisites:
  commands: [curl]
  notes: "No special tools needed — uses curl + standard Unix tools. Browser tools not required."
---

# RSS News Pipeline

Monitor industry news via RSS feeds, extract article content and images, and feed into downstream content creation tools (e.g. carousel poster generation, daily briefing summaries, training material).

## When to Use

- User asks to "find news sources" or "monitor industry updates"
- User wants to create regular content (carousels, summaries, social posts) from news
- User wants an automated pipeline: "check sources → get articles + images → create asset"

## Step-by-Step: Researching + Fetching News

### 1. Identify Top Sources

Find 3–5 authoritative sources for the industry. For **AI industry news**, the canonical top 5 are:

| Source | Feed URL | Format | Best For |
|---|---|---|---|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | RSS 2.0 | Startup funding, enterprise AI, industry analysis |
| The Verge | `https://www.theverge.com/rss/index.xml` | **Atom** | AI product news, consumer AI, tech policy |
| Ars Technica | `https://feeds.arstechnica.com/arstechnica/index` | RSS 2.0 | Deep technical AI research, LLM science, security |
| MIT Technology Review | (no public RSS — React SPA) | N/A | Deep science, AI research, thoughtful analysis |
| WIRED | (no public RSS) | N/A | AI industry impact, culture, policy |

**Important: RSS vs Atom format.** Some sources (The Verge) use **Atom XML**, not RSS 2.0. Atom uses `<feed>` as root, `<entry>` for articles, `<link href="..."/>` for links (not `<link>...</link>`), and `<category term="A"/>` scheme. RSS 2.0 uses `<rss>`, `<item>`, `<link>...</link>`, `<category><![CDATA[A]]></category>`. See "Parsing Atom vs RSS" below.

### 2. Fetch & Parse Feeds (Two Approaches)

#### A. Bash/grep (Quick, fragile — RSS 2.0 only)

```bash
# Fetch RSS feed
curl -s -L -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
  'https://techcrunch.com/category/artificial-intelligence/feed/' | \
  grep -oP '<link>[^<]*</link>' | head -10
```

Only works on RSS 2.0 (XML tags wrapped in `<item>`). Will produce garbage on Atom feeds.

#### B. Python via execute_code (Recommended — handles both RSS and Atom)

Use `execute_code` with `xml.etree.ElementTree` or regex for reliable multi-feed parsing:

```python
from hermes_tools import terminal
import re

# Fetch the feed
r = terminal("curl -s -L -A 'Mozilla/5.0' 'https://www.theverge.com/rss/index.xml'", timeout=30)
xml = r["output"]

# Check format
is_atom = '<feed' in xml[:200]

if is_atom:
    # Atom format: <entry> with <link href="..."/>
    titles = re.findall(r'<title[^>]*><!\[CDATA\[(.*?)\]\]></title>', xml)
    links = re.findall(r'<link[^>]*href="([^"]*)"', xml)[1:]  # skip feed-level link
    cats = re.findall(r'<category[^>]*term="([^"]*)"', xml)
    # Entries are interleaved — group by entry blocks
    entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
    for i, entry in enumerate(entries):
        title = re.search(r'<title[^>]*><!\[CDATA\[(.*?)\]\]></title>', entry)
        link = re.search(r'<link[^>]*href="([^"]*)"', entry)
        cats_in = re.findall(r'<category[^>]*term="([^"]*)"', entry)
        summary = re.search(r'<summary[^>]*><!\[CDATA\[(.*?)\]\]></summary>', entry, re.DOTALL)
        # Filter by category
        if 'AI' in cats_in:
            print(f"AI Article: {title.group(1) if title else ''}")
else:
    # RSS 2.0 format: <item> with <link>...</link>
    items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
    for item in items:
        title = re.search(r'<title>(.*?)</title>', item)
        link = re.search(r'<link>(.*?)</link>', item)
        # CDATA-wrapped categories (e.g. <category><![CDATA[AI]]></category>)
    cats_raw = re.findall(r'<category>(.*?)</category>', item)
    cats_clean = [re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', c) for c in cats_raw]
        # Filter by AI category
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning']
        if any(kw in ' '.join(cats_clean).lower() for kw in ai_keywords):
            print(f"AI Article: {title.group(1) if title else ''}")
```

For sources without RSS (MIT, WIRED), fetch the tag page directly:
```bash
curl -s -L -A 'Mozilla/5.0' 'https://www.wired.com/tag/artificial-intelligence/' | \
  grep -oP 'href="/story/[^"]*"' | head -5
```

### 3. Get Article Images via og:image

Each article page has Open Graph meta tags. Extract the image with bash:

```bash
curl -s -L -A 'Mozilla/5.0' 'ARTICLE_URL' | \
  grep -oP '<meta[^>]*og:image[^>]*content="\K[^"]+'
```

Or with Python for richer extraction (og:image + og:title + og:description together):
```python
import re
r = terminal("curl -s -L -A 'Mozilla/5.0' 'ARTICLE_URL'", timeout=30)
html = r["output"]
og_img = re.search(r'<meta[^>]*og:image[^>]*content="([^"]*)"', html)
og_title = re.search(r'<meta[^>]*og:title[^>]*content="([^"]*)"', html)
og_desc = re.search(r'<meta[^>]*og:description[^>]*content="([^"]*)"', html)
```

**Note for TechCrunch:** RSS `<description>` is often very short (10-15 words). Always fetch the article page and extract `og:description` for richer summaries.

### 4. Download Images

```bash
mkdir -p /opt/data/ai-news-images
curl -s -L -o "article_name.jpg" -A "Mozilla/5.0" \
  -H "Referer: https://SITE.com/" \
  "IMAGE_URL"
```

**Important:** Strip query parameters from image URLs when downloading — some CDNs reject the full query-string URL but accept the base URL.

### 5. Filter for Relevance

Filter articles by keywords in title/category/description to keep only the most relevant ones for your topic (e.g., for AI industry news: 'AI', 'agent', 'automation', 'machine learning', 'LLM', 'enterprise', 'transformation').

## Setting Up Cron Jobs

Once sources are confirmed, create cron jobs to periodically check them:

```bash
# Pattern: cronjob action=create with:
# - schedule (e.g. '0 9 * * *' for daily 9am, 'every 6h' for 4x daily)
# - prompt that fetches latest articles from selected RSS feeds
# - script that outputs JSON with {source, title, link, image_url, summary}
# - downstream step: generate carousel poster from the data
```

**Recommended refresh rates:**
- Daily (9am): For content that covers the "big story" of the day
- Twice daily (9am + 6pm): For fast-moving industries like AI
- Weekly: For deeper analysis sources like MIT Tech Review

## Pitfalls

- **Sites with JavaScript rendering** (e.g., MIT Tech Review, VentureBeat): RSS feed often works when the homepage doesn't. Always try RSS first.
- **Cloudflare/Vercel blocks**: Some sites (VentureBeat, CNBC) use bot protection. Set `-A` (User-Agent) header to a real browser string. If still blocked, skip that source.
- **Image CDN blocks**: The `og:image` URL often has `?quality=90&strip=all&...` query params. When downloading via curl, some CDNs reject these or return 403. **Two fixes to try (in order):**
  1. Set `-H "Referer: https://SOURCE_DOMAIN.com/"` header first — this works for most sites (platform.theverge.com, techcrunch.com, cdn.arstechnica.com, media.wired.com).
  2. Strip query params from the URL (everything after `?`) — fallback if Referer alone doesn't work.
  Always try Referer first before stripping params, because some CDNs require the full URL with params.
- **TechCrunch RSS**: Uses `&apos;` HTML entities in titles — parse with `--xml` awareness or pre-decode.
- **Short descriptions**: TechCrunch RSS `<description>` can be brief (10-15 words). For richer content, fetch individual article pages and extract `og:description`.
- **Podcast episodes may mix in**: Some RSS feeds include podcast entries alongside articles. Filter them out by checking for `<enclosure>` or `media:content` tags.

## Verification

After fetching, verify:
- [ ] All 3–5 sources returned articles (not error pages)
- [ ] Images downloaded successfully (check file size > 5KB)
- [ ] Image files are in a standard format (.jpg, .png, .webp)
- [ ] Article links are real URLs (not relative paths or feed URLs)

## Session-Specific Data

When you run this skill for a specific topic (e.g. "AI industry news for carousel posters"), save the collected articles + images to a dated reference file under `references/<topic>-<YYYY-MM-DD>.md`. This preserves the research for downstream content creation pipelines (carousel generation, cron jobs). The file should include:

- Sources table (RSS URL, format, notes)
- Best articles per source (title, link, image URL, summary)
- Downloaded image paths
- Download command patterns that worked for each source's CDN
- Any source-specific quirks discovered (e.g. CDATA categories, Atom vs RSS format, image CDN block workarounds)
