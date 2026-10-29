"""GLOSSKN festive gift reel: first shot -> beat-cut close-up montage (flashes + slow-mo) -> closing line -> logo card.
No text. Writes renders/GLOSSKN-Festive-Gift.mp4"""
import os, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
SRC = os.path.join(P, "media", "source.mp4"); TMP = os.path.join(P, "media", "build"); os.makedirs(TMP, exist_ok=True)
FPS = 30; BPM = 112; BEAT = 60 / BPM; M0 = 7.6          # montage starts on a downbeat at 7.6s

# (src_in, beats, speed, z0, z1, cx, cy, flash)  -- close-ups, re-sequenced
MONTAGE = [
    (9.20, 2, 0.5, 1.15, 1.30, 0.50, 0.60, True),    # box placed beside the diyas
    (12.00, 2, 1.0, 1.20, 1.08, 0.50, 0.70, False),  # lid lifts, kit revealed
    (17.10, 1, 0.5, 1.90, 2.10, 0.00, 0.05, True),   # candle flame
    (18.30, 1, 1.0, 1.25, 1.30, 0.60, 0.40, False),  # kit from the top
    (23.00, 2, 0.6, 1.60, 1.80, 0.55, 0.45, True),   # pen writing her name
    (14.10, 1, 1.0, 1.30, 1.35, 0.50, 0.50, False),  # founder opening the box
    (19.20, 1, 1.0, 1.40, 1.45, 0.50, 0.30, False),  # headband in the kit
    (28.40, 2, 0.5, 1.30, 1.50, 0.40, 0.35, True),   # hands lifting the headband
    (26.75, 2, 1.0, 1.12, 1.20, 0.15, 0.65, False),  # founder holding the headband
    (11.30, 2, 0.5, 1.15, 1.30, 0.50, 0.50, False),  # closed box on petals
    (21.10, 2, 1.0, 1.00, 1.35, 0.50, 0.20, True),   # POWER RESET push-in
]
GRADE = ("eq=contrast=1.08:saturation=1.22:gamma=0.97,"
         "colorbalance=rs=0.04:bs=-0.04:rm=0.03:bm=-0.03:rh=0.02:bh=-0.02,"
         "split[a][b];[b]gblur=sigma=28[g];[a][g]blend=all_mode=screen:all_opacity=0.15,"
         "vignette=angle=PI/6,unsharp=5:5:0.35")

segs = []  # (src_in, frames, speed, z0, z1, cx, cy, extra_filters, grade)
segs.append((0.0, round(M0 * FPS), 1.0, 1.0, 1.08, 0.5, 0.25, "", True))   # FIRST shot (kept first)
cum = 0
for s, b, sp, z0, z1, cx, cy, fl in MONTAGE:
    a = round((M0 + cum * BEAT) * FPS); cum += b; e = round((M0 + cum * BEAT) * FPS)
    segs.append((s, e - a, sp, z0, z1, cx, cy, "fade=t=in:st=0:d=0.16:color=white" if fl else "", True))
T_CLOSE = (round(M0 * FPS) + sum(x[1] for x in segs[1:])) / FPS
segs.append((32.60, round(4.4 * FPS), 1.0, 1.10, 1.00, 0.5, 0.30,
             f"fade=t=out:st={4.4 - 0.22:.2f}:d=0.22:color=white", True))      # closing line
segs.append((37.07, round(2.6 * FPS), 1.0, 1.00, 1.03, 0.5, 0.5, "", False))  # LAST shot: logo card
TOTAL = sum(x[1] for x in segs) / FPS

files = []
for i, (s, n, sp, z0, z1, cx, cy, extra, grade) in enumerate(segs):
    out = os.path.join(TMP, f"s{i:02d}.mp4"); files.append(out)
    vf = "setpts=PTS-STARTPTS"
    if sp != 1.0:
        vf += f",setpts=PTS/{sp},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    vf += (f",scale=2304:4096:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*on/{n}':"
           f"x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':d=1:s=1080x1920:fps={FPS}")
    if grade: vf += "," + GRADE
    if extra: vf += "," + extra
    need = n / FPS * sp + 0.3
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-ss", f"{s}", "-t", f"{need}", "-i", SRC,
                    "-filter_complex", f"[0:v]{vf},format=yuv420p[v]", "-map", "[v]", "-frames:v", str(n),
                    "-an", "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-r", str(FPS), out], check=True)
    print("seg", i, n, "frames")

