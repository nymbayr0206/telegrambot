# Postly Cold Email Outreach — Prospecting Tactic

A specific prospecting tactic for Postly.mn: find companies with broken/non-functional websites and send cold sales emails offering web development services.

## Workflow

### Step 1: Company Research
- Search for the company name on Google/Zangia/LinkedIn to confirm existence and industry.
- Check if they have a website: `curl -sI --max-time 10 https://www.{domain}.mn` and `curl -sI --max-time 10 http://{domain}.mn` (HTTP version often reveals 404 vs working).
- Document status: working, 404, or no website.

### Step 2: Find Contact Email
- **Preferred source: Facebook page** — search for the company's Facebook page and look for email in the About section. Facebook page descriptions in search results often include the email inline.
- **Fallback:** If Facebook doesn't have it, check their own website's Contact page, Zangia.mn company listing, or other public sources.
- Verify the email looks valid. If from a website, double-check against Facebook.

### Step 3: Send Email
- **From:** aimongoliatushig@gmail.com (Battushig Tuguldur)
- **Language:** Mongolian, professional tone
- **Subject:** "Танай компанид зориулсан вэбсайтын санал" or "Таны вэбсайтын асуудал болон шинэчлэлтийн санал"
- **Body structure:** Greeting → state finding (website not working) → introduce Postly.mn → list key features → CTA: www.postly.mn → closing

### Step 4: Confirm
- No need to ask for approval unless the user explicitly hesitates. Default: execute immediately.
- If email was wrong and user corrects you, find the right one from Facebook and resend.

## Email Template (Mongolian)

```
Сайн байна уу,

{Context about finding their website issue / offering services}

Бид Postly.mn баг нь орчин үеийн, аюулгүй, хямд өртөгтэй вэб хөгжүүлэлтийн шийдлийг санал болгож байна.

Манай онцлогууд:
- Fully responsive, modern design
- Өндөр аюулгүй байдал (SSL, firewall, хамгаалалт)
- Search Engine Friendly
- Хямд өртөг
- Түргэн ажиллагаатай

Дэлгэрэнгүй мэдээллийг www.postly.mn хаягаар авна уу. Хамтран ажиллахад бэлэн байна.

Хүндэтгэсэн,
Battushig Tuguldur
Postly.mn баг
```

## Tool Reference

Send via Gmail:
```bash
/opt/hermes/.venv/bin/python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py gmail send \
  --to recipient@example.com \
  --from "Battushig Tuguldur" \
  --subject "Таны вэбсайтын асуудал болон шинэчлэлтийн санал" \
  --body "email body here"
```

## Pitfalls
- Facebook pages are JS-rendered — curl/browser extraction often fails. Search for the page and check if email appears in Google's search results snippet instead.
- Zangia.mn is Next.js client-rendered; curl won't extract emails from the raw HTML.
- Some companies list different emails on different platforms (website vs Facebook) — Facebook email takes priority per user preference.
