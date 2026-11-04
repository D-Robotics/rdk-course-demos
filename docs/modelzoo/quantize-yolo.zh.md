# 以 YOLO 为例讲量化

> 所属章节：RDK 小课堂 · 第 2 章 Model Zoo · 第 4 课
>
> 适用板卡：RDK X5、RDK S100 / S100P / S600（RDK Model Zoo `main` 分支；本课板上实测为 **S600 + X5**）
>
> 课程目标：以 YOLO 检测为例，讲清工具链针对 YOLO 的特定优化（切后处理、板端解码、敏感层）如何显著减算量、提升板卡运行效果；覆盖输出头协议、导出切点与板端解码、一条 mapper 进两套工具链、Softmax / int16，以及精度掉了怎么分流；命令可跟做
>
> 学习方式：概念讲解 + conversion README 原命令 + 板上 `model_info` / `main` 实测。OE 开箱回指 **2-03**，本课直接进 mapper
>
> 配套视频：**待发布**
>
> 配套课件：[查看中文 HTML 课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/04_quantize-yolo/lesson-2-04.zh.html) · [English slide source](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/04_quantize-yolo/lesson-2-04.html)

---

## 配套资源

| 资源 | 用途 |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | 转换配方、板端 runtime、对照制品 |
| [`samples/vision/ultralytics_yolo/`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo) | 本课主 Sample |
| [`…/ultralytics_yolo/conversion`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo/conversion) | 导出补丁 · mapper · Softmax 配置 |
| [RDK 文档资源中心](https://developer.d-robotics.cc/rdk_doc_center/) | 各板卡官方手册入口 |
| [X5 OE 文档](https://developer.d-robotics.cc/oe_x5_doc) | accuracy_tune / 工具链 |
| [S OE 文档](https://developer.d-robotics.cc/oe_s_doc) | accuracy_debug / 工具链 |
| [hrt_model_exec](https://developer.d-robotics.cc/oe_s_doc/guide/ucp/runtime/tool_introduction/hrt_model_exec) | 板端 `model_info` / `infer` |
| 本课板测汇总 | 课内 `board-tests/measured.json` |

!!! note "插图说明"
    下面四段占位对应本课冻结 26 页课件。带 hash 的 jpg 尚未入库，本讲义只标出 PLACEHOLDER 文件名，便于对照四段结构。

---

## 1. 本课要解决什么问题

上一课（2-03）已经跟着做完了 **ResNet 完整 PTQ**，并开过 OE。换成检测时，常见卡点变成：

1. **输出头**：分类一路 logits；YOLO 是三路 stride，各带类别与 DFL——协议怎么配对？
2. **切图与解码**：后处理放哪？导出切点停在哪？板端怎么 `decode_dfl`？
3. **mapper 与敏感层**：同一 ONNX 怎么进 X5 / S 两套工具链？Softmax、int16 怎么写？
4. **上板与精度分流**：掉点了先查配置还是敏感层？数字认谁？

本课用一条贯穿线回答：**输出头 → 切点/解码 → 一条 mapper + 敏感层 → 板上实测分流**。合起来记住价值线：**针对 YOLO 的特定优化 → 大大减少计算量 → 提升板卡运行效果**（切掉后处理、板端 `decode_dfl` 先过滤再解码、敏感层单独抬——不编造 latency/FPS，数字只认板上实测）。

> **本课路线 PLACEHOLDER** · `assets/lesson-2-04-zh-PLACEHOLDER-route.jpg`

---

## 2. 完成本课后你能做到什么

- 用一句话说清本课价值：针对 YOLO 的特定优化如何减算量、让检测在板上更好跑；
- 说出 YOLO DFL 检测相对分类多出来的输出结构（三路 cls + 三路 DFL），并区分 YOLO26 direct-LTRB；
- 按 conversion README 用 `export_monkey_patch` 导出（X5 opset 11 / S opset 19），图停在 logits；
- 用一条 `mapper.py` 分别打出 X5 `.bin` 与 S `.hbm`，并会写 Softmax int8 / `--quantized int16`；
- 在板上用 `model_info` + `main.py` 核对输出张量数与检测数；
- 精度掉了先分流：大掉查校准/预处理/切点，小掉查 Softmax/int16；**不以 README mAP 引用值上页**。

---

## 3. 输出头（课件 p04–p07）

### 3.1 对照分类

> **输出头对照 PLACEHOLDER** · `assets/lesson-2-04-zh-PLACEHOLDER-heads.jpg`

- 分类（如 ResNet）：一路特征 → 一路 logits；Softmax 常在 runtime。
- YOLO Detect（DFL）：输入 640 → backbone / neck → stride 8/16/32；每层 **cls logits + DFL 64 通道**。
- **导出切点**：六路张量停在图里；后处理不进 ONNX。

### 3.2 形状表（NHWC · 80 类 · 640）

| 路 | 含义 | valid shape |
|---|---|---|
| cls8 | stride8 分类 | 1×80×80×80 |
| DFL8 | stride8 框 | 1×80×80×64 |
| cls16 | stride16 分类 | 1×40×40×80 |
| DFL16 | stride16 框 | 1×40×40×64 |
| cls32 | stride32 分类 | 1×20×20×80 |
| DFL32 | stride32 框 | 1×20×20×64 |

> 不要只按张量个数猜协议；以 conversion README 与 runtime 绑定为准。

### 3.3 协议差异

| 家族 | 契约 |
|---|---|
| DFL（v5u/v8/v9/v10/11/12/13） | 三路 cls + 三路 DFL（64 通道） |
| YOLO26 | direct-LTRB：三路 cls + 三路四通道框；**单独导出器** |

制品 **不可互换**。分割 / 姿态 / 分类是在检测协议之上扩展。

---

## 4. 切图与解码（课件 p08–p11）

### 4.1 五步链路

> **切图与解码 PLACEHOLDER** · `assets/lesson-2-04-zh-PLACEHOLDER-cut.jpg`

1. Ultralytics `.pt` → `export_monkey_patch`
2. ONNX 切点停在 cls / DFL logits（Softmax / dist2bbox / NMS 不进图）
3. mapper 在 **OE** 里编成 `.bin` / `.hbm`（OE 开箱见 **2-03**）
4. 板端 `decode_dfl`：筛选 → 期望 → xyxy
5. 按绑定 IoU 做 NMS 出框

先过滤再算框，利用 Sigmoid 单调性，不必算满约 8400 格。

### 4.2 导出命令（README 原命令骨架）

```bash
# X5 · opset 11
python …/export_monkey_patch.py \
  --platform x5 --pt /models/yolo11n.pt \
  --require-local --opset 11

# S600 · opset 19
python …/export_monkey_patch.py \
  --platform s600 --pt /models/yolo11n.pt \
  --require-local --opset 19
```

从仓库根目录执行；ONNX 通常写在权重旁。

### 4.3 校准与 conversion 目录

```bash
ls samples/vision/ultralytics_yolo/conversion/
# → export_monkey_patch.py  mapper.py
# → mapper_x5.py  mapper_s.py  config_x5.yaml
```

- 仓库 **不附带** 校准集；默认 `--cal-sample-num 20`，建议准备 **20–50** 张有代表性的图。
- X5：原始 RGB / NCHW；S：除以 255 的 npy。
- NMS 默认：X5 检测 **0.70**；S 检测 **0.45**；S 的 YOLOv10 无 NMS。

---

## 5. mapper 与敏感层（课件 p12–p18）

> OE 怎么开、容器怎么进：**回指 2-03**。本课不设 OE 开箱专章，直接 mapper。

### 5.1 两套工具链

| 侧 | 工具 | march | 校准 | 产物 |
|---|---|---|---|---|
| X5 | `hb_mapper makertbin` | bayes-e | 原始 RGB | `.bin` |
| S | `hb_compile` | nash-e / m / p | 归一化 npy | `.hbm` |

共同：Softmax int8；需要时 `--quantized int16`。Nash **不支持 O3**，用 O0/O1/O2。

### 5.2 一条 mapper

```bash
# X5
python …/conversion/mapper.py \
  --platform x5 \
  --onnx /models/yolo11n.onnx \
  --cal-images /datasets/calibration \
  --output-dir /models/compiled
# → yolo11n_bayese_640x640_nv12.bin

# S600
python …/conversion/mapper.py \
  --platform s600 --march nash-p \
  --onnx /models/yolo11n.onnx \
  --cal-images /datasets/calibration \
  --output-dir /models/compiled
# → yolo11n_nashp_640x640_nv12.hbm
```

同名需显式 `--overwrite`。S100 / S100P 分别换 `nash-e` / `nash-m`。

### 5.3 Softmax 与 int16

**X5**（`config_x5.yaml`）：

```yaml
optimization: set_Softmax_input_int8, set_Softmax_output_int8
```

**S**（`quant_config`）：

```yaml
quant_config: {"op_config": {"softmax": {"qtype": "int8"}}}
```

仍掉点再 `--quantized int16`（整网抬精度，更慢更大）。

### 5.4 默认产物名（ONNX stem=`yolo11n`，640）

| 目标 | march | 文件名 |
|---|---|---|
| X5 | bayes-e | `yolo11n_bayese_640x640_nv12.bin` |
| S100 | nash-e | `yolo11n_nashe_640x640_nv12.hbm` |
| S100P | nash-m | `yolo11n_nashm_640x640_nv12.hbm` |
| S600 | nash-p | `yolo11n_nashp_640x640_nv12.hbm` |

发布名可能带 `_detect_`；以 `download_model` / 实测为准。`output-dir` 只改位置。

---

## 6. 上板与精度分流（课件 p19–p26）

### 6.1 model_info / main

板上只写 `/tmp/course_2-04/`。先 `model_info` 核对张量，再 `main.py` 跑 `bus.jpg`。

```bash
mkdir -p /tmp/course_2-04 && cd /tmp/course_2-04
hrt_model_exec model_info --model_file \
  yolo11n_detect_nashp_640x640_nv12.hbm

python …/runtime/python/main.py \
  --platform s600 --family yolo11 \
  --task detect --model-path <hbm> \
  --test-img …/bus.jpg \
  --img-save-path /tmp/course_2-04/out.jpg
```

X5 跨家族对照可用 yolov8n（`--platform x5 --family yolov8`）。命令一律显式 `--model-path`。

### 6.2 板上实测（权威：`board-tests/measured.json`）

录制时间：2026-11-02 11:14:31（Asia/Shanghai）。Model Zoo 制品 · `bus.jpg`。

| 板 | 制品 | 输出张量数 | 检测数 | 备注（来自 measured notes） |
|---|---|---|---|---|
| S600 | `yolo11n_detect_nashp_640x640_nv12.hbm` | **6** | **5** | NMS 默认 0.45；persons 0.89/0.85/0.83/0.50 + bus 0.92 |
| X5U | `yolov8n_detect_bayese_640x640_nv12.bin` | **6** | **5** | NMS 默认 0.70；persons 0.86/0.84/0.82/0.36 + bus 0.85 |

**本课不上 README mAP**（如 36.77 / 35.74 / 35.72）。精度页只认检测数 / 张量数分流与板上实测。

### 6.3 精度分流

> **精度分流 PLACEHOLDER** · `assets/lesson-2-04-zh-PLACEHOLDER-triage.jpg`

1. **浮点对齐**：导出 ONNX ≈ 训练结果。
2. **掉很多**：查校准 / 预处理 / 切点配置。
3. **掉一点**：查 Softmax / `--quantized int16`。
4. **板上复测**：`model_info` + `main`；再用文档中心 `accuracy_tune` / `accuracy_debug`。

敏感度工具现场命令以文档中心为准（**待文档**）；本课只给分流路线。

---

## 7. 本课小结

合起来一条价值线：**针对 YOLO 的特定优化 → 大大减少计算量 → 提升板卡运行效果**（切后处理、板端解码、敏感层单独抬）。再带走五句：

1. 输出头是多尺度多路；协议看导出与 runtime 绑定。
2. 切点停在 logits；`decode_dfl` 在板端，先过滤再算框。
3. 一条 mapper：X5 → `.bin`，S → `.hbm`。
4. Softmax 单独 int8；不够再抬 int16。
5. 精度掉了先分流；数字只认板上实测。

---

## 8. 下一课预告（2-05）

**自训 YOLO + feature map / NV12**：自己训一条 YOLO，先用 feature map 打通链路，再改 NV12；含完整 OE 实操。

---

## 附录 · 待核实（不上假数）

| 项 | 状态 |
|---|---|
| PC 端自转 YOLO 的转换相似度 / evaluator mAP | 待板测/待文档（本机 OE 转换未在本轮重跑） |
| 自转制品 vs Model Zoo 制品逐框对比 | 待板测（当前 measured.json 为 Model Zoo 制品） |
| 无 `--model-path` 时板端是否自动下载 | 待板测/待文档（本课命令一律显式 `--model-path`） |
| 敏感度工具现场命令 | 待文档（hmct-debugger / get_sensitivity_of_nodes 以文档中心为准） |
