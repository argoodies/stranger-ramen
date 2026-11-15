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
NEW = {'en-US': "- Toppings look the way they do in their jars: rings of chili, leaves of cilantro, and thin slices of beef, one slice for each helping\n- The ramen shop sits in the middle of the screen, the same size as the other rooms, and its window looks out on the sky\n- When the chef eats his own bowl, the noodles, the soup and the bowl go in time with the three notes\n- The crow's beak is a deeper orange",
       'zh-Hant': "· 配料跟罐子裡的一樣：辣椒圈、香菜葉，牛肉是薄薄的肉片，加一次一片\n· 拉麵店置中，和其他房間一樣大，上餐窗外直接看到天空\n· 主角自己吃麵時，麵、湯、碗跟著三聲音效依次消失\n· 烏鴉的嘴變成更深的橙色",
       'zh-Hans': "· 配料跟罐子里的一样：辣椒圈、香菜叶，牛肉是薄薄的肉片，加一次一片\n· 拉面店居中，和其他房间一样大，上餐窗外直接看到天空\n· 主角自己吃面时，面、汤、碗跟着三声音效依次消失\n· 乌鸦的嘴变成更深的橙色"}
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
