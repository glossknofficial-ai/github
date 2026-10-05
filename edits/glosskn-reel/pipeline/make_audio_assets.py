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
# --- softer, more playful kit (v4) ---
d = 0.12; t = T(d)
snap = band(rng.standard_normal(len(t)), 1800, 6500) * np.exp(-t * 90) * .9 + np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 160) * .3
sfx["snap"] = reverb(snap, .35, .18)
d = 0.04; t = T(d)
sfx["tick"] = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 220) + band(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 500) * .4
sc = np.zeros(int(SR * 0.42))
for k, (o0, d0) in enumerate([(0, .09), (.1, .08), (.2, .1), (.31, .09)]):
    n = int(d0 * SR); x = band(rng.standard_normal(n), 1200 + 300 * k, 5000) * np.sin(np.pi * np.arange(n) / n) ** .6
    i = int(o0 * SR); sc[i:i + n] += x[: len(sc) - i]
sfx["scribble"] = sc
d = 0.22; t = T(d); fr = np.geomspace(380, 1150, len(t))
sfx["heartpop"] = reverb(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 14) * np.minimum(1, t / .004), .5, .2)
bb = np.zeros(int(SR * 1.1))
for k in range(9):
    f0 = float(rng.uniform(500, 1200)); n = int(.07 * SR); tt = np.arange(n) / SR
    b0 = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f0 * 1.9, n)) / SR) * np.exp(-tt * 45)
    i = int(float(rng.uniform(0, 1.0)) * SR); bb[i:i + n] += b0[: len(bb) - i] * float(rng.uniform(.4, 1))
sfx["bubbles"] = reverb(bb, .4, .2)
d = 0.36; t = T(d)
bl = sum(np.sin(2 * np.pi * f * t) * ((t > o0) & (t < o0 + .14)) * np.exp(-(t - o0).clip(0) * 9) for f, o0 in [(330, 0), (247, .17)])
sfx["blip"] = bl
d = 0.3; t = T(d)
sfx["swipe"] = pan_sweep(sweep_filter(rng.standard_normal(len(t)), 900, 3800, .5) * np.sin(np.pi * t / d) ** 2 * .7, -0.4, 0.4)
for k, v in sfx.items():
    save(os.path.join(OUT, "sfx", k + ".wav"), v)

# ---------------------------------------------------------------- music (v4: clean EP / soft groove)
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
DROP = float(sys.argv[2]) if len(sys.argv) > 2 else 4.8
BREAK = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (None, None)
BPM = 118; beat = 60 / BPM; bar = 4 * beat
N = int(SR * DUR); keys = np.zeros((N, 2)); drums = np.zeros((N, 2)); bass = np.zeros((N, 2))


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    if sig.ndim == 1:
        sig = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    j = min(N, i + len(sig)); buf[i:j] += sig[: j - i] * gain


mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [[53, 57, 60, 64], [55, 59, 62, 66], [52, 55, 59, 62], [57, 60, 64, 67]]  # Fmaj7 G6 Em7 Am7
ROOTS = [41, 43, 40, 45]


def ep(f, d=1.6):  # FM electric piano
    t = T(d); idx = 1.4 * np.exp(-t * 5)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t * 1.5)
    s += 0.12 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 30)  # tine
    return s * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.05)


kt = T(0.32); kick = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 48, len(kt))) / SR) * np.exp(-kt * 11)
st = T(0.14); snp = band(rng.standard_normal(len(st)), 1800, 6000) * np.exp(-st * 70) + np.sin(2 * np.pi * 2900 * st) * np.exp(-st * 140) * .3
ht = T(0.05); shk = band(rng.standard_normal(len(ht)), 6000, 13000) * np.sin(np.pi * ht / 0.05)
in_break = lambda tt: BREAK[0] is not None and BREAK[0] <= tt < BREAK[1]

for b in range(int(DUR / bar) + 2):
    t0 = b * bar; ch = CHORDS[b % 4]
    for st_, vel in ((0, 1.0), (1.5, .7), (2.5, .8)) if t0 >= DROP else ((0, 1.0), (2, .7)):
        tt = t0 + st_ * beat
        if in_break(tt): continue
        for k, m in enumerate(ch):
            add(keys, ep(mtof(m)), tt + k * 0.008, 0.07 * vel, (-0.3, -0.1, 0.1, 0.3)[k])
    for i in range(8):
        tt = t0 + i * beat / 2
        if tt < DROP - 0.01 or in_break(tt): continue
        if i in (0, 4) or (i == 7 and b % 2): add(drums, kick, tt, 0.5)
        if i in (2, 6): add(drums, snp, tt, 0.28, 0.1)
        add(drums, shk, tt, 0.016 + 0.01 * (i % 2), -0.35)
        if i in (0, 3, 4):
            bt = T(beat * 0.9); f = mtof(ROOTS[b % 4] - 12)
            add(bass, np.sin(2 * np.pi * f * bt) * np.exp(-bt * 3) * np.minimum(1, bt / 0.01), tt, 0.26)

keys = reverb(keys, 1.6, 0.28)[:N]
mix = keys + drums + bass
cut = int(DROP * SR)
if cut > 0:  # soft, filtered intro
    seg = mix[:cut].copy(); X = np.fft.rfft(seg, axis=0); f = np.fft.rfftfreq(len(seg), 1 / SR)
    X *= (1 / (1 + (f / 1100) ** 4))[:, None]; mix[:cut] = np.fft.irfft(X, len(seg), axis=0) * 0.8
if BREAK[0]:  # tape-stop into the break
    a = int((BREAK[0] - 0.4) * SR); b = int(BREAK[0] * SR); src = mix[a:b].copy()
    idx = np.clip(np.cumsum(np.linspace(1, 0.05, b - a)), 0, len(src) - 1).astype(int)
    mix[a:b] = src[idx] * np.linspace(1, 0, b - a)[:, None]
tail = sum(ep(mtof(m), 2.4) for m in CHORDS[0]); add(mix, tail, DUR - 2.4, 0.08)
mix = np.tanh(mix * 1.6) / 1.6  # gentle saturation glue
fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
save(os.path.join(OUT, "music.wav"), mix, 0.8)
print("sfx", len(sfx), "music", DUR, "s")
