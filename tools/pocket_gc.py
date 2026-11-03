"""Game Center setup for Pocket Clocktower: detail, leaderboard, achievements, in three languages. Safe to run again.
usage: pocket_gc.py"""
import sys, json
sys.path.insert(0, '/root'); from asc_api import req
APP = '6829382085'
def J(m, p, b=None, ok=(200, 201, 204)):
    st, tx = req(m, p, b); d = json.loads(tx) if tx.strip().startswith('{') else {}
    if st not in ok: print('!!', m, p, st, tx[:420].replace('\n', ' '))
    return st, d
st, d = J('GET', f'/v1/apps/{APP}/gameCenterDetail', ok=(200, 404))
GC = (d.get('data') or {}).get('id')
if not GC:
    st, d = J('POST', '/v1/gameCenterDetails', {'data': {'type': 'gameCenterDetails', 'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}}); GC = d['data']['id']
print('detail', GC)
L = ['en-US', 'zh-Hans', 'zh-Hant']
# id, points, shown before earned, names (en, hans, hant), how (en, hans, hant)
A = [('pc.first_win', 50, True, ('First Win', '首胜', '首勝'), ('Win a game.', '赢下一局。', '贏下一局。')),
 ('pc.wins_100', 50, True, ('One Hundred Wins', '一百胜', '一百勝'), ('Win one hundred games.', '累计赢下一百局。', '累計贏下一百局。')),
 ('pc.wins_300', 50, True, ('Three Hundred Wins', '三百胜', '三百勝'), ('Win three hundred games.', '累计赢下三百局。', '累計贏下三百局。')),
 ('pc.wins_1000', 50, True, ('A Thousand Wins', '一千胜', '一千勝'), ('Win a thousand games.', '累计赢下一千局。', '累計贏下一千局。')),
 ('pc.day_7', 50, True, ('A Long Week', '漫长的一周', '漫長的一週'), ('Last to day seven and win as good.', '撑到第七天，以好人身份获胜。', '撐到第七天，以好人身份獲勝。')),
 ('pc.exec_survive', 50, True, ('Undying', '不死之身', '不死之身'), ('Be executed, and do not die.', '被处决，却没有死。', '被處決，卻沒有死。')),
 ('pc.drink_alone', 50, True, ('Drinking Alone', '一人饮酒', '一人飲酒'), ('Choose to get yourself drunk.', '夜里选择让自己醉酒。', '夜裡選擇讓自己醉酒。')),
 ('pc.self_reverse', 50, True, ('Turn the Tables', '亲手逆转', '親手逆轉'), ('Be executed, and set off your own reversal of the result.', '被处决，并亲手触发胜负反转。', '被處決，並親手觸發勝負反轉。')),
 ('pc.all_tokens', 50, True, ('Irresistible', '魅魔体质', '魅魔體質'), ("Be executed carrying both other players' tokens.", '被处决时，身上带着另外两人的标记。', '被處決時，身上帶著另外兩人的標記。')),
 ('pc.trick_pukka', 50, True, ('Double Dose', '双份毒药', '雙份毒藥'), ('Have two players poisoned by you.', '两名玩家都中了你的毒。', '兩名玩家都中了你的毒。')),
 ('pc.self_poison', 50, True, ('Self-Poisoned', '自毒', '自毒'), ('Poison yourself at night.', '夜里给自己下毒。', '夜裡給自己下毒。'))]
st, d = J('GET', f'/v1/gameCenterDetails/{GC}/gameCenterAchievements?limit=100')
have = {a['attributes']['vendorIdentifier']: a['id'] for a in d.get('data', [])}
for vid, pts, show, names, how in A:
    if vid in have: continue
    st, d = J('POST', '/v1/gameCenterAchievements', {'data': {'type': 'gameCenterAchievements', 'attributes': {'referenceName': vid, 'vendorIdentifier': vid, 'points': pts, 'showBeforeEarned': show, 'repeatable': False}, 'relationships': {'gameCenterDetail': {'data': {'type': 'gameCenterDetails', 'id': GC}}}}})
    if st >= 300: continue
    aid = d['data']['id']; have[vid] = aid
    for i, loc in enumerate(L):
        J('POST', '/v1/gameCenterAchievementLocalizations', {'data': {'type': 'gameCenterAchievementLocalizations', 'attributes': {'locale': loc, 'name': names[i], 'beforeEarnedDescription': how[i], 'afterEarnedDescription': how[i]}, 'relationships': {'gameCenterAchievement': {'data': {'type': 'gameCenterAchievements', 'id': aid}}}}})
print('achievements', len(have))
st, d = J('GET', f'/v1/gameCenterDetails/{GC}/gameCenterLeaderboards?limit=20')
lb = {a['attributes']['vendorIdentifier']: a['id'] for a in d.get('data', [])}
if 'pc.total_wins' not in lb:
    st, d = J('POST', '/v1/gameCenterLeaderboards', {'data': {'type': 'gameCenterLeaderboards', 'attributes': {'referenceName': 'Total wins', 'vendorIdentifier': 'pc.total_wins', 'defaultFormatter': 'INTEGER', 'submissionType': 'BEST_SCORE', 'scoreSortType': 'DESC', 'scoreRangeStart': '0', 'scoreRangeEnd': '9999'}, 'relationships': {'gameCenterDetail': {'data': {'type': 'gameCenterDetails', 'id': GC}}}}})
    if st < 300:
        lid = d['data']['id']; lb['pc.total_wins'] = lid
        for loc, n in zip(L, ('Most Wins', '总胜场', '總勝場')):
            J('POST', '/v1/gameCenterLeaderboardLocalizations', {'data': {'type': 'gameCenterLeaderboardLocalizations', 'attributes': {'locale': loc, 'name': n}, 'relationships': {'gameCenterLeaderboard': {'data': {'type': 'gameCenterLeaderboards', 'id': lid}}}}})
print('leaderboard', lb)
