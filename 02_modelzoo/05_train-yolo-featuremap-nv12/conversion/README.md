# 2-05 conversion · 自训 YOLO11n PTQ YAML

本目录只服务 RDK 小课堂第 2 章第 5 课。不要修改 [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) 上游仓库。

对照只读：[`samples/vision/ultralytics_yolo/conversion`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo/conversion)（调查时的 `main`：`218a3e78970c3f1ee117d59586cf8dd3ada3864f`）。

仓库里没有 ONNX、权重、校准图片、`.bin` / `.hbm`。`scripts/prepare_cal_data.py` 生成的目录在 `.gitignore` 里。

进入 OE 容器的方式以官方环境页为准。不要把账号、口令或内网地址写进配置：

- [X5 环境安装 / OE Docker](https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/env_install.html)
- [S 系列环境部署](https://developer.d-robotics.cc/oe_s_doc/guide/env_install)

## 文件与磁盘现状

| 文件 | 板 | 输入 | march | 校准（磁盘现状） |
| --- | --- | --- | --- | --- |
| `ptq_featuremap_x5.yaml` | X5 | featuremap | `bayes-e` | `cal_featuremap_x5_rgbchw/`（`.rgbchw`，float32 **0..255**） |
| `ptq_featuremap_s100.yaml` | S100 | featuremap | `nash-e` | `cal_featuremap_s100_npy/`（`.npy`，float32 **/255 → 0..1**） |
| `ptq_nv12_x5.yaml` | X5 | nv12 + rgb | `bayes-e` | `cal_nv12_rgb_f32/`（`.rgbchw`，float32 **0..255**；YAML 含 `norm_type: data_scale` + `scale_value≈1/255` 字段） |
| `ptq_nv12_s100.yaml` | S100 | nv12 + rgb | `nash-e` | `cal_nv12_s100_npy/`（`.npy`，float32 **/255 → 0..1**；YAML 同样含 `data_scale` 字段。工具链如何组合「已 /255 文件 + data_scale」**待核**，这里只记录文件和字段，不写成已验证闭环） |
| `scripts/prepare_cal_data.py` | — | — | — | 从 JPG/PNG 生成上述四类校准目录 |
| `MARCH.md` | — | — | — | 本课 march 与公开出处 |

`march` 与 Model Zoo 一致。本仓库没有重新执行 `hb_mapper` / `hb_compile`。X5 NV12 YAML 没有写 `input_shape`，与上游 `config_x5.yaml` 一样交给 ONNX；S100 两份写了 `1x3x640x640`。S100 NV12 的 `mean_value` 是空字符串，norm 仍是 `data_scale`，不是 `data_mean_and_scale`。

导出后的 ONNX 放在编译工作目录，不要提交：

- X5：`selftrain_yolo11n_detect_opset11.onnx`
- S100：`selftrain_yolo11n_detect_opset19.onnx`

## 生成校准文件

依赖：`numpy`、`opencv-python`。在开发机执行。

```bash
python3 02_modelzoo/05_train-yolo-featuremap-nv12/conversion/scripts/prepare_cal_data.py \
  --src /path/to/jpg_or_png \
  --out-root /path/to/course_2-05_workspace \
  --width 640 --height 640 --limit 32
```

脚本只做 BGR→RGB、resize、HWC→NCHW float32，然后：

- X5 featuremap 与 X5 NV12：同一份 **0..255**，`tofile` 成 `.rgbchw`
- S100 featuremap 与 S100 NV12：同一份 **除以 255 一次**，`np.save` 成 `.npy`

它不会把 S100 的 npy 再乘 `1/255`，也不会删掉 YAML 里的 `scale_value`。

校验文件域（不调用 OE，通过也不表示量化精度已验证）：

```bash
python3 02_modelzoo/05_train-yolo-featuremap-nv12/conversion/scripts/test_cal_domains.py
```

## 编译命令（官方 OE 容器内）

建议顺序：每块板先 featuremap，再 NV12。产物后缀：X5 `.bin`，S100 `.hbm`。本目录没有编译日志。

```bash
hb_mapper makertbin --config ptq_featuremap_x5.yaml --model-type onnx
hb_mapper makertbin --config ptq_nv12_x5.yaml --model-type onnx
hb_compile --config ptq_featuremap_s100.yaml
hb_compile --config ptq_nv12_s100.yaml
```

## 文档怎么区分两套工具，以及还缺哪一步

下面是公开文档和上游源码的阅读结果。**没有在本环境跑过 OE，不能当成校准闭环已经证实。**

1. X5 量化编译：`input_type_train` 是原始浮点模型输入域，`input_type_rt` 是边缘侧输入。`featuremap` 的中间类型是 float32，不是 CNN 中间层。  
   https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_usage/quantize_compile.html
2. X5 `norm_type`：`no_preprocess` 不添加预处理；`data_scale` 是乘 scale。页面写明 YAML 加了 mean/scale 之后，校准前处理里不要再加 MeanTransformer / ScaleTransformer。运行时 HzPreprocess 公式是 `((input[-128,127] + 128) - mean) * scale`。  
   https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_appendix/norm_type.html
3. X5 校准数据准备：示例注释写「transformer 里没有减 mean、乘 scale，因为 mean/scale 已经融合进模型」，并把 skimage 的 `[0,1]` 乘回 255 再存盘。  
   https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_usage/prepare_calibration_data.html
4. S100 **校准集**一节：校准样本要做成与原始浮点模型一致的 npy。分类示例的 transformer **包含**减 mean 和乘 scale。校准之后的 `optimized_float_model.onnx` / `calibrated_model.onnx` / `ptq_model.onnx` 输入仍与原始浮点模型一致。  
   https://developer.d-robotics.cc/oe_s_doc/guide/ptq/ptq_usage/prepare_data.html#prepare_calibration_data
5. 同一页后半「无需再归一化」在 **HBIR/HBM 推理准备**，不在校准集一节。它说的是编译后的模型会做色彩转换和归一化，推理侧按 `input_type_rt` 准备，不要对这份推理数据再归一化。  
   https://developer.d-robotics.cc/oe_s_doc/guide/ptq/ptq_usage/prepare_data.html
6. S100 阶段顺序：校准阶段用校准数据统计量化参数，产出 `calibrated_model.onnx` 与 `ptq_model.onnx`。量化阶段才「根据前处理配置（包括 `input_type_rt` 到 `input_type_train` 的色彩转换，mean/scale 的处理等）」生成 `quantized_model.bc`。  
   https://developer.d-robotics.cc/oe_s_doc/guide/ptq/ptq_usage/quantize_compile.html
7. Model Zoo `workflow.py` 对 X5 和 S 系列写入同一组 NV12 字段：`rt=nv12`、`train=rgb`、`norm_type=data_scale`、`scale_value=0.003921568627451`。X5 `normalize_calibration=False`（`.rgbchw` 不除 255）；S 系列 `normalize_calibration=True`（`.npy` 除以 255 一次）。README 称这是编译器标定格式，运行时 NV12 仍由板端绑定负责。上游这条路径**没有** featuremap YAML。  
   https://github.com/D-Robotics/rdk_model_zoo/blob/218a3e78970c3f1ee117d59586cf8dd3ada3864f/samples/vision/ultralytics_yolo/conversion/workflow.py  
   https://github.com/D-Robotics/rdk_model_zoo/blob/218a3e78970c3f1ee117d59586cf8dd3ada3864f/samples/vision/ultralytics_yolo/conversion/README_cn.md

因此现在只能分开记录，不能合成「S100 已经 /255，YAML 再缩放一次并已证实」：

- S100 文档把校准数据对准浮点模型，把 mean/scale 放在随后的量化阶段写进编译模型。这**支持**「npy 的 /255 与 YAML `data_scale` 不是同一次乘法」这一种读法，但本仓库没有 `hb_compile` 日志，所以讲义保持待核。
- X5 文档要求校准文件不要预先做已融合的 mean/scale。这与 X5 NV12 磁盘 0..255、YAML 仍保留 `data_scale` 同向。同样没有本地编译。
- featuremap 两份都是 `no_preprocess`，配置里没有 scale 可融合。上游「X5 不除 255」只描述带 `data_scale` 的 NV12 配方，不能自动证明 X5 featuremap 的 0..255 已经对齐 Ultralytics ONNX（图外通常还有一次 /255）。这一格也待核。本 PR 不改文件数值，也不删 YAML scale。

## 尚需的最小实测

云端没有 OE，也没有 X5 / S100。下面四项不要求完整 mAP。

1. 用同一张图生成 640×640 校准文件。用 ONNX Runtime 跑自训 ONNX：输入 A 为 0..255，输入 B 为 /255。看首个卷积输出的数量级，确认这张 ONNX 的输入域是 A 还是 B。
2. S100：把 `ptq_nv12_s100.yaml` 编译到出现 `calibrated_model.onnx`。用**同一份 /255 npy** 比较原始 ONNX 与 calibrated 模型（或工具打印的 Calibrated Cosine）。余弦高且数量级一致，才说明校准没有把 npy 再乘 1/255。激活大约缩小 255 倍，才是「YAML 对校准数据又缩放了一次」。
3. X5：对 `ptq_nv12_x5.yaml` 做同样对照。ONNX 侧用第 1 步确认的训练域，校准文件用磁盘上的 0..255。
4. 两板 featuremap：在 `no_preprocess` 下把校准模型分别对 ONNX(A) 和 ONNX(B)。哪一侧余弦高，featuremap 文件就应该用哪一个域。在这步有结果之前，不要把 X5 featuremap 的 0..255 写成已经与 ONNX 对齐。
