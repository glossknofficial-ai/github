"""3D GLOSSKN wordmark (lilac face, plum extrusion, soft shadow) + rising-from-behind animation frames.
Writes media/v3/logo3d.png and media/v3/logo_<id>/%03d.png (1080x1920 RGBA) for each logo window."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v3")
src = Image.open(os.path.join(P, "media", "logo_dark.png")).convert("RGBA")
W = 880; h = round(src.height * W / src.width)
a = np.asarray(src.resize((W, h), Image.LANCZOS))[..., 3].astype(np.float32) / 255
DEPTH = 16; pad = 40
H2, W2 = h + DEPTH + 2 * pad, W + DEPTH + 2 * pad
out = np.zeros((H2, W2, 4), np.float32)

def put(rgb, alpha, dx, dy):
    sl = (slice(pad + dy, pad + dy + h), slice(pad + dx, pad + dx + W))
    al = alpha[..., None]
    out[sl][..., :3] = out[sl][..., :3] * (1 - al) + np.asarray(rgb, np.float32) * al
    out[sl][..., 3:] = out[sl][..., 3:] * (1 - al) + al

# soft contact shadow
sh = np.zeros((H2, W2), np.float32); sh[pad + DEPTH + 6:pad + DEPTH + 6 + h, pad + DEPTH:pad + DEPTH + W] = a
sh = np.asarray(Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32) / 255 * 0.35
out[..., 3] = sh; out[..., :3] = np.array([60, 30, 70], np.float32)
# extrusion: deep plum stepping back
for d in range(DEPTH, 0, -1):
    k = d / DEPTH
    put([110 - 50 * k, 72 - 40 * k, 128 - 50 * k], a, d // 2, d)
# face: lilac vertical gradient with a light top edge
yy = np.linspace(0, 1, h)[:, None, None]
face = (1 - yy) * np.array([246, 232, 251]) + yy * np.array([196, 150, 214])
sl = (slice(pad, pad + h), slice(pad, pad + W)); al = a[..., None]
out[sl][..., :3] = out[sl][..., :3] * (1 - al) + face * al
out[sl][..., 3:] = np.maximum(out[sl][..., 3:], al)
# glossy bevel highlight on the upper edges
edge = np.clip(a - np.roll(a, 3, axis=0), 0, 1)[..., None] * 0.8
out[sl][..., :3] = out[sl][..., :3] * (1 - edge) + 255 * edge
out[..., 3] *= 255
logo = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
logo.save(os.path.join(V, "logo3d.png"))

ease_back = lambda t, s=1.4: 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
FPS = 30; TOP = 205          # resting position, above her head
for wid, dur, t_in, t_out in [("w1", 2.7, 0.26, 2.44 - 0.35), ("w2", 3.3, 0.19, 3.3)]:
    d = os.path.join(V, f"logo_{wid}"); os.makedirs(d, exist_ok=True)
    for f in range(round(dur * FPS)):
        t = f / FPS; fr = Image.new("RGBA", (1080, 1920))
        p = min(1, max(0, (t - t_in) / 0.8))
        if t >= t_in:
            e = ease_back(p)
            sc = 0.82 + 0.18 * e
            y = TOP + (430 - TOP) * (1 - e)           # rises from behind her head
            op = min(1, (t - t_in) / 0.25)
            if t > t_out: op *= max(0, 1 - (t - t_out) / 0.3)
            lg = logo.resize((round(logo.width * sc), round(logo.height * sc)), Image.LANCZOS)
            if op < 1:
                al = np.asarray(lg).copy(); al[..., 3] = (al[..., 3] * op).astype(np.uint8); lg = Image.fromarray(al, "RGBA")
            fr.alpha_composite(lg, (round((1080 - lg.width) / 2), round(y)))
        fr.save(os.path.join(d, f"{f:03d}.png"))
    print("frames", wid)
