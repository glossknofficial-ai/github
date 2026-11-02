"""GLOSSKN cart promo: same design, livelier. The animation is kept as is; the two long static holds
(cart, then 'LAST FEW hours left' cake) get a slow eased camera push so the frame keeps breathing, and the
pale lilac is given a little contrast and richness. Labels, packaging and logo are not altered."""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(P, "media", "source.mp4"), os.path.join(P, "renders", "GLOSSKN-cart-smooth.mp4")
FPS = 30
# zoom keys (seconds, zoom, centre-x, centre-y): still during the fly-in, push on the cart, ease back
# through the crossfade, push on the cake/headline
K = [(0.0, 1.0, .5, .3), (2.8, 1.0, .5, .3), (7.45, 1.035, .5, .3), (8.35, 1.0, .5, .3), (12.77, 1.05, .5, .3)]   # anchored high: header and wheels stay in frame
def seg(key, i):   # smoothstep between consecutive keys, as an ffmpeg expression of time `it`
    out = str(K[-1][key])
    for (t0, *v0), (t1, *v1) in reversed(list(zip(K, K[1:]))):
        a, b = v0[key - 1], v1[key - 1]
        u = f"clip((it-{t0})/{t1 - t0},0,1)"
        out = f"if(lt(it,{t1}),{a}+({b}-{a})*({u}*{u}*(3-2*{u})),{out})"
    return out
z, cx, cy = seg(1, 0), seg(2, 0), seg(3, 0)
expr = lambda e: e.replace("it", "(on/%d)" % FPS)
vf = (f"zoompan=z='{expr(z)}':x='(iw-iw/zoom)*{expr(cx)}':y='(ih-ih/zoom)*{expr(cy)}':d=1:s=2160x3840:fps={FPS},"
      "eq=contrast=1.07:saturation=1.16:gamma=0.98,vibrance=intensity=0.12,format=yuv420p")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-movflags", "+faststart", OUT], check=True)
print("done", OUT)
