#!/usr/bin/env bash
# Matte only the behind-text windows (.cache/windows.txt: id start dur) -> media/matte/<id>.webm,
# then assemble a full-length person-matte video (black outside the windows) -> media/fg_1080.webm
set -euo pipefail
cd "$(dirname "$0")/.."
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 media/base.mp4)
inputs=(-f lavfi -i "color=c=black@0.0:s=1080x1920:r=30:d=$DUR,format=yuva420p"); chain="[0:v]null[c0]"; i=0
while read -r id start dur; do
  ffmpeg -nostdin -v error -y -ss "$start" -t "$dur" -i media/base.mp4 -vf scale=1080:1920 -c:v libx264 -crf 14 -preset fast "media/matte/$id.src.mp4"
  hyperframes remove-background "media/matte/$id.src.mp4" -o "media/matte/$id.webm" --device cpu --quality best < /dev/null > /dev/null 2>&1
  echo "matted $id"
  i=$((i+1)); inputs+=(-c:v libvpx-vp9 -i "media/matte/$id.webm")
  chain="$chain;[$i:v]setpts=PTS-STARTPTS+$start/TB[m$i];[c$((i-1))][m$i]overlay=eof_action=pass:format=auto[c$i]"
done < .cache/windows.txt
ffmpeg -nostdin -v error -y "${inputs[@]}" -filter_complex "$chain" -map "[c$i]" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 2M -auto-alt-ref 0 media/fg_1080.webm
echo "matte assembled"
