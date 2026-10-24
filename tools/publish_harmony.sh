#!/bin/bash
# Put a HarmonyOS build from the "HarmonyOS HAP" workflow on https://ramen-puzzle.fly.dev/harmony
# usage: tools/publish_harmony.sh <run number>      (the release is harmony-<run>)
set -eo pipefail
RUN=$1; [ -n "$RUN" ] || { echo "usage: $0 <run>"; exit 1; }
cd "$(dirname "$0")/../deploy"
gh release download "harmony-$RUN" -R argoodies/stranger-ramen -p ramen-puzzle.hap --clobber
VER=$(sed -n "s/.*versionName '\(.*\)'.*/\1/p" ../android/app/build.gradle)
SIZE=$(python3 -c "import os; n=os.path.getsize('ramen-puzzle.hap'); print(f'{n/1048576:.1f} MB' if n >= 1048576 else f'{round(n/1024)} KB')")
python3 - "$VER" "$RUN" "$SIZE" <<'PY'
import re, sys
ver, run, size = sys.argv[1:]
s = open('harmony.tpl.html').read()
s = re.sub(r'<small>HAP · .*?</small>', f'<small>HAP · {size} · 版本 {ver} (build {run})</small>', s)
open('harmony.html', 'w').write(s)
PY
grep -o '<small>HAP[^<]*' harmony.html
FLY_API_TOKEN=$(cat /root/.fly_token) ~/.fly/bin/flyctl deploy --ha=false
