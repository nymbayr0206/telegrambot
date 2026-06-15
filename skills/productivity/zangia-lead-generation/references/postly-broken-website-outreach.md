# Postly: Broken-Website Cold Email Outreach (Mongolia)

## Overview

A focused sub-pattern of Mongolia B2B lead generation: find companies whose websites are broken/down, locate their contact email from public sources (Zangia, Worki.mn), and send a professional Mongolian cold email offering Postly.mn web development services.

## Workflow

### Step 1: Find a target company

Identify the company from the user's lead (e.g. company name, industry). The user may provide a company name directly (e.g. "Orchlon Consulting LLC", "UA Properties").

### Step 2: Check if their website is working

Use curl to probe both `https://` and `http://` variants:

```bash
curl -sI --max-time 10 https://<company-domain>.mn | head -20
curl -sI --max-time 10 http://<company-domain>.mn | head -20
```

Look for:
- `HTTP/1.1 404 Not Found` — site is down/broken
- Connection timeout / `Could not resolve host` — no website
- `HTTP/1.1 200 OK` — working (not a target for this pattern)

### Step 3: Find their email (public sources)

Worki.mn (`worki.mn/company/<id>`) often exposes company email, phone, and address alongside job listings. Zangia.mn also works:

```bash
web_search "Company Name LLC Mongolia email"
web_search "Company Name Mongolia contact"
```

Check:
- Worki.mn company profile pages — often list email directly
- Zangia.mn company pages
- Facebook business pages

Common Mongolian company email patterns: `info@<company-domain>.mn`, `contact@<company-domain>.mn`

### Step 4: Send the cold email (Mongolian)

Use Google Workspace Gmail API:

```bash
/opt/hermes/.venv/bin/python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py gmail send \
  --to <target@email.com> \
  --from "Battushig Tuguldur" \
  --subject "Таны вэбсайтын асуудал болон шинэчлэлтийн санал" \
  --body "..."
```

**Email template (Mongolian):**

```
Сайн байна уу,

[Company Name]-ийн вэбсайтыг үзэхэд ([domain]) ажиллахгүй байгааг олж мэдсэн.
Энэ нь таны үйлчлүүлэгчдэд сөрөг сэтгэгдэл төрүүлж, бизнесийн боломжуудыг
алдахад хүргэж болзошгүй.

Бид Postly.mn баг нь орчин үеийн, аюулгүй, хямд өртөгтэй вэб хөгжүүлэлтийн
шийдлийг санал болгож байна.

Манай онцлогууд:
- Fully responsive, modern design
- Өндөр аюулгүй байдал (SSL, firewall, хамгаалалт)
- Search Engine Friendly
- Хямд өртөг
- Түргэн ажиллагаатай

Дэлгэрэнгүй мэдээллийг www.postly.mn хаягаар авна уу.
Хамтран ажиллахад бэлэн байна.

Хүндэтгэсэн,
Battushig Tuguldur
Postly.mn баг
```

### Step 5: Confirm delivery

The Gmail API returns JSON with `status: "sent"` + `id` + `threadId` on success.

## Tips

- Use `--from "Battushig Tuguldur"` to set a sender name (defaults to email address)
- The subject line above works for any target — keep it generic
- CTA to `www.postly.mn` is included in the body
- No attachments needed — cold emails should be text-only
- Always ask the user before sending (per Google Workspace skill rules)
