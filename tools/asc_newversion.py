"""Create the next App Store version from a processed build, fill in "what's new", make sure every
language has screenshots (re-uploading from a folder if they were not carried over), and attach the build.
usage: asc_newversion.py <versionString> <buildNumber> <screenshotDir> [--replace]   — then run asc_submit.py <versionId> --submit
  --replace: drop the carried-over screenshots and upload every iphone_N / ipad_N in screenshotDir (or screenshotDir/<locale>), in order"""
import sys, json, os, hashlib, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; ver, bn, shots = sys.argv[1], sys.argv[2], sys.argv[3]; REPLACE = '--replace' in sys.argv
def must(m, p, b=None):
    st, tx = req(m, p, b); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in (200, 201, 204): print('!!', m, p, st, json.dumps(d.get('errors', d), ensure_ascii=False)[:800]); raise SystemExit(1)
    return d
b = must('GET', f'/v1/builds?filter[app]={APP}&filter[version]={bn}&fields[builds]=version,processingState')['data']
assert b and b[0]['attributes']['processingState'] == 'VALID', b
vs = must('GET', f'/v1/apps/{APP}/appStoreVersions?limit=20')['data']
v = next((x for x in vs if x['attributes']['versionString'] == ver), None)
if not v: v = must('POST', '/v1/appStoreVersions', {'data': {'type': 'appStoreVersions', 'attributes': {'platform': 'IOS', 'versionString': ver, 'releaseType': 'AFTER_APPROVAL', 'copyright': '2026 ARGoodies'}, 'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}})['data']
VID = v['id']; print('version', ver, VID, v['attributes'].get('appStoreState'))
NEW = {'en-US': "- After chapter one, the flower girl tells you chapter two is still being made\n- Once the iced coffee in the bar is taken, it stays gone for the rest of that day, even after reopening the game\n- Soft shadows at the foot of small things: tree trunks, lamp posts, potted plants, the bin, candlesticks, the chest\n- The town's street lamps light up at night with a warm pool of light, and go out by day\n- Clouds with one round puff on top\n- The corner buttons are nearly see-through, with a white edge and mark, and follow the sky on screen\n- The prophecy buttons are two small circles in a row beside the backpack\n- In the church fight, the drink, hearts and charm line up with the top row of buttons\n- Ramen shop: the chef only says it's time to make a bowl for himself once the third customer has eaten and left\n- The English home-screen name is now Ramen Odd",
       'zh-Hant': "· 通關第一章後，賣花女孩會告訴你第二章還在製作中\n· 酒館的冰咖啡被拿走後，重新打開遊戲當天也不會再出現\n· 小物件腳下多了淡淡的影子：樹幹、燈柱、盆栽、垃圾桶、燭台、寶箱\n· 小鎮的路燈夜裡會亮，燈下有一圈暖光；白天熄燈\n· 雲朵改成上方一個圓鼓包\n· 左上右上的按鈕幾乎透明，白邊白圖示，跟著畫面裡的天空變化\n· 預言按鈕改成兩個小圓，和背包排成一行\n· 教堂戰鬥時，飲品、生命值和飾品與第一排按鈕對齊\n· 拉麵店：等第三位客人吃完離開後，主角才說要給自己做一碗",
       'zh-Hans': "· 通关第一章后，卖花女孩会告诉你第二章还在制作中\n· 酒馆的冰咖啡被拿走后，重新打开游戏当天也不会再出现\n· 小物件脚下多了淡淡的影子：树干、灯柱、盆栽、垃圾桶、烛台、宝箱\n· 小镇的路灯夜里会亮，灯下有一圈暖光；白天熄灯\n· 云朵改成上方一个圆鼓包\n· 左上右上的按钮几乎透明，白边白图标，跟着画面里的天空变化\n· 预言按钮改成两个小圆，和背包排成一行\n· 教堂战斗时，饮品、生命值和饰品与第一排按钮对齐\n· 拉面店：等第三位客人吃完离开后，主角才说要给自己做一碗"}
def upload(set_id, path):
    data = open(path, 'rb').read()
    r = must('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(path), 'fileSize': len(data)}, 'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': set_id}}}}})['data']
    for op in r['attributes']['uploadOperations']:
        q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
        for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
        urllib.request.urlopen(q).read()
    must('PATCH', f"/v1/appScreenshots/{r['id']}", {'data': {'type': 'appScreenshots', 'id': r['id'], 'attributes': {'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']:
    lc, lid = l['attributes']['locale'], l['id']
    if lc in NEW: must('PATCH', f'/v1/appStoreVersionLocalizations/{lid}', {'data': {'type': 'appStoreVersionLocalizations', 'id': lid, 'attributes': {'whatsNew': NEW[lc]}}})
    sets = must('GET', f'/v1/appStoreVersionLocalizations/{lid}/appScreenshotSets?include=appScreenshots&limit=50')['data']
    have = {s['attributes']['screenshotDisplayType']: len(s['relationships']['appScreenshots']['data']) for s in sets}
    print(lc, 'whatsNew set; screenshots carried over:', have)
    for typ, pre in (('APP_IPHONE_67', 'iphone'), ('APP_IPAD_PRO_3GEN_129', 'ipad')):
        if have.get(typ) and not REPLACE: continue
        for s in sets:
            if s['attributes']['screenshotDisplayType'] == typ: must('DELETE', f"/v1/appScreenshotSets/{s['id']}")
        sid = must('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': lid}}}}})['data']['id']
        src = f'{shots}/{lc}' if os.path.isdir(f'{shots}/{lc}') else shots      # per-language folders when present
        n = 0
        while os.path.exists(f'{src}/{pre}_{n + 1}.png'): n += 1; upload(sid, f'{src}/{pre}_{n}.png')
        print(lc, typ, 'uploaded', n)
must('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': b[0]['id']}})
print('build on version', must('GET', f'/v1/appStoreVersions/{VID}/build?fields[builds]=version')['data']['attributes']['version'])
print('VERSION_ID', VID)
