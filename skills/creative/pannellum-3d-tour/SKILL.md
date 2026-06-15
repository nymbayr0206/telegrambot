---
name: pannellum-3d-tour
description: "Build 3D virtual tours from equirectangular panorama images using Pannellum. Generate self-contained HTML files for single panoramas or multi-scene tours with navigation hot spots."
version: 1.0.0
author: Hermes Agent
tags: [panorama, 3d, virtual-tour, pannellum, 360, html, equirectangular]
---

# Pannellum 3D Tour Builder

Create immersive 3D virtual tours from equirectangular (360°) panorama images using [Pannellum](https://pannellum.org/) — a lightweight, open-source panorama viewer.

## When to use

- User provides 360° panorama images and wants a web-based virtual tour
- Need to link multiple panoramas into a navigable tour
- Want to embed a single 360° view in an HTML page
- Real estate virtual tours, property walkthroughs, museum exhibits, etc.

## How it works

Pannellum uses WebGL to render equirectangular images inside an HTML page. The skill generates a complete HTML file that includes Pannellum from CDN and the proper JSON configuration.

## Usage

### Step 1: Get images from user

Ask the user for equirectangular (2:1 aspect ratio) panorama images. For a single panorama, just needs one image. For a tour, collect all images first.

For each image, note:
- File path / name
- Scene name / title (e.g., "Гаднаас харагдах байдал", "Зочны өрөө", etc.)
- If linking scenes, note which direction leads to which scene

### Step 2: Copy images to a web-accessible directory

Copy images to `/opt/data/www/tours/` or a similar directory that can be served by a web server. If no web server is configured, generate a standalone HTML file with base64-encoded images (small images only — for large panoramas, serve from a web server).

```bash
mkdir -p /opt/data/www/tours/
cp /path/to/image.jpg /opt/data/www/tours/
```

### Step 3: Generate the HTML

#### A) Single Panorama (simplest)

Generate a minimal HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>360° Panorama</title>
    <link rel="stylesheet" href="https://cdn.pannellum.org/2.5/pannellum.css"/>
    <script type="text/javascript" src="https://cdn.pannellum.org/2.5/pannellum.js"></script>
    <style>
        html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
        #panorama { width: 100%; height: 100%; }
    </style>
</head>
<body>
    <div id="panorama"></div>
    <script>
        pannellum.viewer('panorama', {
            "type": "equirectangular",
            "panorama": "image.jpg",
            "autoLoad": true,
            "title": "Өрөөний нэр",
            "author": "Хэрэглэгч",
            "hfov": 100,
            "autoRotate": -2
        });
    </script>
</body>
</html>
```

#### B) Multi-Scene Virtual Tour (with navigation hot spots)

Generate with scenes and hot spots connecting them:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Virtual Tour</title>
    <link rel="stylesheet" href="https://cdn.pannellum.org/2.5/pannellum.css"/>
    <script type="text/javascript" src="https://cdn.pannellum.org/2.5/pannellum.js"></script>
    <style>
        html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
        #panorama { width: 100%; height: 100%; }
    </style>
</head>
<body>
    <div id="panorama"></div>
    <script>
        pannellum.viewer('panorama', {
            "default": {
                "firstScene": "scene1",
                "author": "Эзэмшигч",
                "sceneFadeDuration": 1000,
                "autoLoad": true
            },
            "scenes": {
                "scene1": {
                    "title": "Гаднаас харагдах байдал",
                    "hfov": 110,
                    "pitch": -3,
                    "yaw": 117,
                    "type": "equirectangular",
                    "panorama": "outside.jpg",
                    "hotSpots": [
                        {
                            "pitch": -2.1,
                            "yaw": 132.9,
                            "type": "scene",
                            "text": "Дотор руу орох",
                            "sceneId": "scene2"
                        }
                    ]
                },
                "scene2": {
                    "title": "Зочны өрөө",
                    "hfov": 110,
                    "yaw": 5,
                    "type": "equirectangular",
                    "panorama": "livingroom.jpg",
                    "hotSpots": [
                        {
                            "pitch": -0.6,
                            "yaw": 37.1,
                            "type": "scene",
                            "text": "Гадагш гарах",
                            "sceneId": "scene1"
                        }
                    ]
                }
            }
        });
    </script>
</body>
</html>
```

## Pannellum Configuration Reference

### Common options
| Option | Type | Description |
|--------|------|-------------|
| `type` | string | `equirectangular` (default), `cubemap`, or `multires` |
| `panorama` | string | URL/path to the equirectangular image |
| `title` | string | Displayed as panorama title |
| `author` | string | Displayed as panorama author |
| `autoLoad` | boolean | Auto-load panorama (default: false) |
| `autoRotate` | number | Rotation speed in deg/sec. Negative = clockwise |
| `hfov` | number | Initial horizontal FOV (1-360, default: 100) |
| `pitch` | number | Initial pitch in degrees (default: 0) |
| `yaw` | number | Initial yaw in degrees (default: 0) |
| `compass` | boolean | Show compass (default: false) |
| `northOffset` | number | North offset for compass in degrees |
| `preview` | string | Low-res preview image URL |
| `sceneFadeDuration` | number | Fade duration between scenes in ms |

### Hot Spot options
| Option | Type | Description |
|--------|------|-------------|
| `pitch` | number | Hot spot pitch location in degrees |
| `yaw` | number | Hot spot yaw location in degrees |
| `type` | string | `scene` (scene link) or `info` (info popup) or `URL` (external link) |
| `text` | string | Text shown on hover |
| `sceneId` | string | For `scene` type: target scene ID |
| `URL` | string | For `URL` type: target URL |
| `targetPitch` | number | Target scene initial pitch |
| `targetYaw` | number | Target scene initial yaw (use `same` to maintain direction) |

### Tour config structure
```
{
  "default": {
    "firstScene": "scene_id",       // Required: first scene to show
    "sceneFadeDuration": 1000,      // Optional: fade duration
    "autoLoad": true,               // Optional
    "author": "Name"               // Optional
  },
  "scenes": {
    "scene_id_1": {
      "title": "Scene Title",
      "type": "equirectangular",
      "panorama": "image1.jpg",
      "hotSpots": [ ... ]
    },
    "scene_id_2": { ... }
  }
}
```

## Tips for positioning hot spots (important!)

To find the correct pitch/yaw coordinates for hot spots:

1. Open the generated HTML in a browser
2. In the console, run:
   ```js
   // Enable hot spot debug mode
   viewer.hotSpotDebug(true);
   // or add "hotSpotDebug": true to config
   ```
3. Click on the location where you want a hot spot → pitch/yaw values print to console
4. Use those values in your hot spot config

Alternative: Use the `hotSpotDebug: true` option in the config JSON while building.

## Serving the tour

### Option A: Static HTML + images (recommended)
Place the HTML file and images together in a web-accessible directory:
```
/opt/data/www/tours/my-tour/
  ├── index.html
  ├── outside.jpg
  ├── livingroom.jpg
  └── bedroom.jpg
```
Serve via any web server (nginx, Apache, Python `http.server`, etc.)

### Option B: Self-contained HTML (small images only)
For small panoramas, use base64-encoded data URIs (NOT recommended for large 4K+ images):
```js
"panorama": "data:image/jpeg;base64,/9j/4AAQ..."
```

### Option C: Send file directly
Generate the HTML and send to user with:
```
MEDIA:/path/to/tour.html
```

## Troubleshooting: When users provide regular (non-360°) photos

### Problem
User sends standard camera photos (3:2 ratio, e.g. 800x534) instead of 360° equirectangular images (2:1 ratio).

### What NOT to do
Do NOT claim you can stitch them into a 360° panorama unless they were actually taken as a 360° sequence (same point, overlapping 30-40%). Regular property photos of different rooms won't stitch into a usable 360° panorama.

### What to check
1. **Check aspect ratio** with Python/PIL. 2:1 = potential 360° photo
2. **Check if images overlap** — run OpenCV stitcher to test
3. **If no EXIF data** and standard 3:2 ratio → 95% chance they're regular photos

### If they ARE overlapping 360° sequence shots
Use OpenCV's built-in stitcher (available in Hermes venv):

```python
import cv2, glob
images = [cv2.imread(f) for f in sorted(glob.glob('*.jpg'))]
stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
status, pano = stitcher.stitch(images)
if status == cv2.Stitcher_OK:
    cv2.imwrite('panorama.jpg', pano)
```

⚠️ Result must be 2:1 aspect ratio for Pannellum. If smaller/incomplete, images weren't taken as a proper 360° sequence.

### If they're regular property photos — offer alternatives:
- **Option A**: User takes actual 360° photos (Google Street View app, 360° camera, or manual sequence from one point)
- **Option B**: Create a **Photo Gallery tour** instead — HTML page showing all images with navigation, room labels, and a polished real-estate-agent style layout. No 360° rotation but looks professional. See `templates/photo-gallery.html` for the HTML template.
- **Option C**: Use the images as individual scenes in Pannellum by cropping them to 2:1 (will look distorted — not recommended)

### Photo Gallery Tour: Quick Build

When the user has standard (non-360°) property photos:

1. **Copy images** to a working directory with sequential names `photo_01.jpg`, `photo_02.jpg`, etc.
2. **Load the template** from `templates/photo-gallery.html` — it has placeholder `{TOTAL}` for the photo count
3. **Replace `{TOTAL}`** with the actual number of photos (e.g., `11`)
4. **Write the HTML** alongside the images
5. **Deliver** as tar.gz archive via `MEDIA:/path/to/archive.tar.gz`
6. Tell the user to extract and open `index.html` in their browser

The gallery has: navigation arrows, keyboard ← →, touch swipe, thumbnail strip, fullscreen toggle, and fade transitions. No web server needed — works directly from local files.

### How to explain to the user (in Mongolian):
"Таны зургууд энгийн гэрэл зураг байна (360° биш). 360° панорама хийхийн тулд нэг цэг дээр зогсоод 360° эргүүлэн зураг авах хэрэгтэй. Эсвэл эдгээр зургаар л сайхан фото тур хийж өгье."

## Limitations

- Pannellum requires WebGL — won't work on very old browsers
- Large images (>8192px wide) may have performance issues on low-end devices
- For real 3D tours with room-to-room navigation, each scene needs a separate equirectangular image
- Pannellum expects equirectangular (spherical) projection images with 2:1 aspect ratio
- Hot spot positioning requires manual calibration
- OpenCV stitcher may fail on standard photos of different rooms/views — this is expected, not a bug