# ---------------- original festive music (numpy) ----------------
SR = 48000; N = int(TOTAL * SR) + SR; mus = np.zeros((N, 2)); rng = np.random.default_rng(7)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
def add(sig, at, g, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    j = min(N, i + len(sig)); st = sig[: j - i]
    mus[i:j, 0] += st * g * np.sqrt(1 - pan); mus[i:j, 1] += st * g * np.sqrt(1 + pan)
def tt(d): return np.arange(int(SR * d)) / SR
def dhol_boom():
    t = tt(0.6); f = 55 + 70 * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * np.minimum(1, t / 0.002)
def dhol_slap():
    t = tt(0.18); n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(6) / 6, "same") - np.convolve(n, np.ones(40) / 40, "same")
    return (n * 1.6 + 0.6 * np.sin(2 * np.pi * 330 * t)) * np.exp(-t * 30)
def tabla(f=620):
    t = tt(0.35)
    return sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (9 + 6 * k)) for k, a in [(1, 1), (2, .5), (3, .3), (4.1, .2)])
def ghungroo(v=1.0):
    t = tt(0.22); s = sum(np.sin(2 * np.pi * rng.uniform(4500, 9500) * t + rng.uniform(0, 6)) for _ in range(6))
    s += rng.standard_normal(len(t)) * 0.6
    return s * np.exp(-t * 22) * v / 4
def santoor(m, d=1.6):
    t = tt(d); f = mtof(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.2 + 1.4 * k)) for k, a in [(1, 1), (2.003, .5), (3.01, .25), (4.02, .12)])
    return s * np.minimum(1, t / 0.002)
def strike(m, at, g, pan):  # santoor double-strike
    add(santoor(m), at, g, pan); add(santoor(m), at + 0.035, g * 0.45, pan)
def drone(d):
    t = tt(d); s = np.zeros(len(t))
    for root in (38, 45, 50):  # D2 A2 D3 (Sa Pa Sa)
        f = mtof(root)
        s += sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0007 * np.sin(2 * np.pi * 0.13 * t)) + k) / k ** 1.3 for k in range(1, 9))
    return s / 9
def bell(m, d=3.0):
    t = tt(d); f = mtof(m)
    return sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * e) for k, a, e in [(1, 1, 1.2), (2.76, .5, 2.5), (5.4, .25, 4), (8.9, .1, 6)])

T_END = T_CLOSE + 4.4                         # logo card begins
SCALE = [62, 64, 66, 69, 71, 74, 76, 78, 81]   # D E F# A B D' E' F#' A'
# drone throughout with section levels
dr = drone(TOTAL + 1)
env = np.interp(np.arange(len(dr)) / SR, [0, 1.2, M0, M0 + 0.3, T_CLOSE, T_CLOSE + .3, TOTAL - 1.2, TOTAL + 1],
                [0, .55, .55, 1, 1, .7, .5, 0])
add(dr * env, 0, 0.10)
# intro: sparse santoor phrases + soft shimmer under the first line
for t0, m in [(0.3, 74), (1.4, 71), (2.1, 69), (3.2, 66), (4.3, 69), (5.0, 71), (5.9, 74), (6.6, 76)]:
    strike(m, t0, 0.13, rng.uniform(-.4, .4))
for k in range(int(M0 / (BEAT / 2))):
    add(ghungroo(0.35), k * BEAT / 2, 0.10, -0.3)
