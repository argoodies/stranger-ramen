#!/usr/bin/env python3
"""Upload assets/achievements/<id>.png (from tools/mkbadges.py) as the Game Center image of each Tiny Clocktower achievement, in every language.
Replaces an image already there. usage: pocket_gc_images.py"""
import sys, os, json, hashlib, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
GC = 'dac05b71-54d0-4da1-a3d9-03d18c09804f'; DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'achievements')
def J(m, p, b=None, ok=(200, 201, 204)):
    st, tx = req(m, p, b); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in ok: print('!!', m, p, st, tx[:400].replace('\n', ' '))
    return st, d
st, d = J('GET', f'/v1/gameCenterDetails/{GC}/gameCenterAchievements?limit=100&include=localizations')
locs = {x['id']: x for x in d.get('included', [])}
for a in d['data']:
    vid = a['attributes']['vendorIdentifier']; f = os.path.join(DIR, vid.split('.', 1)[1] + '.png')
    if not os.path.exists(f): print('no image for', vid); continue
    data = open(f, 'rb').read()
    for l in a['relationships']['localizations']['data']:
        L = l['id']; st, old = J('GET', f'/v1/gameCenterAchievementLocalizations/{L}/gameCenterAchievementImage')
        if old.get('data'): J('DELETE', f"/v1/gameCenterAchievementImages/{old['data']['id']}")
        st, r = J('POST', '/v1/gameCenterAchievementImages', {'data': {'type': 'gameCenterAchievementImages', 'attributes': {'fileName': os.path.basename(f), 'fileSize': len(data)}, 'relationships': {'gameCenterAchievementLocalization': {'data': {'type': 'gameCenterAchievementLocalizations', 'id': L}}}}})
        if st >= 300: continue
        r = r['data']
        for op in r['attributes']['uploadOperations']:
            q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
            for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
            urllib.request.urlopen(q).read()
        st, _ = J('PATCH', f"/v1/gameCenterAchievementImages/{r['id']}", {'data': {'type': 'gameCenterAchievementImages', 'id': r['id'], 'attributes': {'uploaded': True}}})
        print(vid, locs.get(L, {}).get('attributes', {}).get('locale'), st, flush=True)
