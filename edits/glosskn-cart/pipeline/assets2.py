"""Assets for the reference-style rebuild: empty Instagram top panel, story circles (exact crops),
and the cart at each fill stage (0..3 products) cut from the flat lilac with the strict matte."""
import os, numpy as np
from PIL import Image
from scipy import ndimage
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media"); V = os.path.join(M, "v2")
BG = np.array([236, 228, 237], np.int16)
def load(n): return np.asarray(Image.open(os.path.join(M, f"f{n}.png")).convert("RGB").resize((1080, 1920), Image.LANCZOS))
def matte(rgb, tol=4, min_area=160):
    bgl = (np.abs(rgb.astype(np.int16) - BG).max(axis=2) <= tol)
    lab, n = ndimage.label(bgl); sizes = ndimage.sum(bgl, lab, range(1, n + 1))
    keep = np.isin(lab, np.nonzero(sizes >= min_area)[0] + 1)
    a = 1.0 - ndimage.gaussian_filter(keep.astype(np.float32), 0.6)
    return np.dstack([rgb, (np.clip(a, 0, 1) * 255).astype(np.uint8)])
f0 = load(0)
col = f0[:, 1050].astype(int).sum(1); PANEL = int(np.argmax(col < 3 * 250)) if (col < 750).any() else 612
print("panel bottom", PANEL)
Image.fromarray(load(120)[:PANEL]).save(os.path.join(V, "panel.png"))          # header + 'Your story' only
for k, n in enumerate([0, 36, 68, 120]):                                        # cart with 0,1,2,3 products
    Image.fromarray(matte(load(n))[PANEL:], "RGBA").save(os.path.join(V, f"cart{k}.png"))
# story circles + labels from the first frame (exact pixels), white panel keyed to transparent
g = f0.astype(int)
for name, cx in [("cleanse", 392), ("melt", 655), ("reset", 918)]:
    x0, x1, y0, y1 = cx - 125, cx + 125, 180, 470
    crop = g[y0:y1, x0:x1]
    a = np.clip((255 * 3 - crop.sum(2)) / 30.0, 0, 1)                           # anything not pure white
    yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]
    a = np.where((xx - 125) ** 2 + (yy - (306 - y0)) ** 2 <= 113 ** 2, 1.0, a)   # the circle itself is fully solid
    Image.fromarray(np.dstack([crop.astype(np.uint8), (a * 255).astype(np.uint8)]), "RGBA").save(os.path.join(V, f"story_{name}.png"))
print("ok")
