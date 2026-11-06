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

The companion video is not published yet. Board latency and detection counts printed in the handbook are draft anchors. This commit does not include `board-tests/measured.json`, weights, ONNX, calibration tensors, or compiled models, and it does not claim those numbers were re-measured here.

S100 calibration files are divided by 255 on disk while the NV12 YAML still lists `data_scale`. That combination is recorded as pending toolchain confirmation. See `conversion/README.md`. Do not read the YAML scale as a proven second multiply, and do not delete it until the OE check in that README is done.

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

配套视频尚未发布。讲义里的时延和检测数是课件草稿锚点。本次提交没有 `board-tests/measured.json`、权重、ONNX、校准张量或编译制品，也没有在板上复测这些数字。

S100 校准文件在磁盘上已除以 255，NV12 YAML 仍写着 `data_scale`。这个组合记为待工具链确认，说明见 `conversion/README.md`。在那里的 OE 对照做完之前，不要把它写成已经证实的第二次缩放，也不要删掉 YAML 里的 scale。
