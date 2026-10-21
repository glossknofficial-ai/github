"""Colour-grade assets/hero.png into assets/hero-graded.png: warmer, punchier, less purple.

Lilac/purple hues are swung toward candy pink, overall saturation and contrast go up,
and whites stay clean so the white packaging and labels still read as white.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def rgb_to_hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r); gg = m & (mx == g) & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    h = h / 6.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    out = np.zeros(h.shape + (3,))
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        sel = i == k
        out[sel] = np.stack([r[sel], g[sel], b[sel]], -1)
    return out


def main():
    a = np.asarray(Image.open(ROOT / "assets" / "hero.png").convert("RGB")).astype(float) / 255
    h, s, v = rgb_to_hsv(a)
    deg = h * 360
    # swing lilac/purple (255°–320°) toward candy pink (~338°), strongest at ~290°
    w = np.clip(1 - np.abs(deg - 290) / 45, 0, 1)
    deg = deg + w * (338 - deg) * 0.85
    h = (deg % 360) / 360
    # saturation up, but leave near-white packaging alone
    boost = 1.0 + 1.0 * np.clip((s - 0.06) / 0.25, 0, 1)
    s = np.clip(s * boost, 0, 1)
    out = hsv_to_rgb(h, s, v)
    # warm white balance + gentle S-curve contrast
    out[..., 0] *= 1.03
    out[..., 2] *= 0.96
    out = np.clip(out, 0, 1)
    out = 0.5 + (out - 0.5) * 1.12
    out = np.clip(out, 0, 1) ** 0.97
    Image.fromarray((out * 255).astype(np.uint8)).save(ROOT / "assets" / "hero-graded.png")
    print("wrote assets/hero-graded.png")


if __name__ == "__main__":
    main()
