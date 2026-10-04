#!/bin/bash
# Headless screenshots of each game state (title, far, world, stall, test) into /dev/shm/botc/game.png
HS=/root/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for h in title far world stall test; do
  hash="#$h"; [ $h = title ] && hash=""
  timeout 60 $HS --no-sandbox --disable-gpu --hide-scrollbars --window-size=390,844 --virtual-time-budget=4000 --screenshot=/dev/shm/botc/g_$h.png "file:///root/clocktower-ramen/index.html$hash" 2>&1 | grep -iv "bytes written\|dbus\|fontconfig\|^$" | head -5
done
timeout 60 $HS --no-sandbox --disable-gpu --window-size=390,844 --virtual-time-budget=3000 --dump-dom "file:///root/clocktower-ramen/index.html#test" 2>/dev/null | grep -o "<title>[^<]*</title>\|id=\"err\">[^<]*<"
python3 -c "
from PIL import Image
ims=[Image.open(f'/dev/shm/botc/g_{h}.png') for h in ('title','far','world','stall','test')]
s=Image.new('RGB',(390*5,844))
for i,im in enumerate(ims): s.paste(im,(i*390,0))
s.save('/dev/shm/botc/game.png')"
