"""Synthesize the BOGO reel soundtrack into sfx/mix.wav (10 s, plays once).

- 0.0–0.6  tiles cascade in: quick rising marimba taps over a filtered beat
- 0.6–4.8  tile swaps: a soft pitched tap (C-major pentatonic) on every swap, beat opens up
- 4.8–5.6  tiles click into place: rising tap run + snare roll + riser
- 5.6      photo complete: the drop — warm chords, bass, full drums, bell shimmer
- 6.0      BUY 1 GET 1 pops: soft thump + sparkle; groove rings out by 10 s
Timings mirror the constants in index.html — change them in both places.
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 10.0
OUT = Path(__file__).resolve().parent.parent / "sfx" / "mix.wav"
rng = np.random.default_rng(5)

INTRO = (0.0, 0.6)
SCATTER, STEP = (0.6, 4.8), 0.12
BUILD = (4.8, 5.6)
TILES = 15
DROP = 5.6
POP = 6.15
BPM = 120
BEAT = 60 / BPM


def t(n):
    return np.arange(int(n * SR)) / SR


def place(buf, clip, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[k] = acc
    return y


def hp(x, fc):
    return x - lp(x, fc)


def reverb(x, secs=1.6, mix=0.25, bright=5000):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-t(secs) * (6.0 / secs))
    ir = lp(ir, bright)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    wet = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x)]
    return x * (1 - mix) + wet * mix * 0.7


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------- instruments
def marimba(f, d=0.35):
    tt = t(d)
    env = np.exp(-tt * 14) * (1 - np.exp(-tt * 2500))
    return env * (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt * 40)
                  + 0.12 * np.sin(2 * np.pi * f * 10.0 * tt) * np.exp(-tt * 90))


def bell(f, d=1.6):
    tt = t(d)
    env = np.exp(-tt * 3.2) * (1 - np.exp(-tt * 1500))
    return env * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 5)
                  + 0.2 * np.sin(2 * np.pi * f * 3.0 * tt) * np.exp(-tt * 8))


def epiano(f, d):
    tt = t(d)
    env = (1 - np.exp(-tt * 90)) * np.exp(-tt * 1.3)
    mod = np.sin(2 * np.pi * f * tt) * 1.1 * np.exp(-tt * 3.5)
    return (np.sin(2 * np.pi * f * tt + mod) + 0.2 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 4)) * env * (1 + 0.06 * np.sin(2 * np.pi * 5 * tt))


def bass(f, d):
    tt = t(d)
    x = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)
    return np.tanh(1.6 * x) * (1 - np.exp(-tt * 200)) * np.exp(-tt * 2.2)


def kick():
    tt = t(0.42)
    f = 46 + 130 * np.exp(-tt * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7.5)
    click = hp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 400) * 0.25
    return 0.85 * body + click


def clap():
    tt = t(0.3)
    n = hp(rng.standard_normal(len(tt)), 1200)
    env = np.zeros_like(tt)
    for k, off in enumerate((0.0, 0.009, 0.018)):
        env += np.where(tt >= off, np.exp(-(tt - off) * (90 if k < 2 else 18)), 0)
    return n * env * 0.3


def snare(g=1.0):
    tt = t(0.16)
    n = hp(rng.standard_normal(len(tt)), 1500) * np.exp(-tt * 30)
    tone = np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 40)
    return (0.5 * n + 0.4 * tone) * g


def shaker(acc):
    tt = t(0.06)
    n = hp(rng.standard_normal(len(tt)), 6000)
    return n * np.exp(-tt * 70) * (0.11 if acc else 0.07)


def thump():
    tt = t(0.5)
    f = 60 + 60 * np.exp(-tt * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6)


def riser(d):
    tt = t(d)
    n = rng.standard_normal(len(tt))
    sweep = np.zeros_like(n)
    # crude rising band: blend of progressively brighter noise
    for k, fc in enumerate((800, 2000, 5000)):
        w = np.clip(tt / d * 3 - k, 0, 1)
        sweep += hp(n, fc) * w
    return sweep * (tt / d) ** 2 * 0.2


# ---------------- arrangement
PENTA = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93]  # C major pentatonic, two octaves
PROG = [(41, [53, 57, 60, 64]), (43, [55, 59, 62, 67]), (45, [57, 60, 64, 67]), (48, [55, 60, 64, 67])]  # Fmaj7 G Am C


def music():
    out = np.zeros(int(DUR * SR))
    drums = np.zeros_like(out)
    keys = np.zeros_like(out)
    low = np.zeros_like(out)
    n_beats = int(DUR / BEAT)
    for b in range(n_beats):
        tb = b * BEAT
        pre = tb < DROP - 1e-6
        if tb < BUILD[0] or tb >= DROP:
            place(drums, kick(), tb, 0.8 if pre else 1.0)
        if b % 2 == 1 and (tb >= DROP or (SCATTER[0] < tb < BUILD[0])):
            place(drums, clap(), tb, 0.75 if pre else 1.0)
        for e in range(4):
            place(drums, shaker(e == 2), tb + e * BEAT / 4 + (0.012 if e % 2 else 0), 1.0)
    # snare roll into the drop
    k = 0
    while True:
        tr = BUILD[0] + k * (BEAT / 4)
        if tr >= DROP - 1e-6:
            break
        place(drums, snare(0.35 + 0.65 * (tr - BUILD[0]) / (DROP - BUILD[0])), tr)
        k += 1
    # pre-drop: soft chord stabs; post-drop: full chords + bass
    bar = 4 * BEAT
    for i in range(int(DUR / bar) + 1):
        t0 = i * bar
        root, chord = PROG[i % 4]
        if t0 + bar <= DROP + 1e-6:
            for s in (0.0, 1.5, 2.5):
                for m in chord:
                    place(keys, epiano(hz(m + 12), 0.5), t0 + s * BEAT, 0.035)
        elif t0 >= DROP - 1e-6 or t0 + bar > DROP:
            start = max(t0, DROP)
            for m in chord:
                place(keys, epiano(hz(m + 12), bar + 0.6), start, 0.06)
            for s in range(8):
                ts = t0 + s * BEAT / 2
                if ts >= DROP - 1e-6:
                    place(low, bass(hz(root - 12 + (12 if s in (3, 7) else 0)), 0.3), ts, 0.45)
    keys_w = reverb(keys, 1.8, 0.35)
    # sidechain pump from kicks
    pump = np.ones_like(out)
    for b in range(n_beats):
        tb = b * BEAT
        if tb < BUILD[0] or tb >= DROP:
            i0 = int(tb * SR)
            seg = 1 - 0.45 * np.exp(-t(BEAT) * 11)
            j = min(len(pump), i0 + len(seg))
            pump[i0:j] = np.minimum(pump[i0:j], seg[: j - i0])
    # open the filter over the intro/scatter: everything before the drop is darker
    pre = int(DROP * SR)
    tone = keys_w * pump + low * pump
    dark = lp(tone[:pre], 1800)
    tone[:pre] = dark * np.linspace(0.6, 1.0, pre)
    mix = tone + reverb(drums, 0.5, 0.12)
    place(mix, riser(BUILD[1] - BUILD[0] + 0.15), BUILD[0] - 0.15, 1.0)
    # tail: let the last chord ring, fade out the groove
    i = int((DUR - 1.8) * SR)
    mix[i:] *= np.linspace(1, 0, len(mix) - i) ** 1.6
    return mix


def sfx():
    out = np.zeros(int(DUR * SR))
    taps = np.zeros_like(out)
    # cascade-in: rising taps
    for k in range(TILES):
        place(taps, marimba(hz(PENTA[k % len(PENTA)])), INTRO[0] + k * (INTRO[1] - INTRO[0]) / TILES, 0.35)
    # swaps: one pitched tap per step, melody wanders within the scale
    idx = 4
    k = 0
    while SCATTER[0] + k * STEP < SCATTER[1] - 1e-6:
        idx = int(np.clip(idx + rng.integers(-2, 3), 0, len(PENTA) - 1))
        place(taps, marimba(hz(PENTA[idx])), SCATTER[0] + k * STEP, 0.42)
        k += 1
    # build: a clean rising run as tiles click into place
    for k in range(TILES):
        place(taps, marimba(hz(PENTA[k % len(PENTA)] + (12 if k >= len(PENTA) else 0)), 0.3), BUILD[0] + k * (BUILD[1] - BUILD[0]) / TILES, 0.4)
    out += reverb(taps, 0.9, 0.22, 7000)
    # drop: bell chord shimmer + thump
    shimmer = np.zeros_like(out)
    for k, m in enumerate([84, 88, 91, 96]):
        place(shimmer, bell(hz(m)), DROP + k * 0.035, 0.12)
    out += reverb(shimmer, 2.0, 0.4)
    place(out, thump(), DROP, 0.5)
    # headline pop
    place(out, thump(), POP, 0.35)
    sp = np.zeros_like(out)
    for k, m in enumerate([96, 100, 103]):
        place(sp, bell(hz(m), 0.8), POP + 0.05 + k * 0.05, 0.07)
    out += reverb(sp, 1.2, 0.4)
    return out


def main():
    mix = music() * 0.8 + sfx()
    mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6) * 0.89  # gentle soft-clip master
    data = (np.stack([mix, mix], axis=1) * 32767).astype("<i2").tobytes()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
