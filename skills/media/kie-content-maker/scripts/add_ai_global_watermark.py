#!/usr/bin/env python3
"""
Add AI Global watermark logo to top-right corner of any video.
Logo size = 1/10th of video width (10%).
Usage:
    python3 scripts/add_ai_global_watermark.py input_video.mp4 [output_video.mp4]

Adapt LOGO_PATH for other brands.
"""
import sys, os, subprocess

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../social-content/brands/ai-global/assets/logos/watermark-ai-global.png"
)

def add_watermark(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"ERROR: Input video not found: {input_path}")
        return False
    if not os.path.exists(LOGO_PATH):
        print(f"ERROR: Watermark not found: {LOGO_PATH}")
        return False
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_watermarked{ext}"
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", LOGO_PATH,
        "-filter_complex",
        "[1:v]scale='iw/10':-1[logo];[0:v][logo]overlay=W-w-20:20",
        "-c:a", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0 and os.path.exists(output_path):
        print(f"✅ Watermarked: {os.path.basename(output_path)}")
        return True
    else:
        print(f"❌ FFmpeg error: {result.stderr[:500]}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: add_ai_global_watermark.py input.mp4 [output.mp4]")
        sys.exit(1)
    success = add_watermark(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.exit(0 if success else 1)
