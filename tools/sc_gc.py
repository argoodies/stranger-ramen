#!/usr/bin/env python3
"""Game Center achievements for 星穹十字小镇 (app 6782641107), in three languages, with their images from assets/sc_achievements/<name>.png
(rendered by the game's own drawing code). Safe to run again: existing achievements are kept, images are replaced.
usage: tools/sc_gc.py"""
import sys, os, json, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sc_achievements')
L = ['zh-Hant', 'zh-Hans', 'en-US']
# vendor id 'sc.<name>' (the game reports it with scAch('<name>') in index.html), points, names (hant, hans, en), how (hant, hans, en)
A = [('own_ramen', 20, ('給自己做拉麵', '给自己做拉面', 'A Bowl for Me'), ('第一次給自己做一碗拉麵。', '第一次给自己做一碗拉面。', 'Make yourself a bowl of ramen for the first time.')),
     ('iced_coffee', 20, ('自取咖啡', '自取咖啡', 'Coffee to Go'), ('在酒館拿走桌上的冰咖啡。', '在酒馆拿走桌上的冰咖啡。', 'Take the iced coffee from the table in the bar.')),
     ('prophecy_speed', 20, ('速度預言', '速度预言', 'Prophecy of Speed'), ('得到速度預言。', '得到速度预言。', 'Receive the Prophecy of Speed.')),
     ('prophecy_freeze', 20, ('冰凍預言', '冰冻预言', 'Prophecy of Frost'), ('得到冰凍預言。', '得到冰冻预言。', 'Receive the Prophecy of Frost.')),
     ('whirlwind_story', 20, ('迷亂的漩渦一周目', '迷乱的漩涡一周目', 'The Whirlwind, First Run'), ('第一次看完「迷亂的漩渦」。', '第一次看完「迷乱的漩涡」。', 'Watch "The Whirlwind" story to the end for the first time.'))]
def J(m, p, b=None, ok=(200, 201, 204)):
    st, tx = req(m, p, b); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in ok: print('!!', m, p, st, tx[:400].replace('\n', ' '))
    return st, d
st, d = J('GET', f'/v1/apps/{APP}/gameCenterDetail', ok=(200, 404))
GC = (d.get('data') or {}).get('id')
if not GC:
    st, d = J('POST', '/v1/gameCenterDetails', {'data': {'type': 'gameCenterDetails', 'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}}); GC = d['data']['id']
print('detail', GC)
st, d = J('GET', f'/v1/gameCenterDetails/{GC}/gameCenterAchievements?limit=100')
have = {a['attributes']['vendorIdentifier']: a['id'] for a in d.get('data', [])}
for name, pts, names, how in A:
    vid = 'sc.' + name
    if vid not in have:
        st, d = J('POST', '/v1/gameCenterAchievements', {'data': {'type': 'gameCenterAchievements', 'attributes': {'referenceName': vid, 'vendorIdentifier': vid, 'points': pts, 'showBeforeEarned': True, 'repeatable': False}, 'relationships': {'gameCenterDetail': {'data': {'type': 'gameCenterDetails', 'id': GC}}}}})
        if st >= 300: continue
        have[vid] = d['data']['id']
    aid = have[vid]
    st, d = J('GET', f'/v1/gameCenterAchievements/{aid}/localizations?limit=10')
    locs = {x['attributes']['locale']: x['id'] for x in d.get('data', [])}
    for i, loc in enumerate(L):
        if loc not in locs:
            st, r = J('POST', '/v1/gameCenterAchievementLocalizations', {'data': {'type': 'gameCenterAchievementLocalizations', 'attributes': {'locale': loc, 'name': names[i], 'beforeEarnedDescription': how[i], 'afterEarnedDescription': how[i]}, 'relationships': {'gameCenterAchievement': {'data': {'type': 'gameCenterAchievements', 'id': aid}}}}})
            if st >= 300: continue
            locs[loc] = r['data']['id']
        # the badge, in every language
        f = os.path.join(DIR, name + '.png'); data = open(f, 'rb').read(); LID = locs[loc]
        st, old = J('GET', f'/v1/gameCenterAchievementLocalizations/{LID}/gameCenterAchievementImage')
        if old.get('data'): J('DELETE', f"/v1/gameCenterAchievementImages/{old['data']['id']}")
        st, r = J('POST', '/v1/gameCenterAchievementImages', {'data': {'type': 'gameCenterAchievementImages', 'attributes': {'fileName': name + '.png', 'fileSize': len(data)}, 'relationships': {'gameCenterAchievementLocalization': {'data': {'type': 'gameCenterAchievementLocalizations', 'id': LID}}}}})
        if st >= 300: continue
        r = r['data']
        for op in r['attributes']['uploadOperations']:
            q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
            for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
            urllib.request.urlopen(q).read()
        st, _ = J('PATCH', f"/v1/gameCenterAchievementImages/{r['id']}", {'data': {'type': 'gameCenterAchievementImages', 'id': r['id'], 'attributes': {'uploaded': True}}})
        print(vid, loc, 'image', st, flush=True)
print('achievements', sorted(have))
