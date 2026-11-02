"""Music + soft pops for the cart reel -> media/v2/bed.wav (Diwali track from the GLOSSKN festive edit)."""
import os, json, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v2")
cj = json.load(open(os.path.join(V, "cues.json"))); DUR = cj["dur"]
MUSIC = os.path.join(P, "..", "glosskn-emotional", "media", "music.mp3"); POP = os.path.join(P, "..", "glosskn-reel", "media", "sfx", "pop.wav")
ins = ["-i", MUSIC] + sum([["-i", POP] for _ in cj["pops"]], [])
g = f"[0:a]atrim=start=9.5:duration={DUR},asetpts=PTS-STARTPTS,aresample=48000,volume=-1dB,afade=t=in:d=0.4,afade=t=out:st={DUR - 1.4}:d=1.4[m];"
mix = "[m]"
for k, t in enumerate(cj["pops"]):
    ms = int(t * 1000); g += f"[{k + 1}:a]aresample=48000,volume=0.9,adelay={ms}|{ms}[p{k}];"; mix += f"[p{k}]"
g += f"{mix}amix=inputs={len(cj['pops']) + 1}:normalize=0:duration=first,alimiter=limit=0.89:level=false[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", g, "-map", "[out]", "-ac", "2", "-c:a", "pcm_s16le", os.path.join(V, "bed.wav")], check=True)
print("bed ok")
