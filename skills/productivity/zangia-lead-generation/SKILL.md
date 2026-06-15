---
name: zangia-lead-generation
description: "Use when generating Mongolia B2B lead lists from public sources, especially Zangia.mn hiring signals and MNCCI/iKon TOP-100 company rankings, then turning them into outreach-ready Google Sheets/Odoo lead lists."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [zangia, leads, sales, recruiting, mongolia, b2b, prospecting]
    related_skills: [google-workspace, odoo19-query]
---

# Mongolia B2B Lead Generation

## Overview

This skill generates Mongolia B2B leads from public sources. The primary source is public Zangia.mn job postings, but the workflow also covers high-value public company rankings such as MNCCI/iKon TOP-100 companies when the user asks for "top taxpayers", "top 100 companies", or major enterprise targets.

Zangia's public website is `https://www.zangia.mn` and job search data is available through the public API endpoint `https://new-api.zangia.mn/api/jobs/search` used by the site.

Use this when the user asks for leads such as:
- companies hiring sales/accounting/driver/operations staff
- companies with many active job ads
- leads in a specific sector or location
- top Mongolian taxpayers / TOP-100 companies / large enterprise prospect lists
- outreach targets to import into Gmail, Sheets, Odoo CRM, or another sales pipeline

## Safety and Compliance

- Use only public job posting data.
- Do not bypass login, CAPTCHA, paywalls, or access controls.
- Keep request rates low; avoid bulk scraping.
- Do not spam. Generate leads and draft outreach only; ask before sending emails/messages.
- Treat phone/email/contact details as personal/business contact data and avoid exposing unnecessary data.
- Include source URLs so the user can verify each lead.

## Helper Script

Use:

```bash
python /opt/data/skills/productivity/zangia-lead-generation/scripts/zangia_leads.py search --query sales --limit 20 --format json
python /opt/data/skills/productivity/zangia-lead-generation/scripts/zangia_leads.py search --query "нягтлан" --limit 20 --format csv --output /tmp/zangia_leads.csv
python /opt/data/skills/productivity/zangia-lead-generation/scripts/zangia_leads.py search --query driver --pages 2 --limit 30 --format markdown
```

Output fields include:
- `company_name`
- `company_id`
- `company_alias`
- `job_title`
- `job_code`
- `job_url`
- `company_url`
- `contact` if present in the public job payload
- `address`
- `salary_phrase`
- `job_level`
- `posted_or_sort_time`

For richer contact enrichment, fetch each public job detail endpoint:

```bash
curl -s 'https://new-api.zangia.mn/api/jobs/<job_code>' \
  -H 'Accept: application/json' \
  -H 'Origin: https://www.zangia.mn' \
  -H 'Referer: https://www.zangia.mn/job/<job_code>'
```

The job-detail JSON can expose:
- `contact` — HR/recruiting phone(s) for that posting; prefer this for outreach phone fields.
- `company.phone` — general company phone.
- `company.emails` — public company email(s) from the Zangia company profile.
- `company.facebook`, `company.website` — public social/website fields, sometimes a name rather than a URL.
- `company.staffs_cnt` — employee/staff count when available.
- `description`, `requirements`, `additional` — may contain extra phones/emails; strip HTML before regex extraction.

## Query Workflow

### MNCCI / iKon TOP-100 lead source

When the user asks for Mongolia's top taxpayers, TOP-100 companies, or large enterprise targets, use the MNCCI TOP-100 list before ad-hoc web search. The public source is typically `https://www.mongolchamber.mn/p/558` plus iKon's article/interactive visualization. The 2024 interactive CSV discovered in-session was `https://content.ikon.mn/visuals/2024top100/top100-2024.csv?v=4`.

Important: explain that this is the **TOP-100 AAN** ranking, not a pure tax-only ranking. It includes sales revenue, tax paid, insured employee count, profit, and assets; however, the article states the 2024 TOP-100 companies paid 7.64 trillion MNT in taxes, 28% of total tax revenue.

For reusable extraction details and a lead-sheet column template, see `references/mongolia-top100-enterprise-leads.md`.

### Zangia job-signal workflow

1. Convert the user's target into search terms or a category filter. Examples:
   - "construction leads" → `барилга`, `construction`
   - "accounting leads" → `нягтлан`, `accountant`
   - "companies hiring drivers" → `жолооч`, `driver`
   - "sales leads" → `sales`, `борлуулалт`
   - "health care companies" / "healthcare category" → Zangia public GraphQL `searchJobs` with `branch_id: [13]`
