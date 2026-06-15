#!/usr/bin/env python3
"""
Reusable KIE GPT Image 2 Image-to-Image workflow.
Usage: python3 workflow.py <template_path> <aspect_ratio> "<prompt>"

Uploads template to tmpfiles.org, submits to KIE, downloads result.
"""

import json, urllib.request, time, subprocess, sys, os

API_KEY = os.environ.get("KIE_API_KEY", "")
KIE_BASE = "https://api.kie.ai/api/v1/jobs"
WEBHOOK_URL = "https://hook.eu1.make.com/xb37pnxrn674ngf8ixurm4eoj1pdf21e"

def upload_template(filepath):
    """Upload image to tmpfiles.org, return public download URL."""
    result = subprocess.run(
        ["curl", "-s", "-F", f"file=@{filepath}", "https://tmpfiles.org/api/v1/upload"],
        capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise Exception(f"Upload failed: {result.stderr}")
    data = json.loads(result.stdout)
    url_path = data["data"]["url"]  # e.g. https://tmpfiles.org/wXyZabc/file.jpg
    hash_part = url_path.rstrip('/').split('/')[-2]
    filename = url_path.rstrip('/').split('/')[-1]
    return f"https://tmpfiles.org/dl/{hash_part}/{filename}"

def create_task(model, inp):
    req = urllib.request.Request(
        f"{KIE_BASE}/createTask",
        data=json.dumps({"model": model, "input": inp}).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["data"]["taskId"]

def wait_for_result(task_id, timeout=300):
    """Poll until task completes, return result image URL."""
    start = time.time()
    while time.time() - start < timeout:
        req = urllib.request.Request(
            f"{KIE_BASE}/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())["data"]
        state = d["state"]
        if state == "success":
            rj = json.loads(d.get("resultJson", "{}"))
            urls = rj.get("resultUrls", [])
            return urls[0] if urls else rj.get("url", "")
        if state in ("fail", "failed"):
            raise Exception(f"Task failed: {d.get('failMsg', 'unknown')}")
        print(f"  {state} ({int(time.time()-start)}s)")
        time.sleep(10)
    raise TimeoutError(f"Task {task_id} timed out")

def download_result(url, output_path):
    """Download generated image using curl (urllib gets 403)."""
    r = subprocess.run(["curl", "-s", url, "-o", output_path],
                      capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise Exception(f"Download failed: {r.stderr}")
    return os.path.getsize(output_path)

def send_to_make(image_path, caption, poster_number=1, total=4):
    """Send poster to Make.com webhook."""
    r = subprocess.run(["curl", "-s", "-X", "POST",
        "-F", f"image=@{image_path};type=image/png",
        "-F", f"caption={caption}",
        "-F", f"poster_number={poster_number}",
        "-F", f"total_posters={total}",
        "-F", "source=kie_gpt_image_2_img2img",
        "-F", "brand=AI Global",
        WEBHOOK_URL], capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: workflow.py <template_path> <aspect_ratio> \"<prompt>\" [output.png]")
        print("Example: workflow.py temp1.jpg 1:1 \"On this background...\"")
        sys.exit(1)
    
    template_path = sys.argv[1]
    aspect = sys.argv[2]
    prompt = sys.argv[3]
    output = sys.argv[4] if len(sys.argv) > 4 else "output.png"
    
    if not API_KEY:
        print("Error: KIE_API_KEY not set")
        sys.exit(1)
    
    print(f"1. Uploading template: {template_path}")
    template_url = upload_template(template_path)
    print(f"   URL: {template_url}")
    
    print(f"2. Submitting image-to-image task...")
    task_id = create_task("gpt-image-2-image-to-image", {
        "input_urls": [template_url],
        "prompt": prompt,
        "aspect_ratio": aspect,
        "resolution": "1K"
    })
    print(f"   Task: {task_id}")
    
    print(f"3. Waiting for result...")
    result_url = wait_for_result(task_id)
    print(f"   URL: {result_url[:80]}...")
    
    print(f"4. Downloading...")
    size = download_result(result_url, output)
    print(f"   Saved: {output} ({size/1024:.0f} KB)")
    
    print("Done!")
