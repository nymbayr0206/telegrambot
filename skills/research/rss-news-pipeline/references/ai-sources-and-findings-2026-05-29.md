# AI News Sources — Research Session (May 29, 2026)

## Sources Tested

| Source | RSS Works? | Direct Page Works? | Notes |
|---|---|---|---|
| TechCrunch AI | ✅ Yes | ✅ Yes | Best RSS for AI — structured, reliable |
| The Verge AI | ✅ Yes (main RSS) | ✅ Yes | AI-specific sub-RSS 404s; use main RSS then filter by category tag `AI` |
| Ars Technica AI | ✅ Yes (main RSS) | ✅ Yes (js-rendered page) | AI-specific RSS at feeads.arstechnica.com/arstechnica/ai gave 404; use main feed + filter by `<category>AI</category>` |
| MIT Technology Review | ❌ RSS N/A (SPA) | ⚠️ Partial (React SPA) | Homepage is a React app; article pages render fine with direct URLs |
| WIRED AI | ❌ RSS N/A | ✅ Yes | Tag page works; articles have rich og:image |
| VentureBeat AI | ❌ Blocked | ❌ Blocked | Vercel security checkpoint — skip |
| CNBC AI | ❌ Blocked | ❌ Blocked | Bot detection — skip |

## Best 5 Sources (Confirmed Working)

### 1. TechCrunch AI
- RSS: `https://techcrunch.com/category/artificial-intelligence/feed/`
- Format: WordPress RSS 2.0 with CDATA
- Refresh: hourly (per `<sy:updatePeriod>`)
- Image extraction: ✅ `og:image` on article pages
- Article structure: `<item>` with `<title>`, `<link>`, `<dc:creator>`, `<pubDate>`, `<category>`, `<description>`, `<guid>`

### 2. The Verge
- RSS (full): `https://www.theverge.com/rss/index.xml`
- Format: Atom feed
- AI filtering: Check `<category term="AI" />` in each `<entry>`
- Image extraction: ✅ `og:image` on article pages; CDN at `platform.theverge.com/wp-content/uploads/`
- Article structure: `<entry>` with `<title type="html" />`, `<link>`, `<updated>`, `<published>`, `<category term="...">`, `<summary type="html">`

### 3. Ars Technica
- RSS (full): `https://feeds.arstechnica.com/arstechnica/index`
- Format: RSS 2.0 with `<media:content>`, `<content:encoded>`
- AI filtering: Check `<category><![CDATA[AI]]></category>` in each `<item>`
- Image extraction: ✅ `og:image` on article pages; CDN at `cdn.arstechnica.net/wp-content/uploads/`
- Good for: Deep LLM research, AI security, scientific AI

### 4. MIT Technology Review
- No public RSS (React SPA homepage)
- Article pattern: `https://www.technologyreview.com/YYYY/MM/DD/ARTICLE_ID/SLUG/`
- Use direct article URLs (find via Google News or sitemap)
- Image extraction: ✅ `og:image` at `wp.technologyreview.com/wp-content/uploads/`
- Good for: Deep analysis, AI research, long-form

### 5. WIRED
- No public RSS
- Article pattern: `https://www.wired.com/story/SLUG/`
- AI tag page: `https://www.wired.com/tag/artificial-intelligence/`
- Image extraction: ✅ `og:image` at `media.wired.com/photos/`
- Good for: Industry impact, culture, policy stories; excellent og:images

## Articles Collected This Session

### TechCrunch
| Title | Link | Image |
|---|---|---|
| Anthropic raises $65B, nears $1T valuation ahead of IPO | https://techcrunch.com/2026/05/28/anthropic-raises-65-billion-nears-1t-valuation-ahead-of-ipo/ | techcrunch.com/wp-content/uploads/2025/09/... |
| The internet is being rebuilt for machines | https://techcrunch.com/2026/05/28/the-internet-is-being-rebuilt-for-machines/ | techcrunch.com/wp-content/uploads/2026/05/ai-agents-GettyImages-2229880232.jpg |
| Just like gold and oil — AI token futures | https://techcrunch.com/2026/05/28/just-like-gold-and-oil-well-soon-be-able-to-trade-ai-token-futures/ | techcrunch.com/wp-content/uploads/2025/09/GettyImages-640351099.jpg |
| Glean's top line crosses $300M | https://techcrunch.com/2026/05/28/gleans-top-line-crosses-300m-as-ai-budget-cutting-becomes-its-major-selling-point/ | (from article page) |
| Asana acquires no-code agent-builder StackAI | https://techcrunch.com/2026/05/28/asana-acquires-no-code-agent-builder-stack-ai/ | (from article page) |

