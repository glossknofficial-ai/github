"""Mix the piano bed (quiet) with the SFX cue sheet -> media/bed.wav. The founder's voice stays on her video track."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE); M = os.path.join(PROJECT, "media")
SFX = os.path.join(PROJECT, "..", "glosskn-reel", "media", "sfx")
cj = json.load(open(os.path.join(M, "cues.json")))
ins, g, mix = ["-i", os.path.join(M, "music.wav")], "[0:a]volume=0.16[m];", ["[m]"]
for j, (n, t, gain) in enumerate(cj["cues"]):
    ins += ["-i", os.path.join(SFX, n + ".wav")]; ms = int(t * 1000)
    g += f"[{j + 1}:a]volume={gain * 0.5:.3f},adelay={ms}|{ms}[s{j}];"; mix.append(f"[s{j}]")
g += "".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{cj['duration']}[out]"
r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", *ins, "-filter_complex", g, "-map", "[out]", "-ar", "48000",
                    "-c:a", "pcm_s16le", os.path.join(M, "bed.wav")], capture_output=True, text=True)
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
print("bed mixed with", len(cj["cues"]), "sfx")
