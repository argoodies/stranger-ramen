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
 ('pc.win_sailor', 10, True, ('Sailor Wins', '水手获胜', '水手獲勝'), ('Win as the Sailor.', '以水手身份获胜。', '以水手身份獲勝。')),
 ('pc.win_heretic', 10, True, ('Heretic Wins', '异端获胜', '異端獲勝'), ('Win as the Heretic.', '以异端分子身份获胜。', '以異端分子身份獲勝。')),
 ('pc.win_pukka', 10, True, ('Pukka Wins', '普卡获胜', '普卡獲勝'), ('Win as the Pukka.', '以普卡身份获胜。', '以普卡身份獲勝。')),
 ('pc.trick_sailor', 20, False, ('Hard to Kill', '死不了', '死不了'), ('As the sober Sailor, survive your own execution vote.', '作为清醒的水手，被处决投票通过却活下来。', '作為清醒的水手，被處決投票通過卻活下來。')),
 ('pc.trick_pukka', 20, False, ('Two Marks', '双重标记', '雙重標記'), ('Win as the Pukka with your mark on two different players.', '以普卡身份获胜，且场上有两名玩家各带一个普卡标记。', '以普卡身份獲勝，且場上有兩名玩家各帶一個普卡標記。')),
 ('pc.trick_heretic', 20, False, ('Martyr', '殉道者', '殉道者'), ('As the Heretic, be executed and still win.', '作为异端分子被处决，却赢了。', '作為異端分子被處決，卻贏了。')),
 ('pc.streak_3', 20, True, ('Three in a Row', '三连胜', '三連勝'), ('Win three games in a row.', '连续赢下三局。', '連續贏下三局。')),
 ('pc.streak_5', 40, True, ('Five in a Row', '五连胜', '五連勝'), ('Win five games in a row.', '连续赢下五局。', '連續贏下五局。')),
 ('pc.wins_10', 20, True, ('Ten Wins', '十胜', '十勝'), ('Win ten games.', '累计赢下十局。', '累計贏下十局。')),
 ('pc.wins_50', 50, True, ('Fifty Wins', '五十胜', '五十勝'), ('Win fifty games.', '累计赢下五十局。', '累計贏下五十局。')),
 ('pc.day_3', 10, True, ('Third Day', '第三个白天', '第三個白天'), ('Reach the third day of a game.', '一局游戏进行到第三个白天。', '一局遊戲進行到第三個白天。')),
 ('pc.day_4', 20, True, ('Fourth Day', '第四个白天', '第四個白天'), ('Reach the fourth day of a game.', '一局游戏进行到第四个白天。', '一局遊戲進行到第四個白天。')),
 ('pc.day_5', 30, True, ('Fifth Day', '第五个白天', '第五個白天'), ('Reach the fifth day of a game.', '一局游戏进行到第五个白天。', '一局遊戲進行到第五個白天。')),
 ('pc.day_7', 50, True, ('A Long Week', '漫长的一周', '漫長的一週'), ('Play a game to the seventh day and win the forced settlement on the good side.', '一局进行到第七天，触发强制结算，以好人身份获胜。', '一局進行到第七天，觸發強制結算，以好人身份獲勝。')),
 ('pc.streak_7', 50, True, ('Seven in a Row', '七连胜', '七連勝'), ('Win seven games in a row.', '连续赢下七局。', '連續贏下七局。')),
 ('pc.streak_10', 70, True, ('Ten in a Row', '十连胜', '十連勝'), ('Win ten games in a row.', '连续赢下十局。', '連續贏下十局。')),
 ('pc.streak_15', 100, True, ('Fifteen in a Row', '十五连胜', '十五連勝'), ('Win fifteen games in a row.', '连续赢下十五局。', '連續贏下十五局。')),
 ('pc.wins_5', 10, True, ('Five Wins', '五胜', '五勝'), ('Win five games.', '累计赢下五局。', '累計贏下五局。')),
 ('pc.wins_25', 30, True, ('Twenty-Five Wins', '二十五胜', '二十五勝'), ('Win twenty-five games.', '累计赢下二十五局。', '累計贏下二十五局。')),
 ('pc.wins_100', 70, True, ('One Hundred Wins', '一百胜', '一百勝'), ('Win one hundred games.', '累计赢下一百局。', '累計贏下一百局。')),
 ('pc.wins_200', 100, True, ('Two Hundred Wins', '两百胜', '兩百勝'), ('Win two hundred games.', '累计赢下两百局。', '累計贏下兩百局。')),
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
if 'pc.best_streak' not in lb:
    st, d = J('POST', '/v1/gameCenterLeaderboards', {'data': {'type': 'gameCenterLeaderboards', 'attributes': {'referenceName': 'Best win streak', 'vendorIdentifier': 'pc.best_streak', 'defaultFormatter': 'INTEGER', 'submissionType': 'BEST_SCORE', 'scoreSortType': 'DESC', 'scoreRangeStart': '0', 'scoreRangeEnd': '10000'}, 'relationships': {'gameCenterDetail': {'data': {'type': 'gameCenterDetails', 'id': GC}}}}})
    if st < 300:
        lid = d['data']['id']; lb['pc.best_streak'] = lid
        for loc, n in zip(L, ('Best Win Streak', '最长连胜', '最長連勝')):
            J('POST', '/v1/gameCenterLeaderboardLocalizations', {'data': {'type': 'gameCenterLeaderboardLocalizations', 'attributes': {'locale': loc, 'name': n}, 'relationships': {'gameCenterLeaderboard': {'data': {'type': 'gameCenterLeaderboards', 'id': lid}}}}})
print('leaderboard', lb)
