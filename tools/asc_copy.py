"""Store text for 星穹十字物语 / Starcross Tales: name, subtitle, description and keywords. usage: asc_copy.py <versionId>"""
import sys, json
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; V = sys.argv[1]
HANS = """《星穹十字物语》：星空下，一座悬浮的小岛，一座钟楼，和一间小小的拉面店。

散步：想走就走，到悬浮的小岛上逛逛。和岛上的人打声招呼，看白天变成黑夜，到图书馆里瞧一瞧。

煮面：站到料理台后，亲手做好每一碗。点面锅下面、捞起、放进碗里、加汤，再照客人说的放辣、放香菜、加牛肉，端到客人面前。招呼完几位客人，也给自己做一碗，放到吧台上慢慢吃。

酒馆：白天来杯咖啡，晚上来杯麦酒。店里有只猫，摸摸它会喵一声。

登塔：走进钟楼，守塔人会带你登上塔顶看风景。脚下的小岛照常热闹；要是赶上夜里，还能看见一颗流星划过天空。钟声敲过两下，再慢慢走下来。

教堂：过桥到小岛上的教堂，点燃火把，和恶魔打一场。点敌人出手，还能弹刀反击；一路得到的道具和预言放进背包，比如能挡下致命一击的守护十字。打赢后打开宝箱，会有人来找你。第一章共七场战斗。

手绘等距视角场景，柔和的生成式音乐。"""
HANT = """《星穹十字物語》：星空下，一座懸浮的小島，一座鐘樓，和一間小小的拉麵店。

散步：想走就走，到懸浮的小島上逛逛。和島上的人打聲招呼，看白天變成黑夜，到圖書館裡瞧一瞧。

煮麵：站到料理台後，親手做好每一碗。點麵鍋下麵、撈起、放進碗裡、加湯，再照客人說的放辣、放香菜、加牛肉，端到客人面前。招呼完幾位客人，也給自己做一碗，放到吧台上慢慢吃。

酒館：白天來杯咖啡，晚上來杯麥酒。店裡有隻貓，摸摸牠會喵一聲。

登塔：走進鐘樓，守塔人會帶你登上塔頂看風景。腳下的小島照常熱鬧；要是趕上夜裡，還能看見一顆流星劃過天空。鐘聲敲過兩下，再慢慢走下來。

教堂：過橋到小島上的教堂，點燃火把，和惡魔打一場。點敵人出手，還能彈刀反擊；一路得到的道具和預言放進背包，比如能擋下致命一擊的守護十字。打贏後打開寶箱，會有人來找你。第一章共七場戰鬥。

手繪等距視角場景，柔和的生成式音樂。"""
EN = """Starcross Tales: under the stars, a little floating island, a clock tower and a tiny ramen shop.

Wander: leave whenever you like and stroll around the island. Say hello to the islanders, watch day turn to night, peek into the library.

Cook: step behind the counter and make each bowl by hand. Tap the pot to boil the noodles, lift them into the bowl, add the broth, then the chili, cilantro or beef each customer asks for, and set it down in front of them. After a few bowls, make one for yourself and eat it at the counter.

Tavern: coffee by day, ale by night. There is a cat; stroke it and it meows.

Climb: step into the clock tower and its keeper will take you up to the top. Look out over the island while life goes on below, and if it is night, watch a shooting star cross the sky. Two strokes of the bell, then wander back down.

Church: cross the bridge to the church on its little island, light the torch and fight the demons. Tap a foe to strike, and parry to hit back harder. Items and prophecies you find go into your backpack, like the Guardian Cross that can turn aside a deadly blow. Win, open the chest, and someone comes to find you. Chapter One has seven fights.

Hand-drawn isometric scenes and soft generative music."""
T = {'zh-Hans': ('星穹十字物语', '星空下的悬浮小镇', HANS, '休闲,放松,散步,等距,星空,钟楼,十字,风景,拉面,料理,酒馆,教堂'),
     'zh-Hant': ('星穹十字物語', '星空下的懸浮小鎮', HANT, '休閒,放鬆,散步,等距,星空,鐘樓,十字,風景,拉麵,料理,酒館,教堂'),
     'en-US': ('Starcross Tales', 'A floating town under the stars', EN, 'cozy,relax,wander,isometric,stars,clock tower,cross,scenery,ramen,cooking,tavern,church')}
def J(m, p, b=None):
    st, tx = req(m, p, b)
    if st >= 300: print('!!', m, p, st, tx[:400].replace('\n', ' '))
    return st, (json.loads(tx) if tx.strip().startswith('{') else {})
_, d = J('GET', f'/v1/appStoreVersions/{V}/appStoreVersionLocalizations')
for l in d['data']:
    loc = l['attributes']['locale']; n, sub, desc, kw = T[loc]; st, _ = J('PATCH', f"/v1/appStoreVersionLocalizations/{l['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id'], 'attributes': {'description': desc, 'keywords': kw}}}); print(loc, 'description', st)
_, d = J('GET', f'/v1/apps/{APP}/appInfos')
ai = next(a for a in d['data'] if a['attributes'].get('state') not in ('READY_FOR_DISTRIBUTION',))
_, d = J('GET', f"/v1/appInfos/{ai['id']}/appInfoLocalizations")
for l in d['data']:
    loc = l['attributes']['locale']; n, sub, _1, _2 = T[loc]; st, _ = J('PATCH', f"/v1/appInfoLocalizations/{l['id']}", {'data': {'type': 'appInfoLocalizations', 'id': l['id'], 'attributes': {'name': n, 'subtitle': sub}}}); print(loc, 'name', st)
st, _ = J('PATCH', f"/v1/ageRatingDeclarations/{ai['id']}", {'data': {'type': 'ageRatingDeclarations', 'id': ai['id'], 'attributes': {'socialMedia': False}}}); print('age', st)
print('appInfo', ai['id'])
