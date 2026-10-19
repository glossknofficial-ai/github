"""Replace the AI-garbled label text in the hero still with the real label artwork.

Upscales refs/hero-generated.webp to 1080 wide, then warps the real gold-framed label
panels (cropped from the product photos) onto each product, matching colour and the
generated lighting, and writes assets/hero.png.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
W = 2160  # 4K-ready; label quads below are measured at 1080 wide and scaled

# (source photo, source crop box, target quad in upscaled hero: tl, tr, br, bl)
LABELS = [
    ("power-melt.webp", (811, 721, 1195, 1223), [(460, 899), (578, 899), (578, 1056), (461, 1056)]),
    ("power-cleanse.webp", (836, 998, 1217, 1522), [(605, 1010), (715, 1010), (715, 1160), (605, 1160)]),
    ("power-cleanse-box.webp", (538, 454, 1005, 1007), [(232, 1361), (368, 1349), (369, 1504), (236, 1519)]),
    ("power-cleanse-box.webp", (510, 1500, 1050, 1640), [(229, 1668), (383, 1645), (385, 1694), (231, 1717)]),
]


def coeffs(src_quad, dst_quad):
    """Perspective coefficients mapping output (dst) pixels back to source pixels."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst_quad, src_quad):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def main():
    hero = Image.open(ROOT / "refs" / "hero-generated.webp").convert("RGB")
    hero = hero.resize((W, round(hero.height * W / hero.width)), Image.LANCZOS)
    hero = hero.filter(ImageFilter.UnsharpMask(radius=2.4, percent=70, threshold=2))
    out = np.asarray(hero).astype(float)

    k = W / 1080
    for name, box, quad in LABELS:
        quad = [(x * k, y * k) for x, y in quad]
        src = Image.open(ROOT / "refs" / name).convert("RGB").crop(box)
        sw, sh = src.size
        c = coeffs([(0, 0), (sw, 0), (sw, sh), (0, sh)], quad)
        warped = np.asarray(src.transform(hero.size, Image.PERSPECTIVE, c, Image.BICUBIC,
                                          fillcolor=(0, 0, 0)).filter(ImageFilter.GaussianBlur(0.6))).astype(float)
        mask_img = Image.new("L", src.size, 255).transform(hero.size, Image.PERSPECTIVE, c, Image.BILINEAR, fillcolor=0)
        mask = np.asarray(mask_img.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(2.2))).astype(float)[..., None] / 255

        xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
        x0, x1, y0, y1 = int(min(xs)), int(max(xs)) + 1, int(min(ys)), int(max(ys)) + 1
        inside = mask[y0:y1, x0:x1, 0] > 0.9
        # lighting of the generated product without its garbled text: fit a smooth quadratic
        # surface to the bright (paper) pixels only, so old lettering leaves no grey halo
        reg = np.asarray(hero.crop((x0, y0, x1, y1))).astype(float)
        hh, ww = reg.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww]
        u, v = xx / ww - 0.5, yy / hh - 0.5
        lum = reg.mean(axis=2)
        paper_px = inside & (lum >= np.percentile(lum[inside], 55))
        X = np.stack([np.ones_like(u), u, v, u * u, v * v, u * v], axis=-1)
        tgt = np.empty_like(reg)
        for ch in range(3):
            coef, *_ = np.linalg.lstsq(X[paper_px], reg[..., ch][paper_px], rcond=None)
            tgt[..., ch] = X @ coef
        src_reg = warped[y0:y1, x0:x1]
        # match the paper colour: brightest-quartile means of source vs target
        def paper(a):
            lum = a.mean(axis=2)[inside]
            sel = lum >= np.percentile(lum, 60)
            return a[inside][sel].mean(axis=0)
        # multiply the label ink onto the smoothed product surface: keeps the generated
        # paper colour and lighting exactly, so no patch edge shows
        ink = src_reg / np.maximum(paper(src_reg), 1)
        fixed = np.clip(tgt * np.minimum(ink, 1.08), 0, 255)
        m = mask[y0:y1, x0:x1]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + fixed * m

    (ROOT / "assets").mkdir(exist_ok=True)
    Image.fromarray(out.astype(np.uint8)).save(ROOT / "assets" / "hero.png")
    print("wrote assets/hero.png", hero.size)


if __name__ == "__main__":
    main()
