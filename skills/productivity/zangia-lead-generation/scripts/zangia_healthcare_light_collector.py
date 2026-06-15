#!/usr/bin/env python3
"""Light Zangia healthcare lead collector.

Collects public Zangia health-care category jobs (branch_id=13), dedupes companies,
and lightly scans company pages for employee-count evidence when publicly visible.
Designed for low server load: one worker, small pages, fixed delays, resumable-by-output.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

GRAPHQL_URL = "https://new-api.zangia.mn/graphql"
SITE_URL = "https://www.zangia.mn"
BRANCH_ID = 13  # Healthcare / Эрүүл мэнд
LIMIT = 20
DELAY_BETWEEN_JOB_PAGES = 3.0
DELAY_BETWEEN_COMPANY_PAGES = 4.0
OUT_DIR = Path("/opt/data/zangia_leads")

QUERY = """
query SearchJobs($limit:Int!,$page:Int!,$branchId:[Int!]){
  searchJobs(limit:$limit,page:$page,branch_id:$branchId){
    items {
      id title code company_id company_name company_alias branch_id profession_id
      address salary_min salary_max job_level sort_time time
    }
    pagination { total page limit totalPages hasNextPage nextPage }
  }
}
"""

EMP_PATTERNS = [
    re.compile(r"(\d{2,5})\s*(?:\+|дээш)?\s*(?:ажилтан|ажилтантай|хүний бүрэлдэхүүн|мэргэжилтэн)", re.I),
    re.compile(r"(?:ажилтан|ажилтантай|employees?|staff)\D{0,30}(\d{2,5})", re.I),
    re.compile(r"(\d{2,5})\s*(?:\+)?\s*(?:employees?|staff)", re.I),
]


def log(msg: str, log_path: Path) -> None:
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def gql_page(page: int) -> dict[str, Any]:
    payload = json.dumps({"query": QUERY, "variables": {"limit": LIMIT, "page": page, "branchId": [BRANCH_ID]}}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "User-Agent": "Mozilla/5.0 Hermes Zangia healthcare light collector",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": SITE_URL,
            "Referer": f"{SITE_URL}/job/list",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False))
    return data["data"]["searchJobs"]


def company_url(alias: str | None, company_id: int | str | None) -> str:
    path = (alias or str(company_id or "")).strip()
    return f"{SITE_URL}/company/{path}" if path else ""


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Hermes Zangia healthcare light collector"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", "ignore")
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def employee_evidence(text: str) -> tuple[int | None, str]:
    for pat in EMP_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        try:
            count = int(m.group(1))
        except Exception:
            continue
        start, end = max(0, m.start() - 80), min(len(text), m.end() + 100)
        return count, text[start:end]
    return None, ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUT_DIR / f"healthcare_branch13_{run_id}.json"
    csv_path = OUT_DIR / f"healthcare_branch13_{run_id}.csv"
    log_path = OUT_DIR / f"healthcare_branch13_{run_id}.log"

    log("Starting light healthcare collector: branch_id=13, page=1, limit=20, delay=3s", log_path)
    jobs: list[dict[str, Any]] = []
    first = gql_page(1)
    pagination = first.get("pagination") or {}
    total_pages = int(pagination.get("totalPages") or 1)
    log(f"Healthcare category reports {pagination.get('total') or 0} jobs across {total_pages} pages", log_path)

    for page in range(1, total_pages + 1):
        result = first if page == 1 else gql_page(page)
        for j in result.get("items") or []:
            row = dict(j)
            row["company_url"] = company_url(row.get("company_alias"), row.get("company_id"))
            row["job_url"] = f"{SITE_URL}/job/{row.get('code')}" if row.get("code") else ""
            jobs.append(row)
        log(f"Fetched page {page}/{total_pages}: {len(result.get('items') or [])} jobs, total collected={len(jobs)}", log_path)
        if page < total_pages:
            time.sleep(DELAY_BETWEEN_JOB_PAGES)

    companies: dict[str, dict[str, Any]] = {}
    for j in jobs:
        key = str(j.get("company_id") or j.get("company_name") or "")
        if not key:
            continue
        c = companies.setdefault(key, {
            "company_id": j.get("company_id"),
            "company_name": j.get("company_name") or "",
            "company_alias": j.get("company_alias") or "",
            "company_url": j.get("company_url") or "",
            "address_examples": [],
            "active_jobs_count": 0,
            "job_titles": [],
            "job_urls": [],
            "employee_count_found": None,
            "employee_count_evidence": "",
            "over_50_employees": "unknown",
        })
        c["active_jobs_count"] += 1
        if j.get("address") and j.get("address") not in c["address_examples"]:
            c["address_examples"].append(j.get("address"))
        if j.get("title") and j.get("title") not in c["job_titles"]:
            c["job_titles"].append(j.get("title"))
        if j.get("job_url") and j.get("job_url") not in c["job_urls"]:
            c["job_urls"].append(j.get("job_url"))

    company_list = list(companies.values())
    log(f"Deduped to {len(company_list)} healthcare companies. Lightly scanning company pages for employee-count evidence.", log_path)
    for idx, c in enumerate(company_list, 1):
        if idx > 1:
            time.sleep(DELAY_BETWEEN_COMPANY_PAGES)
        try:
            count, evidence = employee_evidence(fetch_text(c["company_url"]))
            c["employee_count_found"] = count
            c["employee_count_evidence"] = evidence[:500]
            if count is not None:
                c["over_50_employees"] = "yes" if count >= 50 else "no"
        except urllib.error.HTTPError as e:
            c["employee_count_evidence"] = f"profile fetch HTTP {e.code}"
        except Exception as e:
            c["employee_count_evidence"] = f"profile fetch error: {type(e).__name__}: {e}"
        if idx % 10 == 0 or idx == len(company_list):
            yes = sum(1 for x in company_list[:idx] if x.get("over_50_employees") == "yes")
            log(f"Scanned company {idx}/{len(company_list)}; confirmed 50+ so far={yes}", log_path)

    output = {
        "source": "Zangia public GraphQL searchJobs + public company pages",
        "branch_id": BRANCH_ID,
        "category": "Healthcare / Эрүүл мэнд",
        "total_jobs": len(jobs),
        "unique_companies": len(company_list),
        "confirmed_over_50_companies": sum(1 for c in company_list if c.get("over_50_employees") == "yes"),
        "note": "over_50_employees remains 'unknown' when no public employee-count phrase is visible on the company page.",
        "companies": company_list,
        "jobs": jobs,
    }
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = ["company_name", "company_id", "company_alias", "over_50_employees", "employee_count_found", "active_jobs_count", "company_url", "address_examples", "job_titles", "job_urls", "employee_count_evidence"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for c in company_list:
            row = dict(c)
            row["address_examples"] = "; ".join(row.get("address_examples") or [])
            row["job_titles"] = "; ".join((row.get("job_titles") or [])[:10])
            row["job_urls"] = "; ".join((row.get("job_urls") or [])[:10])
            w.writerow(row)

    log(f"DONE. Jobs={len(jobs)}, unique_companies={len(company_list)}, confirmed_over_50={output['confirmed_over_50_companies']}", log_path)
    print(json.dumps({"status": "done", "json": str(json_path), "csv": str(csv_path), "log": str(log_path), **{k: output[k] for k in ("total_jobs", "unique_companies", "confirmed_over_50_companies")}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
