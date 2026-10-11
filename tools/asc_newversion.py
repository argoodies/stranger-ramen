"""Create the next App Store version from a processed build, fill in "what's new", make sure every
language has screenshots (re-uploading from a folder if they were not carried over), and attach the build.
usage: asc_newversion.py <versionString> <buildNumber> <screenshotDir>   — then run asc_submit.py <versionId> --submit"""
import sys, json, os, hashlib, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; ver, bn, shots = sys.argv[1], sys.argv[2], sys.argv[3]
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
NEW = {'en-US': "- A church on the little island across the bridge. Step inside and the lights go out: beat the small foes, then the whirlwind that follows them, and the lights come back on\n- Strike just as a foe attacks and the blow lands as a heavy parry\n- After every fight a chest stands before the cross with something new to carry or wear; speak to whoever turns up and you can fight on, up to three rounds\n- A backpack: drag knives and charms between your hands and your pack\n- The painting is back on the ramen shop wall",
       'zh-Hant': "· 過了橋的小島上多了一座教堂。走進去燈就熄了：先打倒小兵，再打倒隨後現身的旋風，燈才會重新亮起\n· 看準對方出手的一瞬砍過去，就是一記振刀重擊\n· 每次打完，十字架前都會出現寶箱，裡面是新的刀或飾品；和現身的人說話，可以繼續再戰，最多三輪\n· 新增背包：用拖曳的方式更換手上的刀和身上的飾品\n· 拉麵店牆上換回了那幅畫",
       'zh-Hans': "· 过了桥的小岛上多了一座教堂。走进去灯就熄了：先打倒小兵，再打倒随后现身的旋风，灯才会重新亮起\n· 看准对方出手的一瞬砍过去，就是一记振刀重击\n· 每次打完，十字架前都会出现宝箱，里面是新的刀或饰品；和现身的人说话，可以继续再战，最多三轮\n· 新增背包：用拖动的方式更换手上的刀和身上的饰品\n· 拉面店墙上换回了那幅画"}
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
        if have.get(typ): continue
        for s in sets:
            if s['attributes']['screenshotDisplayType'] == typ: must('DELETE', f"/v1/appScreenshotSets/{s['id']}")
        sid = must('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': lid}}}}})['data']['id']
        for i in range(1, 6): upload(sid, f'{shots}/{pre}_{i}.png')
        print(lc, typ, 'uploaded 5')
must('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': b[0]['id']}})
print('build on version', must('GET', f'/v1/appStoreVersions/{VID}/build?fields[builds]=version')['data']['attributes']['version'])
print('VERSION_ID', VID)
