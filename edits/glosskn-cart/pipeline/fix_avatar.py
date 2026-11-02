"""The small profile avatar next to 'glosskndaily' has a garbled logo in the source; repaint its inside with
the clean GLOSSKN wordmark (ring untouched)."""
import os, numpy as np
from PIL import Image, ImageDraw
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.join(P, "media", "v2", "panel.png")
p = Image.open(F).convert("RGB"); a = np.asarray(p).astype(int)
y0, y1, x0, x1 = 460, 615, 10, 150
col = (a[y0:y1, x0:x1].max(2) - a[y0:y1, x0:x1].min(2)) > 80                    # saturated ring pixels
ys, xs = np.nonzero(col); cy, cx = y0 + (ys.min() + ys.max()) / 2, x0 + (xs.min() + xs.max()) / 2
r_out = max(ys.max() - ys.min(), xs.max() - xs.min()) / 2
yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]; d = np.hypot(yy - cy, xx - cx)
ringd = d[y0:y1, x0:x1][col]; r_in = np.percentile(ringd, 3) - 1.5               # just inside the ring
print("centre", cx, cy, "outer", r_out, "inner", round(r_in, 1))
bg = tuple(int(v) for v in np.median(a[(d < r_in - 2) & (d > r_in - 6)].reshape(-1, 3), axis=0))
m = Image.new("L", p.size, 0); ImageDraw.Draw(m).ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in), fill=255)
p.paste(Image.new("RGB", p.size, bg), (0, 0), m)
logo = Image.open(os.path.join(P, "..", "glosskn-birthday", "media", "logo_dark.png")).convert("RGBA")
lw = int(r_in * 1.5); logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
p.paste(logo, (round(cx - lw / 2), round(cy - logo.height / 2)), logo); p.save(F)
