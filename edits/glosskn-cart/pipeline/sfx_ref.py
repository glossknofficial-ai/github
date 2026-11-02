"""Sound effects in the reference's style (its punch comes from an 808 kick with falling pitch, a clap/snap and
hats): crisp snap when a story lifts off, deep 808 boom + light clap when it lands, a softer boom when the
last slide comes in, sparkle on the title shimmer. No music. -> media/v2/sfx.wav"""
import os, json, wave
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v2")
cj = json.load(open(os.path.join(V, "cues.json"))); DUR = cj["dur"]; SR = 48000
mix = np.zeros((int(DUR * SR), 2)); rng = np.random.default_rng(3)
def t_(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g, pan=0.0):
    i = int(at * SR); j = min(len(mix), i + len(sig)); s = sig[: j - i]
    mix[i:j, 0] += s * g * (1 - max(0, pan)); mix[i:j, 1] += s * g * (1 + min(0, pan))
def boom808(d=0.55):
    t = t_(d); f = 46 + 110 * np.exp(-t * 28)                   # pitch drops fast, like the reference kick
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.25
    return np.tanh(2.2 * (s + click)) / np.tanh(2.2)
def clap():
    t = t_(0.22); n = rng.standard_normal(len(t))
    env = sum(np.exp(-np.clip(t - o, 0, None) * 60) * (t >= o) for o in (0, 0.011, 0.022)) * np.exp(-t * 14)
    n = np.convolve(n, [1, -0.6], "same")                         # brighten
    return n * env * 0.5
def snap():
    t = t_(0.09); n = rng.standard_normal(len(t)); n = n - np.convolve(n, np.ones(8) / 8, "same")
    return (n * 0.8 + np.sin(2 * np.pi * 2100 * t) * 0.5) * np.exp(-t * 70)
def hat():
    t = t_(0.06); n = rng.standard_normal(len(t)); n = n - np.convolve(n, np.ones(4) / 4, "same")
    return n * np.exp(-t * 90)
def sparkle():
    t = t_(0.9); s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (5 + k)) * (t >= k * 0.06) for k, f in enumerate([2093, 2637, 3136, 4186]))
    return s * 0.25
for t in cj["ticks"]:
    add(snap(), t, 0.5, -0.1); add(hat(), t + 0.27, 0.25, 0.2)
for t in cj["pops"]:
    add(boom808(), t, 0.95); add(clap(), t + 0.005, 0.45, 0.05)
add(sparkle(), cj["shine"], 0.35, 0.2)
add(boom808(0.7), 6.93, 0.6)                                       # last slide arrives
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
w = wave.open(os.path.join(V, "sfx.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype("<i2").tobytes()); w.close(); print("sfx ok")
