"""Join the three takes into one tight founder track.
- Voice: the clean vocal stem (background noise separated out), levelled; silent between phrases.
- Cuts: every pause longer than MAX_GAP is trimmed out (picture + voice together), so there are no dead gaps.
- Stumble removed: v2 ends at 'wristbands', v3 continues 'which helps your clothes from getting wet'.
Writes media/founder.mp4 and data/words.json on the new timeline."""
import os, subprocess, json
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
RANGES = [("v1", 0.0, 22.45, 1), ("v2", 0.45, 5.22, 2), ("v3", 0.0, 2.62, 3)]
MAX_GAP, PAD = 0.22, 0.12
N = {"v1": 1, "v2": 2, "v3": 3}
def speech_intervals(v, a, b):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(M, f"{v}_voice.wav"), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(r, np.float32); hop = 160
    db = np.array([20 * np.log10(np.sqrt((x[i:i + hop] ** 2).mean()) + 1e-9) for i in range(0, len(x) - hop, hop)])
    db = np.convolve(db, np.ones(3) / 3, "same"); thr = max(np.percentile(db, 30) + 5, -56)
    on = db > thr
    for w in json.load(open(os.path.join(P, "data", f"w{N[v]}.json"))):   # never cut inside an aligned word
        on[int(w["s"] * 100):int(w["e"] * 100) + 1] = True
    iv, s = [], None
    for k in range(int(a * 100), min(len(on), int(b * 100))):
        if on[k] and s is None: s = k
        if not on[k] and s is not None: iv.append([s / 100, k / 100]); s = None
    if s is not None: iv.append([s / 100, min(b, len(on) / 100)])
    iv = [[max(a, s - PAD), min(b, e + PAD)] for s, e in iv if e - s > 0.04]
    out = []
    for s, e in iv:                                           # merge short pauses: keep natural rhythm inside phrases
        if out and s - out[-1][1] <= MAX_GAP: out[-1][1] = e
        else: out.append([s, e])
    return out
keep = []
for v, a, b, n in RANGES:
    for s, e in speech_intervals(v, a, b): keep.append((v, round(s, 3), round(e, 3), n))
fc, lab = "", ""
ins = sum([["-i", os.path.join(M, v + ".mp4"), "-i", os.path.join(M, v + "_voice.wav")] for v, _, _, _ in RANGES], [])
idx = {v: 2 * i for i, (v, _, _, _) in enumerate(RANGES)}
for i, (v, s, e, _) in enumerate(keep):
    fc += (f"[{idx[v]}:v]trim={s}:{e},setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,setsar=1,fps=30[v{i}];"
           f"[{idx[v] + 1}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.02,afade=t=out:st={e - s - 0.03:.3f}:d=0.03[a{i}];")
    lab += f"[v{i}][a{i}]"
fc += (f"{lab}concat=n={len(keep)}:v=1:a=1[v][a0];"
       "[a0]highpass=f=90,lowpass=f=12000,acompressor=threshold=-30dB:ratio=2.5:attack=8:release=200:makeup=1,volume=24dB,alimiter=limit=0.89:level=false[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", os.path.join(M, "founder.mp4")], check=True)
# remap word timings onto the new timeline
words, off = [], 0.0
for v, s, e, n in keep:
    for w in json.load(open(os.path.join(P, "data", f"w{n}.json"))):
        mid = (w["s"] + w["e"]) / 2
        if s - 0.02 <= mid <= e + 0.02:
            words.append(dict(w=w["w"], s=round(max(w["s"], s) - s + off, 3), e=round(min(w["e"], e) - s + off, 3)))
    off += e - s
seen, out = set(), []
for w in words:
    k = (w["w"], round(w["s"], 1))
    if k not in seen: seen.add(k); out.append(w)
json.dump(out, open(os.path.join(P, "data", "words.json"), "w"))
json.dump({"duration": round(off, 3), "segments": len(keep)}, open(os.path.join(P, "data", "edit.json"), "w"))
print("founder", round(off, 2), "s from", len(keep), "speech pieces;", len(out), "words")
