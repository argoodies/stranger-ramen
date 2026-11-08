#!/bin/bash
# Put an Android build from the "Android APK" workflow on https://ramen-puzzle.fly.dev/android
# usage: tools/publish_android.sh <run number> [--no-deploy]      (the release is android-<run>)
set -eo pipefail
RUN=$1; [ -n "$RUN" ] || { echo "usage: $0 <run> [--no-deploy]"; exit 1; }
cd "$(dirname "$0")/../deploy"
gh release download "android-$RUN" -R argoodies/stranger-ramen -p ramen-puzzle.apk -O ramen-puzzle.apk --clobber
VER=$(sed -n "s/.*versionName '\(.*\)'.*/\1/p" ../android/app/build.gradle)
SIZE=$(python3 -c "import os; n=os.path.getsize('ramen-puzzle.apk'); print(f'{n/1048576:.1f} MB' if n >= 1048576 else f'{round(n/1024)} KB')")
python3 - "$VER" "$RUN" "$SIZE" <<'PY'
import re, sys
ver, run, size = sys.argv[1:]
s = open('android.html').read()
s = re.sub(r'<small>APK · .*?</small>', f'<small>APK · {size} · 版本 {ver} (build {run})</small>', s)
open('android.html', 'w').write(s)
PY
grep -o '<small>APK[^<]*' android.html
[ "$2" = "--no-deploy" ] || FLY_API_TOKEN=$(cat /root/.fly_token) ~/.fly/bin/flyctl deploy --ha=false
