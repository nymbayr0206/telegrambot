#!/usr/bin/env python3
"""
Supernova carousel Pillow overlay v3 — two-stage pattern.
Stage 1: KIE generates a text-free background.
Stage 2: This script composites brand logo, colors, text, phone, frames.

DEPENDENCIES:
  - Pillow (PIL) — install via: uv pip install Pillow
  - DejaVu fonts at /usr/share/fonts/truetype/dejavu/ (DejaVuSans-Bold.ttf, DejaVuSans.ttf)
    for Cyrillic/Mongolian text rendering. Falls back to default font if missing,
    but output quality will be poor.

LOGO FORMAT REQUIREMENT:
  The --logo must be a PNG with transparency (alpha channel). The script calls
  .convert("RGBA") on the logo, then passes it as a mask in bg.paste(). JPG images
  lack alpha and will paste as opaque rectangles with their background color.
  If only JPG is available, pre-process it:
    - Crop tightly around the logo
    - Create a mask where the background color is transparent
    - Save as PNG

Usage:
  python3 supernova-carousel-overlay-v3.py \
    --background background.png \
    --logo assets/logos/logo.png \
    --slide 1/4 \
    --title "Your title here" \
    --subtitle "Your subtitle here" \
    --output final-slide-01.jpg

Brand colors (from brand-guide.md):
  Red:      #F20B2E (phone, emphasis)
  Blue:     #1768B5 (ribbons, accents)
  Sky blue: #DDEFF8 (background wash)
  Navy:     #071B4D (main text)
  Gray:     #6B6F77 (tagline)
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# Brand colors
RED = (242, 11, 46)
BLUE = (23, 104, 181)
SKY = (221, 239, 248)
NAVY = (7, 27, 77)
GRAY = (107, 111, 119)
WHITE = (255, 255, 255)
BLACK = (31, 41, 55)

# Font paths (server)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def draw_rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle on the image."""
    x1, y1, x2, y2 = bbox
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)


