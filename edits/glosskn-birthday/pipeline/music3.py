"""Emotional bed from real recorded instruments (MusyngKite piano / strings / harp / bells samples) -> media/music.wav.
Soft piano arpeggios that open up with strings at "But then there were little moments" and bloom into the end card."""
import functools, json, os, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
SMP = os.path.join(P, "..", "glosskn-festive", "media", "samples")
cj = json.load(open(os.path.join(P, "media", "cues.json"))); DUR = cj["duration"]; END_AT = cj["end_at"]
LIFT = 31.1   # "But then there were little moments"
SR = 48000; N = int(DUR * SR); mix = np.zeros((N, 2)); rng = np.random.default_rng(5)
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

@functools.lru_cache(None)
def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(r, np.float32).astype(np.float64); a = np.abs(x)
    return x[max(0, int(np.argmax(a > a.max() * 0.02)) - 48):]

def note(inst, m, dur, rel=0.5):
    x = load(os.path.join(SMP, inst, f"{NAMES[m % 12]}{m // 12 - 1}.mp3")); assert len(x) > SR, (inst, m)
    if dur + rel > len(x) / SR - 0.05:
        body = x[int(0.8 * SR):int(2.6 * SR)]; cf = int(0.4 * SR); out = x[:int(2.6 * SR)].copy()
        while len(out) < (dur + rel) * SR:
            fd = np.linspace(0, 1, cf); out[-cf:] = out[-cf:] * (1 - fd) + body[:cf] * fd; out = np.concatenate([out, body[cf:]])
        x = out
    L = min(len(x), int((dur + rel) * SR)); y = x[:L].copy(); r = int(rel * SR)
    if L > r: y[-r:] *= np.linspace(1, 0, r) ** 2
    return y

def add(sig, at, g, pan=0.0):
    i = int(round(at * SR))
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[: j - i]
    mix[i:j, 0] += s * g * np.sqrt((1 - pan) / 2) * 1.414; mix[i:j, 1] += s * g * np.sqrt((1 + pan) / 2) * 1.414

BPM = 70; beat = 60 / BPM; bar = 4 * beat
# D  A/C#  Bm  G   (I - V6 - vi - IV)
PROG = [(38, [62, 66, 69, 74]), (37, [61, 64, 69, 73]), (35, [62, 66, 71, 74]), (31, [62, 67, 71, 74])]
nb = int(END_AT / bar) + 1
for b in range(nb):
    t0 = b * bar; root, ch = PROG[b % 4]; lifted = t0 >= LIFT - 0.5
    vel = 0.75 + 0.25 * min(1, t0 / LIFT)
    add(note("acoustic_grand_piano", root, bar, 0.8), t0, 0.22 * vel, -0.25)
    add(note("acoustic_grand_piano", root + 12, bar, 0.8), t0, 0.12 * vel, -0.15)
    pat = [0, 1, 2, 3, 2, 1, 2, 3] if not lifted else [0, 2, 1, 3, 2, 3, 1, 2]
    for k, idx in enumerate(pat):
        add(note("acoustic_grand_piano", ch[idx], 1.6, 0.6), t0 + k * beat / 2 + rng.uniform(-.008, .008),
            0.10 * vel * (1.0 if k % 2 == 0 else 0.8), (idx - 1.5) * 0.22)
    if lifted:   # strings + cello open up for the "little moments" and the thank-you
        for k, m in enumerate([root + 12] + ch[:3]):
            add(note("string_ensemble_1", m, bar + 0.3, 0.9), t0, 0.07 if k else 0.09, (k - 1.5) * 0.25)
        add(note("cello", root + 12, bar + 0.3, 0.8), t0, 0.08, -0.2)
        if b % 2 == 1:
            add(note("acoustic_grand_piano", ch[-1] + 12, 1.8, 0.8), t0 + 2.5 * beat, 0.08, 0.3)
# end card bloom
for k, m in enumerate([38, 50, 62, 66, 69, 74, 78]):
    add(note("acoustic_grand_piano", m, 2.6, 1.0), END_AT - 0.1 + k * 0.05, 0.12, (k - 3) * 0.12)
for k, m in enumerate([50, 62, 66, 69]):
    add(note("string_ensemble_1", m + 12, 2.6, 1.0), END_AT - 0.1, 0.08, (k - 1.5) * 0.25)
add(note("tubular_bells", 86, 2.5, 1.0), END_AT + 0.2, 0.05, 0.2)

n = int(SR * 2.4); t = np.arange(n) / SR
for c in range(2):
    ir = rng.standard_normal(n) * np.exp(-t * 2.8); ir[: int(.02 * SR)] = 0; L = N + n
    wet = np.fft.irfft(np.fft.rfft(mix[:, c], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, c] = mix[:, c] + wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix[:, c])) * 0.3
fi = int(1.0 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(1.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.8
w = wave.open(os.path.join(P, "media", "music.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype("<i2").tobytes()); w.close(); print("music", DUR)