sw = tt(0.6); swell = rng.standard_normal(len(sw)) * (sw / 0.6) ** 3        # riser into the montage
swell = np.convolve(swell, np.ones(3) / 3, "same"); add(swell, M0 - 0.6, 0.12)
# montage groove
nb = round((T_CLOSE - M0) / BEAT)
mel = [74, 76, 78, 81, 78, 76, 74, 71, 69, 71, 74, 76, 78, 76, 74, 71, 74, 78]
for k in range(nb):
    t0 = M0 + k * BEAT; bar_pos = k % 4
    if bar_pos in (0, 2): add(dhol_boom(), t0, 0.9)
    if bar_pos == 1: add(dhol_boom(), t0 + BEAT / 2, 0.6)
    if bar_pos in (1, 3): add(dhol_slap(), t0, 0.45, 0.15)
    add(tabla(620), t0 + BEAT / 2, 0.25, -0.2)
    if bar_pos == 3: add(tabla(700), t0 + 3 * BEAT / 4, 0.2, 0.2)
    for h in range(2): add(ghungroo(1.0 if h == 0 else 0.6), t0 + h * BEAT / 2, 0.22, 0.35)
    strike(mel[k % len(mel)], t0, 0.17, -0.25); strike(mel[k % len(mel)] - 12, t0 + BEAT / 2, 0.08, 0.25)
add(dhol_boom(), M0, 0.4)
# closing line: soft, sparse
for k in range(int(4.4 / BEAT)):
    t0 = T_CLOSE + k * BEAT
    if k % 2 == 0: add(tabla(560), t0, 0.10)
    add(ghungroo(0.4), t0, 0.07, 0.3)
for k, m in enumerate([74, 69, 71, 66, 69, 62, 66, 69]):
    strike(m, T_CLOSE + k * BEAT, 0.10, (k % 2 - .5) * .6)
# logo card: dhol hit, santoor roll and temple bell
add(dhol_boom(), T_END, 0.8)
for k, m in enumerate([62, 66, 69, 74, 78, 81]): strike(m, T_END + k * 0.06, 0.14, (k - 2.5) * 0.15)
add(bell(86), T_END + 0.05, 0.10, 0.2); add(bell(74, 4), T_END + 0.05, 0.08, -0.2)
# small room
n = int(SR * 1.6); t = np.arange(n) / SR
for c in range(2):
    ir = rng.standard_normal(n) * np.exp(-t * 4); ir[: int(.015 * SR)] = 0
    L = N + n; wet = np.fft.irfft(np.fft.rfft(mus[:, c], L) * np.fft.rfft(ir, L), L)[:N]
    mus[:, c] = mus[:, c] + wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mus[:, c])) * 0.22
mus = mus[: int(TOTAL * SR)]
fo = int(1.0 * SR); mus[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mus = mus / (np.max(np.abs(mus)) + 1e-9) * 0.85
# duck music under the two spoken lines
tl = np.arange(len(mus)) / SR
spk = [(0.4, 7.3), (T_CLOSE + 33.0 - 32.6, T_CLOSE + 36.45 - 32.6)]
duck = np.ones(len(mus))
for a, b in spk: duck = np.minimum(duck, np.interp(tl, [a - .3, a, b, b + .3], [1, .35, .35, 1], left=1, right=1))
mus *= duck[:, None]
w = wave.open(os.path.join(TMP, "music.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mus, -1, 1) * 32767).astype("<i2").tobytes()); w.close()

# ---------------- assemble ----------------
lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
out = os.path.join(P, "renders", "GLOSSKN-Festive-Gift.mp4")
VG = 19  # linear voice gain in dB (raw peak -22.3 dB -> ~-3 dB), no limiter
fc = (f"[1:a]atrim=0:{M0},asetpts=PTS-STARTPTS,highpass=f=80,volume={VG}dB,afade=t=out:st={M0-0.15}:d=0.15[v1];"
      f"[1:a]atrim=32.6:37.0,asetpts=PTS-STARTPTS,highpass=f=80,volume={VG}dB,afade=t=in:d=0.1,afade=t=out:st=4.2:d=0.2,"
      f"adelay={int(T_CLOSE*1000)}:all=1[v2];"
      f"[2:a]volume=0.9[m];[v1][v2][m]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-f", "concat", "-safe", "0", "-i", lst, "-i", SRC,
                "-i", os.path.join(TMP, "music.wav"), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", "-t", f"{TOTAL}", out], check=True)
print("done", out, round(TOTAL, 2), "s; closing at", round(T_CLOSE, 2))
