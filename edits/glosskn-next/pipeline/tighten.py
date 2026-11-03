"""Remove the pauses the founder pointed out (times on the founder.mp4 timeline), leaving a tiny natural breath.
Writes media/founder_tight.mp4 and data/words_tight.json (from the clean-audio word alignment)."""
import os, subprocess, json
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
SRC = os.path.join(M, "founder.mp4")
CUT = [(4.82, 6.10),    # "...for you." -> "So this box"
       (8.52, 8.78),    # "products," -> "a face wash"
       (10.58, 10.65),  # "makeup," -> "is super gentle"
       (18.98, 19.06),  # "super gentle," -> "non-greasy"
       (23.40, 23.80),  # "comes with" -> "power bands"
       (26.36, 26.92)]  # "wristbands" -> "which helps your clothes..."
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)
keep, t = [], 0.0
for a, b in CUT: keep.append((t, a)); t = b
keep.append((t, DUR))
fc, lab = "", ""
for i, (a, b) in enumerate(keep):
    fc += (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
           f"afade=t=in:d=0.015,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[a{i}];")
    lab += f"[v{i}][a{i}]"
fc += f"{lab}concat=n={len(keep)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", os.path.join(M, "founder_tight.mp4")], check=True)
def remap(t):
    off = 0.0
    for a, b in keep:
        if t < a: return a - off
        if t <= b: return t - off
        off += 0
    return t
# map each word onto the tightened timeline
shift = []; acc = 0.0
for a, b in CUT: acc += b - a; shift.append((b, acc))
def m(t):
    s = 0.0
    for (a, b), (_, acc) in zip(CUT, shift):
        if t >= b: s = acc
        elif t > a: return a - (acc - (b - a))
    return t - s
W = json.load(open(os.path.join(P, "data", "words_clean.json")))
out = [dict(w=w["w"], s=round(m(w["s"]), 3), e=round(m(w["e"]), 3)) for w in W]
json.dump(out, open(os.path.join(P, "data", "words_tight.json"), "w"))
newdur = DUR - sum(b - a for a, b in CUT)
json.dump({"duration": round(newdur, 3)}, open(os.path.join(P, "data", "edit_tight.json"), "w"))
print("tightened", round(DUR, 2), "->", round(newdur, 2), "s")
