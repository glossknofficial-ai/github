"""Layers for the rebuilt cart reel.
- Glitch frames in the source (header + cart vanish: 30-32, 63-65, 96-97) are removed.
- The story->cart fly-in is slowed (SLOW x) with motion-interpolated in-betweens.
- Background separation is strict: only pixels that match the flat lilac (#ECE4ED) within a hair, in regions
  bigger than a speck, become transparent. Products, labels, packaging and the logo are left pixel-for-pixel."""
import os, subprocess, glob
import numpy as np
from PIL import Image
from scipy import ndimage
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media"); K = os.path.join(M, "k")
BG = np.array([236, 228, 237], np.int16); TOL, MIN_AREA = 4, 160
GLITCH = [30, 31, 32, 63, 64, 65, 96, 97]; END = 100; SLOW = 1.8
def matte(rgb):
    bgl = (np.abs(rgb.astype(np.int16) - BG).max(axis=2) <= TOL)
    lab, n = ndimage.label(bgl); sizes = ndimage.sum(bgl, lab, range(1, n + 1))
    keep = np.isin(lab, np.nonzero(sizes >= MIN_AREA)[0] + 1)          # specks inside products stay opaque
    a = 1.0 - ndimage.gaussian_filter(keep.astype(np.float32), 0.6)    # 1-px soft edge
    return np.dstack([rgb, (np.clip(a, 0, 1) * 255).astype(np.uint8)])
sel = "+".join(f"eq(n,{g})" for g in GLITCH)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(M, "source.mp4"), "-vf",
                f"trim=end_frame={END},select='not({sel})',setpts=N/30/TB,scale=1080:1920:flags=lanczos,setpts={SLOW}*PTS,"
                "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none",
                os.path.join(K, "a", "%04d.png")], check=True)
for f in sorted(glob.glob(os.path.join(K, "a", "*.png"))):
    Image.fromarray(matte(np.asarray(Image.open(f).convert("RGB"))), "RGBA").save(f)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(K, "a", "%04d.png"), "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-auto-alt-ref", "0", os.path.join(M, "fgA.webm")], check=True)
def frame(n):
    out = os.path.join(M, f"f{n}.png")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(M, "source.mp4"), "-vf", f"select='eq(n,{n})'",
                        "-vsync", "0", "-frames:v", "1", "-update", "1", out], check=True)
    return np.asarray(Image.open(out).convert("RGB").resize((1080, 1920), Image.LANCZOS))
hold = matte(frame(150)); Image.fromarray(hold, "RGBA").save(os.path.join(M, "holdA.png"))
yy, xx = np.mgrid[0:1920, 0:1080]; cx, cy, r = 805, 1436, 150
badge = hold.copy(); badge[..., 3] = np.where((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r, badge[..., 3], 0)
Image.fromarray(badge, "RGBA").crop((cx - r, cy - r, cx + r, cy + r)).save(os.path.join(M, "badge.png"))
x0, y0, x1, y1 = 40, 650, 560, 1000
ink = hold[y0:y1, x0:x1, :3].astype(int).sum(2) < 200
t = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); t[..., 3] = np.where(ink, 255, 0)
Image.fromarray(t, "RGBA").save(os.path.join(M, "title_mask.png"))
b = matte(frame(300)); b[430:850, :, 3] = 0                              # old headline out, logo (above) kept
Image.fromarray(b, "RGBA").save(os.path.join(M, "fgB.png"))
print("A frames", len(glob.glob(os.path.join(K, "a", "*.png"))))
