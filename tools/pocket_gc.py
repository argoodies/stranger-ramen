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
A = [('pc.first_win', 10, True, ('First Win', '首胜', '首勝'), ('Win a game.', '赢下一局。', '贏下一局。')),
 ('pc.trick_pukka', 20, True, ('Double Dose', '双份毒药', '雙份毒藥'), ('Win as evil with two players poisoned by you.', '以邪恶阵营获胜，两名玩家都中了你的毒。', '以邪惡陣營獲勝，兩名玩家都中了你的毒。')),
 ('pc.exec_survive', 20, True, ('Undying', '不死之身', '不死之身'), ('Be executed, and do not die.', '被处决，却没有死。', '被處決，卻沒有死。')),
 ('pc.self_reverse', 20, True, ('Turn the Tables', '亲手逆转', '親手逆轉'), ('Be executed, and set off your own reversal of the result.', '被处决，并亲手触发胜负反转。', '被處決，並親手觸發勝負反轉。')),
 ('pc.streak_3', 20, True, ('Three in a Row', '三连胜', '三連勝'), ('Win three games in a row.', '连续赢下三局。', '連續贏下三局。')),
 ('pc.streak_5', 40, True, ('Five in a Row', '五连胜', '五連勝'), ('Win five games in a row.', '连续赢下五局。', '連續贏下五局。')),
 ('pc.wins_10', 20, True, ('Ten Wins', '十胜', '十勝'), ('Win ten games.', '累计赢下十局。', '累計贏下十局。')),
 ('pc.wins_50', 50, True, ('Fifty Wins', '五十胜', '五十勝'), ('Win fifty games.', '累计赢下五十局。', '累計贏下五十局。')),
 ('pc.day_3', 10, True, ('Third Day', '第三个白天', '第三個白天'), ('Reach the third day of a game.', '一局游戏进行到第三个白天。', '一局遊戲進行到第三個白天。')),
 ('pc.day_5', 30, True, ('Fifth Day', '第五个白天', '第五個白天'), ('Reach the fifth day of a game.', '一局游戏进行到第五个白天。', '一局遊戲進行到第五個白天。')),
 ('pc.day_7', 50, True, ('A Long Week', '漫长的一周', '漫長的一週'), ('Play a game to the seventh day and win the forced settlement on the good side.', '一局进行到第七天，触发强制结算，以好人身份获胜。', '一局進行到第七天，觸發強制結算，以好人身份獲勝。')),
 ('pc.wins_5', 10, True, ('Five Wins', '五胜', '五勝'), ('Win five games.', '累计赢下五局。', '累計贏下五局。')),
 ('pc.wins_25', 30, True, ('Twenty-Five Wins', '二十五胜', '二十五勝'), ('Win twenty-five games.', '累计赢下二十五局。', '累計贏下二十五局。')),
 ('pc.wins_100', 70, True, ('One Hundred Wins', '一百胜', '一百勝'), ('Win one hundred games.', '累计赢下一百局。', '累計贏下一百局。')),
 ('pc.wins_200', 100, True, ('Two Hundred Wins', '两百胜', '兩百勝'), ('Win two hundred games.', '累计赢下两百局。', '累計贏下兩百局。')),
 ('pc.wins_300', 100, True, ('Three Hundred Wins', '三百胜', '三百勝'), ('Win three hundred games.', '累计赢下三百局。', '累計贏下三百局。')),
 ('pc.wins_500', 100, True, ('Five Hundred Wins', '五百胜', '五百勝'), ('Win five hundred games.', '累计赢下五百局。', '累計贏下五百局。')),
 ('pc.wins_1000', 100, True, ('A Thousand Wins', '一千胜', '一千勝'), ('Win a thousand games.', '累计赢下一千局。', '累計贏下一千局。'))]
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
