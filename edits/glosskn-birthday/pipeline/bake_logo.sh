#!/usr/bin/env bash
# Bake the 3D GLOSSKN rise into the founder video: founder -> logo (behind) -> her cutout (front) -> media/v3/founder_baked.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -nostdin -v error -y -i media/v3/founder.mp4 \
  -framerate 30 -i media/v3/logo_w1/%03d.png -c:v libvpx-vp9 -i media/v3/matte/w1.webm \
  -framerate 30 -i media/v3/logo_w2/%03d.png -c:v libvpx-vp9 -i media/v3/matte/w2.webm \
  -filter_complex "[1:v]setpts=PTS-STARTPTS+9.0/TB[l1];[2:v]setpts=PTS-STARTPTS+9.0/TB[m1];\
[3:v]setpts=PTS-STARTPTS+47.9/TB[l2];[4:v]setpts=PTS-STARTPTS+47.9/TB[m2];\
[0:v][l1]overlay=eof_action=pass:format=auto[a];[a][m1]overlay=eof_action=pass:format=auto[b];\
[b][l2]overlay=eof_action=pass:format=auto[c];[c][m2]overlay=eof_action=pass:format=auto,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 14 -preset medium -c:a copy media/v3/founder_baked.mp4
echo baked
