"""GLOSSKN festive gift reel v2 — luxury/emotional cut.
First shot (her opening line) -> 20-beat product montage (real-sample festive score, warm light leaks, slow-mo)
-> closing line -> logo card (last shot). No text. Writes renders/GLOSSKN-Festive-Gift-v2.mp4"""
import os, subprocess, wave, functools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE); MED = os.path.join(P, "media")
TMP = os.path.join(MED, "build2"); os.makedirs(TMP, exist_ok=True)
SRC = {k: os.path.join(MED, f"{k}.mp4") for k in ("source", "assorting", "box_push", "box_diyas")}
FPS = 30; BPM = 92; BEAT = 60 / BPM; M0 = 7.6     # montage starts on the downbeat right after her first line

# (file, src_in, beats, speed, z0, z1, cx, cy, leak)
MONTAGE = [
    ("box_diyas", 1.0, 2, 0.5, 1.90, 2.00, 0.00, 0.48, True),   # diya flames
    ("box_push", 1.2, 2, 1.0, 1.00, 1.06, 0.50, 0.50, False),   # push in on the GLOSSKN box
    ("source", 12.0, 2, 1.0, 1.08, 1.00, 0.50, 0.70, False),    # lid lifts, kit revealed
    ("assorting", 4.0, 1, 1.0, 1.04, 1.08, 0.50, 0.60, False),  # first bottle placed
    ("assorting", 7.0, 1, 1.0, 1.08, 1.04, 0.60, 0.60, False),  # second bottle
    ("assorting", 10.5, 1, 1.0, 1.04, 1.08, 0.40, 0.60, False), # headband roll
    ("assorting", 15.2, 2, 0.5, 1.05, 1.12, 0.40, 0.55, True),  # bow headband, slow
    ("source", 17.1, 1, 0.5, 1.50, 1.55, 0.00, 0.05, False),    # candle flame
    ("source", 21.1, 1, 1.0, 1.00, 1.08, 0.50, 0.20, False),    # POWER RESET lid
    ("source", 23.0, 2, 0.6, 1.25, 1.35, 0.55, 0.45, True),     # her name being written
    ("source", 26.75, 1, 1.0, 1.05, 1.10, 0.20, 0.60, False),   # founder with the headband
    ("assorting", 21.8, 2, 1.0, 1.04, 1.10, 0.60, 0.55, False), # thank-you card
    ("assorting", 24.9, 2, 1.0, 1.10, 1.02, 0.50, 0.60, True),  # lid closes — gift ready
]
GRADE = ("eq=contrast=1.04:saturation=1.12:gamma=1.03,"
         "curves=all='0/0.03 0.25/0.245 0.5/0.52 0.8/0.84 1/0.975',"
         "colorbalance=rs=0.03:bs=-0.03:rm=0.04:gm=0.01:bm=-0.04:rh=0.03:bh=-0.02,"
         "split[ga][gb];[gb]gblur=sigma=40[gg];[ga][gg]blend=all_mode=screen:all_opacity=0.14,"
         "vignette=angle=PI/7")
FINISH = "cas=0.55,noise=c0s=4:allf=t"

segs = [("source", 0.0, round(M0 * FPS), 1.0, 1.0, 1.06, 0.5, 0.25, False, True, "")]   # FIRST shot
cum = 0
for f, s, b, sp, z0, z1, cx, cy, lk in MONTAGE:
    a = round((M0 + cum * BEAT) * FPS); cum += b; e = round((M0 + cum * BEAT) * FPS)
    segs.append((f, s, e - a, sp, z0, z1, cx, cy, lk, True, ""))
F_CLOSE = sum(x[2] for x in segs); T_CLOSE = F_CLOSE / FPS
segs.append(("source", 32.60, round(4.4 * FPS), 1.0, 1.08, 1.0, 0.5, 0.30, False, True,
             f"fade=t=out:st={4.4 - 0.3:.2f}:d=0.3:color=white"))                       # closing line
segs.append(("source", 37.07, round(2.6 * FPS), 1.0, 1.0, 1.03, 0.5, 0.5, False, False, ""))  # LAST: logo card
T_LOGO = T_CLOSE + 4.4; TOTAL = sum(x[2] for x in segs) / FPS


