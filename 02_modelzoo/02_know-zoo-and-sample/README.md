# Meet RDK Model Zoo Sources

This directory stores the Chinese HTML page and slide spec for the Meet RDK Model Zoo tutorial (RDK Classroom, Chapter 2 Model Zoo, Lesson 2). An English handbook is not included yet.

本目录存放「认识 RDK Model Zoo」的中文 HTML 课件和幻灯片规格（RDK 小课堂 · 第 2 章 Model Zoo · 第 2 课）。英文讲义尚未收录。

- Chinese handbook / 中文讲义: [`docs/modelzoo/know-zoo-and-sample.zh.md`](../../docs/modelzoo/know-zoo-and-sample.zh.md)
- English nav placeholder / 英文导航占位: [`docs/modelzoo/know-zoo-and-sample.md`](../../docs/modelzoo/know-zoo-and-sample.md) (points at the Chinese handbook; not a translation)
- Chinese slide source / 中文课件: `lesson-2-02.zh.html`
- Chinese slide spec / 中文幻灯片规格: `blueprint.zh.json`

The HTML slides are self-contained; open them directly in a browser. Use ←/→ to change slides, N for speaker notes, F for full screen, and S for the scroll view.

HTML 课件可单独在浏览器中打开。←/→ 翻页，N 打开讲稿，F 全屏，S 进入滚动视图。

The slide spec uses the deck schema (`mode: deck`, layout-based slides with speaker notes), not the pattern-based blueprint schema used by earlier lessons.

幻灯片规格使用 deck schema（`mode: deck`，按版式组织并带讲稿），不是早期课程使用的 pattern blueprint。

The lesson covers RDK X5, RDK S100, RDK S100P, and RDK S600 on the RDK Model Zoo `main` branch. Toolchain versions are not fixed here; follow the sample READMEs and the toolchain documentation.

本课覆盖 RDK X5、RDK S100、RDK S100P 和 RDK S600，仓库使用 RDK Model Zoo 的 `main` 分支。工具链版本不在此处固定，以 Sample README 和工具链文档为准。
