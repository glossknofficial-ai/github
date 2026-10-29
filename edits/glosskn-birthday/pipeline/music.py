"""Original soft piano bed (I–V–vi–IV arpeggios, ~68 BPM) that swells into the end card -> media/music.wav"""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.dirname(HERE)
SR = 48000
cj = json.load(open(os.path.join(PROJECT, "media", "cues.json")))
DUR = cj["duration"]; END_AT = cj["end_at"]
rng = np.random.default_rng(3)
N = int(DUR * SR); mix = np.zeros((N, 2))
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)


def piano(f, d=3.0, vel=1.0):
    t = np.arange(int(SR * d)) / SR
    s = sum(a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (0.9 + 0.7 * k))
            for k, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06)])
    s *= np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.2)
    return s * vel


def add(sig, at, gain, pan=0.0):
    i = max(0, int(at * SR))
    if i >= N: return
    st = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    j = min(N, i + len(st)); mix[i:j] += st[: j - i] * gain


BPM = 68; beat = 60 / BPM; bar = 4 * beat
PROG = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69])]  # C G/B Am F
for b in range(int(DUR / bar) + 1):
    t0 = b * bar; root, ch = PROG[b % 4]
    build = min(1.0, 0.55 + 0.45 * t0 / max(1, END_AT))          # slowly opens up over the story
    add(piano(mtof(root), 4.5, .9), t0, 0.16 * build, -0.2)
    add(piano(mtof(root + 12), 4.0, .6), t0, 0.08 * build, -0.1)
    pattern = [0, 1, 2, 3, 2, 1, 2, 3] if t0 < END_AT - bar else [0, 2, 3, 2, 1, 3, 2, 3]
    for k, idx in enumerate(pattern):
        tt = t0 + k * beat / 2 + float(rng.uniform(-0.006, 0.006))   # tiny human timing
        add(piano(mtof(ch[idx]), 2.6, 0.75 + 0.25 * (k % 2 == 0)), tt, 0.085 * build, (idx - 1.5) * 0.25)
    if b % 2 == 1 and t0 > 20:                                         # sparse top melody in the second half
        add(piano(mtof(ch[-1] + 12), 3.0, .6), t0 + beat * 2.5, 0.05 * build, 0.3)

# final chord ringing under the end card
for m in (48, 60, 64, 67, 72, 76):
    add(piano(mtof(m), 4.0, .9), END_AT + 0.1, 0.09, (m - 62) / 30)

# small room reverb
n = int(SR * 2.2); t = np.arange(n) / SR
for c in range(2):
    ir = rng.standard_normal(n) * np.exp(-t * 3.2); ir[: int(0.02 * SR)] = 0
    L = N + n
    wet = np.fft.irfft(np.fft.rfft(mix[:, c], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, c] = mix[:, c] * 0.75 + wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix[:, c])) * 0.35
fi = int(1.5 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(1.8 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.7
w = wave.open(os.path.join(PROJECT, "media", "music.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype("<i2").tobytes()); w.close()
print("music", DUR, "s")