### The Verge
| Title | Link | Image |
|---|---|---|
| Claude's new model is more 'honest' when it messes up (Opus 4.8) | https://www.theverge.com/ai-artificial-intelligence/939094/anthropic-claude-4-8-opus-honesty-effort | platform.theverge.com/wp-content/uploads/sites/2/2025/08/STKB364_CLAUDE_C.jpg |
| Microsoft 365 Copilot gets a speed boost and cleaner design | https://www.theverge.com/tech/939273/microsoft-365-copilot-redesign | platform.theverge.com/wp-content/uploads/sites/2/2026/05/M365Copilot_Hero_BannerImage_1920x1080.webp |
| A $2,000 AI-generated film will debut at Tribeca | https://www.theverge.com/entertainment/939067/ai-film-dreams-of-violets-tribeca | platform.theverge.com/wp-content/uploads/sites/2/2026/05/ai-dreams-of-violets.png |

### Ars Technica
| Title | Link | Image |
|---|---|---|
| LLMs believe false statements even after explicit warnings | https://arstechnica.com/ai/2026/05/llms-believe-false-statements-even-after-explicit-warnings-that-theyre-false/ | cdn.arstechnica.net/wp-content/uploads/2026/05/GettyImages-2207567240-1152x648.jpg |
| Fed up with vibe coders, dev sneaks data-nuking prompt injection | https://arstechnica.com/security/2026/05/fed-up-with-vibe-coders-dev-sneaks-data-nuking-prompt-injection-into-their-code/ | cdn.arstechnica.net/wp-content/uploads/2026/01/coding_robots_agents-1152x648.jpg |

### MIT Technology Review
| Title | Link | Image |
|---|---|---|
| The AI Hype Index: AI gets booed in graduation season | https://www.technologyreview.com/2026/05/28/1138053/the-ai-hype-index-ai-gets-booed-in-graduation-season/ | wp.technologyreview.com/wp-content/uploads/2026/05/MJ26-Thumb.jpg |
| The Download: keeping up with AI, and the future of IVF | https://www.technologyreview.com/2026/05/27/1138048/the-download-ai-future-ivf-technology/ | wp.technologyreview.com/wp-content/uploads/2026/05/Screenshot-2026-05-27-at-12.49.53.png |
| How a new extraction process could unlock the world's lithium | https://www.technologyreview.com/2026/05/28/1138096/lithium-extraction-rock-zero/ | wp.technologyreview.com/wp-content/uploads/2026/05/AdobeStock_1948655467.jpg |

### WIRED
| Title | Link | Image |
|---|---|---|
| Illinois Lawmakers Just Passed America's Strongest AI Safety Bill | https://www.wired.com/story/illinois-pass-major-ai-safety-law-pritzker/ | media.wired.com/photos/6a1769e135f75a644600c4ac/... |
| AI Agents Plunged the Tech World Into Chaos | https://www.wired.com/story/how-ai-agents-plunged-tech-world-into-chaos/ | media.wired.com/photos/69fdc07896ebc549bb094216/... |
| AI Is Taking Over the Most Cursed Job in the World (Debt Collection) | https://www.wired.com/story/ai-takes-over-debt-collection/ | media.wired.com/photos/6a047c1d138310676483b3fe/... |
| Former Google/Apple Researchers Launch AI Feedback Loop Startup | https://www.wired.com/story/ex-google-apple-ai-researchers-want-to-make-ai-that-gets-smarter-as-you-use-it/ | media.wired.com/photos/6a15ed31ceac52c54a0384c0/... |

## Downloaded Images

All stored at `/opt/data/ai-news-images/`:
- `claude_opus.jpg` (160KB)
- `m365_copilot.webp` (62KB)
- `ai_film_tribeca.png` (1.6MB)
- `internet_machines.jpg` (1.8MB)
- `llm_false.jpg` (53KB)
- `ai_agents_chaos.jpg` (98KB)
- `ai_safety_law.jpg` (58KB)

## Key curl Parameters

```bash
# Standard headers that work across all sources
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
REFERER="https://SOURCE_DOMAIN.com/"

# Article page fetch (to extract og:image)
curl -s -L -A "$USER_AGENT" "ARTICLE_URL" | \
  grep -oP '<meta[^>]*og:image[^>]*content="\K[^"]+'

# Image download (strip query params from URL)
curl -s -L -o "output.jpg" -A "$USER_AGENT" -H "Referer: $REFERER" \
  "BASE_IMAGE_URL"  # without ?quality=90&strip=all&...
```