def make_leak():
    """Warm golden light leak (screen-blended): two soft blobs sweep in from the edge and fade."""
    out = os.path.join(TMP, "leak.mp4")
    if os.path.exists(out): return out
    W, H, n = 270, 480, 24
    yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    frames = []
    for i in range(n):
        t = i / FPS; env = min(1, t / 0.1) * np.exp(-max(0, t - 0.1) * 4.5)
        b1 = np.exp(-(((xx - (-0.1 + 0.9 * t)) / 0.35) ** 2 + ((yy - 0.35) / 0.5) ** 2))
        b2 = np.exp(-(((xx - (1.1 - 0.6 * t)) / 0.3) ** 2 + ((yy - 0.75) / 0.35) ** 2))
        img = (b1[..., None] * [1.0, 0.72, 0.38] + b2[..., None] * [1.0, 0.45, 0.30] * 0.8) * env
        frames.append((np.clip(img, 0, 1) * 255).astype(np.uint8))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-vf", "scale=1080:1920:flags=bicubic,gblur=sigma=20",
                          "-c:v", "libx264", "-crf", "8", "-pix_fmt", "yuv444p", out], stdin=subprocess.PIPE)
    p.communicate(np.stack(frames).tobytes()); return out


LEAK = make_leak()
files = []
for i, (f, s, n, sp, z0, z1, cx, cy, lk, grade, extra) in enumerate(segs):
    out = os.path.join(TMP, f"s{i:02d}.mp4"); files.append(out)
    if os.environ.get("REUSE") and os.path.exists(out): continue
    vf = "setpts=PTS-STARTPTS"
    if sp != 1.0:
        vf += f",setpts=PTS/{sp},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    if grade: vf += ",hqdn3d=2:1.5:3:3"   # clean WhatsApp compression before upscaling
    vf += (f",scale=2160:3840:flags=lanczos,setsar=1,zoompan=z='{z0}+({z1}-{z0})*on/{n}':"
           f"x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':d=1:s=1080x1920:fps={FPS}")
    if grade: vf += "," + GRADE + "," + FINISH
    if extra: vf += "," + extra
    inputs = ["-ss", f"{s}", "-t", f"{n / FPS * sp + 0.3}", "-i", SRC[f]]
    if lk:
        inputs += ["-i", LEAK]
        fc = f"[0:v]{vf},format=gbrp[base];[1:v]format=gbrp[lk];[base][lk]blend=all_mode=screen:all_opacity=0.8:shortest=0:repeatlast=0,format=yuv420p[v]"
    else:
        fc = f"[0:v]{vf},format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *inputs, "-filter_complex", fc, "-map", "[v]",
                    "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "10", "-preset", "medium", "-r", str(FPS), out],
                   check=True)
    print("seg", i, f, n, "frames", flush=True)

# ======================= score: real recorded samples =======================
SR = 48000; N = int((TOTAL + 1) * SR); mix = np.zeros((N, 2)); rng = np.random.default_rng(11)
SMP = os.path.join(MED, "samples"); NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


@functools.lru_cache(None)
def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(r, np.float32).astype(np.float64)
    a = np.abs(x); on = int(np.argmax(a > a.max() * 0.02)) if len(x) else 0
    return x[max(0, on - 48):]


def note(inst, m, dur, rel=0.4):
    x = load(os.path.join(SMP, inst, f"{NAMES[m % 12]}{m // 12 - 1}.mp3"))
    assert len(x) > SR, (inst, m)
    if dur + rel > len(x) / SR - 0.05:    # sustain longer notes by cross-fading the loop body
        body = x[int(0.8 * SR):int(2.6 * SR)]; cf = int(0.4 * SR); out = x[:int(2.6 * SR)].copy()
        while len(out) < (dur + rel) * SR:
            seg = body.copy(); fade = np.linspace(0, 1, cf)
            out[-cf:] = out[-cf:] * (1 - fade) + seg[:cf] * fade
            out = np.concatenate([out, seg[cf:]])
        x = out
    L = min(len(x), int((dur + rel) * SR)); y = x[:L].copy()
    r = int(rel * SR); 
    if L > r: y[-r:] *= np.linspace(1, 0, r) ** 2
    return y


def add(sig, at, g, pan=0.0):
    i = int(round(at * SR))
    if i >= N: return
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig)); s = sig[: j - i]
    mix[i:j, 0] += s * g * np.sqrt((1 - pan) / 2) * 1.414; mix[i:j, 1] += s * g * np.sqrt((1 + pan) / 2) * 1.414


def dirt(name, dur=0.6):
    x = load(os.path.join(SMP, "dirt", name)); L = min(len(x), int(dur * SR)); y = x[:L].copy()
    r = min(L, int(0.12 * SR)); y[-r:] *= np.linspace(1, 0, r); return y


