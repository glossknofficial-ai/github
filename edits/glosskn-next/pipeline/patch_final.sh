#!/usr/bin/env bash
# Patch the finished reel without the (lost) source takes:
# 1) swap B-rolls: white-robe clip on "gentle on the eyes" (9.14-12.54), floral clip on the Power Melt "super gentle" (16.11-17.86)
# 2) redraw subtitles over those windows from subs/ (transparent HyperFrames render of the subtitle track only)
# 3) audio: voice separated from the old mix (UVR), de-hissed and gated, remixed with the regenerated journey music
set -euo pipefail
echo "see conversation steps; inputs: media/prev_final.mp4 media/robe.mp4 media/floral.mp4 media/subs.mov"
