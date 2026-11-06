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
| `ptq_featuremap_x5.yaml` | X5 | featuremap | `bayes-e` | `cal_featuremap_x5_rgbchw/`（原始 `.rgbchw`，float32 **/255 → 0..1**；`norm_type` 仍是 `no_preprocess`） |
| `ptq_featuremap_s100.yaml` | S100 | featuremap | `nash-e` | `cal_featuremap_s100_npy/`（`.npy`，float32 **/255 → 0..1**） |
| `ptq_nv12_x5.yaml` | X5 | nv12 + rgb | `bayes-e` | `cal_nv12_rgb_f32/`（`.rgbchw`，float32 **0..255**；YAML 含 `norm_type: data_scale` + `scale_value≈1/255` 字段） |
| `ptq_nv12_s100.yaml` | S100 | nv12 + rgb | `nash-e` | `cal_nv12_s100_npy/`（`.npy`，float32 **/255 → 0..1**；YAML 仍含 `data_scale`。这是量化阶段才插入的运行时前处理，不是对 npy 再乘一次，也不是 featuremap 的依据） |
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

- X5 featuremap：再除以 255，`tofile` 成原始 `.rgbchw`（数值 0..1，YAML 仍是 `no_preprocess`）
- S100 featuremap：除以 255 一次，`np.save` 成 `.npy`（数值 0..1，YAML 仍是 `no_preprocess`）
- X5 NV12：保持 0..255 `.rgbchw`。YAML `data_scale` 不动
- S100 NV12：除以 255 一次的 `.npy`。YAML `data_scale` 不动，不再除第二次

旧的 `cal_featuremap_x5_rgbchw/*.rgbchw` 若仍是 0..255，必须删掉后重跑本脚本。只改文件不够，X5 featuremap 的 `.bin` 还要重编再上板。这一步本仓库没有做。

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

8. Ultralytics 检测训练在 `Format` 之后、进网络之前做 `/255`。`v8.3.0` 与当前 `main`（`4ecb2b5b5457954a1276115b5bcb42f09c358cd6`）的 `DetectionTrainer.preprocess_batch` 都是 `batch["img"].float() / 255`。`Format._format_img` 只做 HWC→CHW，不把除法写进图。ONNX 导出追踪的是网络本身（检测输出名默认 `output0`），不插入这个 Div。推理侧 `predictor.preprocess` 对 ndarray 做 `.div_(255)`，对已经是 tensor 的输入则要求调用方自己处于 0..1。  
   https://github.com/ultralytics/ultralytics/blob/v8.3.0/ultralytics/models/yolo/detect/train.py  
   https://github.com/ultralytics/ultralytics/blob/4ecb2b5b5457954a1276115b5bcb42f09c358cd6/ultralytics/models/yolo/detect/train.py  
   https://github.com/ultralytics/ultralytics/blob/4ecb2b5b5457954a1276115b5bcb42f09c358cd6/ultralytics/engine/exporter.py  
   https://github.com/ultralytics/ultralytics/blob/4ecb2b5b5457954a1276115b5bcb42f09c358cd6/ultralytics/engine/predictor.py

两条路径不要互相证明：

- **featuremap + `no_preprocess`**：文件就是 ONNX 输入，所以两板 featuremap 都写成 0..1。X5 仍是原始 `.rgbchw`，S100 仍是 `.npy`。这来自 Ultralytics 的训练前处理，不来自 NV12 配方。
- **X5 NV12**：校准文件保持 0..255，YAML `data_scale` 保留。X5 文档里的 HzPreprocess 公式是 `((input[-128,127] + 128) - mean) * scale`，scale 在工具链里做。不要把 featuremap 改成同样的 0..255，也不要删掉这个 scale。
- **S100 NV12**：校准 npy 按浮点模型输入写成 0..1；YAML `data_scale` 留在量化阶段，写进编译后的运行时前处理。文档没有把它写成对 npy 再乘 1/255。本仓库仍然没有 `hb_compile` 日志。不要用这条 NV12 惯例反过来解释 featuremap。

余弦不能单独当域检查。正数倍缩放后余弦仍是 1，数值范围会变。旧 X5 featuremap `.bin` 用 /255 喂入时，曾报告三路 80 通道 cls 最大值约 -2.37 / -5.50 / -4.61，而 ORT(/255) 的 `output0` 最大值约 +1.11，余弦仍约 0.983。那次对照属于错域旧制品。本仓库没有那份 `.bin`，没有重跑 ORT，这三个数不能写成新测值。

## 尚需的最小实测

云端没有 OE，也没有板卡。脚本测试只检查新文件的数值。下面几步都还没做，所以不能写「实测通过」：

1. 删掉旧的 `cal_featuremap_x5_rgbchw/`（里面是 0..255），用本脚本按 640 重新生成。抽一个 `.rgbchw`，确认 float32 最大值 ≤ 1。
2. 用新的 0..1 校准文件重编 X5 featuremap `.bin`。用同一张 0..1 输入对比新 bin 与 ORT。看类别通道的最大值和符号，不要只看余弦。
3. S100 featuremap 文件本来就是 0..1 `.npy`。若板上制品是用旧脚本编的，X5 这一路必须重编；S100 只有在当时 npy 不是 /255 时才要重编。无论哪一路，本 PR 都没有新的板端时延或检测数。
4. NV12 两份 YAML 的 `scale_value` 不要改。X5 NV12 校准继续用 0..255；S100 NV12 校准继续用已经 /255 的 npy。
