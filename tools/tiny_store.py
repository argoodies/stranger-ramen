#!/usr/bin/env python3
"""App Store listing for Tiny Clocktower (app 6829382085), English only: version string, store text, URLs, category,
review contact and screenshots (iphone_N / ipad_N from a folder).
usage: tiny_store.py <versionString> <screenshotDir> [buildNumber]"""
import sys, json, os, hashlib, urllib.request, time
sys.path.insert(0, '/root'); from asc_api import req
APP = '6829382085'; VER, SHOTS = sys.argv[1], sys.argv[2]; BN = sys.argv[3] if len(sys.argv) > 3 else None
SITE = 'https://tiny-clocktower.fly.dev'      # the app's own little site (tiny-site/), apart from the game's
SUB = 'A pocket game of hidden roles'
DESC = """Three seats, one Storyteller, and a secret in every hand.

Tiny Clocktower is a pocket-sized game of hidden roles for one player. You and two computer players sit around a small floating table. Each of you is dealt a role in secret, and only the Storyteller knows the truth.

THE ROLES
• Sailor (good): each night, choose a player — either you or they are drunk until dusk. You can't die.
• Heretic (good): whoever wins, loses, and whoever loses, wins — even if you are dead.
• Pukka (evil): each night, poison a player. The player poisoned the night before dies.

NIGHT AND DAY
At night, the roles act in the dark. By day, the others claim who they are — and one of them may be lying. Then you nominate, everyone votes, and the table decides who is executed. A drunk or poisoned player's ability quietly fails, so nothing is quite what it seems. Reach the seventh day and the game is settled: good wins.

THE REVEAL
When the game ends, every token turns over, with the drunk and poisoned markers, so you can see exactly what happened.

• A full game in a few minutes
• Calm isometric art and soft generative music
• Game Center achievements and a most-wins leaderboard
• No ads, no accounts, no data collected
• English, 简体中文 and 繁體中文"""
KW = 'social deduction,hidden role,bluff,storyteller,mystery,logic,deduction,detective,secret,party'
PROMO = 'You, two rivals and a Storyteller: one secret each. Who is lying?'
def J(m, p, b=None, ok=(200, 201, 204)):
    st, tx = req(m, p, b); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in ok: print('!!', m, p, st, json.dumps(d.get('errors', d))[:600]); raise SystemExit(1)
    return d
vs = J('GET', f'/v1/apps/{APP}/appStoreVersions?limit=10')['data']
v = next((x for x in vs if x['attributes']['appVersionState'] in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED', 'REJECTED', 'METADATA_REJECTED')), None)
VID = v['id']
J('PATCH', f'/v1/appStoreVersions/{VID}', {'data': {'type': 'appStoreVersions', 'id': VID, 'attributes': {'versionString': VER, 'copyright': '2026 ARGoodies'}}}); print('version', VER, VID)
if BN:
    b = J('GET', f'/v1/builds?filter[app]={APP}&filter[version]={BN}&fields[builds]=version,processingState')['data']
    assert b and b[0]['attributes']['processingState'] == 'VALID', b
    J('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': b[0]['id']}}); print('build', BN)
L = J('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']
for l in L:
    if l['attributes']['locale'] != 'en-US': J('DELETE', f"/v1/appStoreVersionLocalizations/{l['id']}"); print('removed', l['attributes']['locale'])
LID = next(l['id'] for l in L if l['attributes']['locale'] == 'en-US')
J('PATCH', f'/v1/appStoreVersionLocalizations/{LID}', {'data': {'type': 'appStoreVersionLocalizations', 'id': LID, 'attributes': {'description': DESC, 'keywords': KW, 'promotionalText': PROMO, 'supportUrl': SITE + '/support', 'marketingUrl': SITE + '/support'}}}); print('text ok')
ai = J('GET', f'/v1/apps/{APP}/appInfos')['data'][0]
for l in J('GET', f"/v1/appInfos/{ai['id']}/appInfoLocalizations")['data']:
    J('PATCH', f"/v1/appInfoLocalizations/{l['id']}", {'data': {'type': 'appInfoLocalizations', 'id': l['id'], 'attributes': {'subtitle': SUB, 'privacyPolicyUrl': SITE + '/privacy'}}}); print('info', l['attributes']['locale'])
J('PATCH', f"/v1/appInfos/{ai['id']}", {'data': {'type': 'appInfos', 'id': ai['id'], 'relationships': {'primaryCategory': {'data': {'type': 'appCategories', 'id': 'GAMES'}}, 'primarySubcategoryOne': {'data': {'type': 'appCategories', 'id': 'GAMES_BOARD'}}, 'primarySubcategoryTwo': {'data': {'type': 'appCategories', 'id': 'GAMES_STRATEGY'}}}}}); print('category ok')
c = J('GET', '/v1/apps/6782641107/betaAppReviewDetail')['data']['attributes']
rd = J('GET', f'/v1/appStoreVersions/{VID}/appStoreReviewDetail', ok=(200, 404)).get('data')
att = {'contactFirstName': c['contactFirstName'], 'contactLastName': c['contactLastName'], 'contactPhone': c['contactPhone'], 'contactEmail': c['contactEmail'], 'demoAccountRequired': False, 'notes': 'A single-player game against two computer players. No account or login is needed; Game Center sign-in is optional.'}
if rd: J('PATCH', f"/v1/appStoreReviewDetails/{rd['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': rd['id'], 'attributes': att}})
else: J('POST', '/v1/appStoreReviewDetails', {'data': {'type': 'appStoreReviewDetails', 'attributes': att, 'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': VID}}}}})
print('review details ok')
def upload(set_id, path):
    data = open(path, 'rb').read()
    r = J('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(path), 'fileSize': len(data)}, 'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': set_id}}}}})['data']
    for op in r['attributes']['uploadOperations']:
        q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
        for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
        urllib.request.urlopen(q).read()
    J('PATCH', f"/v1/appScreenshots/{r['id']}", {'data': {'type': 'appScreenshots', 'id': r['id'], 'attributes': {'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
sets = {s['attributes']['screenshotDisplayType']: s['id'] for s in J('GET', f'/v1/appStoreVersionLocalizations/{LID}/appScreenshotSets')['data']}
for kind, typ in (('iphone', 'APP_IPHONE_67'), ('ipad', 'APP_IPAD_PRO_3GEN_129')):
    if typ in sets: J('DELETE', f'/v1/appScreenshotSets/{sets[typ]}')
    sid = J('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': LID}}}}})['data']['id']
    n = 0
    while os.path.exists(os.path.join(SHOTS, f'{kind}_{n + 1}.png')): n += 1; upload(sid, os.path.join(SHOTS, f'{kind}_{n}.png'))
    print(typ, n, 'uploaded')
