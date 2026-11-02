"""'Add to cart' sound effects: a soft tap as a story is picked, and the classic shopping-app add-to-cart sound
(a quick bubbly pop into a bright two-note 'ding-ding') when it lands in the cart. No music. -> media/v2/sfx.wav"""
import os, json, wave
import numpy as np
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = os.path.join(P, "media", "v2")
cj = json.load(open(os.path.join(V, "cues.json"))); DUR = cj["dur"]; SR = 48000
mix = np.zeros((int(DUR * SR), 2))
def t_(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g, pan=0.0):
    i = int(at * SR); j = min(len(mix), i + len(sig)); s = sig[: j - i]
    mix[i:j, 0] += s * g * (1 - max(0, pan)); mix[i:j, 1] += s * g * (1 + min(0, pan))
def tap():                                    # soft UI tap as the story is picked
    t = t_(0.07); f = 900 - 300 * t / 0.07
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 60)
def bloop():                                  # bubbly pop: pitch rises quickly
    t = t_(0.09); f = 380 + 900 * (t / 0.09) ** 0.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * np.clip(t / 0.09, 0, 1)) ** 0.5 * np.exp(-t * 12)
def bell(f, d=0.6):                           # clean bright bell note
    t = t_(d)
    return sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + 5 * k)) for k, a in [(1, 1), (2, .35), (3, .12), (4.2, .06)]) * np.minimum(1, t / 0.002)
def add_to_cart(at, g=1.0, up=0):
    add(bloop(), at, 0.55 * g)
    add(bell(1318.5 * 2 ** (up / 12)), at + 0.07, 0.42 * g, -0.1)      # E6
    add(bell(1975.5 * 2 ** (up / 12)), at + 0.15, 0.42 * g, 0.1)       # B6
for t in cj["ticks"]:
    add(tap(), t, 0.35)
for k, t in enumerate(cj["pops"]):
    add_to_cart(t - 0.02, 1.0, up=2 * k)      # each item a step brighter: the cart is filling up
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
w = wave.open(os.path.join(V, "sfx.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype("<i2").tobytes()); w.close(); print("add-to-cart sfx ok", cj["pops"])
