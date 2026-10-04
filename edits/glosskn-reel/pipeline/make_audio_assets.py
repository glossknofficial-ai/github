"""Synthesize the SFX kit and an original ~122 BPM light pop/house bed -> media/sfx/*.wav, media/music.wav"""
import os, sys, wave
import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
os.makedirs(os.path.join(OUT, "sfx"), exist_ok=True)
rng = np.random.default_rng(7)


def save(path, x, peak=0.89):
    x = np.asarray(x, float)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype("<i2").tobytes()); w.close()


def T(d): return np.arange(int(SR * d)) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def sweep_filter(x, f0, f1, q=0.2):
    """state-variable bandpass with cutoff gliding f0 -> f1 (log)"""
    f = np.geomspace(f0, f1, len(x)); y = np.zeros_like(x); lp = bp = 0.0
    for i in range(len(x)):
        g = 2 * np.sin(np.pi * f[i] / SR)
        hp = x[i] - lp - q * bp; bp += g * hp; lp += g * bp; y[i] = bp
    return y


def reverb(x, decay=1.2, mix=0.3, pre=0.012):
    n = int(SR * decay); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / decay)[:, None]
    ir[: int(pre * SR)] = 0
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    L = len(x) + n
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir[:, c], L), L) for c in range(2)], 1)
    wet /= np.max(np.abs(wet)) + 1e-9
    dry = np.vstack([x, np.zeros((n, 2))]) / (np.max(np.abs(x)) + 1e-9)
    return dry * (1 - mix) + wet * mix


def pan_sweep(x, a=-0.8, b=0.8):
    p = np.linspace(a, b, len(x)); return np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1)


def bell(freq, d=1.2, k=3.0):
    t = T(d)
    return sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * k * (1 + m / 3))
               for m, a in [(1, 1), (2.0, .5), (2.76, .25), (5.4, .12)]) * np.minimum(1, t / 0.002)


# ---------------------------------------------------------------- SFX kit
sfx = {}
d = 0.6; t = T(d)
sfx["whoosh"] = pan_sweep(sweep_filter(rng.standard_normal(len(t)), 250, 2600, .25) * np.sin(np.pi * t / d) ** 2)
d = 0.32; t = T(d)
sfx["whoosh_fast"] = pan_sweep(sweep_filter(rng.standard_normal(len(t)), 600, 5000, .3) * np.sin(np.pi * t / d) ** 1.5, 0.6, -0.6)
d = 0.18; t = T(d)
sfx["swish"] = pan_sweep(sweep_filter(rng.standard_normal(len(t)), 2000, 9000, .35) * np.sin(np.pi * t / d) ** 1.2, -0.3, 0.5)
d = 0.11; t = T(d); fr = np.geomspace(1300, 320, len(t))
sfx["pop"] = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 40) + band(rng.standard_normal(len(t)), 2000, 6000) * np.exp(-t * 400) * .3
d = 0.05; t = T(d)
sfx["click"] = band(rng.standard_normal(len(t)), 1500, 7000) * np.exp(-t * 300) + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * .5
notes = [1046.5, 1318.5, 1568, 2093, 2637]
sh = np.zeros(int(SR * 1.6))
for i, f in enumerate(notes):
    b = bell(f, 1.2, 4) * (0.9 - i * .1); o = int(i * 0.045 * SR); sh[o:o + len(b)] += b[: len(sh) - o]
sfx["shimmer"] = reverb(sh, 1.6, .45)
d = 1.4; t = T(d); fr = np.geomspace(90, 38, len(t))
imp = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 3.2) + band(rng.standard_normal(len(t)), 40, 900) * np.exp(-t * 18) * .6
sfx["impact"] = reverb(imp, 1.4, .25)
d = 1.5; t = T(d)
ris = sweep_filter(rng.standard_normal(len(t)), 200, 7000, .3) * (t / d) ** 2.2 + np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 900, len(t))) / SR) * (t / d) ** 3 * .25
sfx["riser"] = pan_sweep(ris, -0.2, 0.2)
d = 0.16; t = T(d); sht = np.zeros(len(t))
for o, a in [(0, 1), (0.055, .7)]:
    i = int(o * SR); c = band(rng.standard_normal(len(t) - i), 900, 6500) * np.exp(-np.arange(len(t) - i) / SR * 160); sht[i:] += a * c
sfx["shutter"] = sht
ty = np.zeros(int(SR * 0.9))
for k, o in enumerate(np.cumsum(rng.uniform(0.07, 0.13, 8))):
    i = int(o * SR); c = band(rng.standard_normal(int(.03 * SR)), 1800, 8000) * np.exp(-np.arange(int(.03 * SR)) / SR * 260)
    if i + len(c) < len(ty): ty[i:i + len(c)] += c * (0.7 + 0.3 * (k % 2))
