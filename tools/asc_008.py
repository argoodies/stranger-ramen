"""0.0.7 never got reviewed: turn that version record into 0.0.8 (new build, new what's-new text, review notes).
usage: asc_008.py <buildNumber>   (then asc_swap.py for screenshots, asc_submit.py --submit)"""
import sys, json, time
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = 'fe67c80d-93ba-4ced-9e7d-3d985597a25b'; BN = sys.argv[1]
def call(m, p, b=None):
    st, tx = req(m, p, b); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
def must(m, p, b=None):
    st, d = call(m, p, b)
    if st not in (200, 201, 204): print('!!', m, p, st, json.dumps(d.get('errors', d), ensure_ascii=False)[:800]); raise SystemExit(1)
    return d
b = must('GET', f'/v1/builds?filter[app]={APP}&filter[version]={BN}&fields[builds]=version,processingState')['data']; assert b and b[0]['attributes']['processingState'] == 'VALID', b
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
d = must('PATCH', f'/v1/appStoreVersions/{VID}', {'data': {'type': 'appStoreVersions', 'id': VID, 'attributes': {'versionString': '0.0.8'}}}); print('version is now', d['data']['attributes']['versionString'])
must('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': b[0]['id']}})
print('build on version', must('GET', f'/v1/appStoreVersions/{VID}/build?fields[builds]=version')['data']['attributes']['version'])
NEW = {'en-US': "- Achievement board on the ramen shop wall: collect five wooden badges and arrange them however you like\n- The owner now walks over before putting a bowl down, throwing something away or looking at the board\n- Tap the stairs or the door to enter the clocktower\n- Ramen shop hints and sounds tidied up",
       'zh-Hant': "· 拉麵店牆上多了一塊成就木板：收集五枚木質徽章，想怎麼擺就怎麼擺\n· 老闆會先走過去，再放碗、丟東西或看木板\n· 點樓梯或門才會走進鐘樓\n· 整理了拉麵店裡的提示和音效",
       'zh-Hans': "· 拉面店墙上多了一块成就木板：收集五枚木质徽章，想怎么摆就怎么摆\n· 老板会先走过去，再放碗、丢东西或看木板\n· 点楼梯或门才会走进钟楼\n· 整理了拉面店里的提示和音效"}
W = ['血染', '普卡', '水手', '异端', '異端', '说书人', '說書人', '恶魔', '惡魔', '镇民', '鎮民', '魔典', 'Pukka', 'Sailor', 'Heretic', 'Storyteller', 'Demon', 'ownsfolk', 'Grimoire', 'Blood']
for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']:
    lc = l['attributes']['locale']
    must('PATCH', f"/v1/appStoreVersionLocalizations/{l['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id'], 'attributes': {'whatsNew': NEW[lc]}}})
    chk = must('GET', f"/v1/appStoreVersionLocalizations/{l['id']}")['data']['attributes']
    print(lc, 'whatsNew set | terms left:', {k: [w for w in W if w in (chk.get(k) or '')] for k in ('description', 'whatsNew', 'promotionalText', 'keywords')})
rd = must('GET', f'/v1/appStoreVersions/{VID}/appStoreReviewDetail')['data']
must('PATCH', f"/v1/appStoreReviewDetails/{rd['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': rd['id'], 'attributes': {'notes': 'No login or account required. Fully offline single-player game. Tap anywhere on the title screen to start; tap the ground to walk, tap the small house to enter the ramen shop, tap the stairs or the door of the tall tower for the mini-game. In the ramen shop, tap the wooden board on the wall to see the badges.'}}})
print('review notes updated')
