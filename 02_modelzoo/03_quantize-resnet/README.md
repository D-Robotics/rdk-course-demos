# ResNet Quantization Hands-on Sources

This directory stores the standalone bilingual HTML pages and slide specs for the ResNet Quantization Hands-on tutorial (RDK Classroom, Chapter 2 Model Zoo, Lesson 3).

- English handbook: [`docs/modelzoo/quantize-resnet.md`](../../docs/modelzoo/quantize-resnet.md)
- Chinese handbook: [`docs/modelzoo/quantize-resnet.zh.md`](../../docs/modelzoo/quantize-resnet.zh.md)
- English slide source: `lesson-2-03.html`
- Chinese slide source: `lesson-2-03.zh.html`
- English slide spec: `blueprint.json`
- Chinese slide spec: `blueprint.zh.json`

The HTML slides are self-contained; open them directly in a browser. Use ←/→ to change slides, N for speaker notes, F for full screen, and S for the scroll view.

The slide specs use the deck schema (`mode: deck`, layout-based slides with speaker notes).

The lesson runs PTQ for ResNet-18 with the X5 toolchain (`hb_mapper`, `.bin`) and the S-series toolchain (`hb_compile`, `.hbm`), then verifies the artifacts on RDK X5 and RDK S100, on the RDK Model Zoo `main` branch. PTQ runs on CPU alone; a GPU is only an optional speed-up. Toolchain versions are not fixed here; follow the sample READMEs and the toolchain documentation.

---

# ResNet 量化实操 资料

本目录存放 RDK 小课堂第 2 章 Model Zoo 第 3 课「ResNet 量化实操」的中英文独立 HTML 课件与课件规格文件。

- 中文讲义：[`docs/modelzoo/quantize-resnet.zh.md`](../../docs/modelzoo/quantize-resnet.zh.md)
- 英文讲义：[`docs/modelzoo/quantize-resnet.md`](../../docs/modelzoo/quantize-resnet.md)
- 中文课件源码：`lesson-2-03.zh.html`
- 英文课件源码：`lesson-2-03.html`
- 中文课件规格：`blueprint.zh.json`
- 英文课件规格：`blueprint.json`

HTML 课件为单文件，直接用浏览器打开即可。←/→ 翻页，N 显示讲稿，F 全屏，S 切换滚动视图。

本课在 RDK Model Zoo `main` 分支上，用 X5 工具链（`hb_mapper`，产物 `.bin`）与 S 系列工具链（`hb_compile`，产物 `.hbm`）完成 ResNet-18 的 PTQ，并在 RDK X5、RDK S100 上验证产物。PTQ 纯 CPU 即可完成，GPU 只是可选加速。工具链版本以 Sample README 与工具链文档为准。
