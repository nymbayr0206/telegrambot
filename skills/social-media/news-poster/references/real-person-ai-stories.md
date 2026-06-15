# Real-Person AI Story Sources

Sources for finding genuine stories about real people using AI and how it changed their lives. These are used for success-story content under the `news-post-1` template.

## Primary Sources (RSS-fetchable)

### 1. Hacker News — Show HN
- **RSS:** `https://hnrss.org/show` ✅ Works reliably
- **Content:** People share apps/projects they built. Many include personal backstories.
- **Filter:** Search titles for "AI", "agent", "vibe coding", "built with Claude/ChatGPT/Cursor"
- **Strength:** Real builders, technical depth, honest stories (successes AND failures)

### 2. Substack — AI/Vibe Coding Newsletters
- **RSS:** Most Substacks have `/feed` endpoint (e.g. `https://newsletter-name.substack.com/feed`)
- **Best finds from this session:**
  - `iamjohnellison.substack.com` — "5 Builders Who Turned Vibe Coding Into Serious Money" (Alex Finn, Paulius, Sherry Jiang, etc.)
  - `maxturazzini.substack.com/feed` — "Vibe Coding - Real Life Stories" series
- **Strength:** Curated, narrative-rich with actual revenue numbers

### 3. Indie Hackers
- **RSS:** `https://www.indiehackers.com/rss.xml` (may need cookie handling)
- **Content:** Solo founders building with AI, revenue reports, lessons learned
- **Strength:** Business-focused, real financial data

### 4. TechCrunch / Ars Technica
- Standard RSS feeds (see `rss-news-pipeline`)
- Filter for profile-style articles about individual founders using AI

## Finding Real Person Photos

When a success story names a specific person, get their real photo:

### Method 1: Twitter/X Profile Photo
```bash
# 1. Fetch the person's profile page
curl -s -L -A 'Mozilla/5.0' 'https://x.com/USERNAME' | \
  grep -oP 'https://pbs\.twimg\.com/profile_images/[^"]+'

# 2. Get a larger size (remove _normal, _bigger, _200x200 suffixes)
#    Add _400x400 for medium, or no suffix for original
https://pbs.twimg.com/profile_images/12345/abc_normal.jpg  → remove _normal
https://pbs.twimg.com/profile_images/12345/abc_bigger.jpg  → remove _bigger
https://pbs.twimg.com/profile_images/12345/abc_200x200.jpg → remove _200x200

# 3. Download with proper user-agent
curl -s -L -o person.jpg -A 'Mozilla/5.0' 'https://pbs.twimg.com/profile_images/12345/abc.jpg'
```

### Method 2: LinkedIn Profile Photo
- Scrape is harder (login wall)
- Alternative: search Google Images for "[name] founder [company]" with `&tbm=isch`

### Method 3: Article OG Image
- Some articles about the person include their photo as the og:image
- Extract via: `grep -oP '<meta[^>]*og:image[^>]*content="\K[^"]+'`

## Concrete Example: Alex Finn

**Story:** Non-technical founder. Built Creator Buddy with Claude Code. $300K ARR, 0 employees, 90% margins in 10 months.

**Sources:**
- Substack article: `iamjohnellison.substack.com/p/the-vibe-coding-wave-is-here-5-builders`
- X/Twitter: `https://x.com/AlexFinn`
- LinkedIn: `linkedin.com/in/alex-finn-1848684a`
- Photo URL: `https://pbs.twimg.com/profile_images/2058318378012721152/XuL3nX9B_400x400.jpg`

**4-slide success story structure using news-post-1:**
| Slide | Focus | Headline Pattern | Image |
|-------|-------|-----------------|-------|
| 1 | Hook + Person Intro | "Код мэдэхгүй хүн" (white) + "$300K ARR босгосон" (dark) | Person's portrait photo |
| 2 | Problem / BEFORE | [Problem description] white + dark | Problem-related visual |
| 3 | Solution / AFTER | [Solution description] white + dark | Solution/product photo |
| 4 | CTA / Lesson | [Call to action] white + dark | Optional visual |

## Automation Pattern (Twice Weekly)

```bash
# Cron: fetch from HN Show + Substack → filter for AI stories → pick best → extract photo → generate
```

Recommended schedule: Mon 09:00 + Thu 09:00 ULAT.
