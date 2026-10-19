"""Synthesize the BOGO reel soundtrack into sfx/mix.wav.

Like the reference: a crisp shutter-style click on every tile swap (a rapid burst while
the tiles click back into the full photo), a light 120 BPM pulse underneath, a soft hit
when the photo completes, and a sparkle on the final offer.
Timings mirror the constants in index.html — change them in both places.
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 10.0
OUT = Path(__file__).resolve().parent.parent / "sfx" / "mix.wav"
rng = np.random.default_rng(11)

# ---- timeline (keep in sync with index.html)
SCATTER, SCATTER_STEP = [(0.6, 4.8)], 0.12   # random tile swaps
BUILD, TILES = [(0.0, 0.6), (4.8, 5.6)], 15   # tiles cascade in, then click into place one by one
SNAPS = [5.6]                                 # full photo complete


def t(n):
    return np.arange(int(n * SR)) / SR


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[k] = acc
    return y


def reverb(x, secs=1.4, mix=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-t(secs) * 5.5)
    ir = onepole_lp(ir, 6000)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    wet = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x)]
    return x * (1 - mix) + wet * mix * 0.6


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def kick():
    tt = t(0.4)
    f = 50 + 120 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)


def clap():
    tt = t(0.22)
    n = rng.standard_normal(len(tt))
    n = n - onepole_lp(n, 1100)
    env = np.exp(-tt * 24) + 0.7 * np.exp(-np.maximum(tt - 0.01, 0) * 30) * (tt > 0.01)
    return n * env * 0.35


def hat(open_=False):
    tt = t(0.16 if open_ else 0.04)
    n = rng.standard_normal(len(tt))
    n = n - onepole_lp(n, 7500)
    return n * np.exp(-tt * (16 if open_ else 110)) * 0.14


def pluck(f, d=0.35):
    tt = t(d)
    saw = 2 * ((f * tt) % 1) - 1
    return onepole_lp(saw * np.exp(-tt * 10), 3200) * (1 - np.exp(-tt * 800))


def pad(f, d):
    tt = t(d)
    env = (1 - np.exp(-tt * 12)) * np.exp(-tt * 0.6)
    return (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * env


def bass(f, d):
    tt = t(d)
    return (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * (1 - np.exp(-tt * 150)) * np.exp(-tt * 3)


def shutter(var):
    """Two quick filtered noise snaps (blade open/close) with a little body."""
    c = np.zeros(int(0.07 * SR))
    for k, at in enumerate((0.0, 0.018 + 0.01 * var)):
        tt = t(0.03)
        n = rng.standard_normal(len(tt))
        snap = (n - onepole_lp(n, 2500 + 2500 * var)) * np.exp(-tt * (260 if k == 0 else 200))
        body = np.sin(2 * np.pi * (900 + 500 * var) * tt) * np.exp(-tt * 220) * 0.4
        place(c, snap + body, at, 1.0 if k == 0 else 0.7)
    return c


def bell(f, d=0.9):
    tt = t(d)
    return np.exp(-tt * 5) * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 9)) * (1 - np.exp(-tt * 900))


def music():
    beat = 0.5
    out = np.zeros(int(DUR * SR))
    drums = np.zeros_like(out)
    keys = np.zeros_like(out)
    # C – G – Am – F, bright and celebratory, one chord per bar (2 s)
    prog = [(36, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69])]
    riff = [72, 76, 79, 76, 81, 79, 76, 74]
    for bar in range(5):
        t0 = bar * 4 * beat
        root, chord = prog[bar % 4]
        for m in chord:
            place(keys, pad(hz(m), 2.2), t0, 0.03)
        for s in range(8):
            place(keys, pluck(hz(riff[(s + bar * 2) % 8])), t0 + s * beat / 2, 0.05)
            place(out, bass(hz(root + (12 if s % 4 == 3 else 0)), 0.22), t0 + s * beat / 2, 0.33)
        last = bar == 4
        for q in range(4):
            if last and q > 0:
                break
            place(drums, kick(), t0 + q * beat, 0.95)
            if q in (1, 3):
                place(drums, clap(), t0 + q * beat, 1.0)
            for e in range(4):
                place(drums, hat(open_=(e == 2)), t0 + q * beat + e * beat / 4, 0.8 if e % 2 == 0 else 0.45)
    pump = np.ones_like(out)
    for k in range(int(DUR / beat)):
        i = int(k * beat * SR)
        seg = 1 - 0.4 * np.exp(-t(beat) * 10)
        j = min(len(pump), i + len(seg))
        pump[i:j] = np.minimum(pump[i:j], seg[: j - i])
    mix = reverb(keys, 1.2, 0.3) * pump + out * pump + reverb(drums, 0.4, 0.1)
    # risers into each snap
    for s in SNAPS:
        rt = t(0.5)
        n = rng.standard_normal(len(rt))
        place(mix, (n - onepole_lp(n, 1500)) * (rt / 0.5) ** 2.5 * 0.16, s - 0.5)
        place(mix, kick(), s, 0.8)
        hit = rng.standard_normal(int(0.9 * SR)) * np.exp(-t(0.9) * 6)
        place(mix, (hit - onepole_lp(hit, 3000)) * 0.12, s)
    i = int((DUR - 1.6) * SR)
    mix[i:] *= np.linspace(1, 0, len(mix) - i) ** 1.4
    return mix


def main():
    mix = music()
    sfx = np.zeros_like(mix)
    for a, b in SCATTER:
        k = 0
        while a + k * SCATTER_STEP < b - 1e-6:
            place(sfx, shutter(rng.random()), a + k * SCATTER_STEP, 0.9)
            k += 1
    for a, b in BUILD:
        dt = (b - a) / TILES
        for k in range(TILES):
            place(sfx, shutter(0.3 + 0.7 * k / TILES), a + k * dt, 0.6)
    sp = np.zeros(int(1.6 * SR))
    for k, m in enumerate([84, 88, 91, 96]):
        place(sp, bell(hz(m)), k * 0.06, 0.2)
    place(sfx, reverb(sp, 1.2, 0.4), SNAPS[-1] + 0.55)
    mix = mix * 0.45 + sfx
    mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
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
