"""GLOSSKN festive gift reel (emotional, lightly edited): founder's clean voice + licensed Diwali track.
- voice: raised and gently levelled so every word is clear (no other processing)
- music: soft intro under her first line, opens up for the product shots, dips under her closing line,
  swells on the logo card and fades out; smooth fades everywhere
- picture: her original video, copied untouched"""
import os, subprocess
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); M = os.path.join(P, "media")
SRC, MUSIC = os.path.join(M, "voice_only.mp4"), os.path.join(M, "music.mp3")
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                           capture_output=True, text=True).stdout)
SPEECH = [(0.40, 6.02), (17.30, 20.62)]   # her two lines (from silence detection)
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
voice = (f"[0:a]aresample=48000,volume='{gate}':eval=frame,highpass=f=80,acompressor=threshold=-34dB:ratio=2.2:attack=8:release=180:makeup=1,"
         "volume=20dB,alimiter=limit=0.89:level=false,afade=t=in:d=0.15[v]")
# whole mix lifted to Instagram loudness (about -15 LUFS) with a peak limiter so nothing clips
mix = (f"[v][m]amix=inputs=2:normalize=0:duration=first,volume=7dB,alimiter=limit=0.89:attack=3:release=60:level=false,"
       f"afade=t=out:st={DUR - 0.6}:d=0.6[a]")

# picture: her original video stream is copied bit-for-bit (no re-encode, no resize, no zoom)
out = os.path.join(P, "renders", "GLOSSKN-Festive-Gift-Emotional.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", MUSIC, "-filter_complex", f"{voice};{music};{mix}",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", "-t", f"{DUR}", out], check=True)
print("done", out, round(DUR, 2))
