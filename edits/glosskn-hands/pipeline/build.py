"""GLOSSKN 'packing the PR box' reel, modelled on the reference: one continuous overhead take (clip 3), lid opens ->
products go in one by one -> card -> lid closes -> closed GLOSSKN box. Speed-ramped to ~10 s; gentle fixed crop;
no filters, no sound (no music, as requested)."""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(P, "media", "clip3.mp4"), os.path.join(P, "final", "GLOSSKN-PR-Box-Reel-HD.mp4")
Z, OX, OY = 1.06, 0.70, 0.40                      # gentle crop (keeps the open lid and the closed box in frame)
SEGS = [(3.3, 5.3, 1.5), (5.3, 16.2, 4.0), (16.2, 26.0, 4.0), (26.0, 31.6, 3.5), (31.6, 32.95, 1.15)]
HOLD_AT, HOLD = 32.95, 0.85                       # closed box holds at the end
crop = f"crop=trunc(iw/{Z}/2)*2:trunc(ih/{Z}/2)*2:(iw-iw/{Z})*{OX}:(ih-ih/{Z})*{OY},scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,setsar=1"
fc, labels = "", []
for i, (a, b, sp) in enumerate(SEGS):
    blend = ""                                    # no frame blending: hands stay crisp (blending ghosted them)
    fc += f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS{blend},setpts=PTS/{sp},fps=30,{crop}[s{i}];"; labels.append(f"[s{i}]")
fc += f"[0:v]trim={HOLD_AT}:{HOLD_AT + 0.04},setpts=PTS-STARTPTS,{crop},tpad=stop_mode=clone:stop_duration={HOLD},fps=30[h];"
labels.append("[h]")
fc += "".join(labels) + f"concat=n={len(labels)}:v=1:a=0,format=yuv420p[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-an",
                "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-profile:v", "high", "-movflags", "+faststart", OUT], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT], capture_output=True, text=True).stdout
print("done", OUT, d.strip())
