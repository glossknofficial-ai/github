"""Animated handwritten signature "Jaspreet Ghai Kapoor" (Great Vibes, OFL) on a transparent background.
The ink is revealed left to right like a pen writing, word by word with tiny pauses, then holds.
Outputs: signature.mov (QuickTime Animation, alpha), signature.webm (VP9 alpha), signature.png (final frame)."""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS, SEP = ["Jaspreet", "Ghai", "Kapoor"], "  "     # double space: Great Vibes sets words very tight
TEXT, W, H, FPS = SEP.join(WORDS), 1080, 1920, 30
SS = 2                                                  # supersample
font = ImageFont.truetype(os.path.join(HERE, "fonts", "GreatVibes-Regular.ttf"), 170 * SS)
x0, y0, x1, y1 = font.getbbox(TEXT)
tw, th = x1 - x0, y1 - y0
scale = min(1.0, (W - 120) * SS / tw)                  # fit width with margins
font = ImageFont.truetype(os.path.join(HERE, "fonts", "GreatVibes-Regular.ttf"), int(170 * SS * scale))
x0, y0, x1, y1 = font.getbbox(TEXT); tw, th = x1 - x0, y1 - y0
ox, oy = (W * SS - tw) // 2 - x0, (H * SS - th) // 2 - y0
mask = Image.new("L", (W * SS, H * SS), 0)
ImageDraw.Draw(mask).text((ox, oy), TEXT, font=font, fill=255)
mask = np.asarray(mask, np.float32) / 255

# pen path along x: each word written at constant speed, short lift between words
words = WORDS; segs, pos = [], 0
for i, w in enumerate(words):
    start = ox + font.getlength(SEP.join(words[:i]) + (SEP if i else "")); end = ox + font.getlength(SEP.join(words[:i + 1]))
    segs.append((start - (40 * SS if i == 0 else 10 * SS), end + 12 * SS))
ink_right = float(np.nonzero(mask.max(axis=0) > 0)[0].max())
segs[-1] = (segs[-1][0], ink_right + 30 * SS)         # finish the last swash completely
WRITE, PAUSE, HOLD = 2.9, 0.18, 1.6
total_w = sum(e - s for s, e in segs)
times, t = [], 0.25
for s, e in segs:
    d = WRITE * (e - s) / total_w; times.append((t, t + d, s, e)); t += d + PAUSE
DUR = t - PAUSE + HOLD; N = round(DUR * FPS)
xs = np.arange(W * SS, dtype=np.float32)[None, :]
EDGE = 26 * SS

def pen_x(t):
    x = -1e9
    for a, b, s, e in times:
        if t >= b: x = e
        elif t >= a:
            u = (t - a) / (b - a); u = u * u * (3 - 2 * u) * 0.35 + u * 0.65   # gentle ease, mostly steady speed
            x = s + (e - s) * u; break
    return x

out = os.path.join(HERE, "frames"); os.makedirs(out, exist_ok=True)
INK = np.array([22, 18, 24], np.float32)
for f in range(N):
    px = pen_x(f / FPS)
    reveal = np.clip((px - xs) / EDGE, 0, 1)
    a = mask * reveal
    rgba = np.zeros((H * SS, W * SS, 4), np.float32); rgba[..., :3] = INK; rgba[..., 3] = a * 255
    Image.fromarray(rgba.astype(np.uint8), "RGBA").resize((W, H), Image.LANCZOS).save(os.path.join(out, f"{f:04d}.png"))
Image.open(os.path.join(out, f"{N - 1:04d}.png")).save(os.path.join(HERE, "signature.png"))
src = ["-framerate", str(FPS), "-i", os.path.join(out, "%04d.png")]
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-c:v", "qtrle", "-pix_fmt", "argb", os.path.join(HERE, "signature.mov")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "2M", "-auto-alt-ref", "0",
                os.path.join(HERE, "signature.webm")], check=True)
print("frames", N, "duration", round(DUR, 2))
