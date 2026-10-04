#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export HYPERFRAMES_BROWSER_PATH="${HYPERFRAMES_BROWSER_PATH:-$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/ | head -1)headless_shell}"
pipeline/matte_windows.sh
(cd behind && hyperframes render --format mov -o ../renders/behind.mov --quiet) && echo "behind rendered"
hyperframes render -q delivery -o renders/main.mp4 --quiet && echo "main rendered"
python3 pipeline/composite.py glosskn-power-cleanse-v3-4k.mp4 && echo "composited"
