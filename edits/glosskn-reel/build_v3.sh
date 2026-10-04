#!/usr/bin/env bash
# Full rebuild: picture edit -> overlays/cues -> mix -> person matte (behind-text windows only)
# -> behind layer (alpha) -> main 4K render -> composite
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_BROWSER_PATH="${HYPERFRAMES_BROWSER_PATH:-$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/ | head -1)headless_shell}"
(cd pipeline && python3 build_base.py && python3 gen_comp.py && python3 gen_behind.py && python3 build_mix.py)
python3 - > .cache/windows.txt <<'P'
import re, sys; sys.path.insert(0, "pipeline")
from edl import to_out
s = open("pipeline/gen_behind.py").read()
for m in re.finditer(r'\("(b\w+)", ([0-9.]+), ([0-9.]+),', s):
    a, b = to_out(float(m.group(2))), to_out(float(m.group(3)))
    print(m.group(1), round(a - 0.1, 3), round(b - a + 0.2, 3))
P
pipeline/matte_windows.sh
(cd behind && hyperframes render --format mov -o ../renders/behind.mov --quiet) && echo "behind rendered"
hyperframes render -q delivery -o renders/main.mp4 --quiet && echo "main rendered"
python3 pipeline/composite.py glosskn-power-cleanse-v3-4k.mp4 && echo "composited"
