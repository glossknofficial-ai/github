"""Final composite: main render + behind-text layer masked by the person matte -> renders/<name>.mp4
   behind_alpha_out = behind_alpha * (1 - person_matte)"""
import os, subprocess, sys
from edl import PROJECT
R = os.path.join(PROJECT, "renders"); M = os.path.join(PROJECT, "media")
main, behind = os.path.join(R, "main.mp4"), os.path.join(R, "behind.mov")
fg = os.path.join(M, "fg_1080.webm")
out = os.path.join(R, sys.argv[1] if len(sys.argv) > 1 else "glosskn-power-cleanse-4k.mp4")
fc = ("[2:v]alphaextract,scale=2160:3840:flags=bicubic,gblur=sigma=2,negate,format=gray[keep];"   # 1 - person (soft edge)
      "[1:v]format=yuva444p,split[b1][b2];[b2]alphaextract,format=gray[ba];"
      "[ba][keep]blend=all_mode=multiply[na];[b1]format=yuv444p[brgb];[brgb][na]alphamerge[bm];"
      "[0:v][bm]overlay=0:0:format=auto:shortest=0,format=yuv420p[v]")
cmd = ["ffmpeg", "-y", "-v", "error", "-i", main, "-i", behind, "-c:v", "libvpx-vp9", "-i", fg,
       "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("wrote", out)