2. Run a small probe first and inspect totals/page count.
3. Deduplicate by `company_id` unless the user wants every job ad.
4. Rank leads by relevance, active hiring signal, salary/role seniority, and presence of contact/company info.
5. Present a concise lead list with source links.
6. If the user asks to add leads to Odoo CRM, Gmail, or Sheets, confirm before writing.

### Light category collection

When the user asks to collect a full category but keep server load low, prefer a single-worker background collector: small pages, fixed delays, progress logs, and completion notification. For healthcare, use `scripts/zangia_healthcare_light_collector.py`; see `references/healthcare-category-light-collection.md` for the GraphQL query, category ID, rate limits, and employee-count caveats.

Employee count is not guaranteed in Zangia job payloads. For requests like "companies over 50 employees", scan public company profile text for explicit employee-count evidence and mark missing evidence as `unknown`; do not treat active job volume as proof unless the user agrees to heuristic scoring.

### Industry-specific keyword search (niche discovery)

When the user wants companies in a specific business **sector** (e.g. "security companies", "construction companies", "IT companies") rather than companies hiring a specific job title:

1. **Broad keyword probe** — Search Zangia with 5-10 Mongolian/English terms relevant to the sector. For security: `хамгаалалт`, `секьюрити`, `харуул`, `камер`, `аюулгүй байдал`, `cctv`, `хамгаалалтын байгууллага`, plus known company names in that sector (`Тургут`, `Сэрэмж`, etc.).
2. **Collect all matching companies** — Deduplicate by `company_id`. Accept that many matches will be non-sector companies that happen to hire for security/cctv/guard roles (e.g. a hotel hiring a security guard is not a security company).
3. **Classify by job titles** — After deduplication, filter to companies whose job titles contain the sector keywords. This narrows the list to companies with active security-related hiring.
4. **Present with caveat** — Explain that some companies on the list are the sector itself (e.g. security service firms), while others are non-sector businesses that happen to have security-adjacent openings. The user can prune further manually from the Sheet.
5. **Save to Google Sheets** — Create a new tab named by sector (e.g. "Security Leads") with columns: Company Name, Phone Number, Zangia URL, Address, Job Types, Branch ID.

**Performance:** 10-15 keyword probes × 2 pages each ≈ 1000-2000 raw job items → ~50-100 sector-matched companies after dedupe + classification. Takes about 30-60 seconds of API time at polite delays.

**Endpoint:** `GET https://new-api.zangia.mn/api/jobs/search?query=<url-encoded-keyword>&limit=50&page=N`

**Branch ID exploration:** When a sector doesn't have an obvious `branch_id`, sample the first 50-100 jobs from a few broad keyword probes, collect the `branch_id` values seen, and note which branches have the most relevant job titles. Example: Security companies appeared most in `branch_id=3` (guard jobs), `branch_id=19` (camera/CCTV), and `branch_id=20` (cybersecurity).

## Examples

### Generate 10 sales leads

```bash
python scripts/zangia_leads.py search --query "борлуулалт" --limit 10 --format markdown
```

### Generate a CSV for outreach

```bash
python scripts/zangia_leads.py search --query "нягтлан" --pages 2 --limit 50 --format csv --output /tmp/accounting_leads.csv
```

### Find companies hiring drivers

```bash
python scripts/zangia_leads.py search --query "жолооч" --limit 25 --format json
```

### Find security companies by industry keyword classification

```python
# Pattern: broad keyword probe → dedupe by company_id → classify by job title keywords
keywords = ["хамгаалалт", "секьюрити", "харуул", "камер", "cctv", "аюулгүй байдал"]
all_companies = {}  # keyed by company_id
for kw in keywords:
    for page in [1, 2]:
        resp = requests.get(f"https://new-api.zangia.mn/api/jobs/search?query={quote(kw)}&limit=50&page={page}")
        for job in resp.json()["items"]:
            cid = job["company_id"]
            if cid not in all_companies:
                all_companies[cid] = {"name": job["company_name"], "phone": job.get("contact",""), "jobs": []}
            all_companies[cid]["jobs"].append(job["title"])

# Classify: keep only companies whose job titles contain sector keywords
sector_kws = ["хамгаалалт", "харуул", "аюулгүй", "секьюрити", "камер", "cctv"]
security = {cid: info for cid, info in all_companies.items()
            if any(kw in ' '.join(info["jobs"]).lower() for kw in sector_kws)}
print(f"Found {len(security)} security companies out of {len(all_companies)} raw matches")
```

