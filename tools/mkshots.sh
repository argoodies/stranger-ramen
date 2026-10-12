#!/bin/bash
# App Store screenshots for every store language: 5 scenes (island, ramen shop, a shooting star seen from the tower, church fight, church after the fight) x (iPhone 6.7" + iPad 12.9")
HS=/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
OUT=/dev/shm/botc/shots3; rm -rf $OUT
for pair in "en-US:en" "zh-Hans:hans" "zh-Hant:hant"; do
  lc=${pair%%:*}; lg=${pair##*:}; mkdir -p $OUT/$lc; i=1
  for h in day stall towermeteor shotchurch shotchurch2; do
    timeout 150 $HS --no-sandbox --disable-gpu --hide-scrollbars --window-size=430,932 --force-device-scale-factor=3 --virtual-time-budget=7000 --screenshot=$OUT/$lc/iphone_$i.png "file:///root/clocktower-ramen/index.html?lang=$lg#$h" >/dev/null 2>&1
    timeout 100 $HS --no-sandbox --disable-gpu --hide-scrollbars --window-size=1024,1366 --force-device-scale-factor=1 --virtual-time-budget=7000 --screenshot=$OUT/$lc/ipad_s$i.png "file:///root/clocktower-ramen/index.html?lang=$lg#$h" >/dev/null 2>&1
    i=$((i+1))
  done
done
python3 - <<'PY'
from PIL import Image
import os
O='/dev/shm/botc/shots3'; L=('en-US','zh-Hans','zh-Hant')
for lc in L:
    for i in range(1,6):
        im=Image.open(f'{O}/{lc}/ipad_s{i}.png').convert('RGB'); assert im.size==(1024,1366), im.size; im.resize((2048,2732),Image.LANCZOS).save(f'{O}/{lc}/ipad_{i}.png'); os.remove(f'{O}/{lc}/ipad_s{i}.png')
        im=Image.open(f'{O}/{lc}/iphone_{i}.png').convert('RGB'); assert im.size==(1290,2796), im.size; im.save(f'{O}/{lc}/iphone_{i}.png')
s=Image.new('RGB',(5*240,3*520),(20,20,40))
for r,lc in enumerate(L):
    for i in range(1,6): s.paste(Image.open(f'{O}/{lc}/iphone_{i}.png').resize((240,520)),((i-1)*240,r*520))
s.save('/dev/shm/botc/shots3_sheet.png')
t=Image.new('RGB',(5*240,320),(20,20,40))
for i in range(1,6): t.paste(Image.open(f'{O}/zh-Hans/ipad_{i}.png').resize((240,320)),((i-1)*240,0))
t.save('/dev/shm/botc/shots3_ipad.png')
print('done', sum(len(os.listdir(f'{O}/{lc}')) for lc in L))
PY
