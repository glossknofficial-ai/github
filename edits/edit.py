import json, os, subprocess, sys

U = "/root/.claude/uploads/9c33fb63-44ba-5032-927b-020ae3867ced/"
S = os.path.dirname(os.path.abspath(__file__))
MAIN = U + "1dd37292-After_1.mp4"
BR = {
    "robe": U + "cf0c6cdb-WhatsApp_Video_2026-10-04_at_3.00.39_PM.mp4",
    "floral": U + "4e9865cf-WhatsApp_Video_2026-10-04_at_3.02.49_PM.mp4",
    "close": U + "024d7f60-WhatsApp_Video_2026-10-04_at_3.01.51_PM.mp4",  # landscape
}
W, H, FPS = 2160, 3840, 30
SEG = os.path.join(S, "seg"); os.makedirs(SEG, exist_ok=True)
PREVIEW = "--preview" in sys.argv
if PREVIEW:
    W, H = 1080, 1920

# Kept source ranges (dead air removed), grouped by shot. Shot changes get a whoosh.
SHOTS = [
    [(1.80, 4.65)],                                            # sofa intro
    [(5.75, 6.80), (7.07, 9.55)],                              # desk, side angle
    [(11.02, 13.65), (13.93, 17.24), (17.42, 19.32)],          # office close-up
    [(19.82, 21.89), (22.13, 23.20), (23.47, 25.80), (26.01, 29.17)],  # sofa + bottle
    [(29.94, 31.36), (31.61, 32.03), (32.19, 34.09), (34.25, 40.18),
     (40.44, 41.91), (42.26, 45.36), (45.64, 45.96), (46.18, 47.87)],  # curtain (last part)
    [(48.10, 50.04), (50.37, 50.94), (51.16, 52.40)],          # CTA with product
]
# Source ranges where she is not facing the camera in the last part -> B-roll (file, in-point)
BROLL = [
    ((30.60, 32.10), "robe", 0.0),
    ((33.40, 34.25), "floral", 0.3),
    ((41.20, 43.55), "close", 0.0),
    ((43.55, 45.64), "floral", 1.3),
    ((45.64, 46.60), "robe", 2.0),
]

q = lambda x: round(x * FPS) / FPS  # snap every cut to a frame boundary
SHOTS = [[(q(a), q(b)) for a, b in shot] for shot in SHOTS]
BROLL = [((q(a), q(b)), n, off) for (a, b), n, off in BROLL]

GRADE = "eq=contrast=1.06:saturation=1.08:gamma=0.98,unsharp=5:5:0.6:5:5:0.0"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)


# Build the output timeline: list of pieces (src_a, src_b, out_start)
pieces, shot_starts, t = [], [], 0.0
for si, shot in enumerate(SHOTS):
    shot_starts.append(t)
    for pi, (a, b) in enumerate(shot):
        pieces.append(dict(a=a, b=b, out=t, shot=si, idx=pi))
        t += b - a
TOTAL = t


def src_to_out(x):
    for p in pieces:
        if p["a"] <= x <= p["b"]:
            return p["out"] + x - p["a"]
    # in a removed gap: snap to next piece start
    return min((p["out"] for p in pieces if p["a"] >= x), default=TOTAL)


# Split each piece further where B-roll covers it, producing video sub-segments
vsegs = []
for p in pieces:
    cuts = {p["a"], p["b"]}
    for (ba, bb), _, _ in BROLL:
        for c in (ba, bb):
            if p["a"] < c < p["b"]:
                cuts.add(c)
    cuts = sorted(cuts)
    for a, b in zip(cuts, cuts[1:]):
        br = next(((n, off, ba) for (ba, bb), n, off in BROLL if ba <= a and b <= bb), None)
        vsegs.append(dict(a=a, b=b, shot=p["shot"], idx=p["idx"], broll=br))

