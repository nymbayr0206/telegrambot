# Zangia healthcare category light collection notes

Session-derived notes for collecting public Zangia healthcare leads with minimal server load.

## Category discovery

- Zangia job search results expose `branch_id` on job rows.
- Healthcare / Эрүүл мэнд jobs use `branch_id = 13`.
- The public REST endpoint `https://new-api.zangia.mn/api/jobs/search` is good for keyword searches, but tested URL parameters such as `branchId`, `branch_id`, `branch`, and `salbar` did **not** filter the REST endpoint by branch.
- The website uses public GraphQL at `https://new-api.zangia.mn/graphql`. Use `searchJobs(... branch_id: $branchId ...)` for reliable category filtering.

## GraphQL probe

```graphql
query SearchJobs($limit:Int!,$page:Int!,$branchId:[Int!]){
  searchJobs(limit:$limit,page:$page,branch_id:$branchId){
    items {
      id title code company_id company_name company_alias branch_id profession_id
      address salary_min salary_max job_level sort_time time
    }
    pagination { total page limit totalPages hasNextPage nextPage }
  }
}
```

Variables:

```json
{"limit": 20, "page": 1, "branchId": [13]}
```

Headers that worked:

- `Content-Type: application/json`
- `Accept: application/json`
- `Origin: https://www.zangia.mn`
- `Referer: https://www.zangia.mn/job/list`
- A normal browser-like `User-Agent`

## Light-mode defaults

Use these defaults when the user asks to avoid server load:

- One worker / one process only.
- `limit=20` jobs per page.
- Sleep ~3 seconds between job pages.
- Deduplicate by `company_id` before company profile checks.
- Sleep ~4 seconds between company profile pages.
- Save JSON/CSV/logs under `/opt/data/zangia_leads/`.
- Use a background process with completion notification for long runs.

## Employee count caveat

Employee counts are not guaranteed in the job payload. Confirming “50+ employees” requires scanning public company profile text or doing a later enrichment pass from official websites/social profiles. Mark companies as:

- `yes` when public text provides a count >= 50
- `no` when public text provides a count < 50
- `unknown` when no public employee-count phrase is visible

Do not infer 50+ solely from having many job postings; use it only as a lead-scoring hint unless the user explicitly accepts heuristics.
