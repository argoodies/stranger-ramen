import sys, json, hashlib, os, urllib.request
sys.path.insert(0, '/root'); from asc_api import req, token
APP = '6782641107'; BUILD = 'be84ca82-f888-40a3-9b65-6aadd946e5b1'; BASE = 'https://clocktower-ramen.fly.dev'
def call(m, p, body=None, ok=(200, 201, 204)):
    st, tx = req(m, p, body); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in ok: print('!!', m, p, st, tx[:600]); raise SystemExit(1)
    return d
# 1. version 0.0.4
vs = call('GET', f'/v1/apps/{APP}/appStoreVersions?limit=20')['data']
v = next((x for x in vs if x['attributes']['versionString'] == '0.0.4'), None)
if not v:
    v = call('POST', '/v1/appStoreVersions', {'data': {'type': 'appStoreVersions', 'attributes': {'platform': 'IOS', 'versionString': '0.0.4', 'releaseType': 'AFTER_APPROVAL', 'copyright': '2026 ARGoodies'}, 'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}})['data']
VID = v['id']; print('version', VID, v['attributes'].get('appStoreState'))
# 2. store text
TXT = {
 'en-US': dict(
  description="Clocktower Ramen is a small, quiet game about a ramen shop at the foot of a clocktower.\n\nCook: step behind the counter and make each bowl by hand. Tap the pot to boil the noodles, lift them into the bowl, add the broth, then the chili, cilantro or beef each customer asks for, and set it down in front of them. After a few bowls, make one for yourself.\n\nWander: leave whenever you like and stroll around the little floating island. Say hello to the townsfolk, watch day turn to night, peek into the library.\n\nPlay: step into the clocktower for a short three-player game of bluff and deduction hosted by the Storyteller. Draw a secret role, close your eyes at night, nominate and vote by day.\n\nHand-drawn isometric scenes, soft generative music, no ads, no accounts, fully offline.",
  keywords='ramen,noodles,cooking,cozy,isometric,relax,clocktower,deduction,casual,offline,puzzle,chef',
  whatsNew="A whole new Clocktower Ramen:\n- A new isometric world: a floating island, a clocktower, a ramen shop and a library\n- Make ramen by tapping the real things in the shop\n- A three-player deduction game inside the clocktower\n- Day and night, new music, new icon",
  promotionalText='Cook ramen, take a walk, and play a quiet game of bluff inside the clocktower. Cozy, offline, no ads.'),
 'zh-Hant': dict(
  description="《拉麵怪奇物語》是一款安靜的小品：鐘樓腳下，有一間小小的拉麵店。\n\n煮麵：站到料理台後，親手做好每一碗。點麵鍋下麵、撈起、放進碗裡、加湯，再照客人說的放辣、放香菜、加牛肉，端到客人面前。招呼完幾位客人，也給自己做一碗。\n\n散步：想走就走，到懸浮的小島上逛逛。和鎮民打聲招呼，看白天變成黑夜，到圖書館裡瞧一瞧。\n\n遊戲：走進鐘樓，參加一場由說書人主持的三人推理小遊戲。抽一張秘密身份，夜裡閉上眼睛，白天提名、投票。\n\n手繪等距視角場景、柔和的生成式音樂；無廣告、無帳號、完全離線。",
  keywords='拉麵,煮麵,料理,休閒,放鬆,等距,鐘樓,推理,小遊戲,離線,解壓',
  whatsNew="全新的《拉麵怪奇物語》：\n· 全新等距視角世界：懸浮小島、鐘樓、拉麵店和圖書館\n· 直接點店裡的鍋、碗、配料來做麵\n· 鐘樓裡新增三人推理小遊戲\n· 晝夜交替、全新音樂、全新圖示",
  promotionalText='煮一碗麵，散個步，再到鐘樓裡玩一局安靜的推理小遊戲。'),
}
locs = call('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']
LOC = {}
for l in locs:
    lc = l['attributes']['locale']; LOC[lc] = l['id']
    if lc in TXT:
        call('PATCH', f"/v1/appStoreVersionLocalizations/{l['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id'], 'attributes': dict(TXT[lc], supportUrl=BASE + '/support', marketingUrl=BASE + '/download')}})
        print('text ok', lc)
# 3. app info (name / subtitle / privacy url) on the editable appInfo
infos = call('GET', f'/v1/apps/{APP}/appInfos?limit=10')['data']
ed = next((i for i in infos if i['attributes'].get('state') not in ('READY_FOR_DISTRIBUTION',)), infos[0])
print('appInfo', ed['id'], ed['attributes'].get('state'))
INFO = {'en-US': dict(name='Clocktower Ramen', subtitle='Cozy ramen under the tower'), 'zh-Hant': dict(name='拉麵怪奇物語', subtitle='鐘樓下的手作拉麵小店')}
for l in call('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")['data']:
    lc = l['attributes']['locale']
    if lc in INFO:
        st, tx = req('PATCH', f"/v1/appInfoLocalizations/{l['id']}", {'data': {'type': 'appInfoLocalizations', 'id': l['id'], 'attributes': dict(INFO[lc], privacyPolicyUrl=BASE + '/privacy')}})
        print('info', lc, st, '' if st == 200 else tx[:400])
# 4. screenshots: replace whatever was inherited
def upload(set_id, path):
    data = open(path, 'rb').read()
    r = call('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(path), 'fileSize': len(data)}, 'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': set_id}}}}})['data']
    for op in r['attributes']['uploadOperations']:
        q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
        for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
        urllib.request.urlopen(q).read()
    call('PATCH', f"/v1/appScreenshots/{r['id']}", {'data': {'type': 'appScreenshots', 'id': r['id'], 'attributes': {'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
for lc, lid in LOC.items():
    sets = call('GET', f'/v1/appStoreVersionLocalizations/{lid}/appScreenshotSets?limit=50')['data']
    for s in sets:
        old = call('GET', f"/v1/appScreenshotSets/{s['id']}/appScreenshots?limit=50")['data']
        print(lc, 'existing set', s['attributes']['screenshotDisplayType'], len(old))
        call('DELETE', f"/v1/appScreenshotSets/{s['id']}")
    for typ, pre in (('APP_IPHONE_67', 'iphone'), ('APP_IPAD_PRO_3GEN_129', 'ipad')):
        sid = call('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': lid}}}}})['data']['id']
        for i in range(1, 6): upload(sid, f'/dev/shm/botc/shots/{pre}_{i}.png')
        print(lc, typ, 'uploaded 5')
# 5. build + review notes
call('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': BUILD}})
print('build attached')
rd = call('GET', f'/v1/appStoreVersions/{VID}/appStoreReviewDetail', ok=(200, 404))
if rd.get('data'):
    call('PATCH', f"/v1/appStoreReviewDetails/{rd['data']['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': rd['data']['id'], 'attributes': {'notes': 'No login or account required. Fully offline single-player game. Tap anywhere on the title screen to start; tap the ground to walk, tap the small house to enter the ramen shop, tap the clocktower for the mini-game. This update replaces the previous gameplay with a new version of the same ramen game.'}}})
    print('review notes ok')
print('VERSION_ID', VID)
