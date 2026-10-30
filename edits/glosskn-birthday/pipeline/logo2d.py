"""Original black GLOSSKN wordmark (flat, 2D) rising from behind her head -> media/v3/logo_<id>/%03d.png frames."""
import os
from PIL import Image
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v3")
src = Image.open(os.path.join(P, "media", "logo_dark.png")).convert("RGBA")
W = 620; logo = src.resize((W, round(src.height * W / src.width)), Image.LANCZOS)
# light box behind the wordmark (like the brand logo card) so it stands out on the wall
BOXW, BOXH = 760, 240
card = Image.new("RGBA", (BOXW, BOXH), (243, 242, 242, 255))
card.alpha_composite(logo, ((BOXW - W) // 2, (BOXH - logo.height) // 2)); logo = card; W = BOXW
ease_back = lambda t, s=1.3: 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
FPS, TOP = 30, 190
for wid, dur, t_in, t_out in [("w1", 2.7, 0.26, 2.44 - 0.35), ("w2", 3.3, 0.19, 3.3)]:
    d = os.path.join(V, f"logo_{wid}"); os.makedirs(d, exist_ok=True)
    for f in range(round(dur * FPS)):
        t = f / FPS; fr = Image.new("RGBA", (1080, 1920))
        if t >= t_in:
            e = ease_back(min(1, (t - t_in) / 0.75)); y = TOP + (470 - TOP) * (1 - e)
            op = min(1, (t - t_in) / 0.25) * (max(0, 1 - (t - t_out) / 0.3) if t > t_out else 1)
            lg = logo.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * op)))
            fr.alpha_composite(lg, ((1080 - W) // 2, round(y)))
        fr.save(os.path.join(d, f"{f:03d}.png"))
    print("frames", wid)
