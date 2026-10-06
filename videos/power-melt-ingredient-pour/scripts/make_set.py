"""Generate the studio set for the reel: a seamless lavender sweep (#d7b6e2 base)
with soft left key light, plus the tube's contact + cast shadow on the tabletop.

    python3 scripts/make_set.py

Writes assets/set-bg.png and assets/set-shadow.png (1080x1920). The tube
placement constants must match index.html (S, FLOOR).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
S, FLOOR = 0.8, 1585          # same as index.html
BASE = np.array([0xD7, 0xB6, 0xE2], float)

y = np.arange(H)[:, None] / H
x = np.arange(W)[None, :] / W


def sstep(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# --- seamless sweep: wall (upper) curves into tabletop (lower) -------------
SWEEP_A, SWEEP_B = 0.60, 0.73                  # soft wall→table transition
surface = sstep(SWEEP_A, SWEEP_B, y)
wall_shade = 0.90 + 0.11 * sstep(0.0, SWEEP_A, y)          # darker toward the top
table_shade = 1.04 - 0.06 * sstep(SWEEP_B, 1.0, y)          # lighter tabletop, falls off to front edge
lum = wall_shade * (1 - surface) + table_shade * surface

# Soft key light from the left, gentle falloff to the right (like the reference).
key = 1.0 + 0.06 * (1 - sstep(0.0, 1.0, x)) - 0.03 * sstep(0.55, 1.0, x)
# A soft glow behind the tube to separate it from the wall.
glow = 0.03 * np.exp(-(((x - 0.5) / 0.32) ** 2 + ((y - 0.52) / 0.30) ** 2))
# Slight darkening in the top corners.
vign = 1 - 0.07 * sstep(0.35, 1.0, np.hypot((x - 0.5) * 1.4, (y - 0.62) * 1.0))

L = lum * key * vign + glow
# Warm the tabletop very slightly so wall and surface read as different planes.
rgb = BASE[None, None, :] * L[:, :, None]
# desaturate the tabletop a touch so it reads as a matte surface, not a light
grey = rgb.mean(axis=2, keepdims=True)
rgb = rgb * (1 - 0.18 * surface[:, :, None]) + grey * 0.18 * surface[:, :, None]
rgb += surface[:, :, None] * np.array([4.0, 3.0, 0.0])

rng = np.random.default_rng(7)
rgb += rng.normal(0, 1.6, rgb.shape)           # fine film grain, also kills banding
Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").save(ROOT / "assets" / "set-bg.png")

# --- shadows ---------------------------------------------------------------
tube = Image.open(ROOT / "assets" / "tube.png")
a = np.asarray(tube)[:, :, 3] > 128
tw = tube.width * S
cx = W / 2
ys, = np.where(a.any(axis=1))
widths = np.array([a[r].sum() for r in range(a.shape[0])]) * S

def shadow_layer(length_k, lift_k, thick_k, blur, step=3):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    for r in range(ys.min(), ys.max() + 1, step):
        h = (tube.height - r) * S                 # height above the tabletop
        w = widths[r]
        if w <= 0:
            continue
        sx = cx + h * length_k                    # light from the left → shadow runs right
        sy = FLOOR - h * lift_k
        rx = max(w * 0.5 * 0.55, 6)
        ry = max(w * thick_k, 3)
        d.ellipse([sx - rx, sy - ry, sx + rx, sy + ry], fill=255)
    return np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(float) / 255

near = shadow_layer(0.30, 0.045, 0.07, 6)
far = shadow_layer(0.30, 0.045, 0.07, 26)
dist = np.clip((np.arange(W)[None, :] - cx) / 420, 0, 1)
cast = (near * (1 - dist) + far * dist) * (0.62 - 0.40 * dist)

contact = Image.new("L", (W, H), 0)
ImageDraw.Draw(contact).ellipse([cx - tw * 0.30, FLOOR - 6, cx + tw * 0.30, FLOOR + 6], fill=255)
contact = np.asarray(contact.filter(ImageFilter.GaussianBlur(4))).astype(float) / 255 * 0.8
amb = Image.new("L", (W, H), 0)
ImageDraw.Draw(amb).ellipse([cx - tw * 0.62, FLOOR - 26, cx + tw * 0.62, FLOOR + 30], fill=255)
amb = np.asarray(amb.filter(ImageFilter.GaussianBlur(22))).astype(float) / 255 * 0.3

alpha = np.clip(1 - (1 - cast) * (1 - contact) * (1 - amb), 0, 1)
shadow = np.zeros((H, W, 4), np.uint8)
shadow[:, :, 0], shadow[:, :, 1], shadow[:, :, 2] = 0x6E, 0x47, 0x80   # deep plum, not grey
shadow[:, :, 3] = (alpha * 255).astype(np.uint8)
Image.fromarray(shadow, "RGBA").save(ROOT / "assets" / "set-shadow.png")
print("wrote set-bg.png, set-shadow.png")
