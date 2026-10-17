import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
NAME = sys.argv[1] if len(sys.argv) > 1 else 'Tara'
N = 2160; BG = np.array([213, 195, 230]) / 255.; BOX = np.array([225, 206, 228]) / 255.; INK = np.array([38, 36, 38]) / 255.
rng = np.random.default_rng(3)
def fblur(x, s):
    p = int(3 * s) + 2; H0, W0 = x.shape; x = np.pad(x, p, mode='edge'); h, w = x.shape
    k = np.fft.fftfreq(h)[:, None] ** 2 + np.fft.fftfreq(w)[None, :] ** 2
    return np.real(np.fft.ifft2(np.fft.fft2(x) * np.exp(-2 * np.pi ** 2 * s * s * k)))[p:p + H0, p:p + W0]
S = 1300; EDGE = 64                         # lid size, visible front edge depth
X0 = (N - S) // 2 - 40; Y0 = 1835 - S - EDGE
yy, xx = np.mgrid[0:N, 0:N].astype(float)
lid = (xx >= X0) & (xx < X0 + S) & (yy >= Y0) & (yy < Y0 + S)
front = (xx >= X0) & (xx < X0 + S) & (yy >= Y0 + S) & (yy < Y0 + S + EDGE)
def soft(m, s=0.7): return np.clip(fblur(m.astype(float), s), 0, 1)
lidA, frontA = soft(lid), soft(front)
# shadow: long and soft to the right, like the single-product images
box = np.clip(lidA + frontA, 0, 1)
sh = np.zeros((N, N)); ys, xs = np.where(box[::2, ::2] > .5); ys *= 2; xs *= 2
hgt = 1835 - ys; tx = np.clip((xs + 0.58 * hgt).astype(int), 0, N - 1); ty = np.clip((1835 - 0.105 * hgt).astype(int), 0, N - 1)
np.maximum.at(sh, (ty, tx), 0.62 * (1 - 0.8 * hgt / 1395))
sh = np.clip(fblur(sh, 4) * 3.2, 0, .62); dist = np.clip((xx - (X0 + S * .5)) / 900, 0, 1); sh = sh * (1 - dist) + fblur(sh, 16) * dist
con = ((yy > 1832) & (yy < 1840) & (xx > X0) & (xx < X0 + S)).astype(float); con = fblur(con, 5) * .5
img = BG * (1 - np.clip(np.maximum(sh, con), 0, .75))[..., None]
# lid: soft studio light from top-left, fine paper grain
u = (xx - X0) / S; v = (yy - Y0) / S
light = 1.035 - 0.07 * (0.55 * u + 0.45 * v)
grain = fblur(rng.normal(0, 1, (N, N)), 0.8) * 0.006
lidc = np.clip(BOX * (light + grain)[..., None], 0, 1)
# faint bevel on the lid rim
rim = np.clip(1 - np.minimum.reduce([xx - X0, X0 + S - 1 - xx, yy - Y0, Y0 + S - 1 - yy]) / 6, 0, 1) * lid
lidc = lidc * (1 - 0.05 * rim[..., None])
frontc = np.clip(BOX * (0.86 - 0.05 * ((yy - Y0 - S) / EDGE)) [..., None] * (1 + grain[..., None]), 0, 1)
# --- artwork on the lid: real GLOSSKN logo bottom-right, name in script above it
art = Image.new('L', (N, N), 0); 
logo = Image.open('/home/user/github/website/assets/logo.png').convert('RGBA'); logo = logo.crop(logo.getchannel('A').getbbox())
lw = int(S * 0.40); lh = round(logo.height * lw / logo.width); la = logo.getchannel('A').resize((lw, lh), Image.LANCZOS)
lx = X0 + S - int(S * 0.085) - lw; ly = Y0 + S - int(S * 0.10) - lh
art.paste(la, (lx, ly), la)
F = ImageFont.truetype('../fonts/Parisienne-Regular.ttf', 400)
bb = F.getbbox(NAME); tw, th = bb[2] - bb[0], bb[3] - bb[1]
tgt_w = int(lw * 0.74); sc = tgt_w / tw
T = Image.new('L', (tw + 40, th + 40), 0); ImageDraw.Draw(T).text((20 - bb[0], 20 - bb[1]), NAME, font=F, fill=255)
T = T.resize((int(T.width * sc), int(T.height * sc)), Image.LANCZOS)
tx0 = lx + (lw - T.width) // 2; ty0 = ly - int(lh * 0.45) - T.height
art.paste(T, (tx0, ty0), T)
A = np.asarray(art).astype(float) / 255.
lidc = lidc * (1 - A[..., None]) + INK * A[..., None]
out = img * (1 - box[..., None]) + (lidc * lidA[..., None] + frontc * frontA[..., None])
res = Image.fromarray(np.clip(out * 255, 0, 255).round().astype(np.uint8))
res.save(f'engraved-{NAME.lower()}.png'); res.resize((800, 800), Image.LANCZOS).save('v.jpg', quality=90)