sfx["typing"] = ty
d = 0.55; t = T(d); fr = np.geomspace(1400, 90, len(t)) * (1 + 0.04 * np.sin(2 * np.pi * 18 * t))
ph = 2 * np.pi * np.cumsum(fr) / SR
sfx["rewind"] = (np.sign(np.sin(ph)) * .3 + np.sin(ph)) * np.minimum(1, (d - t) / 0.05) * np.minimum(1, t / .01)
sfx["ding"] = reverb(bell(1318.5, 1.6, 2.4) + bell(1975.5, 1.6, 3) * .5, 1.5, .3)
sp = np.zeros(int(SR * 0.9))
for i in range(10):
    f = float(rng.uniform(2500, 6500)); b = bell(f, .25, 12) * .5; o = int(i * 0.035 * SR); sp[o:o + len(b)] += b[: len(sp) - o]
sfx["sparkle"] = reverb(sp, .9, .4)
for k, v in sfx.items():
    save(os.path.join(OUT, "sfx", k + ".wav"), v)

# ---------------------------------------------------------------- music
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
DROP = float(sys.argv[2]) if len(sys.argv) > 2 else 4.8      # drums enter (the turnaround)
BREAK = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (None, None)  # tape-stop gap
BPM = 122; beat = 60 / BPM; bar = 4 * beat
N = int(SR * DUR); mix = np.zeros((N, 2))


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    if sig.ndim == 1:
        sig = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    j = min(N, i + len(sig)); mix[i:j] += sig[: j - i] * gain


mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [[53, 57, 60, 64], [55, 59, 62, 69], [52, 55, 59, 62], [57, 60, 64, 67]]  # Fmaj7 G(add9) Em7 Am7
ROOTS = [41, 43, 40, 45]


def pluck(f, d=0.45):
    t = T(d); return sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (5 + 4 * k)) for k in range(1, 9)) * np.minimum(1, t / 0.003)


def pad(fs, d):
    t = T(d); env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.5)
    s = sum(np.sin(2 * np.pi * f * det * t + p) * a for f in fs for det, p, a in [(1, 0, .5), (1.004, 1, .3), (0.996, 2, .3), (2, 0, .08)])
    return s * env


kick_t = T(0.35); kick = np.sin(2 * np.pi * np.cumsum(np.geomspace(130, 45, len(kick_t))) / SR) * np.exp(-kick_t * 9)
clap_t = T(0.25); cn = band(rng.standard_normal(len(clap_t)), 900, 4500)
clap = sum(cn * np.exp(-np.clip(clap_t - o, 0, None) * 40) * (clap_t >= o) for o in (0, .011, .022)) * .6
hat_t = T(0.06); hat = band(rng.standard_normal(len(hat_t)), 7000, 16000) * np.exp(-hat_t * 70)
shk_t = T(0.05); shk = band(rng.standard_normal(len(shk_t)), 5000, 12000) * np.sin(np.pi * shk_t / 0.05)

nb = int(DUR / bar) + 2
for b in range(nb):
    t0 = b * bar; ch = CHORDS[b % 4]
    in_break = BREAK[0] is not None and BREAK[0] - 0.05 < t0 + bar and t0 < BREAK[1]
    add(pad([mtof(m) for m in ch], bar + 0.4), t0, 0.10)
    for st in (0, 1.5, 3, 3.5) if t0 >= DROP else (0, 2):  # syncopated plucks
        tt = t0 + st * beat
        if BREAK[0] and BREAK[0] <= tt < BREAK[1]: continue
        for m in ch[1:]:
            add(pluck(mtof(m + 12)), tt, 0.05, 0.25 if m % 2 else -0.25)
    for i in range(16):  # drums & bass
        tt = t0 + i * beat / 4
        if tt < DROP - 0.01 or (BREAK[0] and BREAK[0] <= tt < BREAK[1]): continue
        if i % 4 == 0: add(kick, tt, 0.55)
        if i in (4, 12): add(clap, tt, 0.28)
        if i % 4 == 2: add(hat, tt, 0.10, 0.3)
        add(shk, tt, 0.018 + 0.012 * (i % 2), -0.3)
        if i % 4 in (2, 3) or i == 0:
            bt = T(beat / 4 * 0.9); f = mtof(ROOTS[b % 4] - 12 + (12 if i % 4 == 3 else 0))
            add((np.sin(2 * np.pi * f * bt) + .25 * np.sin(4 * np.pi * f * bt)) * np.exp(-bt * 6), tt, 0.22)

# soft filtered intro: low-pass everything before the drop
cut = int(DROP * SR)
if cut > 0:
    seg = mix[:cut].copy(); X = np.fft.rfft(seg, axis=0); f = np.fft.rfftfreq(len(seg), 1 / SR)
    X *= (1 / (1 + (f / 900) ** 4))[:, None]; mix[:cut] = np.fft.irfft(X, len(seg), axis=0)
# tape-stop into the break: pitch-drop the last 0.4s before it
if BREAK[0]:
    a = int((BREAK[0] - 0.4) * SR); b = int(BREAK[0] * SR); src = mix[a:b].copy()
    idx = np.cumsum(np.linspace(1, 0.05, b - a)); idx = np.clip(idx, 0, len(src) - 1).astype(int)
    mix[a:b] = src[idx] * np.linspace(1, 0, b - a)[:, None]
# ending: final chord + fade on the last 1.2s
tail = pad([mtof(m) for m in CHORDS[0]], 2.5); add(tail, DUR - 2.4, 0.12)
fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
save(os.path.join(OUT, "music.wav"), mix, 0.8)
print("sfx", len(sfx), "music", DUR, "s")
