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
g += (f"concat=n={len(PIECES)}:v=0:a=1,aresample=48000,highpass=f=85,afftdn=nf=-30,"
      "equalizer=f=250:t=q:w=1.0:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=9000:t=h:w=1:g=1.5,"
      "acompressor=threshold=-22dB:ratio=3:attack=8:release=120,loudnorm=I=-15:TP=-2:LRA=8,"
      f"apad=whole_dur={DUR},asplit=2[voice][vkey];")
# music: duck under voice via sidechain
g += "[1:a]volume=0.55[mus];[mus][vkey]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=350:makeup=1[mduck];"
ins = ["-i", MAIN, "-i", os.path.join(M, "music.wav")]
mix = ["[voice]", "[mduck]"]
for j, (name, t, gain) in enumerate(cues["cues"]):
    ins += ["-i", os.path.join(M, "sfx", name + ".wav")]
    ms = int(t * 1000)
    g += f"[{j + 2}:a]volume={gain * 0.8:.3f},adelay={ms}|{ms}[s{j}];"
    mix.append(f"[s{j}]")
g += "".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{DUR},alimiter=limit=0.93:level=false[out]"
r = subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", g, "-map", "[out]", "-ar", "48000",
                    "-c:a", "pcm_s16le", os.path.join(M, "mix.wav")], capture_output=True, text=True)
if r.returncode:
    print(r.stderr[-3000:]); sys.exit(1)
print("mixed", len(cues["cues"]), "sfx cues, duration", DUR)
