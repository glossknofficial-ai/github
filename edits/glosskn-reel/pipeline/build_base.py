"""Render the 4K picture edit (no audio): jump cuts, punch-ins, B-roll, grade -> media/base.mp4"""
import hashlib, json, os, subprocess, sys
from edl import *

W, H = 2160, 3840
GRADE = "eq=contrast=1.06:saturation=1.07:gamma=0.98,unsharp=5:5:0.55:5:5:0.0"
MEDIA = os.path.join(PROJECT, "media"); CACHE = os.path.join(PROJECT, ".cache", "seg")
os.makedirs(MEDIA, exist_ok=True); os.makedirs(CACHE, exist_ok=True)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


# Split pieces at zoom toggles and B-roll boundaries
segs = []
for p in PIECES:
    cuts = {p["a"], p["b"]}
    for t in ZOOM_TOGGLES + [x for b in BROLL for x in b[:2]]:
        if p["a"] < t < p["b"]:
            cuts.add(t)
    cuts = sorted(cuts)
    for a, b in zip(cuts, cuts[1:]):
        if round((b - a) * FPS) == 0:
            continue
        br = next(((n, off, ba, bb) for ba, bb, n, off in BROLL if ba <= a and b <= bb), None)
        segs.append(dict(a=a, b=b, shot=p["shot"], piece_a=p["a"], broll=br))

# Framing: each jump cut and each zoom toggle flips between wide and punched-in; new shots open wide
zoom, prev_shot, prev_piece = 1.0, None, None
for s in segs:
    if s["shot"] != prev_shot:
        zoom = 1.0
    elif s["piece_a"] != prev_piece or s["a"] in ZOOM_TOGGLES:
        zoom = PUNCH if zoom == 1.0 else 1.0
    s["zoom"] = zoom; prev_shot, prev_piece = s["shot"], s["piece_a"]

files = []
for s in segs:
    n = round((s["b"] - s["a"]) * FPS)
    key = hashlib.md5(json.dumps([s, W, GRADE, 3]).encode()).hexdigest()[:12]
    out = os.path.join(CACHE, f"{key}.mp4"); files.append(out)
    if os.path.exists(out):
        continue
    if s["broll"] and s["broll"][0] == "lab":  # still image + continuous camera move across the whole window
        name, off, ba, bend = s["broll"]
        k0 = round((to_out(s["a"]) - to_out(ba)) * FPS); NT = max(1, round((to_out(bend, "prev") - to_out(ba)) * FPS))
        p = f"((on+{k0})/{NT})"
        zexpr = f"1.0+0.12*{p}" if off == 0 else f"1.16-0.12*{p}"
        xexpr = "iw/2-iw/zoom/2" if off == 0 else f"(iw-iw/zoom)*(0.3+0.4*{p})"
        fc = (f"[0:v]scale={W}:{H},zoompan=z='{zexpr}':x='{xexpr}':y='(ih-ih/zoom)*0.45':d=1:s={W}x{H}:fps={FPS},"
              f"{GRADE},format=yuv420p[v]")
        run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", BROLL_FILES["lab"],
             "-filter_complex", fc, "-map", "[v]", "-an", "-r", str(FPS), "-frames:v", str(n),
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", out])
        print(f"{s['a']:6.2f}-{s['b']:6.2f} lab", flush=True)
        continue
    if s["broll"]:
        name, off, ba, _ = s["broll"]
        ss = off + (to_out(s["a"]) - to_out(ba))
        crop = "crop=ih*9/16:ih:(iw-ow)*0.42:0," if name == "close" else ""
        fc = (f"[0:v]{crop}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
              f"zoompan=z='1.03+0.05*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},"
              f"{GRADE},tpad=stop_mode=clone:stop_duration=0.5,format=yuv420p[v]")
        src = BROLL_FILES[name]
    else:
        z = s["zoom"]; ss = s["a"]
        fc = (f"[0:v]crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.3,scale={W}:{H}:flags=lanczos,"
              f"{GRADE},fps={FPS},tpad=stop_mode=clone:stop_duration=0.5,format=yuv420p[v]")
        src = MAIN
    run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{ss:.3f}", "-i", src, "-filter_complex", fc, "-map", "[v]",
         "-an", "-r", str(FPS), "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "14", out])
    print(f"{s['a']:6.2f}-{s['b']:6.2f} z={s['zoom']} {s['broll'][0] if s['broll'] else ''}", flush=True)

lst = os.path.join(CACHE, "list.txt")
open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(MEDIA, "base.mp4")])
print("segments", len(segs), "total", TOTAL)
