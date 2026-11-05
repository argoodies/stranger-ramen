# build game.html for recording: the game + a virtual clock + the driver; PingFang SC stands in as Noto Sans SC Light (weights up to 300: the title and thin text) and Noto Sans CJK SC Regular (400: speech bubbles, bold text)
src = open('/root/clocktower-ramen/index.html').read(); s = open('driver.js').read()
src = src.replace("if (!storyRain) for (let i = 0; i < 3; i++) {", "if (!storyRain && !window.__noGeese) for (let i = 0; i < 3; i++) {", 1)
ff = ("<style>@font-face{font-family:'PingFang SC';src:url('font/NotoSansSC-Light.otf');font-weight:100 300}"
      "@font-face{font-family:'PingFang SC';src:url('font/NotoSansCJKsc-Regular.otf');font-weight:400 900}</style>")
src = src.replace('<head>', '<head>' + ff + open('driver_head.js').read(), 1); i = src.rfind('</body>'); open('game.html', 'w').write(src[:i] + s + src[i:])
