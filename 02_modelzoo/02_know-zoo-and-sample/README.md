# Meet RDK Model Zoo Sources

This directory stores the HTML pages and slide specs for the Meet RDK Model Zoo tutorial (RDK Classroom, Chapter 2 Model Zoo, Lesson 2), in Chinese and English.

本目录存放「认识 RDK Model Zoo」的中英文 HTML 课件和幻灯片规格（RDK 小课堂 · 第 2 章 Model Zoo · 第 2 课）。

- Chinese handbook / 中文讲义: [`docs/modelzoo/know-zoo-and-sample.zh.md`](../../docs/modelzoo/know-zoo-and-sample.zh.md)
- English handbook / 英文讲义: [`docs/modelzoo/know-zoo-and-sample.md`](../../docs/modelzoo/know-zoo-and-sample.md)
- Chinese slide source / 中文课件: `lesson-2-02.zh.html`
- English slide source / 英文课件: `lesson-2-02.html`
- Chinese slide spec / 中文幻灯片规格: `blueprint.zh.json`
- English slide spec / 英文幻灯片规格: `blueprint.json`

The HTML slides are self-contained; open them directly in a browser. Use ←/→ to change slides, N for speaker notes, F for full screen, and S for the scroll view.

HTML 课件可单独在浏览器中打开。←/→ 翻页，N 打开讲稿，F 全屏，S 进入滚动视图。

The slide spec uses the deck schema (`mode: deck`, layout-based slides with speaker notes). English `blueprint.json` mirrors the Chinese structure (same slide count, layouts, and diagram element ids); only user-visible prose differs, with `meta.lang=en`. The checked-in `lesson-2-02.html` was produced by aligning the Chinese HTML with that English blueprint (structure/ids preserved), not by re-running dg-deck `build.py` in this drop.

幻灯片规格使用 deck schema（`mode: deck`，按版式组织并带讲稿）。英文 `blueprint.json` 与中文结构一一对应（页数、版式、diagram 元素 id 相同），仅替换可见文案，`meta.lang=en`。本批入库的 `lesson-2-02.html` 由中文 HTML 按英文 blueprint 做结构对齐生成（保留版式与元素 id），不是本机用 dg-deck `build.py` 重编。

The lesson covers RDK X5, RDK S100, RDK S100P, and RDK S600 on the RDK Model Zoo `main` branch. Toolchain versions are not fixed here; follow the sample READMEs and the toolchain documentation.

本课覆盖 RDK X5、RDK S100、RDK S100P 和 RDK S600，仓库使用 RDK Model Zoo 的 `main` 分支。工具链版本不在此处固定，以 Sample README 和工具链文档为准。
