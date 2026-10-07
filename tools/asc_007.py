"""0.0.6 never got reviewed: turn that version into 0.0.7 with the new build and store text that no longer uses the board game's terms."""
import sys, json, time
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = 'fe67c80d-93ba-4ced-9e7d-3d985597a25b'; BN = sys.argv[1]
def call(m, p, b=None):
    st, tx = req(m, p, b); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
def must(m, p, b=None):
    st, d = call(m, p, b)
    if st not in (200, 201, 204): print('!!', m, p, st, json.dumps(d.get('errors', d), ensure_ascii=False)[:800]); raise SystemExit(1)
    return d
b = must('GET', f'/v1/builds?filter[app]={APP}&filter[version]={BN}&fields[builds]=version,processingState')['data']; assert b[0]['attributes']['processingState'] == 'VALID'
a = must('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState,versionString')['data']['attributes']; print('state', a)
if a['appStoreState'] not in ('WAITING_FOR_REVIEW', 'PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED'): print('not touching'); raise SystemExit(2)
if a['appStoreState'] == 'WAITING_FOR_REVIEW':
    for s in must('GET', f'/v1/reviewSubmissions?filter[app]={APP}&filter[state]=WAITING_FOR_REVIEW')['data']:
        must('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'canceled': True}}})
    for k in range(30):
        st8 = must('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState')['data']['attributes']['appStoreState']
        if st8 in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED'): break
        time.sleep(6)
    print('pulled back:', st8)
d = must('PATCH', f'/v1/appStoreVersions/{VID}', {'data': {'type': 'appStoreVersions', 'id': VID, 'attributes': {'versionString': '0.0.7'}}}); print('version is now', d['data']['attributes']['versionString'])
must('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': b[0]['id']}})
print('build on version', must('GET', f'/v1/appStoreVersions/{VID}/build?fields[builds]=version')['data']['attributes']['version'])
SWAP = {'en-US': [(' hosted by the Storyteller', ''), ('at the foot of a clocktower', 'at the foot of a tall tower'), ('step into the clocktower', 'step into the tower'), ('Say hello to the townsfolk', 'Say hello to the islanders')],
        'zh-Hant': [('由說書人主持的', ''), ('鐘樓腳下', '高塔腳下'), ('走進鐘樓', '走進高塔'), ('和鎮民打聲招呼', '和島上的人打聲招呼')],
        'zh-Hans': [('由说书人主持的', ''), ('钟楼脚下', '高塔脚下'), ('走进钟楼', '走进高塔'), ('和镇民打声招呼', '和岛上的人打声招呼')]}
NEW = {'en-US': "- Ramen shop: every step is pick up, then put down, with a hint ring on the rim of what to touch next; add chili and cilantro as many times as you like\n- Tower game: you nominate, votes are called clockwise, everyone answers out loud, and it opens straight into nightfall\n- Library: a proper bookshelf\n- Language button on the start screen",
       'zh-Hant': "· 拉麵店：每一步都是先拿起、再放下，下一步要碰的容器口沿會有提示光環；辣椒和香菜可以想加幾次加幾次\n· 高塔對局：由你提名，順時針唱票，每個人都會說出自己舉不舉手，開局直接入夜\n· 圖書館：書架重新畫過\n· 開始畫面也能切換語言",
       'zh-Hans': "· 拉面店：每一步都是先拿起、再放下，下一步要碰的容器口沿会有提示光环；辣椒和香菜可以想加几次加几次\n· 高塔对局：由你提名，顺时针唱票，每个人都会说出自己举不举手，开局直接入夜\n· 图书馆：书架重新画过\n· 开始画面也能切换语言"}
W = ['血染', '普卡', '水手', '异端', '異端', '说书人', '說書人', '恶魔', '惡魔', '钟楼', '鐘樓', '镇民', '鎮民', '魔典', 'locktower', 'Pukka', 'Sailor', 'Heretic', 'Storyteller', 'Demon', 'ownsfolk', 'Grimoire']
for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']:
    lc, at = l['attributes']['locale'], l['attributes']; desc = at['description']
    for x, y in SWAP[lc]: assert x in desc, (lc, x); desc = desc.replace(x, y)
    new = {'description': desc, 'whatsNew': NEW[lc]}
    for k in ('promotionalText', 'keywords'):
        v = at.get(k) or ''
        for x, y in (('clocktower', 'tower'), ('鐘樓', '高塔'), ('钟楼', '高塔')): v = v.replace(x, y)
        if v != (at.get(k) or ''): new[k] = v
    must('PATCH', f"/v1/appStoreVersionLocalizations/{l['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id'], 'attributes': new}})
    chk = must('GET', f"/v1/appStoreVersionLocalizations/{l['id']}")['data']['attributes']
    print(lc, 'updated', sorted(new), '| terms left:', {k: [w for w in W if w in (chk.get(k) or '')] for k in ('description', 'whatsNew', 'promotionalText', 'keywords')})
infos = must('GET', f'/v1/apps/{APP}/appInfos?limit=10')['data']; ed = next(i for i in infos if i['attributes'].get('state') != 'READY_FOR_DISTRIBUTION')
SUB = {'zh-Hant': '高塔下的手作拉麵小店', 'zh-Hans': '高塔下的手作拉面小店'}
for l in must('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")['data']:
    lc = l['attributes']['locale']
    if lc in SUB: must('PATCH', f"/v1/appInfoLocalizations/{l['id']}", {'data': {'type': 'appInfoLocalizations', 'id': l['id'], 'attributes': {'subtitle': SUB[lc]}}})
print('names/subtitles', [(l['attributes']['locale'], l['attributes']['name'], l['attributes']['subtitle']) for l in must('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")['data']])
rd = must('GET', f'/v1/appStoreVersions/{VID}/appStoreReviewDetail')['data']
must('PATCH', f"/v1/appStoreReviewDetails/{rd['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': rd['id'], 'attributes': {'notes': 'No login or account required. Fully offline single-player game. Tap anywhere on the title screen to start; tap the ground to walk, tap the small house to enter the ramen shop, tap the tall tower for the mini-game.'}}})
print('review notes updated')
