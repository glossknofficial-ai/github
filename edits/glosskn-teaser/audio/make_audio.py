"""Synthesize the teaser soundtrack into sfx/mix.wav.

Notification chimes for the DM cards, keystrokes for the typed lines, and a
warm 100 BPM beat that drops in with the "closer than you think" slide.
Timings mirror the constants in index.html — change them in both places.
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 10.8
OUT = Path(__file__).resolve().parent.parent / "sfx" / "mix.wav"
rng = np.random.default_rng(7)

# ---- timeline (keep in sync with index.html)
NOTIFS = [0.30, 0.72, 1.12, 1.52, 1.92, 2.32, 2.72]
DROP = 3.30
TYPED = [("IT'S CLOSER", 3.75, 0.075), ("THAN YOU THINK", 4.75, 0.070), ("STAY TUNED.", 6.25, 0.085)]
LOGO = 8.40


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


def reverb(x, secs=1.6, mix=0.25):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-t(secs) * 5.0)
    ir = onepole_lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    wet = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[: len(x)]
    return x * (1 - mix) + wet * mix * 0.6


# ---- notification chime: two glassy bell notes, like a phone "note" alert
def bell(f, d=0.55):
    tt = t(d)
    env = np.exp(-tt * 9) * (1 - np.exp(-tt * 900))
    return env * (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt)
                  + 0.18 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 14))


def chime():
    c = np.zeros(int(0.75 * SR))
    place(c, bell(1567.98), 0.0, 0.55)    # G6
    place(c, bell(2093.00), 0.085, 0.65)  # C7
    return reverb(c, 0.6, 0.18)


# ---- keystroke: short filtered click + body thump, a little different each time
def key(var):
    d = 0.06
    tt = t(d)
    n = rng.standard_normal(len(tt))
    click = (n - onepole_lp(n, 2500 + 1500 * var)) * np.exp(-tt * 220)
    thump = np.sin(2 * np.pi * (180 + 60 * var) * tt) * np.exp(-tt * 90)
    return 0.8 * click + 0.3 * thump


# ---- music pieces
def kick():
    tt = t(0.45)
    f = 48 + 110 * np.exp(-tt * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 7) * 0.95


def clap():
    tt = t(0.25)
    n = rng.standard_normal(len(tt))
    n = n - onepole_lp(n, 900)
    env = np.exp(-tt * 22) + 0.6 * np.exp(-np.maximum(tt - 0.012, 0) * 30) * (tt > 0.012)
    return n * env * 0.32


def hat(open_=False):
    tt = t(0.18 if open_ else 0.05)
    n = rng.standard_normal(len(tt))
    n = n - onepole_lp(n, 7000)
    return n * np.exp(-tt * (18 if open_ else 90)) * 0.16


def keys_note(f, d):
    """Soft electric-piano-ish tone."""
    tt = t(d)
    env = (1 - np.exp(-tt * 80)) * np.exp(-tt * 1.1)
    mod = np.sin(2 * np.pi * f * tt) * 0.9 * np.exp(-tt * 3)
    tone = np.sin(2 * np.pi * f * tt + mod) + 0.25 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 4)
    return tone * env * (1 + 0.08 * np.sin(2 * np.pi * 4.5 * tt))


def bass_note(f, d):
    tt = t(d)
    env = (1 - np.exp(-tt * 120)) * np.exp(-tt * 1.4)
    return (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)) * env


def pluck(f, d=0.5):
    tt = t(d)
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * (1 - np.exp(-tt * 600))


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def music():
    bpm = 100
    beat = 60 / bpm
    bars = 4
    out = np.zeros(int(DUR * SR))
    drums = np.zeros_like(out)
    chords_bus = np.zeros_like(out)
    # Fmaj9 – Am7 – Dm9 – Bbmaj7(#11): warm, celebratory but soft
    prog = [(41, [57, 60, 64, 67]), (45, [55, 60, 64, 67]), (38, [57, 60, 64, 65]), (46, [57, 62, 65, 69])]
    melody = [72, 76, 79, 76, 74, 72, 69, 72]
    for b in range(bars):
        t0 = DROP + b * 4 * beat
        root, notes = prog[b % 4]
        for m in notes:
            place(chords_bus, keys_note(hz(m), 4 * beat + 0.4), t0, 0.11)
        place(out, bass_note(hz(root), 1.6 * beat), t0, 0.42)
        place(out, bass_note(hz(root), 0.9 * beat), t0 + 2.5 * beat, 0.34)
        place(out, bass_note(hz(root + 12), 0.8 * beat), t0 + 3.5 * beat, 0.26)
        for s in range(8):
            place(chords_bus, pluck(hz(melody[(s + b * 3) % 8])), t0 + s * beat / 2 + (0.02 if s % 2 else 0), 0.07)
        for q in range(4):
            if q in (0, 2):
                place(drums, kick(), t0 + q * beat, 1.0)
            if q in (1, 3):
                place(drums, clap(), t0 + q * beat, 1.0)
        place(drums, kick(), t0 + 2.75 * beat, 0.55)
        for e in range(8):
            place(drums, hat(open_=(e == 7)), t0 + e * beat / 2 + (0.035 if e % 2 else 0), 0.9 if e % 2 == 0 else 0.6)
    # sidechain-style pump on the tonal parts from each kick
    pump = np.ones_like(out)
    for b in range(bars):
        for q in (0, 2):
            i = int((DROP + (b * 4 + q) * beat) * SR)
            seg = 1 - 0.45 * np.exp(-t(beat) * 9)
            if i >= len(pump):
                continue
            j = min(len(pump), i + len(seg))
            pump[i:j] = np.minimum(pump[i:j], seg[: j - i])
    tonal = reverb(chords_bus, 1.8, 0.35) * pump + out * pump
    mix = tonal + reverb(drums, 0.5, 0.12)
    # soft riser into the drop
    rs = DROP - 0.7
    rt = t(0.7)
    noise = rng.standard_normal(len(rt))
    swell = (noise - onepole_lp(noise, 1200)) * (rt / 0.7) ** 2.5 * 0.12
    place(mix, swell, rs)
    # fade the tail out
    fade_start, fade_len = DUR - 1.4, 1.4
    i = int(fade_start * SR)
    mix[i:] *= np.linspace(1, 0, len(mix) - i) ** 1.5
    return mix


def main():
    mus = music()
    sfx = np.zeros_like(mus)
    ch = chime()
    for at in NOTIFS:
        place(sfx, ch, at, 0.9)
    for text, start, step in TYPED:
        for i, c in enumerate(text):
            if c != " ":
                place(sfx, key(rng.random()), start + i * step, 1.3)
    # gentle sparkle when the logo lands
    sp = np.zeros(int(1.6 * SR))
    for k, m in enumerate([84, 88, 91, 96]):
        place(sp, bell(hz(m), 1.0), k * 0.06, 0.18)
    place(sfx, reverb(sp, 1.2, 0.4), LOGO + 0.1)
    mix = mus * 0.62 + sfx
    mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
    st = np.stack([mix, mix], axis=1)
    data = (st * 32767).astype("<i2").tobytes()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
