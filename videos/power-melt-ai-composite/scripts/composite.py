"""Composite the AI ingredient clip with the real-tube overlay.

  out = our #d1b8e3 set + (AI frame - AI empty plate) inside the upper band only
        then the transparent overlay (real tube, fill, in-tube streams, label reveal) on top.

Only the band above the tube mouth is taken from the AI clip, so its glass and the
watermark at the bottom never reach the output. Writes renders/final-video-only.mp4.

    python3 scripts/composite.py AI_CLIP.mp4
"""
import glob
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
clip = sys.argv[1]

bg = np.asarray(Image.open(ROOT / "assets" / "set-bg.png").convert("RGB")).astype(np.float32)
overlays = sorted(glob.glob(str(ROOT / "renders" / "overlay" / "*.png")))

# The AI clip is shifted up so its pours end at the (larger) tube mouth at y~560.
SHIFT = 130
# Upper band mask: full strength above y=470, fading to zero at the tube mouth (~550).
y = np.arange(H, dtype=np.float32)[:, None]
band = np.clip((550 - y) / 80, 0, 1)
band = (band * band * (3 - 2 * band))[..., None]

def decoder():
    return subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", clip, "-vf",
         f"fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6:5:5:0.0",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

dec = decoder()
frames_needed = len(overlays)
fsz = W * H * 3

def read():
    b = dec.stdout.read(fsz)
    return None if len(b) < fsz else np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)

# Empty plate: per-pixel median over moments when the upper band is (mostly) empty, so a
# leaf peeking in at t=0 or a thin stream in another sample is voted out. (Pass 1.)
pick = {0, 1, 2, 154, 155, 222, 223, 224, 225}     # ~0.0s, ~5.13s, ~7.4-7.5s at 30 fps
samples, idx = [], 0
while True:
    f = read()
    if f is None:
        break
    if idx in pick:
        samples.append(f)
    idx += 1
plate = np.median(np.stack(samples), axis=0)
plate = np.roll(plate, -SHIFT, axis=0)
dec.terminate()
dec = decoder()                                     # pass 2
enc = subprocess.Popen(
    ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p",
     str(ROOT / "renders" / "final-video-only.mp4")], stdin=subprocess.PIPE)

last = None
for i in range(frames_needed):
    f = read()
    if f is None:
        f = last
    last = f
    d = np.roll(f, -SHIFT, axis=0) - plate
    # soft noise gate: ignore tiny lighting flicker so the set stays perfectly clean
    mag = np.abs(d).max(axis=2, keepdims=True)
    gate = np.clip((mag - 4) / 10, 0, 1)
    t = i / FPS
    fade = np.clip((7.6 - t) / 0.2, 0, 1)           # AI layer bows out once the plum has left (before its fake label box appears)
    out = bg + band * gate * d * fade
    ov = np.asarray(Image.open(overlays[i]).convert("RGBA")).astype(np.float32)
    a = ov[..., 3:4] / 255.0
    out = ov[..., :3] * a + out * (1 - a)
    enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    if i % 50 == 0:
        print("frame", i)

enc.stdin.close(); enc.wait(); dec.terminate()
print("wrote renders/final-video-only.mp4")