broll_used = {}
for i, v in enumerate(vsegs):
    d = v["b"] - v["a"]
    import hashlib
    key = hashlib.md5(json.dumps([v["a"], v["b"], v["shot"], v["idx"], v["broll"], W, GRADE, v["broll"] and v["broll"][0] == "close" and 2]).encode()).hexdigest()[:10]
    out = os.path.join(SEG, f"c_{key}.mp4")
    v["file"] = out
    if os.path.exists(out):
        continue
    if v["broll"]:
        name, off, ba = v["broll"]
        ss = off + (src_to_out(v["a"]) - src_to_out(ba))
        src = BR[name]
        if name == "close":  # landscape: full-bleed 9:16 crop around the eye/hand, slow push-in
            fc = (f"[0:v]crop=ih*9/16:ih:(iw-ow)*0.42:0,scale={W}:{H}:flags=lanczos,"
                  f"zoompan=z='1.02+0.05*on/{int(d*FPS)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},"
                  f"{GRADE},tpad=stop_mode=clone:stop_duration=0.5,format=yuv420p[v]")
        else:  # vertical b-roll: fill frame, slow push-in
            fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
                  f"zoompan=z='1.03+0.05*on/{int(d*FPS)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},"
                  f"{GRADE},format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{d:.3f}", "-i", src,
             "-filter_complex", fc, "-map", "[v]", "-an", "-r", str(FPS), "-frames:v", str(round(d * FPS)),
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", out])
    else:
        # Jump-cut punch-in: alternate framing every other piece within a shot
        z = 1.0 if v["idx"] % 2 == 0 else 1.14
        if v["shot"] == 5 and v["idx"] == 0:
            z = 1.0
        fc = (f"[0:v]crop=iw/{z}:ih/{z}:(iw-iw/{z})/2:(ih-ih/{z})*0.3,"
              f"scale={W}:{H}:flags=lanczos,{GRADE},fps={FPS},format=yuv420p[v]")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{v['a']:.3f}", "-t", f"{d:.3f}", "-i", MAIN,
             "-filter_complex", fc, "-map", "[v]", "-an", "-r", str(FPS), "-frames:v", str(round(d * FPS)),
             "-c:v", "libx264", "-preset", "medium", "-crf", "14", out])
    v["file"] = out
    print(f"seg {i:02d} {v['a']:.2f}-{v['b']:.2f} {'BROLL '+v['broll'][0] if v['broll'] else ''}", flush=True)

with open(os.path.join(SEG, "list.txt"), "w") as f:
    for v in vsegs:
        f.write(f"file '{v['file']}'\n")
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(SEG, "list.txt"),
     "-c", "copy", os.path.join(S, "video_only.mp4")])

# ---- Audio: concatenate kept voice ranges with tiny fades, clean up, add SFX ----
af = []
for i, p in enumerate(pieces):
    d = p["b"] - p["a"]
    af.append(f"[0:a]atrim={p['a']}:{p['b']},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.012,afade=t=out:st={d-0.015:.3f}:d=0.015[a{i}]")
voice = ";".join(af) + ";" + "".join(f"[a{i}]" for i in range(len(pieces))) + \
    f"concat=n={len(pieces)}:v=0:a=1,highpass=f=80,afftdn=nf=-30," \
    f"equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=120," \
    f"loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[voice]"

sfx = []  # (file, time, gain)
for si in range(1, len(SHOTS)):
    sfx.append(("whoosh", shot_starts[si] - 0.28, 0.35))
for (ba, bb), _, _ in BROLL:
    t0 = src_to_out(ba)
    if all(abs(t0 - s[1]) > 0.5 for s in sfx):
        sfx.append(("whoosh", t0 - 0.25, 0.28))
sfx.append(("ding", shot_starts[5] + 0.05, 0.22))  # product reveal
caption_sfx = os.path.join(S, "caption_pops.json")
if os.path.exists(caption_sfx):
    sfx += [("pop", t0, 0.22) for t0 in json.load(open(caption_sfx))]

inputs = ["-i", MAIN]
parts = [voice]
mix = ["[voice]"]
for j, (n, t0, g) in enumerate(sfx):
    inputs += ["-i", os.path.join(S, "sfx", n + ".wav")]
    ms = max(0, int(t0 * 1000))
    parts.append(f"[{j+1}:a]volume={g},adelay={ms}|{ms}[s{j}]")
    mix.append(f"[s{j}]")
parts.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95[aout]")
run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[aout]",
     "-c:a", "pcm_s16le", os.path.join(S, "audio.wav")])

json.dump(dict(total=TOTAL, pieces=pieces, shot_starts=shot_starts), open(os.path.join(S, "timeline.json"), "w"))
print("total", round(TOTAL, 2), "sfx", len(sfx))
