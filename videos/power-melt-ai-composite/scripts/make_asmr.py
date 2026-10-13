"""Synthesize the ASMR foley stems for the Power Melt ingredient-pour reel.

Reads the cue sheet embedded in index.html (<script id="cues">) so every sound
lands on its visual. Deterministic (fixed seeds). Writes 48 kHz 16-bit WAVs to
assets/audio/.

    python3 scripts/make_asmr.py
"""
import json
import re
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
html = (ROOT / "index.html").read_text()
CUES = json.loads(re.search(r'<script type="application/json" id="cues">(.*?)</script>', html, re.S).group(1))
DUR = CUES["duration"]
N = int(SR * DUR)
OUT = ROOT / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)


def band(x, lo=None, hi=None, soft=0.15):
    """Zero-phase FFT band filter with soft shoulders."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** (2 / soft * 0.2))
    if hi:
        m *= 1 / (1 + (f / hi) ** (2 / soft * 0.2))
    return np.fft.irfft(X * m, len(x))


def env_window(start, end, attack=0.15, release=0.35):
    t = np.arange(N) / SR
    e = np.clip((t - start) / attack, 0, 1) * np.clip((end + release - t) / release, 0, 1)
    return e ** 1.5


def place(buf, sig, at):
    i = int(at * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i]


def plop(f0, f1, dur, rng, body=0.6):
    """Bubble/drop resonance: upward pitch sweep with exponential decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (1 - np.exp(-t / (dur * 0.35)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / (dur * 0.28))
    thud = np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.022) * body
    click = rng.standard_normal(n) * np.exp(-t / 0.002) * 0.25
    return s + thud + band(click, 1500, 9000)


def write(name, x, peak_db):
    x = x / (np.max(np.abs(x)) + 1e-9) * (10 ** (peak_db / 20))
    fade = int(0.02 * SR)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", OUT / name)


# Room tone: soft, warm, barely there.
rng = np.random.default_rng(1)
room = band(rng.standard_normal(N), 60, 900) + 0.15 * band(rng.standard_normal(N), 3000, 9000)
write("room.wav", room, -40)

# Moringa powder: dense granular sifting + soft landing hiss.
rng = np.random.default_rng(2)
M = CUES["moringa"]
pw = np.zeros(N)
t0, t1 = M["pourStart"], M["pourEnd"]
for at in np.sort(rng.uniform(t0, t1 + 0.25, int((t1 - t0) * 900))):
    n = int(rng.uniform(0.001, 0.005) * SR)
    g = rng.standard_normal(n) * np.hanning(n) * rng.uniform(0.2, 1.0)
    place(pw, g, at)
pw = band(pw, 2500, 11000)
hiss = band(rng.standard_normal(N), 1800, 7000) * env_window(M["fillStart"], t1, 0.3, 0.5) * 0.35
write("moringa-powder.wav", (pw + hiss) * env_window(t0, t1, 0.2, 0.4), -12)

# Jojoba liquid wax: plump, thick drops with small splash ticks.
rng = np.random.default_rng(3)
jj = np.zeros(N)
for k, d in enumerate(CUES["jojoba"]["drops"]):
    f0 = rng.uniform(300, 420)
    place(jj, plop(f0, f0 * 2.1, 0.11, rng, body=0.9), d)
    for _ in range(2):
        place(jj, plop(1400, 2600, 0.03, rng, body=0) * 0.18, d + rng.uniform(0.06, 0.16))
jj = band(jj, 80, 7000)
write("jojoba-drops.wav", jj, -8)

# Plum kernel: slow viscous pour, low silky body + occasional glugs.
rng = np.random.default_rng(4)
P = CUES["plum"]
t = np.arange(N) / SR
pour = band(rng.standard_normal(N), 180, 1300)
pour *= 0.75 + 0.25 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 0.7 * t + 1)
pour *= env_window(P["fillStart"], P["pourEnd"] + 0.25, 0.25, 0.45)
glug = np.zeros(N)
at = P["fillStart"] + 0.05
while at < P["pourEnd"] + 0.3:
    f0 = rng.uniform(170, 300)
    place(glug, plop(f0, f0 * 1.6, 0.09, rng, body=0.3) * rng.uniform(0.25, 0.6), at)
    at += rng.uniform(0.09, 0.22)
place(glug, plop(220, 520, 0.16, rng, body=1.0) * 0.9, P["fillStart"])  # first contact
write("plum-pour.wav", pour * 0.55 + band(glug, 60, 4000), -9)

# Squalane: featherlight fine trickle, tiny glassy plinks, airy shimmer at the reveal.
rng = np.random.default_rng(5)
Q = CUES["squalane"]
tr = band(rng.standard_normal(N), 2200, 8000) * env_window(Q["fillStart"], Q["pourEnd"], 0.15, 0.3) * 0.5
pl = np.zeros(N)
at = Q["fillStart"]
while at < Q["pourEnd"] + 0.2:
    f0 = rng.uniform(1700, 3200)
    place(pl, plop(f0, f0 * 1.5, 0.035, rng, body=0) * rng.uniform(0.15, 0.5), at)
    at += rng.uniform(0.025, 0.07)
R = CUES["reveal"]
air = band(rng.standard_normal(N), 6000, 14000) * env_window(R["start"], R["end"] + 0.1, 0.25, 0.5) * 0.18
write("squalane-trickle.wav", tr + pl + air, -12)
