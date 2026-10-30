"""GLOSSKN festive gift reel (emotional, lightly edited): founder's clean voice + licensed Diwali track.
- voice: raised and gently levelled so every word is clear (no other processing)
- music: soft intro under her first line, opens up for the product shots, dips under her closing line,
  swells on the logo card and fades out; smooth fades everywhere
- picture: her original video, copied untouched"""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
SRC, MUSIC = os.path.join(M, "original_hq2.mov"), os.path.join(M, "music.mp3")   # final cut (voice only, closing clip sped up)
PICTURE = os.path.join(M, "original_hq2.mov")   # her full-quality 1080x1920 original
OUTRO = os.path.join(M, "happy_diwali.mp4")       # Happy Diwali slide replaces the GLOSSKN logo card
CUT_FRAME = 603        # her clip ends here (20.1 s), just after her last word and before her blur-out to the old logo card
OUTRO_SKIP = 2         # the slide opens with two white frames
XF = 0.25              # short dissolve into the slide
OUTRO_DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUTRO],
                                 capture_output=True, text=True).stdout)
DUR = CUT_FRAME / 30 - XF + OUTRO_DUR - OUTRO_SKIP / 30
SPEECH = [(0.40, 6.02), (17.25, 20.02)]   # her two lines (from silence detection)
MUSIC_OFFSET = 3.0                          # start a little into the track's soft intro
FADE_IN, FADE_OUT = 1.5, 2.5

# music gain envelope (dB): low under speech, fuller in the product montage, small swell on the logo card
pts = [(0, -17), (SPEECH[0][1] - 0.15, -17), (SPEECH[0][1] + 0.55, -11), (SPEECH[1][0] - 0.6, -11), (SPEECH[1][0], -21),
       (SPEECH[1][1], -21), (SPEECH[1][1] + 0.7, -12), (DUR, -12)]
expr = "0"
for (t0, g0), (t1, g1) in zip(pts, pts[1:]):   # piecewise-linear volume expression
    expr = f"if(between(t,{t0},{t1}),{g0}+({g1}-{g0})*(t-{t0})/{max(1e-3, t1 - t0)},{expr})"
music = (f"[1:a]atrim=start={MUSIC_OFFSET},asetpts=PTS-STARTPTS,aresample=48000,"
         f"volume='pow(10,({expr})/20)':eval=frame,afade=t=in:d={FADE_IN},afade=t=out:st={DUR - FADE_OUT}:d={FADE_OUT}[m]")
# only her spoken lines are kept: the clips' own sound (box handling, rustle, room noise) is muted in between
R = 0.08
gate = "+".join(f"clip((t-{a - R})/{R},0,1)*clip(({b + R}-t)/{R},0,1)" for a, b in SPEECH)
voice = (f"[0:a]apad,aresample=48000,volume='{gate}':eval=frame,highpass=f=80,acompressor=threshold=-34dB:ratio=2.2:attack=8:release=180:makeup=1,"
         "volume=20dB,alimiter=limit=0.89:level=false,afade=t=in:d=0.15[v]")
# whole mix lifted to Instagram loudness (about -15 LUFS) with a peak limiter so nothing clips
mix = (f"[v][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:{DUR},volume=7dB,alimiter=limit=0.89:attack=3:release=60:level=false,"
       f"afade=t=out:st={DUR - 0.6}:d=0.6[a]")

# picture: her video untouched up to the logo card, then the Happy Diwali slide (4K, scaled to 1080x1920);
# encoded near-lossless (CRF 10) with the original's BT.709 colour tags
vid = ("[2:v]trim=end_frame=%d,setpts=PTS-STARTPTS,settb=1/30,setsar=1[a1];"
       "[3:v]trim=start_frame=%d,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,fps=30,settb=1/30,setsar=1,format=yuv420p[a2];"
       "[a1][a2]xfade=transition=fade:duration=%s:offset=%.4f[vid]" % (CUT_FRAME, OUTRO_SKIP, XF, CUT_FRAME / 30 - XF))
out = os.path.join(P, "renders", "GLOSSKN-Festive-Gift-Emotional.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", MUSIC, "-i", PICTURE, "-i", OUTRO,
                "-filter_complex", f"{voice};{music};{mix};{vid}", "-map", "[vid]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "10", "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", f"{DUR}", out], check=True)
print("done", out, round(DUR, 2))
