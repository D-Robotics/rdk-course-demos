# YOLO Quantization by Example Sources

This directory stores the standalone bilingual HTML pages and slide specs for the YOLO Quantization by Example tutorial (RDK Classroom, Chapter 2 Model Zoo, Lesson 4).

- English handbook: [`docs/modelzoo/quantize-yolo.md`](../../docs/modelzoo/quantize-yolo.md)
- Chinese handbook: [`docs/modelzoo/quantize-yolo.zh.md`](../../docs/modelzoo/quantize-yolo.zh.md)
- English slide source: `lesson-2-04.html`
- Chinese slide source: `lesson-2-04.zh.html`
- English slide spec: `blueprint.json`
- Chinese slide spec: `blueprint.zh.json`

The HTML slides are self-contained; open them directly in a browser. Use ←/→ to change slides, N for speaker notes, F for full screen, and S for the scroll view.

The slide specs use the deck schema (`mode: deck`, layout-based slides with speaker notes).

The lesson uses YOLO detect on the RDK Model Zoo `main` branch to show YOLO-specific toolchain options: cut post-processing, board-side `decode_dfl`, and sensitive layers. One `mapper.py` feeds the X5 toolchain (`hb_mapper makertbin`, `.bin`) and the S-series toolchain (`hb_compile`, `.hbm`). Board measurements in this lesson are on RDK S600 and RDK X5; RDK S100 and RDK S100P are covered in the text. Opening the OE toolchain points back to lesson 2-03; this lesson goes straight to the mapper. Toolchain versions are not fixed here; follow the sample READMEs and the toolchain documentation.

---

# 以 YOLO 为例讲量化 资料

本目录存放 RDK 小课堂第 2 章 Model Zoo 第 4 课「以 YOLO 为例讲量化」的中英文独立 HTML 课件与课件规格文件。

- 中文讲义：[`docs/modelzoo/quantize-yolo.zh.md`](../../docs/modelzoo/quantize-yolo.zh.md)
- 英文讲义：[`docs/modelzoo/quantize-yolo.md`](../../docs/modelzoo/quantize-yolo.md)
- 中文课件源码：`lesson-2-04.zh.html`
- 英文课件源码：`lesson-2-04.html`
- 中文课件规格：`blueprint.zh.json`
- 英文课件规格：`blueprint.json`

HTML 课件为单文件，直接用浏览器打开即可。←/→ 翻页，N 显示讲稿，F 全屏，S 切换滚动视图。

本课在 RDK Model Zoo `main` 分支上，以 YOLO 检测讲清工具链针对 YOLO 的特定优化：切后处理、板端 `decode_dfl`、敏感层。一条 `mapper.py` 分别进入 X5 工具链（`hb_mapper makertbin`，产物 `.bin`）与 S 系列工具链（`hb_compile`，产物 `.hbm`）。本课板上实测为 RDK S600 与 RDK X5；RDK S100、RDK S100P 只在文字里覆盖。OE 开箱回指第 3 课，本课直接进 mapper。工具链版本以 Sample README 与工具链文档为准。
