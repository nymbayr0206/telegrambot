#!/usr/bin/env python3
"""
Postly comparison slide compositor — two-stage carousel slide.
Stage 1: KIE generates text-free background (two panels).
Stage 2: This script overlays brand logo, text, prices, and icons.

Usage:
  python3 postly-comparison-slide-composer.py <background.png> [--output output.png]

Dependencies: Pillow (PIL), font files as configured below.
"""

from PIL import Image, ImageDraw, ImageFont
import os, sys

# === CONFIG ===
LOGO_PATH = "/opt/data/social-content/brands/postly/assets/logos/postly-logo-turquoise-p.jpg"
FONT_BOLD = "/opt/data/fonts/Nunito-Bold.ttf"
FONT_REG = "/opt/data/fonts/Nunito-Regular.ttf"
OUTPUT = "/opt/data/social-content/brands/postly/drafts/comparison-slide-final.png"

# Brand colors (RGBA)
TURQUOISE = (92, 212, 192)
AQUA = (76, 191, 221)
DEEP_TEAL = (6, 59, 74)
WHITE = (255, 255, 255)
DARK_RED = (140, 30, 40)
SOFT_SKY = (234, 251, 255)

# === FONT LOAD WITH VERIFICATION ===
def load_font(path, size):
    try:
        font = ImageFont.truetype(path, size)
        print(f"  Font loaded: {path}")
        return font
    except Exception as e:
        print(f"  Font error ({path}): {e}")
        # Known-good fallback
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        print(f"  Falling back to: {fallback}")
        return ImageFont.truetype(fallback, size)

