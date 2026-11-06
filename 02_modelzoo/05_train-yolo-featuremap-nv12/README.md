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

The cut is approved. The public video link is not posted yet. This directory does not contain weights, ONNX, calibration tensors, or the compiled `.bin`.

X5 featuremap files are float32 0..1 raw `.rgbchw`, and `norm_type` stays `no_preprocess`. [`board-tests/measured.json`](board-tests/measured.json) separates two runs of bin `f728b1d3…`: the approved cut’s live infer is 26.663 ms; 25.772 ms and 8 detections belong to a different log. 26.685 ms is an experiment. S100 on-board infer is 33.145 ms on hbm `35758dce…`; the 7 detections are host-side post-process. 31.316 ms and bin `aee69bc1…` are history. The NV12 Sample count of 5 detections is not featuremap. None of this is mAP. See `conversion/README.md`.

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

成片已审定，公开视频链接尚未挂上。本目录不包含权重、ONNX、校准张量或编译好的 `.bin`。

X5 featuremap 文件是 float32 0..1 的原始 `.rgbchw`，`norm_type` 仍是 `no_preprocess`。[`board-tests/measured.json`](board-tests/measured.json) 把 bin `f728b1d3…` 的两次读数分开：成片实拍是 26.663 ms；25.772 ms 和 8 个检测属于另一次日志。26.685 ms 是实验记录。S100 板上 Infer 是 33.145 ms，制品前缀 `35758dce`；7 个检测是主机离板后处理。31.316 ms 和 bin `aee69bc1…` 是历史。NV12 Sample 的 5 个检测不是 featuremap。这些都不是 mAP。说明见 `conversion/README.md`。
