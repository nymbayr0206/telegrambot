#!/usr/bin/env python3
"""KIE ElevenLabs TTS wrapper for Hermes command TTS provider.

Usage: python3 kie_elevenlabs_tts.py <input_text_path> <output_audio_path> <voice> <model>

Reads text from a temp file, submits to KIE.ElevenLabs API via marketplace endpoint,
polls until complete, downloads the result to output_path.

Requires: KIE_API_KEY env var, Python 3 stdlib only (no extra deps).
SSL: Uses unverified context (required on this server).

Available voices (confirmed working): Rachel, Lily, Sarah, Alice
Models: elevenlabs/text-to-dialogue-v3 (dialogue[] format), elevenlabs/text-to-speech-turbo-2-5, elevenlabs/text-to-speech-multilingual-v2
"""
import sys, json, os, time, urllib.request, urllib.error, ssl

POLL_INTERVAL = 3       # seconds between polls
MAX_POLLS = 60          # max polls before timeout
REQUEST_TIMEOUT = 120   # per-request timeout

# This server has SSL cert issues with KIE API; unverified context is required
SSL_CTX = ssl._create_unverified_context()


def main():
    if len(sys.argv) < 4:
        print("Usage: kie_elevenlabs_tts.py <input_path> <output_path> <voice> [model]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    voice = sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "elevenlabs/text-to-speech-turbo-2-5"

    # Read input text
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("ERROR: Empty input text", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("KIE_API_KEY", "")
    if not api_key:
        print("ERROR: KIE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Build payload for KIE ElevenLabs via marketplace endpoint
    # For dialogue-v3 model, use dialogue[] array format
    payload = json.dumps({
        "model": model,
        "input": {
            "dialogue": [
                {
                    "text": text,
                    "voice": voice
                }
            ],
            "stability": 0.5
        }
    }).encode("utf-8")

    # Submit task
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, context=SSL_CTX, timeout=REQUEST_TIMEOUT)
        body = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"ERROR submitting TTS task: {e}", file=sys.stderr)
        sys.exit(1)

    task_id = body.get("data", {}).get("taskId") or body.get("data", {}).get("recordId", "")
    if not task_id:
        print(f"ERROR: No task ID in response: {json.dumps(body, indent=2)[:300]}", file=sys.stderr)
        sys.exit(1)

    # Poll until complete
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        preq = urllib.request.Request(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        try:
            presp = urllib.request.urlopen(preq, context=SSL_CTX, timeout=30)
            poll_body = json.loads(presp.read().decode("utf-8"))
            state = poll_body.get("data", {}).get("state", "")

            if state == "success":
                # Parse result URLs from resultJson
                result_json_raw = poll_body.get("data", {}).get("resultJson", "{}")
                if isinstance(result_json_raw, str) and result_json_raw != "{}":
                    result_data = json.loads(result_json_raw)
                    result_urls = result_data.get("resultUrls", [])
                    if result_urls:
                        # Convert to signed download URL
                        dreq = urllib.request.Request(
                            "https://api.kie.ai/api/v1/common/download-url",
                            data=json.dumps({"url": result_urls[0]}).encode(),
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            }
                        )
                        dresp = urllib.request.urlopen(dreq, context=SSL_CTX, timeout=60)
                        dbody = json.loads(dresp.read().decode("utf-8"))
                        signed_url = dbody.get("data", "")
                        if isinstance(signed_url, str) and signed_url.startswith("http"):
                            urllib.request.urlretrieve(signed_url, output_path)
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                print(f"TTS saved to {output_path} ({os.path.getsize(output_path)} bytes)", file=sys.stderr)
                                sys.exit(0)
                            else:
                                print(f"ERROR: Downloaded file is empty or missing at {output_path}", file=sys.stderr)
                                sys.exit(1)

            elif state in ("failed", "error"):
                fail_msg = poll_body.get("data", {}).get("failMsg", json.dumps(poll_body))
                print(f"ERROR: TTS task failed: {fail_msg}", file=sys.stderr)
                sys.exit(1)

            # "waiting" or "generating" — keep polling
        except Exception as e:
            if i == 0:
                print(f"Poll error (will retry): {e}", file=sys.stderr)
            continue

    print("ERROR: TTS task timed out after {MAX_POLLS * POLL_INTERVAL}s", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