def compose(background_path, output_path):
    # Load background
    bg = Image.open(background_path).convert("RGBA")
    W, H = bg.size
    print(f"Background: {W}x{H}")

    # Font sizes (relative to image width)
    sz_large = int(W * 0.055)
    sz_medium = int(W * 0.038)
    sz_small = int(W * 0.032)
    sz_tiny = int(W * 0.025)

    f_large = load_font(FONT_BOLD, sz_large)
    f_med = load_font(FONT_BOLD, sz_medium)
    f_small = load_font(FONT_BOLD, sz_small)
    f_reg_small = load_font(FONT_REG, sz_small)
    f_tiny = load_font(FONT_REG, sz_tiny)

    # Create overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # === 1. BRAND LOGO (top-right) ===
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_w = int(W * 0.18)
        logo_h = int(logo_w * logo.height / logo.width)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        margin = int(W * 0.04)
        logo_x = W - logo_w - margin
        logo_y = margin
        # If JPG (no alpha), paste without mask
        if logo.mode == "RGBA" and logo.getextrema()[3] != 255:
            overlay.paste(logo, (logo_x, logo_y), logo)
        else:
            overlay.paste(logo, (logo_x, logo_y))
        print(f"  Logo: ({logo_x}, {logo_y}) {logo_w}x{logo_h}")
    except Exception as e:
        print(f"  Logo SKIPPED (error: {e})")

    # === 2. CENTER DIVIDER ===
    cx = W // 2
    draw.line([(cx, int(H * 0.15)), (cx, int(H * 0.95))], fill=(200, 200, 200, 128), width=3)

    # === 3. TITLES ===
    lt_y = int(H * 0.04)
    # LEFT title bar
    title_bg_l = Image.new("RGBA", (int(W * 0.42), int(H * 0.08)), DEEP_TEAL + (200,))
    overlay.paste(title_bg_l, (int(W * 0.04), lt_y - 5), title_bg_l)
    draw.text((int(W * 0.16), lt_y), "WITHOUT", fill=WHITE, font=f_large)

    # RIGHT title bar
    title_bg_r = Image.new("RGBA", (int(W * 0.44), int(H * 0.08)), TURQUOISE + (220,))
    overlay.paste(title_bg_r, (int(W * 0.54), lt_y - 5), title_bg_r)
    draw.text((int(W * 0.62), lt_y), "WITH POSTLY", fill=WHITE, font=f_large)

    # === 4. LEFT PANEL (WITHOUT: roles + prices) ===
    left_roles = [
        ("📊 Судлаач", "1,000,000₮"),
        ("✏️ Контент зохиолч", "1,500,000₮"),
        ("🎨 Дизайнер", "1,500,000₮"),
        ("🎬 Видео редактор", "1,500,000₮"),
    ]
    l_start = int(H * 0.17)
    for i, (role, price) in enumerate(left_roles):
        y = l_start + i * int(H * 0.17)
        # Icon circle
        r = int(W * 0.035)
        draw.ellipse([int(W * 0.10) - r, y + r - r, int(W * 0.10) + r, y + r + r],
                     fill=(220, 100, 100, 150), outline=(255, 150, 150, 100), width=2)
        draw.text((int(W * 0.18), y - 2), role, fill=WHITE, font=f_small)
        # Price capsule
        pb = draw.textbbox((0, 0), price, font=f_reg_small)
        pw = pb[2] - pb[0] + 16
        ph = pb[3] - pb[1] + 8
        pc = Image.new("RGBA", (pw, ph), (180, 60, 60, 200))
        overlay.paste(pc, (int(W * 0.18), y + int(H * 0.045)), pc)
        draw.text((int(W * 0.18) + 8, y + int(H * 0.045) + 2), price, fill=WHITE, font=f_reg_small)

    # LEFT total bar
    lty = int(H * 0.88)
    ltb = Image.new("RGBA", (int(W * 0.44), int(H * 0.08)), DARK_RED + (220,))
    overlay.paste(ltb, (int(W * 0.03), lty), ltb)
    total_txt = "НИЙТ: 4 ХҮН = 5,500,000₮/сар"
    tb = draw.textbbox((0, 0), total_txt, font=f_med)
    tw = tb[2] - tb[0]
    draw.text((int(W * 0.03) + int(W * 0.22) - tw // 2, lty + 5), total_txt, fill=WHITE, font=f_med)

    # === 5. RIGHT PANEL (WITH POSTLY: AI agents) ===
    r_start = int(H * 0.17)
    agents = [
        ("🤖 AI Marketing Agent", "Researcher, Content, Design, Video"),
        ("🤖 AI Sales Agent", "Prospector, SMS, Email"),
    ]
    for i, (agent, desc) in enumerate(agents):
        y = r_start + i * int(H * 0.23)
        ir = int(W * 0.05)
        cx_icon = cx + int(W * 0.10)
        draw.ellipse([cx_icon - ir, y + ir - 5, cx_icon + ir, y + ir * 3 - 5],
                     fill=(100, 200, 200, 180), outline=TURQUOISE, width=3)
        draw.text((int(W * 0.58), y), agent, fill=DEEP_TEAL, font=f_small)
        draw.text((int(W * 0.58), y + int(H * 0.055)), desc, fill=(80, 80, 80), font=f_tiny)

    # RIGHT price bar
    rpy = int(H * 0.79)
    rpb = Image.new("RGBA", (int(W * 0.44), int(H * 0.13)), TURQUOISE + (230,))
    overlay.paste(rpb, (int(W * 0.53), rpy), rpb)
    draw.text((int(W * 0.55), rpy + 5), "Зөвхөн", fill=WHITE, font=f_small)
    draw.text((int(W * 0.55), rpy + int(H * 0.055)), "390,000₮/сар", fill=WHITE, font=f_large)

    # === 6. BOTTOM TAGLINE ===
    tagline = "1 SMM-ийн цалингаар → complete AI team ⚡"
    tgb = draw.textbbox((0, 0), tagline, font=f_small)
    tgw = tgb[2] - tgb[0]
    draw.text((W // 2 - tgw // 2, int(H * 0.955)), tagline, fill=(150, 150, 150), font=f_small)

    # === FINAL COMPOSITE ===
    result = Image.alpha_composite(bg, overlay)
    result = result.convert("RGB")
    result = result.resize((1080, 1080), Image.LANCZOS)
    result.save(output_path, quality=95)
    print(f"Saved: {output_path} (1080x1080)")

if __name__ == "__main__":
    bg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__) or ".",
        "../../../../../drafts/comparison-bg.png"
    )
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT
    if not os.path.exists(bg_path):
        print(f"Background not found: {bg_path}")
        print("Usage: python3 postly-comparison-slide-composer.py <background.png> [output.png]")
        sys.exit(1)
    compose(bg_path, out_path)
