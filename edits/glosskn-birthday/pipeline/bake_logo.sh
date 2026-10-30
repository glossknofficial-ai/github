#!/usr/bin/env bash
# Bake the 3D GLOSSKN rise into the founder video: founder -> logo (behind) -> her cut-out (front) -> media/v3/founder_baked.mp4
# The cut-out uses only the matte's alpha, applied to the untouched founder frames, so her picture is never altered.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -nostdin -v error -y -i media/v3/founder.mp4 \
  -framerate 30 -i media/v3/logo_w1/%03d.png -c:v libvpx-vp9 -i media/v3/matte/w1.webm \
  -framerate 30 -i media/v3/logo_w2/%03d.png -c:v libvpx-vp9 -i media/v3/matte/w2.webm \
  -filter_complex "[0:v]split=3[base][s1][s2];\
[s1]trim=start=9.0:duration=2.7,setpts=PTS-STARTPTS[f1];[2:v]alphaextract[a1];[f1][a1]alphamerge,setpts=PTS+9.0/TB[p1];\
[s2]trim=start=47.9:duration=3.3,setpts=PTS-STARTPTS[f2];[4:v]alphaextract[a2];[f2][a2]alphamerge,setpts=PTS+47.9/TB[p2];\
[1:v]setpts=PTS-STARTPTS+9.0/TB[l1];[3:v]setpts=PTS-STARTPTS+47.9/TB[l2];\
[base][l1]overlay=eof_action=pass:format=auto[a];[a][p1]overlay=eof_action=pass:format=auto[b];\
[b][l2]overlay=eof_action=pass:format=auto[c];[c][p2]overlay=eof_action=pass:format=auto,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 8 -preset slow -c:a copy media/v3/founder_baked.mp4
echo baked
