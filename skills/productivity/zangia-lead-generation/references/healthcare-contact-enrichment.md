# Zangia Healthcare Contact Enrichment

Session-derived notes for enriching Zangia healthcare leads without heavy scraping or login bypass.

## Healthcare category discovery

- Zangia job search REST endpoint may not honor guessed `branchId` query params.
- The site uses GraphQL `searchJobs` with `branch_id` as a variable.
- Healthcare / medical / pharmacy category was confirmed as `branch_id: 13`.
- Example GraphQL shape:

```graphql
query SearchJobs($limit:Int!, $page:Int!, $branchId:[Int!]) {
  searchJobs(limit:$limit, page:$page, branch_id:$branchId) {
    items { id title code company_id company_name company_alias branch_id profession_id address salary_min salary_max job_level sort_time }
    pagination { total page limit totalPages hasNextPage nextPage }
  }
}
```

POST to `https://new-api.zangia.mn/graphql` with normal public-site headers (`Origin: https://www.zangia.mn`, `Referer: https://www.zangia.mn/job/list`).

## HR phone extraction

For phone numbers from job postings, do **not** rely only on search result payloads or rendered HTML. Use the public job detail API:

```text
GET https://new-api.zangia.mn/api/jobs/{job_code}
```

The response commonly includes:

- `contact` — HR/job-post phone numbers; this is the primary source for outreach phone fields.
- `description`, `requirements`, `additional` — sometimes contain additional phones/emails in HTML.
- `company` object with public company profile fields.

Example fields seen in `company`:

- `phone`
- `emails`
- `facebook`
- `website`
- `staffs_cnt`
- `branch_name`
- `work_count`

Use one request per job code with a small delay (e.g. 1–2 seconds). Deduplicate phones per company after collecting all job postings.

## Google Sheets enrichment columns

For this user's Zangia Sheets workflow, append/update separate columns rather than overwriting original scraped fields:

- `HR Phone(s) from Job Posts`
- `Company Phone`
- `Email`
- `Email Source`
- `Facebook Page`
- `Website`
- `Staff Count`
- `Enrichment Status`
- `Last Enriched At`

## Facebook and email handling

- If the Zangia `company.facebook` field is a plain page/name rather than a URL, store the raw value and optionally a Facebook page-search URL; do not invent a page slug.
- If Zangia `company.emails` is present, label source as `Zangia company profile`.
- If no Zangia email exists and `company.website` is present, lightly check the official website home/contact pages for public emails and label source as `Official website: <url>`.
- Do not bypass Facebook login walls, CAPTCHA, paywalls, or private profile restrictions.

## Outreach safety

After enrichment, bulk email sending from Gmail requires explicit user approval of:

1. recipient scope/count,
2. subject and body,
3. registration link and workshop date/time,
4. sending mode/rate.

Prefer drafting first and sending in light batches. Use BCC or individual personalized sends only after approval; never send immediately from a voice instruction alone.
