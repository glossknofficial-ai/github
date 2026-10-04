"""Voice (edited, cleaned) + music (ducked under voice) + SFX cues -> media/mix.wav"""
import json, os, subprocess, sys
from edl import *

M = os.path.join(PROJECT, "media")
cues = json.load(open(os.path.join(M, "cues.json")))
DUR = cues["duration"]

af = []
for i, p in enumerate(PIECES):
    d = p["b"] - p["a"]
    af.append(f"[0:a]atrim={p['a']}:{p['b']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}]")
g = ";".join(af) + ";" + "".join(f"[a{i}]" for i in range(len(PIECES)))
# Voice stays original: no denoise/EQ/compression - only a linear level match to ~-16 LUFS
raw = os.path.join(M, "voice_raw.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", MAIN, "-filter_complex",
                g + f"concat=n={len(PIECES)}:v=0:a=1,aresample=48000[v]", "-map", "[v]", raw], check=True)
meas = subprocess.run(["ffmpeg", "-nostats", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(meas.split("Summary:")[1].split("I:")[1].split("LUFS")[0])
gain = -16.0 - I
g = (f"[0:a]volume={gain:.2f}dB,alimiter=limit=0.95:level=false,"
     f"apad=whole_dur={DUR},asplit=2[voice][vkey];")
# music: duck under voice via sidechain
g += "[1:a]volume=0.32[mus];[mus][vkey]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=400:makeup=1[mduck];"
ins = ["-i", raw, "-i", os.path.join(M, "music.wav")]
mix = ["[voice]", "[mduck]"]
for j, (name, t, gain) in enumerate(cues["cues"]):
    ins += ["-i", os.path.join(M, "sfx", name + ".wav")]
    ms = int(t * 1000)
    g += f"[{j + 2}:a]volume={gain * 0.6:.3f},adelay={ms}|{ms}[s{j}];"
    mix.append(f"[s{j}]")
g += "".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{DUR},alimiter=limit=0.93:level=false[out]"
r = subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", g, "-map", "[out]", "-ar", "48000",
                    "-c:a", "pcm_s16le", os.path.join(M, "mix.wav")], capture_output=True, text=True)
if r.returncode:
    print(r.stderr[-3000:]); sys.exit(1)
print("mixed", len(cues["cues"]), "sfx cues, duration", DUR)
