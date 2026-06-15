#!/usr/bin/env python3
"""
Reusable Supernova 4-slide carousel overlay template.

Purpose:
- Take KIE/Nano Banana text-free 1:1 backgrounds.
- Apply the approved Supernova v2 carousel frame system deterministically.
- Preserve clean Mongolian Cyrillic text, logo placement, phone capsule, slide ribbon, and footer waves.

Expected workspace shape:
/opt/data/social-content/brands/supernova/
  drafts/<carousel-copy>.json
  generated/<carousel-slug>/slide-01-background.jpg ... slide-04-background.jpg
  assets/logos/supernova-logo-sky-background.jpg

Copy this template into the brand workspace script folder and edit ROOT, SLUG, DRAFT, and copy JSON as needed.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import json, zipfile, math

ROOT = Path('/opt/data/social-content/brands/supernova')
SLUG = 'carousel-XX-topic-slug'
DRAFT = ROOT / 'drafts/carousel-XX-topic-copy.json'
GEN = ROOT / 'generated' / SLUG
LOGO = ROOT / 'assets/logos/supernova-logo-sky-background.jpg'
OUT = GEN / 'final'
OUT.mkdir(parents=True, exist_ok=True)

W = H = 1080
NAVY = (7, 27, 77)
RED = (230, 0, 35)
BLUE = (0, 104, 183)
WHITE = (255, 255, 255)
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

brief = json.loads(DRAFT.read_text(encoding='utf-8'))
logo = Image.open(LOGO).convert('RGB')
logo.thumbnail((170, 110), Image.LANCZOS)

def cover_square(img):
    img = img.convert('RGB')
    w, h = img.size
    scale = max(W / w, H / h)
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    w, h = img.size
    return img.crop(((w - W)//2, (h - H)//2, (w - W)//2 + W, (h - H)//2 + H))

def rounded(base, xy, r, fill, outline=None, width=1, shadow=False):
    if shadow:
        sh = Image.new('RGBA', base.size, (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        off = 7
        sd.rounded_rectangle((xy[0]+off, xy[1]+off, xy[2]+off, xy[3]+off), radius=r, fill=(0,72,130,55))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        base = Image.alpha_composite(base.convert('RGBA'), sh)
    layer = Image.new('RGBA', base.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)
    return Image.alpha_composite(base.convert('RGBA'), layer)

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for word in words:
        trial = (cur + ' ' + word).strip()
        bb = draw.textbbox((0,0), trial, font=font)
        if bb[2] - bb[0] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines

def draw_paragraph(draw, text, x, y, font, fill, maxw, spacing=5):
    for line in wrap(draw, text, font, maxw):
        draw.text((x,y), line, font=font, fill=fill)
        y = draw.textbbox((x,y), line, font=font)[3] + spacing
    return y

def draw_icon(draw, kind, cx, cy):
    draw.ellipse((cx-55,cy-55,cx+55,cy+55), fill=WHITE, outline=(160,220,248), width=4)
    draw.ellipse((cx-48,cy-48,cx+48,cy+48), outline=BLUE, width=3)
    if kind == 'heart-ecg':
        draw.line((cx-35,cy,cx-15,cy,cx-7,cy-20,cx+8,cy+25,cx+18,cy,cx+35,cy), fill=RED, width=5)
    elif kind == 'lightbulb':
        draw.ellipse((cx-22,cy-34,cx+22,cy+10), outline=(245,174,0), width=6)
        draw.rectangle((cx-14,cy+8,cx+14,cy+26), fill=(245,174,0))
    elif kind == 'checklist':
        for i in range(3):
            y = cy - 25 + i*25
            draw.line((cx-24,y,cx-12,y+10,cx+28,y-14), fill=RED if i == 1 else BLUE, width=5)
    else:
        pts=[(cx,cy-36),(cx+31,cy-20),(cx+24,cy+25),(cx,cy+42),(cx-24,cy+25),(cx-31,cy-20)]
        draw.line(pts+[pts[0]], fill=BLUE, width=5)

def add_footer_waves(base):
    layer = Image.new('RGBA', base.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.polygon([(0,930),(120,950),(250,955),(410,945),(575,958),(740,948),(910,928),(1080,910),(1080,1080),(0,1080)], fill=(190,230,252,210))
    d.polygon([(0,948),(150,984),(330,990),(520,976),(680,982),(0,1060)], fill=(0,104,183,235))
    d.polygon([(0,978),(130,1005),(310,1009),(500,996),(660,1005),(0,1078)], fill=(255,255,255,250))
    d.polygon([(0,1000),(155,1028),(345,1031),(515,1018),(670,1031),(0,1080)], fill=(230,0,35,235))
    return Image.alpha_composite(base.convert('RGBA'), layer)

def make_slide(slide):
    n = slide['slide']
    base = cover_square(Image.open(GEN / f'slide-{n:02d}-background.jpg')).convert('RGBA')
    base = Image.alpha_composite(base, Image.new('RGBA', (W,H), (190,230,252,55)))
    d = ImageDraw.Draw(base)

    # Fixed header/title capsule
    base = rounded(base, (30,30,775,128), 38, (255,255,255,238), WHITE, 4, shadow=True)
    d = ImageDraw.Draw(base)
    d.text((78,50), 'Мэдлэгт дусал нэмэр', font=ImageFont.truetype(FONT_BOLD,60), fill=NAVY)
    d.ellipse((655,25,688,70), fill=(0,154,230,210), outline=(255,255,255,200), width=2)
    d.polygon([(671,19),(655,50),(688,50)], fill=(0,154,230,210))

    # Fixed logo card
    card = (910,12,1055,143)
    base = rounded(base, card, 24, (255,255,255,238), (230,244,252,255), 2, shadow=True)
    base.paste(logo.convert('RGBA'), (card[0]+(card[2]-card[0]-logo.width)//2, card[1]+(card[3]-card[1]-logo.height)//2))
    d = ImageDraw.Draw(base)

    # Slide number ribbon
    rx, ry = 54, 130
    d.polygon([(rx,ry),(rx+130,ry),(rx+130,ry+105),(rx+65,ry+84),(rx,ry+105)], fill=BLUE, outline=WHITE)
    d.text((rx+24,ry+22), f'{n}/4', font=ImageFont.truetype(FONT_BOLD,46), fill=WHITE)

    base = add_footer_waves(base)

    # Main content panel
    panel = (36,555,945,928)
    base = rounded(base, panel, 34, (255,255,255,236), WHITE, 3, shadow=True)
    d = ImageDraw.Draw(base)
    draw_icon(d, slide.get('icon','cell-shield'), 106, 665)
    d.rounded_rectangle((178,610,184,795), radius=3, fill=BLUE)

    # Auto-fit headline to avoid clipping long Mongolian text
    hsize = 54
    max_head_w = 690
    while hsize > 42:
        test_font = ImageFont.truetype(FONT_BOLD, hsize)
        if all(d.textbbox((0,0), line, font=test_font)[2] <= max_head_w for line in slide['headline_lines']):
            break
        hsize -= 2
    hfont = ImageFont.truetype(FONT_BOLD, hsize)
    x, y = 214, 594
    for idx, line in enumerate(slide['headline_lines']):
        d.text((x,y), line, font=hfont, fill=RED if idx == slide.get('emphasis_line_index',1) else NAVY)
        y = d.textbbox((x,y), line, font=hfont)[3] + 4
    d.rounded_rectangle((x,y+6,x+250,y+16), radius=5, fill=RED)
    y += 36

    body_size = slide.get('body_font_size', 28)
    small_size = slide.get('small_font_size', 27)
    bfont = ImageFont.truetype(FONT_BOLD, body_size)
    smallfont = ImageFont.truetype(FONT_REG, small_size)
    for i, bullet in enumerate(slide['bullets']):
        if i > 0:
            d.line((214,y+2,790,y+2), fill=(148,200,222), width=2)
            y += 16
        y = draw_paragraph(d, bullet, 214, y, bfont if i == 0 else smallfont, NAVY, 650, 5) + 7

    # Phone capsule: keep compact so digits never clip
    ph = (610,958,1040,1042)
    base = rounded(base, ph, 28, (255,255,255,246), RED, 4, shadow=True)
    d = ImageDraw.Draw(base)
    d.ellipse((632,976,696,1040), fill=RED)
    d.text((647,985), '☎', font=ImageFont.truetype(FONT_BOLD,38), fill=WHITE)
    d.text((718,982), 'Утас:', font=ImageFont.truetype(FONT_BOLD,36), fill=NAVY)
    d.text((835,982), '70000303', font=ImageFont.truetype(FONT_BOLD,36), fill=RED)

    out = OUT / f'{SLUG}-slide-{n:02d}.jpg'
    base.convert('RGB').save(out, quality=95)
    return out

slides = [make_slide(s) for s in brief['slides']]
thumbs = [Image.open(p).resize((360,360), Image.LANCZOS) for p in slides]
sheet = Image.new('RGB', (720,720), (233,246,253))
for i, thumb in enumerate(thumbs):
    sheet.paste(thumb, ((i%2)*360, (i//2)*360))
sheet_path = OUT / f'{SLUG}-contact-sheet.jpg'
sheet.save(sheet_path, quality=95)
zip_path = OUT / f'{SLUG}-final-slides.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in slides:
        z.write(p, p.name)
    z.write(DRAFT, DRAFT.name)
print('contact_sheet', sheet_path)
print('zip', zip_path)
for p in slides:
    print(p)