## Google Sheets Persistence

When the user asks to save Zangia leads "to a database" or asks how to retrieve them later, recommend Google Sheets first unless they explicitly ask for Odoo CRM. This user's preferred workflow is: gather/review Zangia leads → save to a Google Sheet → optionally import selected leads into Odoo CRM after confirmation.

For importing from Google Sheets into Odoo CRM, see `odoo19-query` skill → `references/sheets-to-crm-import.md`. The import script is at `/opt/data/scripts/import_sales_leads_to_crm.py`.

Suggested sheet structure:
- Spreadsheet title: `Zangia Leads`
- Tab name by lead type, e.g. `Sales Leads`, `Accounting Leads`, `Driver Leads`, `Healthcare Leads`
- Columns: `Company Name`, `English Name`, `Phone / Contact`, `Job Title`, `Salary`, `Address`, `Company URL`, `Job Source URL`, `Job Level`, `Company ID`, `Job Code`, `Date Collected`, `Source`, `Status / Notes`
- Enrichment columns when public contact research is requested: `HR Phone(s) from Job Posts`, `Company Phone`, `Email`, `Email Source`, `Facebook Page`, `Website`, `Staff Count`, `Enrichment Status`, `Last Enriched At`
- Keep job-post HR phones separate from general company phones so outreach can target recruiting contacts first.

Workflow:
1. Confirm before creating or modifying a Google Sheet.
2. Generate leads with the helper script in JSON format.
3. Create a new spreadsheet or append to the existing `Zangia Leads` sheet if the user asks to add more leads.
4. Freeze and bold the header row when creating a new sheet.
5. Verify the write by reading back the first rows.
6. Tell the user the sheet title, tab, lead count, and spreadsheet URL.
7. For later retrieval, interpret requests like "show my Zangia leads" or "open my Zangia Leads sheet" as Google Sheets lookups before querying Odoo.

## Public Contact Enrichment

When the user asks to enrich a lead with email/Facebook/website data:
1. Start from the lead's `company_name`, `company_name_en`, `company_url`, and job-source contact details.
2. Search or inspect only public company-controlled pages: official website contact pages, public Facebook business pages, LinkedIn public company profiles, and the Zangia company/job pages.
3. For HR/job-post phone numbers, prefer the public job-detail endpoint `https://new-api.zangia.mn/api/jobs/{job_code}` because it exposes the job `contact` field and a public `company` object (`phone`, `emails`, `facebook`, `website`, `staffs_cnt`) more reliably than rendered HTML.
4. If Facebook does not expose an email publicly, say so clearly; do not imply Facebook had the email if it came from the official website or Zangia company profile.
5. Prefer verified official-site emails over search snippets, but label Zangia company-profile emails as `Zangia company profile` when that is the source.
6. Save both the value and source: e.g. `Email` plus `Email Source`, and optionally `Facebook Page`.
7. Confirm before modifying the Google Sheet, then verify by reading the updated row.

Session example: Toyota Sales Mongolia's Facebook page was public, but no email was visible there; the official contact page exposed `customer_service@toyota-mongolia.mn`, so the Sheet was updated with the email source URL and Facebook page separately. See `references/public-contact-enrichment.md`.

Healthcare-specific enrichment notes (branch/category discovery, HR phone extraction, staff count, and Sheet columns) are in `references/healthcare-contact-enrichment.md`.

## Lead Enrichment

For public email/Facebook/website enrichment, see `references/lead-enrichment.md`.

## Estimating Full-Market Collection Time

When the user asks how long it will take to collect "all" Zangia company data or companies above an employee threshold, first estimate from the public jobs API metadata rather than guessing:

1. Query `https://new-api.zangia.mn/api/jobs/search?limit=1&page=1&time=1` and read `meta.total` / `meta.totalPages`.
2. Probe a few pages with a larger limit (commonly 100) to confirm the API page size and response time.
3. Sample several hundred jobs, dedupe by `company_id`, and estimate unique hiring companies from the observed unique-company/job ratio.
4. Explain that active job postings are fast to collect, but confirming "50+ employees" usually requires company-profile inspection or enrichment because employee count may not be present in the job payload.
5. Give a staged estimate: API collection + dedupe, company-profile checks, then optional contact enrichment. Prefer ranges and label assumptions.

