"""One fixed cart for the whole scene. Each product is revealed in place on the empty cart, using the product's own
silhouette (holes filled) and the original, unkeyed pixels from the source frame, so products are fully solid and
the cart never shifts between stages (the source moved it slightly)."""
import os, numpy as np
from PIL import Image
from scipy import ndimage
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media"); V = os.path.join(M, "v2")
PANEL = 615
c0 = np.asarray(Image.open(os.path.join(V, "cart0.png")).convert("RGBA")).astype(float)
c3 = np.roll(np.asarray(Image.open(os.path.join(V, "cart3.png")).convert("RGBA")).astype(float), 1, axis=0)       # dy=-1 alignment
orig = np.asarray(Image.open(os.path.join(M, "f120.png")).convert("RGB").resize((1080, 1920), Image.LANCZOS)).astype(float)
orig = np.roll(orig[PANEL:], 1, axis=0); orig = np.dstack([orig, np.full(orig.shape[:2], 255.0)])                  # solid product pixels
H, W = c0.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
box = lambda x0, x1, y0, y1: (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
rgb = c3[..., :3]; sat = rgb.max(2) - rgb.min(2); dark = rgb.max(2) < 95; solid = c3[..., 3] > 128
def silhouette(m, close=5):
    m = ndimage.binary_closing(m, iterations=close); lab, n = ndimage.label(m)
    if n: m = lab == (np.argmax(ndimage.sum(m, lab, range(1, n + 1))) + 1)
    return ndimage.binary_fill_holes(m)
m_box = silhouette(box(175, 580, 365, 805) & ((sat > 14) | dark) & solid, 4)
m_box = ndimage.binary_dilation(m_box, iterations=2)
m_tube = silhouette(box(452, 600, 452, 865) & solid & ~ndimage.binary_dilation(m_box, iterations=4) & ~((sat > 26) & solid))
m_bottle = silhouette(box(592, 708, 452, 865) & solid & ~m_box & ~m_tube)
def soft(m): return ndimage.gaussian_filter(m.astype(float), 1.0)[..., None]
cum = np.zeros((H, W, 1))
for k, m in enumerate([m_bottle, m_tube, m_box], start=1):     # order of arrival: cleanse, melt, reset
    cum = np.maximum(cum, soft(m))
    Image.fromarray(np.clip(c0 * (1 - cum) + orig * cum, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(V, f"cartF{k}.png"))
Image.fromarray(c0.astype(np.uint8), "RGBA").save(os.path.join(V, "cartF0.png"))
print("fixed-cart stages written")
