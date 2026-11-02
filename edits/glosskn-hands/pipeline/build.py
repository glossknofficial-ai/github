"""GLOSSKN 'packing the PR box' reel, cut like the reference: real-time speed, one overhead camera, hard jump cuts
that keep only the moment each item is placed (hand sets it in and leaves). Lid opens -> 5 placements -> card ->
lid closes -> closed box. Gentle fixed crop, no filters, no sound."""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(P, "media", "clip3.mp4"), os.path.join(P, "final", "GLOSSKN-PR-Box-Reel-HD.mp4")
Z, OX, OY = 1.06, 0.70, 0.40
SHOTS = [(3.5, 5.0),     # lid opens
         (9.2, 10.2),    # bottle 1 set in
         (14.15, 15.1),  # bottle 2
         (20.2, 21.2),   # headband roll
         (24.35, 25.35), # bow
         (27.6, 28.6),   # sachet
         (29.8, 31.5),   # thank-you card (longest, as in the reference)
         (31.8, 32.95)]  # lid closes
HOLD_AT, HOLD = 32.95, 0.6
crop = f"crop=trunc(iw/{Z}/2)*2:trunc(ih/{Z}/2)*2:(iw-iw/{Z})*{OX}:(ih-ih/{Z})*{OY},scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,setsar=1"
fc, labels = "", []
for i, (a, b) in enumerate(SHOTS):
    fc += f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{crop}[s{i}];"; labels.append(f"[s{i}]")
fc += f"[0:v]trim={HOLD_AT}:{HOLD_AT + 0.04},setpts=PTS-STARTPTS,{crop},tpad=stop_mode=clone:stop_duration={HOLD}[h];"
labels.append("[h]")
fc += "".join(labels) + f"concat=n={len(labels)}:v=1:a=0,fps=30,format=yuv420p[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-an",
                "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-profile:v", "high", "-movflags", "+faststart", OUT], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT], capture_output=True, text=True).stdout
print("done", d.strip(), "s,", len(SHOTS) + 1, "shots")
