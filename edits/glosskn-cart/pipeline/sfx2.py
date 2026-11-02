"""Sound effects only (no music), placed like the hits in the reference: tick on lift, pop on landing, sparkle on shimmer."""
import os, json, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v2")
SFX = os.path.join(P, "..", "glosskn-reel", "media", "sfx")
cj = json.load(open(os.path.join(V, "cues.json"))); DUR = cj["dur"]
cues = [("tick", t, 0.45) for t in cj["ticks"]] + [("pop", t, 1.0) for t in cj["pops"]] + [("sparkle", cj["shine"], 0.5)]
ins = ["-f", "lavfi", "-t", str(DUR), "-i", "anullsrc=r=48000:cl=stereo"]; g = ""; mix = "[0:a]"
for k, (n, t, gain) in enumerate(cues):
    ins += ["-i", os.path.join(SFX, n + ".wav")]; ms = int(t * 1000)
    g += f"[{k + 1}:a]aresample=48000,volume={gain},adelay={ms}|{ms}[s{k}];"; mix += f"[s{k}]"
g += f"{mix}amix=inputs={len(cues) + 1}:normalize=0:duration=first,volume=4dB,alimiter=limit=0.89:level=false[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[out]", "-c:a", "pcm_s16le", os.path.join(V, "sfx.wav")], check=True)
print("sfx", [(n, round(t, 2)) for n, t, _ in cues])
