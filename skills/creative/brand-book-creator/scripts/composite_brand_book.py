#!/usr/bin/env python3
"""
Brand Book Composite Builder

Takes: logo image + 3 background images → outputs one large brand book composite.
Usage: python3 composite_brand_book.py <logo.png> <bg_edu.jpg> <bg_leader.jpg> <bg_sales.jpg> <output.jpg> [--title "Brand Name"] [--colors #HEX1 #HEX2 #HEX3 #HEX4] [--font-head "Headline Font"] [--font-body "Body Font"]
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ── Layout constants ──────────────────────────────────────────────────────
CANVAS_W = 2400
CANVAS_H = 3200
MARGIN = 60
PAD = 30

# Section positions (y-coordinates)
Y_HEADER = 40
Y_LOGO = 240
Y_COLORS = 700
Y_FONTS = 1000
Y_BGS = 1200
BG_H = 1800  # height for the 3 backgrounds area (canvas bottom = 3200)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (245, 245, 245)
ACCENT_LINE = (200, 200, 200)

SWATCH_SIZE = 80
FONT_SIZE_HEADER = 52
FONT_SIZE_SECTION = 36
FONT_SIZE_LABEL = 28
FONT_SIZE_HEX = 22
FONT_SIZE_BODY = 30
FONT_SIZE_BG_LABEL = 24


def hex_to_rgb(hex_str: str) -> tuple:
    """#RRGGBB or RRGGBB → (R, G, B)"""
    h = hex_str.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try common font paths, fall back to default."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/opt/data/fonts/Nunito-Bold.ttf",
        "/opt/data/fonts/Nunito-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius: int, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def composite_brand_book(
    logo_path: str,
    bg_edu_path: str,
    bg_leader_path: str,
    bg_sales_path: str,
    output_path: str,
    brand_name: str = "BRAND NAME",
    colors: list = None,
    font_head: str = "Montserrat Bold",
    font_body: str = "Inter Regular",
):
    if colors is None:
        colors = ["#2C3E50", "#3498DB", "#E74C3C", "#ECF0F1"]

    # ── Create canvas ─────────────────────────────────────────────────
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), WHITE)
    draw = ImageDraw.Draw(canvas)

    # Fonts
    font_big = load_font(FONT_SIZE_HEADER)
    font_section = load_font(FONT_SIZE_SECTION)
    font_label = load_font(FONT_SIZE_LABEL)
    font_hex = load_font(FONT_SIZE_HEX)
    font_body_small = load_font(FONT_SIZE_BODY)
    font_bg_label = load_font(FONT_SIZE_BG_LABEL)

    # ── 1. Header ─────────────────────────────────────────────────────
    draw.text((CANVAS_W // 2, Y_HEADER), "BRAND BOOK", fill=DARK_GRAY, font=font_big, anchor="mt")
    
    # Accent line under header
    line_y = Y_HEADER + 60
    draw.line([(CANVAS_W // 2 - 200, line_y), (CANVAS_W // 2 + 200, line_y)], fill=ACCENT_LINE, width=2)
    
    # Brand name
    draw.text((CANVAS_W // 2, line_y + 30), brand_name.upper(), fill=BLACK, font=font_section, anchor="mt")

    # ── 2. Logo ────────────────────────────────────────────────────────
    try:
        logo = Image.open(logo_path).convert("RGBA")
        # Resize logo to fit max 400px wide, 300px tall
        lw, lh = logo.size
        max_lw, max_lh = 400, 300
        scale = min(max_lw / lw, max_lh / lh, 1.0)
        logo = logo.resize((int(lw * scale), int(lh * scale)), Image.LANCZOS)
        logo_x = (CANVAS_W - logo.width) // 2
        logo_y = Y_LOGO
        canvas.paste(logo, (logo_x, logo_y), logo)
    except Exception as e:
        draw.text((MARGIN, Y_LOGO), f"[Logo load error: {e}]", fill=(200, 0, 0), font=font_label)

    # ── 3. Color palette ──────────────────────────────────────────────
    colors_y = Y_COLORS
    draw.text((MARGIN, colors_y), "COLOR PALETTE", fill=DARK_GRAY, font=font_section)
    colors_y += 60

    swatch_gap = (CANVAS_W - 2 * MARGIN - len(colors) * SWATCH_SIZE) // max(len(colors) - 1, 1)
    for i, c in enumerate(colors):
        x = MARGIN + i * (SWATCH_SIZE + swatch_gap)
        rgb = hex_to_rgb(c)
        # Draw swatch circle
        draw.ellipse(
            [(x, colors_y), (x + SWATCH_SIZE, colors_y + SWATCH_SIZE)],
            fill=rgb,
            outline=GRAY,
            width=2,
        )
        # Hex label under swatch
        label_w = draw.textbbox((0, 0), c, font=font_hex)[2]
        draw.text(
            (x + SWATCH_SIZE // 2, colors_y + SWATCH_SIZE + 8),
            c.upper(),
            fill=DARK_GRAY,
            font=font_hex,
            anchor="mt",
        )

    # ── 4. Font suggestions ───────────────────────────────────────────
    fonts_y = Y_FONTS
    draw.text((MARGIN, fonts_y), "FONT SUGGESTIONS", fill=DARK_GRAY, font=font_section)
    fonts_y += 55

    draw.text((MARGIN + 20, fonts_y), f"Headline:  {font_head}", fill=BLACK, font=font_label)
    fonts_y += 40
    draw.text((MARGIN + 20, fonts_y), f"Body:      {font_body}", fill=BLACK, font=font_label)

    # ── 5. Three backgrounds ──────────────────────────────────────────
    bg_y = Y_BGS
    draw.text((MARGIN, bg_y), "POSTER BACKGROUNDS", fill=DARK_GRAY, font=font_section)
    bg_y += 55

    bg_w = (CANVAS_W - 2 * MARGIN - 2 * PAD) // 3
    available_h = CANVAS_H - bg_y - MARGIN
    bg_h = min(1400, available_h)

    bg_defs = [
        (bg_edu_path, "Educational", "🎓"),
        (bg_leader_path, "Industry Leader", "🏆"),
        (bg_sales_path, "Sales & Promotion", "🛒"),
    ]

    for i, (img_path, label, icon) in enumerate(bg_defs):
        x = MARGIN + i * (bg_w + PAD)
        try:
            bg_img = Image.open(img_path).convert("RGB")
            # Crop to fit aspect ratio
            bg_img = img_fit(bg_img, bg_w, bg_h)
            canvas.paste(bg_img, (x, bg_y))
        except Exception as e:
            draw_rounded_rect(
                draw, (x, bg_y, x + bg_w, bg_y + bg_h), radius=12, fill=LIGHT_GRAY
            )
            draw.text(
                (x + bg_w // 2, bg_y + bg_h // 2),
                f"[{label} not found]",
                fill=GRAY,
                font=font_label,
                anchor="mm",
            )

        # Label under each background
        label_full = f"{icon} {label}"
        draw.text(
            (x + bg_w // 2, bg_y + bg_h + 12),
            label_full,
            fill=DARK_GRAY,
            font=font_bg_label,
            anchor="mt",
        )

    # ── Save ───────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path, "JPEG", quality=92)
    print(f"Brand book saved to: {output_path}")


def img_fit(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Crop and resize image to fill target dimensions."""
    img = img.copy()
    # Scale so it covers target
    scale = max(target_w / img.width, target_h / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    # Center crop
    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


# ── CLI ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a brand-book composite image")
    parser.add_argument("logo", help="Path to brand logo image (PNG with transparency preferred)")
    parser.add_argument("bg_edu", help="Path to educational background image")
    parser.add_argument("bg_leader", help="Path to industry-leader background image")
    parser.add_argument("bg_sales", help="Path to sales/promotion background image")
    parser.add_argument("output", help="Output JPEG path (e.g. /tmp/brand-book.jpg)")
    parser.add_argument("--title", default="BRAND NAME", help="Brand name text")
    parser.add_argument("--colors", nargs="+", default=["#2C3E50", "#3498DB", "#E74C3C", "#ECF0F1"], help="Color hex codes (3-4 values)")
    parser.add_argument("--font-head", default="Montserrat Bold", help="Headline font name")
    parser.add_argument("--font-body", default="Inter Regular", help="Body font name")

    args = parser.parse_args()
    composite_brand_book(
        args.logo,
        args.bg_edu,
        args.bg_leader,
        args.bg_sales,
        args.output,
        brand_name=args.title,
        colors=args.colors,
        font_head=args.font_head,
        font_body=args.font_body,
    )
