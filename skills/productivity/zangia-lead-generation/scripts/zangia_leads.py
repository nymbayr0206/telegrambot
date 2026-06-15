#!/usr/bin/env python3
"""Generate B2B leads from public Zangia.mn job search data."""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Any

API_URL = "https://new-api.zangia.mn/api/jobs/search"
SITE_URL = "https://www.zangia.mn"


def _fetch_jobs(query: str, page: int, limit: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "page": page, "time": 1}
    if query:
        params["query"] = query
    if extra:
        params.update({k: v for k, v in extra.items() if v is not None and v != ""})
    url = API_URL + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Hermes Zangia lead research (public job search)",
            "Accept": "application/json",
            "Origin": SITE_URL,
            "Referer": f"{SITE_URL}/job/list",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _lead_from_job(job: dict[str, Any]) -> dict[str, Any]:
    company_alias = job.get("company_alias") or ""
    company_id = job.get("company_id")
    job_code = job.get("code") or ""
    company_path = company_alias or str(company_id or "")
    return {
        "company_name": job.get("company_name") or "",
        "company_name_en": job.get("company_name_en") or "",
        "company_id": company_id,
        "company_alias": company_alias,
        "company_url": f"{SITE_URL}/company/{company_path}" if company_path else "",
        "job_title": job.get("title") or "",
        "job_id": job.get("id"),
        "job_code": job_code,
        "job_url": f"{SITE_URL}/job/{job_code}" if job_code else "",
        "contact": job.get("contact") or "",
        "address": job.get("address") or "",
        "salary_phrase": job.get("salary_phrase") or job.get("salary") or "",
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "job_level": job.get("job_level") or "",
        "profession_id": job.get("profession_id"),
        "branch_id": job.get("branch_id"),
        "sort_time": job.get("sort_time") or job.get("time") or "",
        "active_until": job.get("end_on") or "",
    }


def search(args: argparse.Namespace) -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    seen_companies: set[Any] = set()
    extra = {}
    if args.location_id:
        extra["addrId"] = args.location_id
    if args.min_salary:
        extra["salaryMin"] = args.min_salary
    if args.max_salary:
        extra["salaryMax"] = args.max_salary

    for page in range(1, args.pages + 1):
        data = _fetch_jobs(args.query, page=page, limit=args.limit, extra=extra)
        items = data.get("items") or data.get("data", {}).get("items") or []
        for job in items:
            lead = _lead_from_job(job)
            key = lead.get("company_id") or lead.get("company_name")
            if args.dedupe_company and key in seen_companies:
                continue
            seen_companies.add(key)
            leads.append(lead)
        if page < args.pages:
            time.sleep(args.delay)
    return leads


def emit_json(leads: list[dict[str, Any]], args: argparse.Namespace) -> str:
    return json.dumps({"count": len(leads), "query": args.query, "leads": leads}, ensure_ascii=False, indent=2)


def emit_csv(leads: list[dict[str, Any]], _args: argparse.Namespace) -> str:
    fields = [
        "company_name", "company_name_en", "contact", "address", "company_url",
        "job_title", "job_url", "salary_phrase", "job_level", "company_id", "job_code",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for lead in leads:
        writer.writerow(lead)
    return buf.getvalue()


def emit_markdown(leads: list[dict[str, Any]], args: argparse.Namespace) -> str:
    lines = [f"# Zangia leads for: {args.query or '*'}", "", f"Total leads: {len(leads)}", ""]
    for i, lead in enumerate(leads, 1):
        lines.append(f"## {i}. {lead['company_name']}")
        if lead.get("company_name_en"):
            lines.append(f"- English name: {lead['company_name_en']}")
        if lead.get("contact"):
            lines.append(f"- Contact: {lead['contact']}")
        if lead.get("address"):
            lines.append(f"- Address: {lead['address']}")
        lines.append(f"- Open role: {lead['job_title']}")
        if lead.get("salary_phrase"):
            lines.append(f"- Salary: {lead['salary_phrase']}")
        if lead.get("company_url"):
            lines.append(f"- Company: {lead['company_url']}")
        if lead.get("job_url"):
            lines.append(f"- Job source: {lead['job_url']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate leads from public Zangia.mn job postings")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search")
    p.add_argument("--query", "-q", default="", help="Search keyword, Mongolian or English")
    p.add_argument("--pages", type=int, default=1, help="Pages to fetch; keep small")
    p.add_argument("--limit", type=int, default=20, help="Results per page")
    p.add_argument("--delay", type=float, default=1.0, help="Delay between pages")
    p.add_argument("--no-dedupe-company", dest="dedupe_company", action="store_false", help="Keep multiple jobs from same company")
    p.add_argument("--location-id", type=int, default=None)
    p.add_argument("--min-salary", type=int, default=None)
    p.add_argument("--max-salary", type=int, default=None)
    p.add_argument("--format", choices=["json", "csv", "markdown"], default="json")
    p.add_argument("--output", default="", help="Optional output file path")

    args = parser.parse_args()
    if args.command == "search":
        leads = search(args)
        if args.format == "json":
            out = emit_json(leads, args)
        elif args.format == "csv":
            out = emit_csv(leads, args)
        else:
            out = emit_markdown(leads, args)
        if args.output:
            with open(args.output, "w", encoding="utf-8", newline="") as f:
                f.write(out)
            print(json.dumps({"status": "written", "path": args.output, "count": len(leads)}, ensure_ascii=False))
        else:
            print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
