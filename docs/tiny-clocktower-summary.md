# Tiny Clocktower 0.0.1 → 0.0.6 合并变更 · Combined changes

把六个版本放在一起比较，只保留到 0.0.6 为止仍然有效的变化；中途加了又删、改了又改回的都不算。
The six versions taken together: only what is still in effect at 0.0.6. Anything added and later removed, or changed and changed back, is left out.

## 中文

**名称与图标**
- App 名称：Tiny Clocktower。
- App 图标：打开的紫书向上发光，水手、异端、普卡三枚 token 在光里浮起。

**规则**
- 一局打到第七个白天就强制结算，好人获胜，异端的颠倒不生效；说书人会专门宣布。原来最多到第 12 天，然后判邪恶胜。

**Game Center**
- 启动时用系统提示登录，解锁成就时显示系统横幅，没有额外的界面。
- 21 个成就，共 830 点，每个都有白色线条的徽章：
  - 首胜；水手、异端、普卡各自获胜；
  - 死不了、双重标记（两名不同玩家各带普卡标记）、殉道者；
  - 三连胜、五连胜；
  - 总胜场 5、10、25、50、100、200、300、500、1000；
  - 第三个白天、第五个白天、漫长的一周（第七天强制结算时以好人身份获胜）。
- 排行榜：总胜场，分数上限 9999。

**画面与操作**
- 规则书在 App 里不论哪种语言都是一本等距画法的紫书，颜色和说书人长袍一致。
- 说书人身边不再有魔典；大厅里他脚下不再有提示光环。
- 白天天空是整片红霞，不再有底部的青色；启动时直接是这片天空，不再先黑屏。
- 夜晚的月亮是秋冬木色的圆月，和图标颜色一致。
- 昼夜切换更快。
- 提示用的小 token 线条随大小等比缩放。
- 语言菜单里，当前正在使用的语言排在最上面。
- 结局时说书人不再说“欢迎下次再玩”。

**其他**
- 隐私政策与支持页面：tiny-clocktower.fly.dev

**还没进 App 的部分**
- 排行榜改成总胜场、三百胜，以及去掉第四个白天和七、十、十五连胜：已在代码和 Game Center 里改好，但当前的 build 30 不含，要再出一个包。

## English

**Name and icon**
- App name: Tiny Clocktower.
- App icon: the open purple book casting light on three rising tokens — Sailor, Heretic and Pukka.

**Rules**
- A game that reaches the seventh day is settled there and then: good wins, and the Heretic's reversal does not apply. The Storyteller announces it. Previously a game could run to day 12 and then went to evil.

**Game Center**
- Sign-in through the system prompt at launch and the system banner when an achievement unlocks; no extra interface.
- 21 achievements worth 830 points, each with a white line-art badge:
  - First win; a win as the Sailor, as the Heretic and as the Pukka;
  - Hard to Kill, Two Marks (the Pukka's mark on two different players), Martyr;
  - 3 and 5 wins in a row;
  - 5, 10, 25, 50, 100, 200, 300, 500 and 1,000 total wins;
  - The third day, the fifth day, and A Long Week (winning the seventh-day settlement on the good side).
- Leaderboard: total wins, capped at 9999.

**Look and play**
- In the app the rule book is an isometric purple book in every language, in the colour of the Storyteller's robe.
- No grimoire beside the Storyteller, and no prompt ring under him in the lobby.
- The day sky is rosy all the way down, with no teal band, and the app starts on it instead of a dark screen.
- The night moon is round, in an autumn-wood colour that matches the icon.
- Day and night change faster.
- Reminder tokens draw their lines in proportion to their size.
- The language in use sits at the top of the language menu.
- The Storyteller no longer says goodbye at the end.

**Other**
- Privacy policy and support pages: tiny-clocktower.fly.dev

**Not in the app yet**
- The total-wins leaderboard, 300 wins, and dropping the fourth day and 7, 10 and 15 wins in a row are done in the code and in Game Center, but build 30 does not have them; they need one more build.
