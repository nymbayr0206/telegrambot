# Photo Gallery Tour (alternative to Pannellum when user only has standard photos)

When user provides standard photos (not 360° panoramas), create a professional photo gallery HTML page instead.

## Key differences from Pannellum tour
| Feature | Pannellum 360° tour | Photo Gallery tour |
|---------|-------------------|-------------------|
| Image type | 360° equirectangular (2:1) | Standard photos (any ratio) |
| Interaction | Drag to look around | Click/arrow to navigate |
| Navigation | Hot spots in 3D space | Thumbnails, prev/next arrows |
| Use case | Virtual walkthrough | Property listing showcase |

## Generated HTML features
- Full-screen viewer with prev/next arrows
- Thumbnail strip at bottom
- Keyboard navigation (← →)
- Touch swipe support (mobile)
- Fullscreen button
- Smooth fade transitions
- Professional dark theme

## How to build
1. Copy images to a directory with sequential names: `property_01.jpg`, `property_02.jpg`, etc.
2. Generate HTML with embedded JavaScript that loads images dynamically
3. Package as tar.gz for delivery
4. User extracts and opens `index.html` in browser

## Script to generate (Python)
```python
import os
TOTAL = 11  # image count
html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Property Photo Tour</title>
<style>/* full styles here */</style>
</head>
<body>
<div id="viewer">
  <img id="mainImage">
  <div id="counter">1/{total}</div>
  <button id="prevBtn">‹</button>
  <button id="nextBtn">›</button>
  <div id="thumbnails"></div>
</div>
<script>
const TOTAL = {total};
let current = 1;
// ... navigation logic
</script>
</body>
</html>'''.format(total=TOTAL)
with open('index.html', 'w') as f:
    f.write(html)
```

## Serving
- Package as `tar.gz`: `tar czf tour.tar.gz images/ index.html`
- No web server needed — just open `index.html` locally in any browser
