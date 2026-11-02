"""Find scale/rotation/offset that puts clip 1's box exactly where clip 3's box is (phase correlation on edges)."""
import subprocess, numpy as np, json, os
from scipy import ndimage
from PIL import Image
def fr(c, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", f"media/{c}.mp4", "-frames:v", "1", "-vf", "scale=180:320,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(320, 180).astype(float)
A, B = fr("clip3", 15.6), fr("clip1", 12.0)                      # same state: two bottles in, no hands
def edges(x):
    g = ndimage.gaussian_filter(x, 1.0); return np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))
EA, EB = edges(A), edges(B)
win = np.zeros_like(EA); win[10:250, 15:175] = 1; win = ndimage.gaussian_filter(win, 6)
FA = np.fft.fft2(EA * win); c = np.array([160., 90.])
def warp(img, s, th):
    r = np.deg2rad(th); R = np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]]) / s
    return ndimage.affine_transform(img, R, offset=c - R @ c, order=1)
best = None
for s in np.arange(1.0, 1.18, 0.01):
    for th in np.arange(1.0, 7.01, 0.5):
        X = FA * np.conj(np.fft.fft2(warp(EB, s, th) * win)); X /= np.abs(X) + 1e-9
        cc = np.real(np.fft.ifft2(X)); k = np.unravel_index(np.argmax(cc), cc.shape)
        if best is None or cc[k] > best[0]:
            best = (cc[k], s, th, k[1] if k[1] < 90 else k[1] - 180, k[0] if k[0] < 160 else k[0] - 320)
v, s, th, dx, dy = best; print("score %.3f scale %.2f rot %.1f dx %d dy %d (at 180x320)" % best)
json.dump({"s": float(s), "rot": float(th), "dx": float(dx) * 4, "dy": float(dy) * 4}, open("media/align_clip1.json", "w"))
W = ndimage.shift(warp(B, s, th), (dy, dx), order=1)
Image.fromarray(np.dstack([A, W, A]).clip(0, 255).astype(np.uint8)).resize((360, 640)).save(
    "/tmp/claude-0/-home-user-github/9c33fb63-44ba-5032-927b-020ae3867ced/scratchpad/align_check.png")
