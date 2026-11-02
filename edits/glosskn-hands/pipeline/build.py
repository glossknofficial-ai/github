"""GLOSSKN 'packing the PR box' reel, cut like the reference: real-time speed, one overhead camera, cuts on each
placement. Opening + bottles from clip 3; headbands, sachet, card, lid and the box being taken away from clip 1
(aligned to clip 3's framing so the box doesn't jump). The headbands flow with soft dissolves instead of hard
jump cuts. Gentle fixed crop, no filters, no sound."""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
OUT = os.path.join(P, "final", "GLOSSKN-PR-Box-Reel-HD.mp4")
Z, OX, OY = 1.06, 0.70, 0.40
ALIGN1 = "scale=iw*1.09:ih*1.09,rotate=3*PI/180:ow=iw:oh=ih,crop=720:1280:(iw-720)/2+16:(ih-1280)/2-20,"   # clip1 -> clip3 framing
# (input, start, end, transition INTO this shot: 'cut' or seconds of dissolve)
SHOTS = [(3, 3.5, 5.0, None),       # lid opens
         (3, 9.2, 10.2, "cut"),     # bottle 1
         (3, 14.15, 15.1, "cut"),   # bottle 2
         (3, 19.4, 21.3, 0.35),   # headband roll   (soft dissolve; clip 3, native framing = sharpest)
         (3, 24.3, 25.8, 0.35),   # bow             (soft dissolve; clip 3)
         (1, 21.5, 22.65, "cut"),   # sachet
         (1, 24.3, 25.75, "cut"),   # thank-you card
         (1, 26.2, 27.6, "cut"),    # lid closes
         (1, 29.6, 31.2, "cut")]   # closed box lifted and taken away
crop = f"crop=trunc(iw/{Z}/2)*2:trunc(ih/{Z}/2)*2:(iw-iw/{Z})*{OX}:(ih-ih/{Z})*{OY},scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,setsar=1"
TMP = os.path.join(M, "shots"); os.makedirs(TMP, exist_ok=True)
files = []
for i, (src, a, b, _) in enumerate(SHOTS):      # each shot rendered on its own (reliable trims, no shared decoders)
    f = os.path.join(TMP, f"s{i}.mp4"); files.append(f)
    pre = ALIGN1 if src == 1 else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", f"{b - a:.3f}", "-i", os.path.join(M, f"clip{src}.mp4"),
                    "-vf", f"{pre}{crop},fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "10", f], check=True)
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout)
ins = sum([["-i", f] for f in files], [])
# hard cuts are plain concats; only the headband shots are joined with soft dissolves
fc, chain, t = "", None, 0.0
for i in range(len(files)):
    lab = f"[{i}:v]"; fc += f"{lab}settb=1/30,setpts=N/30/TB[p{i}];"
    tr = SHOTS[i][3]; d = dur(files[i])
    if chain is None: chain, t = f"[p{i}]", d; continue
    if tr == "cut":
        fc += f"{chain}[p{i}]concat=n=2:v=1:a=0,settb=1/30,setpts=N/30/TB[c{i}];"
        chain, t = f"[c{i}]", t + d
    else:
        fc += f"{chain}[p{i}]xfade=transition=fade:duration={tr}:offset={t - tr:.4f},settb=1/30,setpts=N/30/TB[c{i}];"
        chain, t = f"[c{i}]", t + d - tr
fc = fc[:-1].rsplit(chain, 1)[0] + "[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-pix_fmt", "yuv420p", "-an",
                "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-profile:v", "high", "-movflags", "+faststart", OUT], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT], capture_output=True, text=True).stdout
print("done", d.strip(), "s")
