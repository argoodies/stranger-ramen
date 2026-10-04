import sys, json, hashlib, os, time, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = 'fed92070-816f-4540-a87c-128f9011c636'; BASE = 'https://clocktower-ramen.fly.dev'
def call(m, p, body=None):
    st, tx = req(m, p, body); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
def must(m, p, body=None):
    st, d = call(m, p, body)
    if st not in (200, 201, 204): print('!!', m, p, st, json.dumps(d.get('errors', d), ensure_ascii=False)[:900]); raise SystemExit(1)
    return d
st, app = call('GET', f'/v1/apps/{APP}?fields[apps]=primaryLocale,name'); print('primaryLocale', app['data']['attributes'])
st, v = call('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState'); state = v['data']['attributes']['appStoreState']; print('version state', state)
# pull the version back out of the review queue so it can be edited
if state in ('WAITING_FOR_REVIEW', 'IN_REVIEW'):
    st, subs = call('GET', f'/v1/reviewSubmissions?filter[app]={APP}&filter[state]=WAITING_FOR_REVIEW,IN_REVIEW')
    for s in subs.get('data', []):
        d = must('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'canceled': True}}}); print('cancel submission', s['id'], d['data']['attributes']['state'])
    for k in range(20):
        st, v = call('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState'); state = v['data']['attributes']['appStoreState']
        if state in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED'): break
        time.sleep(6)
    print('version state now', state)
# app info localizations
st, infos = call('GET', f'/v1/apps/{APP}/appInfos?limit=10')
ed = next(i for i in infos['data'] if i['attributes'].get('state') != 'READY_FOR_DISTRIBUTION'); print('appInfo', ed['id'], ed['attributes'].get('state'))
il = {l['attributes']['locale']: l['id'] for l in must('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")['data']}; print('info locales', list(il))
if 'zh-Hans' not in il:
    d = must('POST', '/v1/appInfoLocalizations', {'data': {'type': 'appInfoLocalizations', 'attributes': {'locale': 'zh-Hans', 'name': '拉面怪奇物语', 'subtitle': '钟楼下的手作拉面小店', 'privacyPolicyUrl': BASE + '/privacy'}, 'relationships': {'appInfo': {'data': {'type': 'appInfos', 'id': ed['id']}}}}}); print('info zh-Hans created')
# version localizations
vl = {l['attributes']['locale']: l['id'] for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']}; print('version locales', list(vl))
ZH = dict(
  description="《拉面怪奇物语》是一款安静的小品：钟楼脚下，有一间小小的拉面店。\n\n煮面：站到料理台后，亲手做好每一碗。点面锅下面、捞起、放进碗里、加汤，再照客人说的放辣、放香菜、加牛肉，端到客人面前。招呼完几位客人，也给自己做一碗。\n\n散步：想走就走，到悬浮的小岛上逛逛。和镇民打声招呼，看白天变成黑夜，到图书馆里瞧一瞧。\n\n游戏：走进钟楼，参加一场由说书人主持的三人推理小游戏。抽一张秘密身份，夜里闭上眼睛，白天提名、投票。\n\n手绘等距视角场景、柔和的生成式音乐；无广告、无账号、完全离线。",
  keywords='拉面,煮面,料理,休闲,放松,等距,钟楼,推理,小游戏,离线,解压',
  whatsNew="全新的《拉面怪奇物语》：\n· 全新等距视角世界：悬浮小岛、钟楼、拉面店和图书馆\n· 直接点店里的锅、碗、配料来做面\n· 钟楼里新增三人推理小游戏\n· 昼夜交替、全新音乐、全新图标",
  promotionalText='煮一碗面，散个步，再到钟楼里玩一局安静的推理小游戏。', supportUrl=BASE + '/support', marketingUrl=BASE + '/download')
if 'zh-Hans' in vl:
    must('PATCH', f"/v1/appStoreVersionLocalizations/{vl['zh-Hans']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': vl['zh-Hans'], 'attributes': ZH}}); print('version zh-Hans text set')
else:
    d = must('POST', '/v1/appStoreVersionLocalizations', {'data': {'type': 'appStoreVersionLocalizations', 'attributes': dict(ZH, locale='zh-Hans'), 'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': VID}}}}}); vl['zh-Hans'] = d['data']['id']; print('version zh-Hans created')
def upload(set_id, path):
    data = open(path, 'rb').read()
    r = must('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(path), 'fileSize': len(data)}, 'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': set_id}}}}})['data']
    for op in r['attributes']['uploadOperations']:
        q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
        for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
        urllib.request.urlopen(q).read()
    must('PATCH', f"/v1/appScreenshots/{r['id']}", {'data': {'type': 'appScreenshots', 'id': r['id'], 'attributes': {'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
sets = must('GET', f"/v1/appStoreVersionLocalizations/{vl['zh-Hans']}/appScreenshotSets?limit=50")['data']
have = {s['attributes']['screenshotDisplayType'] for s in sets}
for typ, pre in (('APP_IPHONE_67', 'iphone'), ('APP_IPAD_PRO_3GEN_129', 'ipad')):
    if typ in have: continue
    sid = must('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': vl['zh-Hans']}}}}})['data']['id']
    for i in range(1, 6): upload(sid, f'/dev/shm/botc/shots/{pre}_{i}.png')
    print('zh-Hans', typ, 'uploaded 5')
# primary language → Simplified Chinese
for k in range(30):
    st, ss = call('GET', f"/v1/appStoreVersionLocalizations/{vl['zh-Hans']}/appScreenshotSets?include=appScreenshots&limit=50")
    states = [(x['attributes'].get('assetDeliveryState') or {}).get('state') for x in ss.get('included', [])]
    if states and all(x == 'COMPLETE' for x in states): break
    time.sleep(10)
print('zh-Hans screenshots', len(states), set(states))
d = must('PATCH', f'/v1/apps/{APP}', {'data': {'type': 'apps', 'id': APP, 'attributes': {'primaryLocale': 'zh-Hans'}}}); print('primaryLocale now', d['data']['attributes']['primaryLocale'])
# only Simplified Chinese and English remain
if 'zh-Hant' in vl: st, d = call('DELETE', f"/v1/appStoreVersionLocalizations/{vl['zh-Hant']}"); print('delete version zh-Hant', st, json.dumps(d.get('errors', ''), ensure_ascii=False)[:400])
if 'zh-Hant' in il: st, d = call('DELETE', f"/v1/appInfoLocalizations/{il['zh-Hant']}"); print('delete info zh-Hant', st, json.dumps(d.get('errors', ''), ensure_ascii=False)[:400])
print('final info locales', [(l['attributes']['locale'], l['attributes']['name']) for l in must('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")['data']])
print('final version locales', [l['attributes']['locale'] for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']])
