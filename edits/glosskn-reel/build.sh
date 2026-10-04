#!/usr/bin/env bash
# Rebuild the GlossKN reel end to end: picture edit -> SFX/music -> overlays + cue sheet -> mix -> 4K render
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_BROWSER_PATH="${HYPERFRAMES_BROWSER_PATH:-$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/ | head -1)headless_shell}"
read -r MUSIC_DUR DROP B0 B1 <<< "$(cd pipeline && python3 -c '
from edl import *
print(round(TOTAL + 2.2, 3), SHOT_STARTS[1], round(to_out(40.58), 3), round(to_out(42.26), 3))')"
(cd pipeline && python3 build_base.py)                                  # media/base.mp4 (4K picture, cached per segment)
(cd pipeline && python3 make_audio_assets.py "$MUSIC_DUR" "$DROP" "$B0" "$B1")  # media/sfx/*.wav, media/music.wav
(cd pipeline && python3 gen_comp.py)                                    # index.html + media/cues.json
(cd pipeline && python3 build_mix.py)                                   # media/mix.wav
npx --yes hyperframes@0.8.122 lint
npx --yes hyperframes@0.8.122 render -q delivery -o renders/glosskn-power-cleanse-4k.mp4 "$@"
