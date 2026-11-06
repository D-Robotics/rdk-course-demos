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

The companion video is not published yet. This directory does not contain weights, ONNX, calibration tensors, or the compiled `.bin`.

X5 featuremap files are float32 0..1 raw `.rgbchw`, and `norm_type` stays `no_preprocess`. The recorded single-image check is in [`board-tests/measured.json`](board-tests/measured.json): Infer 31.316 ms, six-head cosine versus ORT(/255) at least 0.991, and 8 detections at score 0.25 / NMS 0.45. That check is not an mAP result. S100 32.193 ms was not remeasured. The NV12 Sample count of 5 detections is not this featuremap result. The old X5 26.739 ms figure used the previous 0..255 calibration. See `conversion/README.md`.

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

配套视频尚未发布。本目录不包含权重、ONNX、校准张量或编译好的 `.bin`。

X5 featuremap 文件是 float32 0..1 的原始 `.rgbchw`，`norm_type` 仍是 `no_preprocess`。已记录的单图核对在 [`board-tests/measured.json`](board-tests/measured.json)：Infer 31.316 ms，六头相对 ORT(/255) 的余弦至少 0.991，score 0.25 / NMS 0.45 下 8 个检测。这不是 mAP。S100 的 32.193 ms 没有重测。NV12 Sample 的 5 个检测不是这次 featuremap 结果。X5 旧的 26.739 ms 来自之前的 0..255 校准。说明见 `conversion/README.md`。
