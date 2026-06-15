#!/usr/bin/env python3
"""KIE ElevenLabs Multi-Voice Dialogue TTS wrapper.

Generates a single audio file from multiple dialogue turns, each with 
a different voice. Uses elevenlabs/text-to-dialogue-v3 model.

Usage:
    python3 kie_elevenlabs_multivoice.py <dialogue_json> <output_path> [model]

Where <dialogue_json> is a JSON file containing:
    {
      "dialogue": [
        {"text": "Hello", "voice": "Lily"},
        {"text": "Hi there!", "voice": "Sarah"},
        {"text": "Let me explain...", "voice": "Lily"}
      ],
      "stability": 0.5   (optional, default 0.5)
    }

Each entry in "dialogue" is a turn with:
  - text (string, required) — text to speak
  - voice (string, required) — ElevenLabs voice NAME (not UUID)

Available voices for dialogue-v3: Lily (female), Sarah (female), Alice (female)
Emotion tags work in text: [excited], [happy], [sad], [whisper], [angry]

Environment: KIE_API_KEY must be set.
Output: MP3 file written to <output_path>.
"""
import sys, json, os, time, urllib.request, urllib.error, ssl

# SSL workaround for this server
ssl_ctx = ssl._create_unverified_context()


def submit_task(payload: dict) -> str:
    """Submit a TTS task to KIE and return task_id."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=body,
        headers={
            "Authorization": f"Bearer {os.environ['KIE_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=120)
    result = json.loads(resp.read().decode("utf-8"))
    task_id = (
        result.get("data", {}).get("taskId")
        or result.get("data", {}).get("recordId", "")
    )
    if not task_id:
        raise RuntimeError(f"No task ID in response: {result}")
    return task_id


def poll_task(task_id: str, max_attempts: int = 60, poll_interval: float = 3.0) -> str:
    """Poll task status until success or failure. Returns output URL on success."""
    poll_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    for _ in range(max_attempts):
        time.sleep(poll_interval)
        try:
            preq = urllib.request.Request(
                poll_url,
                headers={"Authorization": f"Bearer {os.environ['KIE_API_KEY']}"},
            )
            presp = urllib.request.urlopen(preq, context=ssl_ctx, timeout=30)
            body = json.loads(presp.read().decode("utf-8"))
            state = body.get("data", {}).get("state", "")
        except Exception:
            continue

        if state == "success":
            result_json_raw = body.get("data", {}).get("resultJson", "{}")
            if isinstance(result_json_raw, str):
                result_data = json.loads(result_json_raw)
            else:
                result_data = result_json_raw
            urls = result_data.get("resultUrls", [])
            if urls:
                return urls[0]
            raise RuntimeError(f"No resultUrls in success response: {body}")
        elif state in ("failed", "error"):
            raise RuntimeError(f"Task failed: {body}")
        # else still generating/waiting — keep polling

    raise TimeoutError(f"Task {task_id} did not complete after {max_attempts * poll_interval}s")


def download_signed(kie_url: str, output_path: str):
    """Convert KIE temp URL to signed download URL and download."""
    # Get signed URL
    dreq = urllib.request.Request(
        "https://api.kie.ai/api/v1/common/download-url",
        data=json.dumps({"url": kie_url}).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['KIE_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    dresp = urllib.request.urlopen(dreq, context=ssl_ctx, timeout=60)
    dbody = json.loads(dresp.read().decode("utf-8"))
    signed_url = dbody["data"]  # string, not dict
    if not isinstance(signed_url, str) or not signed_url.startswith("http"):
        raise RuntimeError(f"Invalid signed URL: {signed_url}")

    # Download
    urllib.request.urlretrieve(signed_url, output_path)
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("Downloaded file is empty or missing")


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: kie_elevenlabs_multivoice.py <dialogue_json> <output_path> [model]",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "elevenlabs/text-to-dialogue-v3"

    if "KIE_API_KEY" not in os.environ:
        print("ERROR: KIE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Read dialogue JSON
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dialogue_entries = data.get("dialogue", [])
    if not dialogue_entries:
        print("ERROR: 'dialogue' array is empty or missing in input JSON", file=sys.stderr)
        sys.exit(1)

    stability = data.get("stability", 0.5)

    # Build payload
    payload = {
        "model": model,
        "input": {
            "dialogue": dialogue_entries,
            "stability": stability,
        },
    }

    # Submit
    print(f"Submitting {len(dialogue_entries)} dialogue turns to {model}...", file=sys.stderr)
    task_id = submit_task(payload)
    print(f"Task ID: {task_id}", file=sys.stderr)

    # Poll
    print("Polling for completion...", file=sys.stderr)
    kie_url = poll_task(task_id)
    print(f"Got output URL, downloading...", file=sys.stderr)

    # Download
    download_signed(kie_url, output_path)
    size = os.path.getsize(output_path)
    print(f"Saved to {output_path} ({size} bytes)", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