def main():
    parser = argparse.ArgumentParser(description="Supernova carousel overlay")
    parser.add_argument("--background", required=True, help="Text-free background image")
    parser.add_argument("--logo", required=True, help="Brand logo image (PNG with transparency)")
    parser.add_argument("--slide", default="1/4", help="Slide number label (e.g. '1/4')")
    parser.add_argument("--title", default="", help="Main headline text")
    parser.add_argument("--subtitle", default="", help="Subtitle or body text")
    parser.add_argument("--phone", default="Утас: 70000303", help="Phone number text")
    parser.add_argument("--tagline", default="Мэдлэгт дусал нэмэр", help="Top-left tagline")
    parser.add_argument("--output", required=True, help="Output JPEG path")
    parser.add_argument("--colors", default=None, help="JSON with custom color overrides")
    args = parser.parse_args()

    # Open background
    bg = Image.open(args.background).convert("RGBA")
    W, H = bg.size  # should be 1080x1080

    # Create overlay layer
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Load fonts (scale to image size)
    base_size = W // 1080  # scale factor for non-1080 images
    title_size = max(36, int(48 * base_size))
    subtitle_size = max(24, int(32 * base_size))
    tagline_size = max(20, int(26 * base_size))
    phone_size = max(22, int(28 * base_size))
    slide_size = max(28, int(36 * base_size))

    try:
        font_title = ImageFont.truetype(FONT_BOLD, title_size)
        font_subtitle = ImageFont.truetype(FONT_REGULAR, subtitle_size)
        font_tagline = ImageFont.truetype(FONT_BOLD, tagline_size)
        font_phone = ImageFont.truetype(FONT_BOLD, phone_size)
        font_slide = ImageFont.truetype(FONT_BOLD, slide_size)
    except IOError:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        font_phone = ImageFont.load_default()
        font_slide = ImageFont.load_default()

    margin = max(20, int(30 * base_size))

    # 1. Top-left tagline: "Мэдлэгт дусал нэмэр" in navy rounded capsule
    tagline_padding = 12
    bbox_tag = draw.textbbox((0, 0), args.tagline, font=font_tagline)
    tw = bbox_tag[2] - bbox_tag[0] + tagline_padding * 2
    th = bbox_tag[3] - bbox_tag[1] + tagline_padding * 2
    draw.rounded_rectangle(
        (margin, margin, margin + tw, margin + th),
        radius=int(th / 2), fill=NAVY
    )
    draw.text(
        (margin + tagline_padding, margin + tagline_padding),
        args.tagline, fill=WHITE, font=font_tagline
    )

    # 2. Top-right: Brand logo
    logo = Image.open(args.logo).convert("RGBA")
    logo_w = int(180 * base_size)
    logo_h = int(logo_w * logo.height / logo.width)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_x = W - logo_w - margin
    logo_y = margin
    bg.paste(logo, (logo_x, logo_y), logo)

    # 3. Slide number ribbon (left side, below tagline)
    ribbon_y = margin + th + int(20 * base_size)
    ribbon_text = args.slide
    bbox_rib = draw.textbbox((0, 0), ribbon_text, font=font_slide)
    rw = bbox_rib[2] - bbox_rib[0] + 16
    rh = bbox_rib[3] - bbox_rib[1] + 8
    draw.rounded_rectangle(
        (margin, ribbon_y, margin + rw, ribbon_y + rh),
        radius=6, fill=BLUE
    )
    draw.text(
        (margin + 8, ribbon_y + 4),
        ribbon_text, fill=WHITE, font=font_slide
    )

    # 4. Title text (centered or left-aligned, below ribbon)
    title_y = ribbon_y + rh + int(30 * base_size)
    bbox_t = draw.textbbox((0, 0), args.title, font=font_title)
    tw2 = bbox_t[2] - bbox_t[0]
    # Draw title in navy, with possible red emphasis on first word
    title_words = args.title.split(" ", 1)
    if len(title_words) > 1:
        # First word in red, rest in navy
        draw.text((margin, title_y), title_words[0], fill=RED, font=font_title)
        bbox_first = draw.textbbox((margin, title_y), title_words[0], font=font_title)
        fw = bbox_first[2] - bbox_first[0]
        draw.text((margin + fw + 10, title_y), " " + title_words[1], fill=NAVY, font=font_title)
    else:
        draw.text((margin, title_y), args.title, fill=NAVY, font=font_title)

    # 5. Subtitle below title
    if args.subtitle:
        sub_y = title_y + title_size + int(15 * base_size)
        draw.text((margin, sub_y), args.subtitle, fill=GRAY, font=font_subtitle)

    # 6. Bottom-right: Phone capsule
    bbox_ph = draw.textbbox((0, 0), args.phone, font=font_phone)
    ph_padding = 14
    ph_w = bbox_ph[2] - bbox_ph[0] + ph_padding * 2
    ph_h = bbox_ph[3] - bbox_ph[1] + ph_padding * 2
    ph_x = W - ph_w - margin
    ph_y = H - ph_h - margin
    draw.rounded_rectangle(
        (ph_x, ph_y, ph_x + ph_w, ph_y + ph_h),
        radius=int(ph_h / 2), outline=RED, width=3
    )
    # Red dot/icon
    dot_r = 6 * base_size
    draw.ellipse(
        (ph_x + ph_padding, ph_y + ph_h // 2 - dot_r,
         ph_x + ph_padding + dot_r * 2, ph_y + ph_h // 2 + dot_r),
        fill=RED
    )
    # Phone text (right of icon)
    draw.text(
        (ph_x + ph_padding + dot_r * 2 + 8, ph_y + ph_padding),
        args.phone, fill=RED, font=font_phone
    )

    # 7. Footer red/blue wave ribbons (bottom-left)
    wave_y = H - int(60 * base_size)
    # Red ribbon
    draw.rounded_rectangle(
        (0, wave_y, int(W * 0.5), wave_y + int(12 * base_size)),
        radius=6, fill=RED
    )
    # Blue ribbon below red
    draw.rounded_rectangle(
        (0, wave_y + int(16 * base_size), int(W * 0.35), wave_y + int(12 * base_size) + 10),
        radius=5, fill=BLUE
    )

    # Composite overlay onto background
    result = Image.alpha_composite(bg, overlay)

    # Save as RGB JPEG
    result = result.convert("RGB")
    result.save(args.output, "JPEG", quality=95)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
