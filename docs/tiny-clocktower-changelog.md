# Tiny Clocktower（三人染）更新日志 · Changelog

只列出每个版本最终留下来的变化，中途试过又撤回的改动不写。
Only what each version finally shipped with; changes that were tried and rolled back are left out.

---

## 0.0.6 — 上架候选 · Release candidate（2026-11-02）

> 当前绑定 build 38（已含下面全部改动；★ 为 build 31–38 才进 App 的条目）。
> Bound to build 38, which has everything below; ★ marks what first reached the app in builds 31–38.

**规则 · Rules**
- 一局打到第七个白天，游戏强制结算，好人获胜，异端的颠倒不生效；说书人会宣布“第七个白天到了，强制结算：善良阵营获胜”。之前最多可到第 12 天，然后判邪恶胜。
  A game that reaches the seventh day is settled there and then: good wins, and the Heretic's reversal does not apply. The Storyteller announces it. Previously a game could run to day 12 and then went to evil.

**Game Center**
- 只使用系统自带的交互：登录提示和成就横幅；不再有游戏自己画的 Game Center 按钮。
  Only the system's own Game Center interactions remain: the sign-in prompt and achievement banners. The game's own Game Center button is gone.
- ★ 排行榜改为“总胜场”（原为最长连胜），分数上限 9999。
  ★ The leaderboard now ranks total wins instead of the best streak, capped at 9999.
- ★ 成就精简为 11 个，每个 50 分，共 550 分；文案里不出现角色名。
  ★ Eleven achievements, 50 points each (550 in all); no role names in their texts.
  - 胜场：首胜、一百胜、三百胜、一千胜。白天：只留“漫长的一周”（撑到第七天，以好人身份获胜）。
    Wins: first, 100, 300 and 1,000. Days: only A Long Week (last to day seven and win as good).
  - 角色成就：不死之身、一人饮酒（夜里选择让自己醉酒）、亲手逆转、魅魔体质（被处决时，身上带着另外两人的标记）、双份毒药（两名玩家都中了你的毒）、自毒（夜里给自己下毒）。
    Role achievements: Undying, Drinking Alone (get yourself drunk), Turn the Tables, Irresistible (executed carrying both other players' tokens), Double Dose (two players poisoned by you) and Self-Poisoned (poison yourself).
  - 去掉连胜、第三/第五个白天，以及五、十、二十五、五十、两百、五百胜。
    Removed: the streaks, the third and fifth days, and 5, 10, 25, 50, 200 and 500 wins.
  - 徽章都是 token 样式：角色成就用对应角色的 token；胜场是金色橄榄枝加手绘数字，第七天是明黄色太阳。
    Every badge is a token: the role achievements show their role's token; wins a gold laurel wreath with a hand-drawn number, the seventh day the bright yellow sun.

**Token**
- ★ 水手的线条变细，锚顶的圆环完整，锚杆像棒棒糖杆一样接上；普卡的箭头按视觉居中。App 图标、截图、支持页随之更新。
  ★ The Sailor's lines are finer, the anchor's ring is whole and its shank joins it like a lollipop stick; the Pukka's arrow is centred by eye. The app icon, screenshots and support page follow.

**画面 · Look**
- App 里不论哪种语言都显示紫书（网页版是红色小染书）；紫书改为等距画法，书页平直，没有透视。
  In the app the purple book shows in every language (the web version keeps the red label); the book is drawn isometric and flat, with no perspective.
- 小 token 恢复原来的大小；同一人有两枚时并排放在右下。
  Reminder tokens are back to their original size; two on one player sit side by side, lower right.
- 两名对手戴回尖帽子。
  The two opponents wear their pointed hats again.
- 说书人身边不再有魔典；大厅里说书人脚下的提示光环去掉。
  No grimoire beside the Storyteller; no prompt ring under him in the lobby.
- 月亮颜色和 App 图标统一。
  The moon matches the app icon's colour.
- 新 App 图标：打开的紫书向上发光，三枚角色 token 在光里浮起。
  New app icon: the open purple book casting light on three rising role tokens.

**其他 · Other**
- 新的隐私政策与支持页面：tiny-clocktower.fly.dev
  New privacy policy and support pages at tiny-clocktower.fly.dev

---

## 0.0.5（2026-11-01）

- 新 App 图标：主角站在绿色圆台上，身后是发光的月亮。
  New app icon: the hero on a green dais before a glowing moon.

---

## 0.0.4（2026-11-01）

- App 改名为 **Tiny Clocktower**。
  The app is renamed **Tiny Clocktower**.
- 紫书改成硬壳 3D 模型，正对镜头，V 形开口对准亮片。
  The purple book becomes a stiff 3D model, facing the camera, its V under the sparkle.
- 月亮改为圆月，秋冬木色，只有一点点泛光。
  The moon is round again, in an autumn-wood colour with only a faint glow.

---

## 0.0.3（2026-11-01）

- 新增 11 个成就：第三、第四、第五个白天和漫长的一周，更多连胜，更多总胜场。
  11 new achievements: the third, fourth and fifth days and A Long Week, longer streaks and more total wins.
- 紫书改成说书人长袍的紫色。
  The purple book takes the colour of the Storyteller's robe.
- 小 token 缩小，线条随之等比变细。
  Reminder tokens are smaller, with lines that scale with them.
- 白天天空去掉底部的青色，改为整片红霞；启动时也是红霞，不再先闪黑屏。
  The day sky loses its teal lower band and is rosy all the way down; the app starts on that sky instead of a dark screen.
- 昼夜切换更快。
  Day and night change faster.

---

## 0.0.2（2026-11-01）

- 接入 Game Center：启动时登录，11 个成就，排行榜。
  Game Center: sign-in at launch, 11 achievements and a leaderboard.
- App 里的规则书显示为紫书。
  In the app the rule book appears as the purple book.
- 结局时说书人不再说“欢迎下次再玩”。
  The Storyteller no longer says goodbye at the end.

---

## 0.0.1（2026-11-01）

- 首个 TestFlight 版本：三人染独立成 App。你和两名电脑玩家围坐在浮空的桌旁，说书人主持；水手、异端、普卡三种身份；夜晚行动，白天提名投票，结局亮出所有身份。
  First TestFlight build: the three-player game as its own app. You and two computer players sit at a floating table with a Storyteller; three roles (Sailor, Heretic, Pukka); night actions, daytime nominations and votes, and a reveal at the end.
