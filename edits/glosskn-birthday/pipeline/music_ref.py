"""Music bed taken from the reference reel (instrumental stem separated from her voice -> media/ref_music.wav).
Like the reference, the music comes in on "I was literally raising two children"; the reference's beat lands on "raising"."""
import json, os, subprocess, wave
import numpy as np

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
cj = json.load(open(os.path.join(M, "cues.json"))); DUR, END_AT = cj["duration"], cj["end_at"]
WORDS = json.load(open(os.path.join(P, "data", "words_v3.json")))
t_word = lambda w: next(x["s"] for x in WORDS if x["w"].lower().startswith(w))
SR = 48000; HIT_REF = 12.72                       # first downbeat in the reference music
START = t_word("literally") - 0.30; HIT = t_word("raising")
r = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(M, "ref_music.wav"), "-af", "highpass=f=200,highpass=f=200,afftdn=nf=-40", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                   capture_output=True).stdout
ref = np.frombuffer(r, np.float32).reshape(-1, 2).astype(np.float64)
src0 = HIT_REF - (HIT - START)                     # reference time that plays at START
seg = ref[int(src0 * SR): int(src0 * SR) + int((DUR - START) * SR)]
out = np.zeros((int(DUR * SR), 2)); i = int(START * SR); out[i:i + len(seg)] = seg
t = np.arange(len(out)) / SR
env = np.interp(t, [0, START, START + 0.6, END_AT - 0.2, END_AT + 0.4, DUR - 1.6, DUR], [0, 0, 1, 1, 1.3, 1.3, 0])
out *= env[:, None]
body = out[int((START + 1) * SR): int(END_AT * SR)]
out *= 10 ** (-40 / 20) / np.sqrt((body ** 2).mean())    # bed sits well under her voice
out = np.clip(out, -0.98, 0.98)
w = wave.open(os.path.join(M, "music.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype("<i2").tobytes()); w.close()
print("music from ref", round(src0, 2), "placed at", round(START, 2), "peak", round(float(np.abs(out).max()), 2))
