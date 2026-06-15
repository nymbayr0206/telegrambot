# Cold Email Prospecting (Mongolian Market)

A repeatable workflow: find a company's email, draft a professional Mongolian cold sales email, and send via Gmail. Bridges `zangia-lead-generation` (finding leads) and `lead-nurture-newsletter` (nurturing warm contacts).

## Workflow

### 0. Verify the target website (optional but recommended)

Before claiming a website is broken, verify with curl:

```
# Check if site returns 404, timeout, or other error
curl -sI --max-time 10 https://company.mn 2>/dev/null | head -20
```

Signals a broken site:
- `404 Not Found` — site exists but doesn't render
- Timeout or connection refused — site is down
- Empty response or redirect to a parking page

Also check whether the company has a website *at all*. If the company domain doesn't resolve or hasn't been registered, use the **no-website** email variant (step 2).

### 1. Find the company's email

Search for the company name in Mongolian on the web:
```bash
web_search("Пример агро ХХК Монгол contact email")
```

Best sources for Mongolian companies:
- **Zangia.mn** — search `site:zangia.mn "Company Name"` for "И-мэйл" field
- **Company website** — find via web search, then extract contact info
- **Worki.mn** — sometimes lists email for registered companies
- **Facebook page** — some companies list their email in Facebook About section. Requires browser (JS-rendered, curl won't work). If no browser is available, tell the user the email from other sources was wrong and ask them to share the Facebook-listed email.

If the company has a website, extract the email from its HTML using curl:
```bash
curl -sL --max-time 10 https://company.mn/contact/ 2>/dev/null | grep -iE 'email|mailto:|@|info'
```

Look for `href="mailto:..."` patterns in the HTML output.

### 2. Draft the cold email in Mongolian

Show the full draft to the user **before sending** (per google-workspace Rule 1). Use this template structure:

**Subject:** `Таны вэбсайтын асуудал болон шинэчлэлтийн санал`

**Body:**
```
Сайн байна уу,

[Компаний нэр]-ийн вэбсайтыг үзэхэд ажиллахгүй байгааг олж мэдсэн.
Энэ нь таны үйлчлүүлэгчдэд сөрөг сэтгэгдэл төрүүлж болзошгүй.

Бид Postly.mn баг нь орчин үеийн, аюулгүй, хямд өртөгтэй вэб
хөгжүүлэлтийн шийдлийг санал болгож байна.

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

**Variants:**
- If the company has **no website at all** → use a general "танай компанид зориулсан вэбсайтын санал" subject
- If the website **exists but is broken** (404, down) → mention the specific issue, cite the URL

### 3. Send via Gmail

```bash
GAPI="/opt/hermes/.venv/bin/python3 /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI gmail send \
  --to recipient@company.mn \
  --from "Battushig Tuguldur" \
  --subject "..." \
  --body "..."
```

### 4. Confirm delivery

The response JSON includes `status: "sent"` and a message `id`. Report back compactly: recipient, subject, status. Keep it brief — the user already knows the content.

### 5. Repeat-send pattern ("бас явуул")

For multi-company outreach, after sending to company A, the user may say:
- **"send now"** or **"бас явуул"** — send the next one immediately without re-showing the draft
- **"bas yawuul"** — also send (same template, different recipient)

When this happens, skip the draft-review step. Find the email, verify, and execute.

## Pitfalls

- **Browser not available** — when `web_extract` fails, use `curl -sL | grep` to extract email from HTML
- **Company website is a WordPress site** — contact info is usually in the `li` with `class="info"` containing `mailto:` links
- **Zangia.mn mobile vs desktop** — mobile site (m.zangia.mn) sometimes shows email, desktop hides it behind a "Contact" button; check both
- **Email not publicly listed** — if no email found, tell the user so they can decide (Facebook DM, phone call, or skip)
- **User prefers direct send** — for repeat outreach (company #2, #3, etc.), users may skip the draft review and say "send now" or "bas yawuul" (also send). Execute immediately without asking for re-approval of the same template.
- **Company website contact email may be wrong** — the email on the website's contact page (e.g. info@company.mn) might not be the right contact. If the user says it's wrong, they may have the correct one from Facebook. Tell them what you found, confirm it's wrong, and ask them to share the correct email.
- **"No website" variant** — when a company genuinely has no website, don't say "your website is not working." Instead: "Танай компанид зориулсан вэбсайтын санал" with a general pitch offering Postly's services. No need to cite a broken URL.
