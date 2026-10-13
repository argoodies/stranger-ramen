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
NEW = {'en-US': "- The clocktower is now a quiet room with a torch and its keeper: ask him and he takes you up to see the whole town from the top, with a shooting star if it is night\n- The church: light the torch in the middle of the floor to start a fight; the boss only appears once the small foes are beaten. Win, open the chest, and you can light the torch again for a harder round\n- New things in the chests: twin blades, a necklace, a cross, a flower\n- Backpack: drag things to put them on, take them off or move them; a tap just shows what they are\n- Ramen shop: tap the floor to walk anywhere\n- Thicker walls and a new arched window in the library",
       'zh-Hant': "· 鐘樓改成了一間安靜的小石室，裡面有一支火把和看守它的人：請他帶你上塔頂，可以俯瞰整座小鎮，晚上還會有流星劃過\n· 教堂：點燃地板中央的火把才會開戰，打倒小兵之後首領才會現身；打贏、開完寶箱，可以再點一次火把挑戰更難的一輪\n· 寶箱裡多了新東西：雙刀、項鍊、十字架、鮮花\n· 背包改為拖曳操作：拖動來裝備、卸下或挪動，點一下只是查看\n· 拉麵店：點地板就能走到任何地方\n· 室內牆壁有了厚度，圖書館換了新的拱形窗",
       'zh-Hans': "· 钟楼改成了一间安静的小石室，里面有一支火把和看守它的人：请他带你上塔顶，可以俯瞰整座小镇，晚上还会有流星划过\n· 教堂：点燃地板中央的火把才会开战，打倒小兵之后首领才会现身；打赢、开完宝箱，可以再点一次火把挑战更难的一轮\n· 宝箱里多了新东西：双刀、项链、十字架、鲜花\n· 背包改为拖拽操作：拖动来装备、卸下或挪动，点一下只是查看\n· 拉面店：点地板就能走到任何地方\n· 室内墙壁有了厚度，图书馆换了新的拱形窗"}
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
