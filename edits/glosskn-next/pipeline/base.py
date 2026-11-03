"""Join the three takes into one founder track (picture untouched, just scaled to 1080x1920):
v1 full line, v2 up to 'wristbands', v3 'which helps your clothes from getting wet'. Voice raised and levelled."""
import os, subprocess, json
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
CUTS = [("v1", 0.0, 22.45), ("v2", 0.45, 5.22), ("v3", 0.0, 2.62)]
fc, lab = "", ""
for i, (v, a, b) in enumerate(CUTS):
    fc += (f"[{i}:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,setsar=1,fps=30[v{i}];"
           f"[{i}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.04,afade=t=out:st={b - a - 0.06:.3f}:d=0.06[a{i}];")
    lab += f"[v{i}][a{i}]"
fc += (f"{lab}concat=n={len(CUTS)}:v=1:a=1[v][a0];"
       "[a0]highpass=f=80,acompressor=threshold=-30dB:ratio=2.5:attack=8:release=200:makeup=1,volume=24dB,alimiter=limit=0.89:level=false[a]")
ins = sum([["-i", os.path.join(M, v + ".mp4")] for v, _, _ in CUTS], [])
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", os.path.join(M, "founder.mp4")], check=True)
# word timings on the joined timeline
out, off = [], 0.0
for i, (v, a, b) in enumerate(CUTS):
    for w in json.load(open(os.path.join(P, "data", f"w{i + 1}.json"))):
        if a - 0.05 <= w["s"] < b - 0.05: out.append(dict(w=w["w"], s=round(w["s"] - a + off, 3), e=round(min(w["e"], b) - a + off, 3)))
    off += b - a
json.dump(out, open(os.path.join(P, "data", "words.json"), "w"))
print("founder", round(off, 2), "s,", len(out), "words; tail:", " ".join(x["w"] for x in out[-12:]))