# tabla bols (real tabla one-shots)
NA = [dirt("tabla2/23645_loofa_A_001.wav"), dirt("tabla2/23646_loofa_A_002.wav"), dirt("tabla2/23649_loofa_A_005.wav")]
TI = [dirt(f"tabla2/{k}.wav", 0.25) for k in ("23653_loofa_A_009", "23655_loofa_A_011", "23659_loofa_A_015", "23662_loofa_A_018")]
GE = dirt("tabla/022_lower4_hit.wav", 0.9); KA = dirt("tabla/003_dead_hit1.wav", 0.2)
DHI = dirt("tabla/007_hi_flick1.wav", 0.8)
def bol(b, t, g=1.0):
    if b in ("dha", "ge", "dhi"): add(GE, t, 0.55 * g, -0.1)
    if b in ("dha", "na"): add(NA[rng.integers(3)], t + rng.uniform(0, .006), 0.42 * g, 0.15)
    if b == "dhi": add(DHI, t, 0.38 * g, 0.15)
    if b == "ti": add(TI[rng.integers(4)], t + rng.uniform(0, .006), 0.30 * g, 0.2)
    if b == "ka": add(KA, t, 0.35 * g, -0.15)
KEHERWA = ["dha", "ge", "na", "ti", "na", "ka", "dhi", "na"]   # 8 eighth-notes

CH = {"D": [50, 57, 62, 66, 69], "Bm": [47, 54, 59, 62, 66], "G": [43, 55, 59, 62, 67], "A": [45, 52, 57, 61, 64],
      "Em": [40, 52, 55, 59, 64]}
def chord(name, t, dur, g_str=0.10, g_pad=0.06):
    for k, m in enumerate(CH[name]):
        add(note("string_ensemble_1", m + 12 if k else m, dur, 0.8), t, g_str * (1.2 if k == 0 else 1), (k - 2) * 0.18)
        if k: add(note("pad_2_warm", m, dur, 0.8), t, g_pad, (2 - k) * 0.15)
    add(note("cello", CH[name][0], dur, 0.6), t, g_str * 1.1, -0.2)
def harp_arp(name, t, beats, step=0.5, g=0.11, up=True):
    tones = [m + 12 for m in CH[name][1:]] + [CH[name][2] + 24]
    seq = tones if up else tones[::-1]
    for k in range(int(beats / step)):
        add(note("orchestral_harp", seq[k % len(seq)], 1.4, 0.5), t + k * step * BEAT + rng.uniform(-.004, .004), g, (k % 4 - 1.5) * 0.25)
def sparkle(t, g=0.05):
    for k, m in enumerate([86, 90, 93, 95]): add(note("tinkle_bell", m, 1.5, 0.6), t + k * 0.07, g, 0.4 - k * 0.25)
def sitar_strum(t, g=0.32, chordfile="dirt/sitar/000_d_maj_sitar_chorda.wav"):
    add(load(os.path.join(SMP, chordfile))[: int(3.5 * SR)] * np.linspace(1, 0, int(3.5 * SR))[: len(load(os.path.join(SMP, chordfile))[: int(3.5 * SR)])] ** 1.5, t, g, 0.1)

bar = 4 * BEAT
# --- A: under her opening line (0 – 7.6): warm strings + harp, sparse and tender
A_START = M0 - 3 * bar        # phrase so the bar grid lands on the montage downbeat
for k, c in enumerate(["D", "Bm", "G"]):
    t0 = A_START + k * bar
    chord(c, max(0, t0), bar + 0.4, 0.2, 0.13)
    harp_arp(c, t0, 4, step=1.0, g=0.2)
sparkle(0.25, 0.1)
add(note("flute", 74, 1.2, 0.6), 2.35, 0.13, -0.2)
# tabla roll pulls into the montage (after her line ends at 7.16)
for k, b in enumerate(["ti", "ti", "ti", "ti", "ka", "ti"]):
    bol(b, M0 - 0.38 + k * 0.065, 0.45 + k * 0.1)
# --- B: montage (5 bars): full festive groove + flute then shehnai melody
B = ["D", "Bm", "G", "A", "D"]
for k, c in enumerate(B):
    t0 = M0 + k * bar
    chord(c, t0, bar + 0.2, 0.11, 0.06)
    harp_arp(c, t0, 4, step=0.5, g=0.07, up=(k % 2 == 0))
    add(note("taiko_drum", 38, 1.2, 0.6), t0, 0.35, 0)
    for e, b in enumerate(KEHERWA):
        bol(b, t0 + e * BEAT / 2, 0.9 if e in (0, 6) else 0.7)
    if k in (1, 3):  # tirakita fill at the end of every second bar
        for q in range(4): bol("ti", t0 + 3.5 * BEAT + q * BEAT / 8, 0.6 + 0.1 * q)
