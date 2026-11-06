# Train YOLO: Feature Map First, Then NV12

Standalone bilingual HTML slides and the PTQ YAML for RDK Classroom, Chapter 2 Model Zoo, Lesson 5.

- English handbook: [`docs/modelzoo/train-yolo-featuremap-nv12.md`](../../docs/modelzoo/train-yolo-featuremap-nv12.md)
- Chinese handbook: [`docs/modelzoo/train-yolo-featuremap-nv12.zh.md`](../../docs/modelzoo/train-yolo-featuremap-nv12.zh.md)
- English slide source: `lesson-2-05.html`
- Chinese slide source: `lesson-2-05.zh.html`
- English slide spec: `blueprint.json`（同内容另存 `spec.json`）
- Chinese slide spec: `blueprint.zh.json`（同内容另存 `spec.zh.json`）
- PTQ YAML and calibration script: [`conversion/`](conversion/README.md)

The HTML slides are self-contained; open them in a browser. Use ←/→ to change slides, N for speaker notes, F for full screen, and S for the scroll view.

The lesson trains YOLO11n on coco128 (default 40 epochs), then runs four OE conversions: X5 `bayes-e` and S100 `nash-e`, each with a featuremap config and an NV12 config. Lesson 2-06 is the inference API; lesson 2-07 is the deeper Sample change. This directory does not change those lessons.

The companion video is not published yet. The handbook figures 26.739 ms, 32.193 ms, and 5 dets are pre-fix slide anchors. This commit does not include weights, ONNX, calibration tensors, or compiled models, and it does not claim a new board pass.

X5 featuremap calibration is now float32 0..1 in a raw `.rgbchw`, with `norm_type: no_preprocess` unchanged. S100 featuremap stays 0..1 `.npy` and `no_preprocess`. NV12 YAMLs keep `data_scale`. Regenerating the X5 featuremap files and recompiling the `.bin` is still required before any new on-board number. See `conversion/README.md`.

---

# 自训 YOLO：先 feature map 再 NV12

本目录存放 RDK 小课堂第 2 章第 5 课的中英文 HTML 课件、课件规格，以及四份 PTQ YAML。

- 中文讲义：[`docs/modelzoo/train-yolo-featuremap-nv12.zh.md`](../../docs/modelzoo/train-yolo-featuremap-nv12.zh.md)
- 英文讲义：[`docs/modelzoo/train-yolo-featuremap-nv12.md`](../../docs/modelzoo/train-yolo-featuremap-nv12.md)
- 中文课件源码：`lesson-2-05.zh.html`
- 英文课件源码：`lesson-2-05.html`
- 中文课件规格：`blueprint.zh.json`（同内容另存 `spec.zh.json`）
- 英文课件规格：`blueprint.json`（同内容另存 `spec.json`）
- PTQ YAML 与校准脚本：[`conversion/`](conversion/README.md)

HTML 课件为单文件，直接用浏览器打开。←/→ 翻页，N 显示讲稿，F 全屏，S 切换滚动视图。

本课范围：coco128 上自训 YOLO11n，默认 40 epoch；X5 `bayes-e` 与 S100 `nash-e` 各做 featuremap 和 NV12，共四轮 OE。2-06 是推理接口，2-07 是 Sample 深改，本目录不改这两课。

配套视频尚未发布。讲义里的 26.739 ms、32.193 ms 和 5 dets 是修正前的课件锚点。本次提交没有权重、ONNX、校准张量或编译制品，也没有新的板端通过结果。

X5 featuremap 校准现为 float32 0..1 的原始 `.rgbchw`，`norm_type` 仍是 `no_preprocess`。S100 featuremap 仍是 0..1 的 `.npy`，同样 `no_preprocess`。NV12 YAML 的 `data_scale` 没有改。旧的 0..255 X5 featuremap 文件要删掉重生成，`.bin` 要重编之后才能写新的板上数字。说明见 `conversion/README.md`。
