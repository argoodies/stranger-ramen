"""Rename the English listing to Ramen Puzzle and point every URL at ramen-puzzle.fly.dev on the editable version.
usage: asc_rename.py <versionId>   (the version must be editable: cancel the review submission first)"""
import sys, json
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = sys.argv[1]; BASE = 'https://ramen-puzzle.fly.dev'; OLD = 'https://clocktower-ramen.fly.dev'
def call(m, p, b=None):
    st, tx = req(m, p, b); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
st, locs = call('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')
for l in locs['data']:
    a = l['attributes']; new = {}
    for k in ('description', 'whatsNew', 'promotionalText', 'keywords'):
        v = a.get(k) or ''
        if 'Clocktower Ramen' in v: new[k] = v.replace('Clocktower Ramen', 'Ramen Puzzle')
    new['supportUrl'] = BASE + '/support'; new['marketingUrl'] = BASE + '/download'
    st, d = call('PATCH', f"/v1/appStoreVersionLocalizations/{l['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id'], 'attributes': new}})
    print('version loc', a['locale'], st, sorted(new), json.dumps(d.get('errors', ''), ensure_ascii=False)[:300])
st, infos = call('GET', f'/v1/apps/{APP}/appInfos?limit=10')
ed = next(i for i in infos['data'] if i['attributes'].get('state') != 'READY_FOR_DISTRIBUTION'); print('appInfo', ed['attributes'].get('state'))
st, il = call('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")
for l in il['data']:
    a = l['attributes']; new = {'privacyPolicyUrl': BASE + '/privacy'}
    if a['locale'] == 'en-US': new['name'] = 'Ramen Puzzle'
    st, d = call('PATCH', f"/v1/appInfoLocalizations/{l['id']}", {'data': {'type': 'appInfoLocalizations', 'id': l['id'], 'attributes': new}})
    print('info loc', a['locale'], st, new, json.dumps(d.get('errors', ''), ensure_ascii=False)[:400])
st, il = call('GET', f"/v1/appInfos/{ed['id']}/appInfoLocalizations")
print('names now', [(l['attributes']['locale'], l['attributes']['name'], l['attributes']['subtitle'], l['attributes']['privacyPolicyUrl']) for l in il['data']])