sitar_strum(M0, 0.30); sparkle(M0, 0.05)
MEL = [  # (bar, beat, midi, beats)
    (0, 0, 69, 1.5), (0, 1.5, 71, .5), (0, 2, 74, 1), (0, 3, 73, 1),
    (1, 0, 71, 1.5), (1, 1.5, 69, .5), (1, 2, 66, 1), (1, 3, 69, 1),
    (2, 0, 67, 1), (2, 1, 69, .5), (2, 1.5, 71, .5), (2, 2, 74, 1.5), (2, 3.5, 76, .5),
    (3, 0, 78, 2), (3, 2, 76, 1), (3, 3, 73, 1),
    (4, 0, 74, 3)]
for b_, bt, m, d in MEL:
    t = M0 + b_ * bar + bt * BEAT
    if b_ < 2: add(note("flute", m, d * BEAT, 0.35), t, 0.16, -0.15)
    else:
        add(note("shanai", m, d * BEAT, 0.3), t, 0.12, -0.1)
        add(note("flute", m, d * BEAT, 0.35), t, 0.07, 0.2)
for k, (b_, bt) in enumerate([(0, 3.5), (1, 3.5), (2, 3.5)]):   # sitar answers between phrases
    add(note("sitar", [74, 71, 78][k], 0.6, 0.4), M0 + b_ * bar + bt * BEAT, 0.14, 0.3)
sparkle(M0 + 2 * bar, 0.04); sparkle(M0 + 4 * bar, 0.05)
# --- C: her closing line: drop the drums, strings + harp carry the emotion
chord("G", T_CLOSE, 2.3, 0.2, 0.13); chord("A", T_CLOSE + 2.2, 2.3, 0.2, 0.13)
harp_arp("G", T_CLOSE, 3.5, 1.0, 0.18); harp_arp("A", T_CLOSE + 2.2, 3.0, 1.0, 0.18)
add(note("flute", 76, 0.9, 0.5), T_CLOSE + 0.05, 0.12, -0.2)
# --- D: logo card: sitar + temple bell + D major bloom
sitar_strum(T_LOGO, 0.30, "dirt/sitar/002_d_maj_sitar_chordc.wav")
chord("D", T_LOGO, 2.8, 0.11, 0.07)
add(note("tubular_bells", 74, 2.8, 0.8), T_LOGO, 0.16, -0.15); add(note("tubular_bells", 81, 2.8, 0.8), T_LOGO + 0.02, 0.08, 0.2)
bol("dha", T_LOGO, 1.0); add(note("taiko_drum", 38, 1.5, 0.6), T_LOGO, 0.4)
sparkle(T_LOGO + 0.1, 0.06)
for k, m in enumerate([74, 78, 81, 86]): add(note("orchestral_harp", m, 1.5, 0.6), T_LOGO + 0.25 + k * 0.09, 0.09, (k - 1.5) * .3)

# hall reverb
n = int(SR * 2.6); t = np.arange(n) / SR
for c in range(2):
    ir = rng.standard_normal(n) * np.exp(-t * 2.6); ir[: int(.02 * SR)] = 0
    L = N + n; wet = np.fft.irfft(np.fft.rfft(mix[:, c], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, c] = mix[:, c] + wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix[:, c])) * 0.28
mix = mix[: int(TOTAL * SR)]
fi = int(0.4 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.9 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
tl = np.arange(len(mix)) / SR; duck = np.ones(len(mix))
for a, b in [(0.4, 7.25), (T_CLOSE + 33.0 - 32.6, T_CLOSE + 36.45 - 32.6)]:
    duck = np.minimum(duck, np.interp(tl, [a - .25, a, b, b + .25], [1, .6, .6, 1], left=1, right=1))
mix *= duck[:, None]
w = wave.open(os.path.join(TMP, "music.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes()); w.close()

# ======================= assemble =======================
lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
out = os.path.join(P, "renders", "GLOSSKN-Festive-Gift-v2.mp4")
VG = 19   # linear voice gain (raw peak -22.3 dB), no compression
fc = (f"[1:a]atrim=0:{M0},asetpts=PTS-STARTPTS,highpass=f=80,volume={VG}dB,afade=t=out:st={M0 - 0.15}:d=0.15[v1];"
      f"[1:a]atrim=32.6:37.0,asetpts=PTS-STARTPTS,highpass=f=80,volume={VG}dB,afade=t=in:d=0.1,afade=t=out:st=4.2:d=0.2,"
      f"adelay={int(round(T_CLOSE * 1000))}:all=1[v2];"
      f"[2:a]volume=0.95[m];[v1][v2][m]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-f", "concat", "-safe", "0", "-i", lst, "-i", SRC["source"],
                "-i", os.path.join(TMP, "music.wav"), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-preset", "slow", "-b:v", "8M", "-maxrate", "10M", "-bufsize", "16M",
                "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart", "-t", f"{TOTAL}", out], check=True)
print("done", out, round(TOTAL, 2), "s; close", round(T_CLOSE, 2), "logo", round(T_LOGO, 2))
