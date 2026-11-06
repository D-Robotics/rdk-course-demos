# 2-05 conversion · 自训 YOLO11n PTQ YAML

本目录只服务 RDK 小课堂第 2 章第 5 课。不要修改 [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) 上游仓库。

对照只读：[`samples/vision/ultralytics_yolo/conversion`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo/conversion)。

仓库里没有 ONNX、权重、校准图片、`.bin` / `.hbm`。`scripts/prepare_cal_data.py` 生成的目录在 `.gitignore` 里。

进入 OE 容器的方式以官方环境页为准。不要把账号、口令或机器路径写进配置：

- [X5 环境安装 / OE Docker](https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/env_install.html)
- [S 系列环境部署](https://developer.d-robotics.cc/oe_s_doc/guide/env_install)

## 文件

| 文件 | 板 | 输入 | march | 校准（磁盘） |
| --- | --- | --- | --- | --- |
| `ptq_featuremap_x5.yaml` | X5 | featuremap | `bayes-e` | `cal_featuremap_x5_rgbchw/`（`.rgbchw`，float32 **0..1**；像素÷255 后 tofile） |
| `ptq_featuremap_s100.yaml` | S100 | featuremap | `nash-e` | `cal_featuremap_s100_npy/`（`.npy`，float32 **0..1**） |
| `ptq_nv12_x5.yaml` | X5 | nv12 + rgb | `bayes-e` | `cal_nv12_rgb_f32/`（`.rgbchw`，float32 **0..255**；YAML `data_scale`≈1/255，由 mapper 的 HzPreprocess 使用） |
| `ptq_nv12_s100.yaml` | S100 | nv12 + rgb | `nash-e` | `cal_nv12_s100_npy/`（`.npy`，**/255**；校准看到 0..1，量化阶段再插入前处理；`data_scale` 给运行时，不是对 npy 再除一次） |
| `scripts/prepare_cal_data.py` | — | — | — | 生成上述四类校准。两板 featuremap 都是 0..1 |
| `MARCH.md` | — | — | — | 本课 march 与公开出处 |

`prepare_cal_data.py` 的 sha256 是 `79716b4ad94a1222013b5a8cceb0aac95fac2a8b8cf1b02af16b94001aef012b`。四份 YAML 的 `norm_type` / `scale_value` 键没有改。自训 ONNX 的浮点输入域是 0..1：Ultralytics 在进网络前除以 255，导出图里没有这个 Div。

导出后的 ONNX 放在编译工作目录，不要提交：

- X5：`selftrain_yolo11n_detect_opset11.onnx`
- S100：`selftrain_yolo11n_detect_opset19.onnx`

## 生成与检查

```bash
python3 02_modelzoo/05_train-yolo-featuremap-nv12/conversion/scripts/prepare_cal_data.py \
  --src /path/to/jpg_or_png \
  --out-root /path/to/course_2-05_workspace \
  --width 640 --height 640 --limit 32

python3 02_modelzoo/05_train-yolo-featuremap-nv12/conversion/scripts/test_cal_domains.py
```

`test_cal_domains.py` 只检查文件数值和 YAML 文本。它通过，也不表示板端精度通过。

容器内编译：

```bash
hb_mapper makertbin --config ptq_featuremap_x5.yaml --model-type onnx
hb_mapper makertbin --config ptq_nv12_x5.yaml --model-type onnx
hb_compile --config ptq_featuremap_s100.yaml
hb_compile --config ptq_nv12_s100.yaml
```

## 已记录的 X5 featuremap 单图结果

公开摘要在 [`../board-tests/measured.json`](../board-tests/measured.json)。2026-11-06，x5-8g，只喂 0..1：

- 新 `.bin` sha256：`aee69bc13281483525a62c38121e1612128aceb7d399d261af5cddcec0336b75`
- `hrt_model_exec` 一帧 Infer：**31.316 ms**
- 六个输出头相对 ORT(/255) 的余弦都 ≥ 0.991
- 三路 80 类 logits 为正峰值
- `decode_dfl`（score 0.25，nms 0.45）：板端 8 个检测，ORT 8 个，类多重集 `{45:3, 50:1, 49:4}`

这是一张图上的输入域核对，不是 mAP，也不是泛化精度认证。

不要把下面的旧数字写成这次 featuremap 结果：X5 旧 Infer 26.739 ms（当时校准文件是 0..255）；S100 32.193 ms（本回合没有重编、没有重测）；NV12 Sample 各 5 dets（`bus.jpg`，不是 featuremap）。