Reference baseline from a May 2026 probe: public search metadata showed ~7,894 active jobs; `limit=100` produced ~79 pages; sampling 500 jobs yielded 195 unique companies (~39%), implying roughly ~3,000 unique active hiring companies before filtering. At polite rates, a clean 50+ employee lead list is more realistically a 3–5 hour batch than a minutes-only scrape; full public contact enrichment can become a 1–2 day workflow.

When the user asks to find emails from Facebook or public pages:
1. Start with one lead or a small batch unless the user asks for bulk enrichment.
2. First fetch Zangia job-detail JSON for each job code and collect `contact` as `HR Phone(s) from Job Posts`; many job list payloads omit this field but detail endpoints include it.
3. Also collect `company.phone`, `company.emails`, `company.facebook`, `company.website`, and `company.staffs_cnt` from the same detail response.
4. Check public Facebook/company pages without bypassing login, CAPTCHA, or access controls.
5. If Facebook does not expose an email, check the official company website/contact page and label the source clearly.
6. Add separate enrichment columns such as `HR Phone(s) from Job Posts`, `Company Phone`, `Email`, `Email Source`, `Facebook Page`, `Website`, `Staff Count`, `Enrichment Status`, and `Last Enriched At` rather than overwriting original Zangia fields.
7. Ask for confirmation before writing enrichment results back to Google Sheets, Odoo, or another database unless the user has already explicitly requested updating the same sheet for the current batch.

## Outreach Rules

When drafting outreach:
- Reference the open role naturally: "I noticed your company is hiring for ..."
- Keep the first message short and professional.
- Do not claim a partnership with Zangia.
- For bulk Gmail outreach, first read/count valid recipients from the Sheet, find/confirm the registration link and event date/time, draft the exact subject/body, then ask for explicit approval before sending.
- For workshop/webinar invitations, verify the signup capture path before asking to send: the public registration URL should be deployed/reachable and the Hermes webhook/Google Sheet tab should be ready to store signups. If only a code patch was prepared but not deployed, say so and do not treat the link as ready.
- Ask for confirmation before sending any email.

### Postly broken-website cold email pattern

For Postly sales outreach targeting companies with non-working Mongolian websites, see `references/postly-broken-website-outreach.md`. The pattern: find company → check website with curl → find email (Worki.mn / Zangia) → send professional Mongolian email with CTA to postly.mn. Use `--from "Battushig Tuguldur"` with the Gmail send command.

## Common Pitfalls

1. **Misspelling Zangia as Zengia.** The working site is `zangia.mn`; `zengia.mn` does not resolve.
2. **Assuming every job has email.** Many postings expose phone/contact but not email. Use website/company page for further enrichment if needed.
3. **Over-scraping.** Keep pages/limits small unless the user explicitly needs a larger export.
4. **Duplicate companies.** Many companies post multiple jobs; deduplicate by `company_id` for lead lists.
5. **Language mismatch.** Search in both English and Mongolian when results look thin.
6. **REST branch filters may be ignored.** For exact Zangia categories, especially healthcare, use public GraphQL `searchJobs` with `branch_id` instead of assuming REST query parameters filter categories.
7. **Employee-count overclaiming.** Zangia job rows usually do not prove company size. Only mark `50+ employees` as confirmed when public profile/official text contains explicit evidence; otherwise use `unknown` or a separate heuristic score.
8. **Enrichment quality varies by vertical.** After saving leads to Google Sheets, always verify which columns are actually populated per tab. In practice:
   - Healthcare leads: ~96% have emails (enriched via Zangia company profiles)
   - Sales leads: ~14% have emails (most lack email enrichment)
   - Security leads: 0% have emails (no email column added during scraping)
   - Workshop signups: 0% (new signups coming from webhook)
   
   Before asking the user to proceed with email/SMS outreach for a given tab, read the sheet and report the fill rate per column (email, phone, Facebook, website). Recommend re-enrichment for verticles with <50% email coverage before sending campaigns.
9. **Phone-number formatting.** Zangia company profiles often expose phone numbers (landline + mobile) in the `company.phone` field. When capturing to Sheets, store both `HR Phone(s) from Job Posts` (from job-detail JSON contact field) and `Company Phone` (general office line) in separate columns. Prefer HR phones for direct hiring outreach.

## Verification Checklist

- [ ] Script returns results for the query.
- [ ] Leads include source URLs.
- [ ] Duplicates are removed unless requested.
- [ ] No login bypass or restricted data used.
- [ ] User confirms before sending outreach or writing into CRM/sheets.
