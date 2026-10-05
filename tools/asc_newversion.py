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
NEW = {'en-US': "- Language setting: Simplified Chinese, Traditional Chinese, English, or follow the system (open the overview and tap the globe)\n- The game now opens at night, with a new title\n- Quieter when the app goes to the background\n- Small fixes",
       'zh-Hant': "· 新增語言設定：簡體中文、繁體中文、English，或跟隨系統（拉到全景後點右上角的地球）\n· 遊戲改為從夜晚開始，換了新的標題\n· 切到背景時不再有雜音\n· 一些細節修正",
       'zh-Hans': "· 新增语言设置：简体中文、繁體中文、English，或跟随系统（拉到全景后点右上角的地球）\n· 游戏改为从夜晚开始，换了新的标题\n· 切到后台时不再有杂音\n· 一些细节修正"}
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
