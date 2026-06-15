#!/usr/bin/env python3
"""
KIE GPT Image 2 Carousel Generator — Generic Template
Generate N slides, poll for completion, download via signed URL, save locally.

Usage:
  python3 generate_kie_carousel.py                    # all defaults
  python3 generate_kie_carousel.py --slides 4 --model gpt-image-2-text-to-image

Environment:
  KIE_API_KEY  — required, set in /opt/data/.env
"""
import json, os, sys, time, urllib.request, urllib.error, ssl

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/kie-carousel")
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")
if not KIE_API_KEY:
    env_path = "/opt/data/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("KIE_API_KEY="):
                    KIE_API_KEY = line.split("=", 1)[1].strip().strip("\"'")
                    break
if not KIE_API_KEY:
    print("ERROR: KIE_API_KEY not set"); sys.exit(1)

# ── Define your slides here ──────────────────────────────────────────
BRAND_PROMPT = "Create ONE separate 1:1 square social media carousel slide, not a collage..."

SLIDES = [
    {"slide": 1, "ribbon": "1/4", "headline": "Title 1", "body": "Body text 1", "visual": "Visual concept"},
    {"slide": 2, "ribbon": "2/4", "headline": "Title 2", "body": "Body text 2", "visual": "Visual concept"},
]

# ── API helpers ──────────────────────────────────────────────────────
def create_task(slide):
    prompt = f"{BRAND_PROMPT}\n\nSlide number ribbon text: \"{slide['ribbon']}\".\nMain headline:\"{slide['headline']}\"\nBody:\"{slide['body']}\"\nVisual: {slide['visual']}"
    payload = json.dumps({"model": "gpt-image-2-text-to-image", "input": {"prompt": prompt}}).encode()
    req = urllib.request.Request("https://api.kie.ai/api/v1/jobs/createTask", data=payload,
        headers={"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=120) as resp:
        data = json.loads(resp.read())
        return data.get("data", {}).get("taskId") or data.get("taskId", "")

def poll_task(task_id, max_attempts=60, delay=10):
    url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    for i in range(1, max_attempts + 1):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KIE_API_KEY}"})
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=30) as resp:
            record = json.loads(resp.read())
        state = record.get("data", {}).get("state", "")
        if state == "success":
            return record
        if state == "failed":
            print(f"  Failed after {i*delay}s"); return None
        print(f"  Poll {i}/{max_attempts} — {state}"); time.sleep(delay)
    print(f"  TIMEOUT"); return None

def get_download_url(kie_url):
    """KIE download-url returns {"data": "<signed-url-string>"} — NOT a nested object."""
    payload = json.dumps({"url": kie_url}).encode()
    req = urllib.request.Request("https://api.kie.ai/api/v1/common/download-url", data=payload,
        headers={"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60) as resp:
        body = json.loads(resp.read())
        signed = body.get("data", "")
        return signed if isinstance(signed, str) and signed.startswith("http") else None

def extract_kie_url(record):
    """Parse resultJson — which is a stringified JSON, not a dict."""
    raw = record.get("data", {}).get("resultJson", "{}")
    result_data = json.loads(raw) if isinstance(raw, str) else raw
    urls = result_data.get("resultUrls", [])
    return urls[0] if urls else None

# ── Main ─────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []
    for slide in SLIDES:
        print(f"\n--- Slide {slide['slide']}/{len(SLIDES)} ---")
        task_id = create_task(slide)
        if not task_id: results.append({"slide": slide["slide"], "status": "create_failed"}); continue
        print(f"  Task: {task_id}")
        record = poll_task(task_id)
        if not record: results.append({"slide": slide["slide"], "status": "poll_failed"}); continue
        kie_url = extract_kie_url(record)
        if not kie_url: results.append({"slide": slide["slide"], "status": "no_url"}); continue
        dl_url = get_download_url(kie_url)
        if not dl_url: dl_url = kie_url  # fallback — may 403
        out = os.path.join(OUTPUT_DIR, f"slide-0{slide['slide']}.jpg")
        req = urllib.request.Request(dl_url)
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=120) as resp:
            with open(out, "wb") as f: f.write(resp.read())
        print(f"  ✅ {out} ({os.path.getsize(out)//1024} KB)")
        results.append({"slide": slide["slide"], "status": "success", "file": out})
        if slide["slide"] < len(SLIDES): time.sleep(3)
    print(f"\n✅ {sum(1 for r in results if r['status']=='success')}/{len(SLIDES)}")

if __name__ == "__main__":
    main()
