# 三人染 /3b 网页开发日志 · Web development log

2026-11-01 至 2026-11-02 的合并结果：只保留到现在仍然有效的变化；中途试过又改回的（主角造型、对手帽子、书的样式、月亮形状等）都不算。
Combined result for 1–2 November 2026: only what is still in effect now. Anything tried and later reverted (the player's look, the opponents' hats, the book's style, the moon's shape and so on) is left out.

## 中文

**规则**
- 一局打到第七个白天就强制结算，好人获胜，异端的颠倒不生效；说书人会宣布“第七个白天到了，强制结算：善良阵营获胜”。原来最多到第 12 天，然后判邪恶胜。
- 结局时说书人不再说“欢迎下次再玩”。

**画面**
- 白天天空去掉底部的青色，改为整片红霞；页面加载时的背景也随之改成红霞，不再露出青色。
- 夜晚的月亮是秋冬木色的圆月，只带一点点泛光；月亮圆盘里不再透出星星。
- 昼夜切换更快，约 0.5 秒完成。
- 说书人身边不再有魔典；大厅里他脚下不再有闪烁的提示光环。
- 提示用的小 token 线条随大小等比缩放，小尺寸下不再显得粗。

**界面**
- 语言菜单里，当前正在使用的语言排在最上面，其余依次是简体中文、繁體中文、English，最后是跟随系统。
- 页面标题改为“三人染”。

**开发与发布**
- 页面不再被搜索引擎收录（返回 noindex），也不在任何公开页面上出现链接，只作调试用。
- 新增小红书小工具打包：`tools/mkxhs.py` 把页面改写成小工具规范（脚本外置并降到 ES2017、存储走小工具 Storage API、补齐 Chrome 61 的 CSS 基线），GitHub Action `xhs-zip.yml` 按需打出 zip，并用 minitool-zip-builder skill 的审计脚本把关。

## English

**Rules**
- A game that reaches the seventh day is settled there and then: good wins, and the Heretic's reversal does not apply. The Storyteller announces "The seventh day has come. The game is settled: good wins." Previously a game could run to day 12 and then went to evil.
- The Storyteller no longer says goodbye at the end.

**Look**
- The day sky loses its teal lower band and is rosy all the way down; the page's loading background matches, so no teal shows while it loads.
- The night moon is round, in an autumn-wood colour with only a faint glow, and no stars show through its disc.
- Day and night change faster, in about half a second.
- No grimoire beside the Storyteller, and no blinking prompt ring under him in the lobby.
- Reminder tokens draw their lines in proportion to their size, so they no longer look heavy when small.

**Interface**
- In the language menu the language in use sits at the top, followed by 简体中文, 繁體中文 and English, with "follow the system" last.
- The page title is now 三人染.

**Development and release**
- The page is kept out of search engines (noindex) and linked from no public page; it is for debugging only.
- New Xiaohongshu mini-tool packaging: `tools/mkxhs.py` rewrites the page to the mini-tool rules (scripts moved out and lowered to ES2017, storage through the mini-tool Storage API, a Chrome 61 CSS baseline), and the GitHub Action `xhs-zip.yml` builds the zip on demand, gated by the minitool-zip-builder skill's audit script.
