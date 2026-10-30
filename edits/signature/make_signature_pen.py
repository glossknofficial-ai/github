"""Pen-drawn signature: the ink follows each stroke's centreline in writing order, like someone actually signing.
Font: Ms Madi (OFL, brush-pen signature style). Transparent background; black and white ink versions.
Outputs: signature_pen_<ink>.mov (QuickTime Animation, alpha), .webm (VP9 alpha), .png (final), + preview on white."""
import os, subprocess, sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT, W, H, FPS, SS = "Jaspreet Ghai Kapoor", 1080, 1920, 30, 2
FONT = os.path.join(HERE, "fonts", "MsMadi-Regular.ttf")
size = 200 * SS
font = ImageFont.truetype(FONT, size)
x0, y0, x1, y1 = font.getbbox(TEXT)
size = int(size * min(1.0, (W - 100) * SS / (x1 - x0))); font = ImageFont.truetype(FONT, size)
x0, y0, x1, y1 = font.getbbox(TEXT); pad = 40 * SS
cw, ch = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
img = Image.new("L", (cw, ch), 0); ImageDraw.Draw(img).text((pad - x0, pad - y0), TEXT, font=font, fill=255)
mask = np.asarray(img, np.float32) / 255
skel = skeletonize(mask > 0.45)

# --- order the skeleton like a pen: components left to right, each traced from its left-most end ---
ys, xs = np.nonzero(skel); idx = {(y, x): i for i, (y, x) in enumerate(zip(ys, xs))}
nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
adj = [[idx[(y + dy, x + dx)] for dy, dx in nb if (y + dy, x + dx) in idx] for y, x in zip(ys, xs)]
lab, ncomp = ndimage.label(skel, structure=np.ones((3, 3)))
comps = sorted(range(1, ncomp + 1), key=lambda c: xs[lab[ys, xs] == c].min())
T = np.full(len(ys), np.inf); t = 0.0
STEP = 1.0                      # arc-length units per skeleton pixel
LIFT = 14.0 * SS                # pen lift between strokes (in arc-length units)
WORD_LIFT = 60.0 * SS
prev_right = None
for c in comps:
    members = np.nonzero(lab[ys, xs] == c)[0]
    if len(members) < 6 * SS: continue
    ends = [m for m in members if len(adj[m]) == 1] or list(members)
    start = min(ends, key=lambda m: (xs[m], ys[m]))
    if prev_right is not None:
        t += WORD_LIFT if xs[members].min() - prev_right > 25 * SS else LIFT
    # depth-first trace preferring to keep going straight (smooth pen motion)
    stack, seen, last_dir = [start], set(), (0, 1)
    cur = start
    while stack:
        cur = stack.pop()
        if cur in seen: continue
        seen.add(cur); T[cur] = t; t += STEP
        nxt = [n for n in adj[cur] if n not in seen]
        nxt.sort(key=lambda n: -((ys[n] - ys[cur]) * last_dir[0] + (xs[n] - xs[cur]) * last_dir[1]))
        if nxt: last_dir = (ys[nxt[0]] - ys[cur], xs[nxt[0]] - xs[cur])
        stack.extend(reversed(nxt))
    prev_right = xs[members].max()
T[np.isinf(T)] = t
# every ink pixel takes the time of its nearest centreline pixel
tm = np.full(skel.shape, np.inf, np.float32); tm[ys, xs] = T
_, (iy, ix) = ndimage.distance_transform_edt(~skel, return_indices=True)
TIME = tm[iy, ix]

WRITE, HOLD, LEAD = 3.4, 1.6, 0.25
TIME = TIME / t * WRITE + LEAD
DUR = LEAD + WRITE + HOLD; N = round(DUR * FPS)
SOFT = 0.035                    # seconds of soft ink-in at the pen tip
ox, oy = (W * SS - cw) // 2, (H * SS - ch) // 2

for ink_name, ink in [("black", (22, 18, 24)), ("white", (255, 255, 255))]:
    out = os.path.join(HERE, f"frames_{ink_name}"); os.makedirs(out, exist_ok=True)
    for f in range(N):
        a = mask * np.clip((f / FPS - TIME) / SOFT + 1, 0, 1)
        crop = np.zeros((ch, cw, 4), np.uint8); crop[..., :3] = ink; crop[..., 3] = (a * 255).astype(np.uint8)
        fr = Image.new("RGBA", (W * SS, H * SS)); fr.paste(Image.fromarray(crop, "RGBA"), (ox, oy))
        fr.resize((W, H), Image.LANCZOS).save(os.path.join(out, f"{f:04d}.png"))
    base = os.path.join(HERE, f"signature_pen_{ink_name}")
    Image.open(os.path.join(out, f"{N - 1:04d}.png")).save(base + ".png")
    src = ["-framerate", str(FPS), "-i", os.path.join(out, "%04d.png")]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-c:v", "qtrle", "-pix_fmt", "argb", base + ".mov"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "2M",
                    "-auto-alt-ref", "0", base + ".webm"], check=True)
    bg = "white" if ink_name == "black" else "0x00C878"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={bg}:s={W}x{H}:r={FPS}", *src,
                    "-filter_complex", "[0][1]overlay=shortest=1,format=yuv420p", "-c:v", "libx264", "-crf", "16",
                    base + "_preview.mp4"], check=True)
print("frames", N, "duration", round(DUR, 2), "skeleton px", len(ys), "strokes", ncomp)
