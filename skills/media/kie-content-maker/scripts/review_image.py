#!/usr/bin/env python3
"""
AI Global Image Review Agent
Uses OpenAI GPT-4o vision to review KIE-generated carousel images
for professionalism, correctness, and brand compliance.

Usage:
    python3 review_image.py /path/to/image.jpg --brand ai-global
    python3 review_image.py /path/to/image.jpg --verbose
    python3 review_image.py /path/to/image.jpg --json
"""
import os, sys, json, base64, argparse

API_KEY = os.environ.get("OPENAI_API_KEY", "")

REVIEW_PROMPT = """You are an expert graphic design reviewer for AI Global, a Mongolian educational brand (black + gold luxury, Italian minimal style). Review this carousel image and provide a structured assessment.

CHECKLIST:
1. BRAND LOGO: Is the AI Global logo present and correctly placed (top-right)? Is it clear and not pixelated?
2. PERSON PHOTO: Is the person photo properly placed with smooth rounded corners? No sharp edges, no overlapping images?
3. TEXT: Is all text in correct Mongolian Cyrillic? No misspellings? Is the student's name visible?
4. BACKGROUND: Is the background clean? No strange artifacts, no blurry areas?
5. OVERALL: Does it look professional for a luxury educational brand? Any overlapping elements? Any pixelation?

RESPOND IN THIS STRICT JSON FORMAT (no other text):
{
  "pass": true/false,
  "score": "A/B/C/D/F",
  "issues": ["issue1", "issue2"],
  "fix_advice": ["fix1", "fix2"],
  "summary": "one sentence summary in Mongolian"
}"""

def encode_image(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def review_image(image_path):
    if not os.path.exists(image_path):
        return {"pass": False, "error": f"File not found: {image_path}"}
    
    base64_image = encode_image(image_path)
    
    import requests
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": REVIEW_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        return {"pass": False, "error": f"API error: {resp.status_code}"}
    
    content = resp.json()['choices'][0]['message']['content']
    try:
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0].strip()
        elif '{' in content:
            json_str = content[content.index('{'):content.rindex('}')+1]
        else:
            json_str = content
        return json.loads(json_str)
    except:
        return {"pass": False, "error": f"Parse failed: {content[:200]}"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image_path', help='Path to image file')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    
    if not API_KEY:
        # Try loading from .env
        env_path = "/opt/data/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENAI_API_KEY="):
                        os.environ['OPENAI_API_KEY'] = line.split("=", 1)[1].strip().strip("\"'")
                        break
        global API_KEY
        API_KEY = os.environ.get("OPENAI_API_KEY", "")
    
    review = review_image(args.image_path)
    
    if args.json:
        print(json.dumps(review, indent=2, ensure_ascii=False))
        return
    
    icons = {'A': 'PASS', 'B': 'MINOR', 'C': 'REVISE', 'D': 'MAJOR', 'F': 'FAIL'}
    icon = icons.get(review.get('score', 'F'), '?')
    
    if review.get('pass'):
        print(f"{icon} ({review.get('score', '?')}) — {review.get('summary', '')}")
    else:
        print(f"{icon} ({review.get('score', '?')}) — {review.get('summary', '')}")
    
    if review.get('issues'):
        print(f"\nIssues ({len(review['issues'])}):")
        for i, issue in enumerate(review['issues'], 1):
            print(f"  {i}. {issue}")
    
    if review.get('fix_advice'):
        print(f"\nFix advice:")
        for i, fix in enumerate(review['fix_advice'], 1):
            print(f"  {i}. {fix}")
    
    sys.exit(0 if review.get('pass') else 1)

if __name__ == '__main__':
    main()
