"""Mouse-click sound effects only: a real-sounding mouse click (press + release) when each story is picked,
and a lighter click as it drops into the cart. No music. -> media/v2/sfx.wav"""
import os, json, wave
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v2")
cj = json.load(open(os.path.join(V, "cues.json"))); DUR = cj["dur"]; SR = 48000
mix = np.zeros((int(DUR * SR), 2)); rng = np.random.default_rng(11)
def add(sig, at, g):
    i = int(at * SR); j = min(len(mix), i + len(sig)); mix[i:j] += sig[: j - i, None] * g
def tick(f, decay, noise=0.6):
    t = np.arange(int(0.03 * SR)) / SR; n = rng.standard_normal(len(t)); n = n - np.convolve(n, np.ones(3) / 3, "same")
    return (np.sin(2 * np.pi * f * t) * 0.7 + n * noise) * np.exp(-t * decay)
def mouse_click():                               # micro-switch press, then a softer release ~70 ms later
    press = tick(3400, 520) + 0.5 * tick(1700, 380, 0.2)
    release = 0.45 * (tick(3900, 650) + 0.4 * tick(2000, 450, 0.2))
    out = np.zeros(int(0.12 * SR)); out[:len(press)] += press; k = int(0.068 * SR); out[k:k + len(release)] += release
    return out
for t in cj["ticks"]:
    add(mouse_click(), t, 0.9)                   # click: the story is picked
for t in cj["pops"]:
    add(mouse_click(), t - 0.02, 0.55)           # lighter click: it lands in the cart
mix = mix / (np.abs(mix).max() + 1e-9) * 0.85
w = wave.open(os.path.join(V, "sfx.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype("<i2").tobytes()); w.close(); print("mouse clicks at", cj["ticks"], cj["pops"])
