# ResNet 量化实操

> 所属章节：RDK 小课堂 · 第 2 章 Model Zoo · 第 3 课
>
> 适用板卡：RDK X5（`bayes-e`，`hb_mapper` → `.bin`）、RDK S100（`nash-e`，`hb_compile` → `.hbm`）；S100P（`nash-m`）、S600（`nash-p`）同样用 `hb_compile`，本课只在文字里提。RDK Model Zoo `main` 分支，仓库 VERSION 2.0.0，提交口径 `7a97c178`
>
> 课程目标：以 `samples/vision/resnet/conversion` 为对照，在电脑上亲手走完一次 ResNet-18 的 PTQ（训练后量化）：导出 ONNX → 准备校准数据 → 写 yaml → X5 工具链与 S 系列工具链各转一遍 → 读相似度 → 把产物放回 Sample，在 X5 与 S100 上验证
>
> 学习方式：概念讲解 + 电脑端转换实操 + 上板验证（一次只演示一块板）
>
> 配套视频：<!-- TODO: B 站视频发布后补充链接 -->**待发布**
>
> 配套课件：[查看中文 HTML 课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/03_quantize-resnet/lesson-2-03.zh.html) · [English slide source](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/03_quantize-resnet/lesson-2-03.html)

---

## 配套资源

| 资源 | 用途 |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | 本课主角：`samples/vision/resnet/conversion/`（`export.py`、`ptq_x5.yaml`、`ptq_s.yaml`）与 `utils/tools/classification/workflow.py` |
| [ResNet Sample README](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/README_cn.md) | 支持矩阵、转换配方入口、参考精度 |
| [S 系列：hb_compile 工具](https://developer.d-robotics.cc/oe_s_doc/guide/ptq/ptq_tool/hb_compile) | S100 / S100P / S600 的转换工具 |
| [S 系列：模型量化与编译](https://developer.d-robotics.cc/oe_s_doc/guide/ptq/ptq_usage/quantize_compile) | 转换流程与相似度信息的读法 |
| [X5：hb_mapper checker](https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_tool/hb_mapper/hb_mapper_checker.html) | X5 检查工具 |
| [X5：hb_mapper makertbin](https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_tool/hb_mapper/hb_mapper_makertbin.html) | X5 转换工具 |
| [X5：PTQ 转换步骤](https://developer.d-robotics.cc/oe_x5_doc/cn/oe_mapper/source/ptq/ptq_usage/ptq_usage.html) | X5 流程总览 |
| [RDK 文档资源中心](https://developer.d-robotics.cc/rdk_doc_center/) | 各板卡手册与工具链版本说明；工具链版本以工具链文档为准 |

实测环境：电脑端 x86_64 Linux + Docker；板端 RDK X5（SoC 为 X5U）、RDK S100；Model Zoo `main` 提交口径 `7a97c178`。

---

## 1. 本课要解决什么问题

上一课你在板上跑通了 Sample：下载发布制品 → `model_info` → `main.py` → 读 Top-5。那份 `.bin` / `.hbm` 是别人转好的。

如果要把**自己的模型**放进 Sample，或者想知道发布制品是怎么来的，就得自己走一遍转换。本课用同一个 ResNet-18，对照 Sample 的 `conversion/` 目录做三件事：

1. **把浮点模型变成 ONNX，再准备校准数据**；
2. **写 yaml，在 X5 与 S 系列两套工具链里各转一遍**，读懂相似度；
3. **把产物放回 Sample，上板验证**，和发布制品对一对。

---

## 2. 完成本课后你能做到什么

- 说出 PTQ 的五个阶段（浮点模型 → 验证 → 校准数据 → 量化编译 → 评估），以及每一步在哪个目录；
- 读懂 `ptq_x5.yaml` / `ptq_s.yaml`：`march`、`input_type_rt: nv12` 与 `input_type_train: rgb`、`norm_type` + `mean_value` / `scale_value`（归一化被编进模型）、`input_space_and_range: bt601_video`、`cal_data_dir`、`calibration_type`、编译参数；
- 分清 X5（`hb_mapper checker` + `makertbin`，OE X5 镜像，产出 `.bin`）与 S 系列（`hb_compile`，OE S 镜像，产出 `.hbm`）的工具与镜像；
- 看懂日志里的 `Cosine Similarity`（X5）与 `Calibrated Cosine` / `Quantized Cosine`（S 系列），知道余弦相似度只是参考，最终以任务精度为准；
- 把产物重命名为发布名称，用上一课的方法在 X5 与 S100 上验证 white wolf。

---

## 3. PTQ 全貌与转换环境（Part 1）

### 3.1 转换要解决两件事

1. **输入数据处理**：板上运行时输入是 NV12（`input_type_rt: nv12`），训练时是 RGB（`input_type_train: rgb`）。减均值、除标准差这一步不在板上做，而是**编进模型**：yaml 里的 `mean_value` / `scale_value`，对应 ImageNet 常用的 `mean = [0.485, 0.456, 0.406] × 255`，`scale = 1 / (255 × std)`。
2. **模型优化与编译**：把 ONNX 变成 BPU 能跑的 INT8 模型，期间用校准数据决定每层的量化参数。

PTQ 五阶段与目录（Sample 的 `conversion/`）：

| 阶段 | 做什么 | 本课对应 |
|---|---|---|
| 浮点模型 | 取权重、导出 ONNX | `workflow.py fetch`、`export.py` |
| 验证 | 与 PyTorch 对比、工具检查 | `export.json`、`hb_mapper checker` |
| 校准数据 | 一批有代表性的输入 | `workflow.py calibrate` |
| 量化编译 | 校准 + 量化 + 编译 | `hb_mapper makertbin` / `hb_compile` |
| 评估 | 在数据集上比精度 | `evaluator/`（本课演示子集 + 说明怎么测，不跑全量） |


### 3.2 两套工具链镜像

两套工具链都装在 Docker 镜像里，不需要在电脑上直接安装 OE：

| | X5 | S 系列（S100 / S100P / S600） |
|---|---|---|
| 镜像 | `local/rdk-x5-oe:v1.2.8-server`（X5 亦有 CPU/GPU 镜像；本课用本地 server） | 本课演示：`…_s100_s600_gpu:v3.7.0`；同版本另有 `…_s100_s600_cpu:v3.7.0`（`run_docker.sh data/ cpu`） |
| 转换命令 | `hb_mapper checker`、`hb_mapper makertbin` | `hb_compile` |
| 最终产物 | `.bin` | `.hbm` |
| 实测工具版本 | hb_mapper 1.24.3、hbdk 3.49.15、horizon_nn 1.1.0 | hb_compile 3.5.3、hbdk4 4.7.5、hmct 2.6.5 |

> 仓库 README 里 X5 写的镜像是 `…/ai_toolchain_ubuntu_20_x5_gpu:v1.2.8`；本课用的是本地已有的 `local/rdk-x5-oe:v1.2.8-server`，工具版本号对应（hb_mapper 1.24.3，版本号 v1.2.8 相同）。两个镜像的内容是否逐一相同，本课没有比较，所以不下这个结论。工具链版本统一以工具链文档为准。

### 3.3 docker run 的写法

```bash
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g \
  -v "$WORK:$WORK" -w "$WORK/x5" local/rdk-x5-oe:v1.2.8-server \
  bash -c '<命令>'
```

- `--entrypoint ''`：直接 `docker run … bash -c '…'` 实测报过 `cannot execute binary file`（退出码 126）；加上 `--entrypoint ''` 后正常——**这是实测踩过的坑**；
- `-v "$WORK:$WORK"`：把工作目录原路径挂进容器，yaml 里写的绝对路径容器内外一样；
- 有 NVIDIA 显卡时，`--gpus all` 是可选的加速参数，**不是** S 系列必需；做 PTQ 用同版本 CPU 镜像就够（见 §5.3）。本课演示保留了 GPU 镜像 + `-e CUDA_VISIBLE_DEVICES=-1` 的实测路径。

### 3.4 工作目录

`$WORK` 放在**仓库外面**，例如 `~/work/course_2-03/resnet-18`，下面分 `weights/`、`export/`、`x5/`、`s100/`。转换产物很大（几十 MB 的中间 ONNX），不要放进 Sample 目录。

---

## 4. ONNX 与校准数据（Part 2）

### 4.1 导出 ONNX

```bash
# cwd：仓库根目录（rdk_model_zoo）
python3 utils/tools/classification/workflow.py fetch --model resnet18 --output $WORK/weights

python3 samples/vision/resnet/conversion/export.py --model resnet18 \
  --source-dir $WORK/weights \
  --images samples/vision/resnet/test_data/white_wolf.JPEG samples/vision/resnet/test_data/zebra_cls.jpg \
  --opset 11 --simplify --output $WORK/export
```

- `fetch` 取固定 revision 的 timm 权重（`timm/resnet18.a1_in1k`），保证每个人拿到同一份权重；
- `export.py --opset 11 --simplify` 输出 `model.onnx`（输入 `data` float32 `[1,3,224,224]`，输出 `logits` `[1,1000]`）和 `export.json`；
- 导出时会拿两张测试图和 PyTorch 对比：实测最大绝对误差 **9.5e-06**（white_wolf）、**6.2e-06**（zebra），白狼图的 Top-5 是 270、269、279、296、272；
- 模型参数 11 689 512 个，Conv / Linear 乘加 1 814 073 344。

> 数字来源：本课电脑端的导出日志与 `export.json`。下载约 27.6 s，导出约 3.2 s。


### 4.2 校准数据

校准要给工具一批「有代表性的输入」。Sample 的配方是：固定 200 张图，预处理为「短边缩放到 235 + 224 中心裁剪」（与运行时是同一几何，缩放用带抗锯齿的 bicubic）。

```bash
# X5 与 S100 各跑一次（本课只做这两个目标）
python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform x5 \
  --manifest $CAL/manifest.json --images-root $CAL \
  --expected-images 200 --evaluation-manifest $EVAL/manifest.json \
  --output $WORK/x5/calibration
python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform s100 \
  --manifest $CAL/manifest.json --images-root $CAL \
  --expected-images 200 --evaluation-manifest $EVAL/manifest.json \
  --output $WORK/s100/calibration
```

两个目标写出的数据**内容不一样**（出处：Sample 的 `conversion/README_cn.md`）：

| | X5 | S100 |
|---|---|---|
| 文件 | `.rgb`：无头小端 float32，**原始 [0,255] RGB**（由校准加载器再转成 NV12） | `.npy`：float32，**已按 ONNX 输入做过归一化** |
| 单张大小（实测） | 602 112 字节（224×224×3×4） | 602 240 字节（同样的数据 + 128 字节 `.npy` 头） |
| yaml 的 `cal_data_type` | `float32` | `float32`（S100 日志提示该参数已弃用，建议改用 npy） |

> 实测每个目标 200 张，各约 1.3 s；X5 的 200 张共 115 MB。
>
> **关于校准图片来源**：本课校准图取自 Hugging Face 上 `detection-datasets/coco` 数据集的一个分片（共 40 个分片，用 seed 42 选其中一个），再按 seed 42 从中抽 200 张，清单里记录了每张图的 sha256。这与发布制品当时用的校准图是否相同，本课没有核对，所以自己转出来的数值和发布制品有细微差别是正常的。
>
> **`--evaluation-manifest`**：脚本用它检查「校准图不能出现在评估集里」。本课只下到 ImageNetV2 的前 1 834 张（完整是 10 000 张），检查只覆盖了这一部分，所以这次**不能**据此说「校准图与评估集无重叠」；本课也没有用它做精度评估。

**要点**：校准数据要和部署时的预处理对齐——几何（缩放 + 裁剪）、颜色格式、归一化位置，都要一致，否则校准出来的量化参数对不上真实输入。

---

## 5. 写 yaml、编译：X5 与 S 系列（Part 3）

### 5.1 yaml 逐字段读

Sample 里的 `ptq_x5.yaml` / `ptq_s.yaml` 用占位符（`@WORK@`、`@SIZE@`、`@TARGET@`、`@MARCH@`），用 `sed` 填成实际路径：

```bash
export SIZE=224
sed -e "s#@WORK@#$WORK#g" -e "s#@SIZE@#$SIZE#g" \
  $REPO/samples/vision/resnet/conversion/ptq_x5.yaml > $WORK/x5/config.yaml
sed -e "s#@WORK@#$WORK#g" -e "s#@TARGET@#s100#g" -e "s#@MARCH@#nash-e#g" -e "s#@SIZE@#$SIZE#g" \
  $REPO/samples/vision/resnet/conversion/ptq_s.yaml > $WORK/s100/config.yaml
```

本课实际用的 X5 yaml（节选，路径用 `$WORK` 代替）：

```yaml
model_parameters:
  onnx_model: $WORK/export/model.onnx
  march: bayes-e
  working_dir: $WORK/x5/build
  output_model_file_prefix: resnet_x5
input_parameters:
  input_name: data
  input_type_rt: nv12            # 板上运行时的输入
  input_type_train: rgb          # 训练时的输入
  input_layout_train: NCHW
  input_shape: 1x3x224x224
  norm_type: data_mean_and_scale # 归一化被编进模型
  mean_value: 123.675 116.28 103.53
  scale_value: 0.0171247538317 0.0175070028011 0.0174291938998
  input_space_and_range: bt601_video   # OpenCV 的 I420→NV12 是 BT.601、有限范围
calibration_parameters:
  cal_data_dir: $WORK/x5/calibration/data
  cal_data_type: float32
  calibration_type: default
  preprocess_on: false           # 校准数据已经预处理好
compiler_parameters:
  optimize_level: O3
  compile_mode: latency
  core_num: 1
  input_source:
    data: pyramid
```

| 字段 | 含义 |
|---|---|
| `march` | 目标架构：X5 是 `bayes-e`；S100 是 `nash-e`（S100P 是 `nash-m`，S600 是 `nash-p`） |
| `input_type_rt` / `input_type_train` | 运行时 `nv12`，训练时 `rgb`；工具会在模型前面加好颜色转换 |
| `norm_type` + `mean_value` / `scale_value` | 把「减均值、乘 scale」编进模型，板上不用再做 |
| `input_space_and_range` | `bt601_video`：NV12 的颜色空间与范围，要和运行时前处理一致 |
| `cal_data_dir` | 校准数据所在目录 |
| `calibration_type: default` | 校准方法设为 `default` 时，工具自动在候选里搜索（候选见下文）；本课用默认，校准方法的比较留给下一课 |
| `optimize_level` / `compile_mode` / `core_num` | 编译参数：X5 本课 `O3`，S100 本课 `O2`；都是 `compile_mode: latency`、`core_num: 1` |
| `input_source`（X5） | `data: pyramid`，输入来自金字塔，对应 `model_info` 里的 `HB_DNN_INPUT_FROM_PYRAMID` |

S100 的 yaml 结构相同，差别主要是：`march: nash-e`、`optimize_level: O2`、校准数据是 `.npy`、多了一批默认为空的选项（`debug_mode`、`output_nodes` 等）。S100 日志里有两条 WARNING：`norm_type` 已被弃用（是否归一化由 `mean` / `scale` / `std` 是否填写决定），`cal_data_type` 已被弃用（建议改用 npy）；本课按 Sample 的 yaml 原样使用。

> 说明：Sample 的 yaml 文件头写明，其中的编译参数就是发布制品所用的参数，只有路径和占位符不同。

**`calibration_type: default` 到底选了什么？** 两套工具链在 `default` 下用同一组候选做自动搜索（日志实测）：`max`、`kl` 两种方法，`max_percentile` 取 0.99995 与 1.0，`per_channel` 与 `asymmetric` 各试开关；以模型级余弦相似度 0.995 为目标。两边搜出来的结果不同：

| | X5 | S100 |
|---|---|---|
| 日志里的选择 | `Select max-percentile:percentile=0.99995 method` | `Select kl:num_bin=1024,max_num_bin=16384 method` |

所以「同一份 yaml 写法 + 同一份数据」，在不同工具链上选出的量化方法可以不一样；这也是两边的相似度不能直接比较的原因之一。

### 5.2 X5：`hb_mapper checker` + `makertbin`

```bash
# 在 X5 镜像里执行，cwd = $WORK/x5
hb_mapper checker --model-type onnx --march bayes-e \
  --model $WORK/export/model.onnx --input-shape data 1x3x224x224

hb_mapper makertbin --config config.yaml --model-type onnx      # → build/resnet_x5.bin
```

- `checker` 先检查模型里的算子哪些能上 BPU、哪些落在 CPU，实测 5.7 s；它的表里相似度列是 `--`——**checker 不算相似度**。
- `makertbin` 做校准、量化、编译，实测 **32.8 s**。完成后输出 `build/resnet_x5.bin`（11 081 570 字节），以及一批中间产物（`*_original_float_model.onnx`、`*_optimized_float_model.onnx`、`*_calibrated_model.onnx`、`*_quantized_model.onnx`、`*_quant_info.json`）。
- 整个过程的日志在 `hb_mapper_makertbin.log`。

### 5.3 S 系列：`hb_compile`（本课演示 S100）

```bash
# 本课演示路径（GPU 镜像 + 强制 CPU）；cwd = $WORK/s100
# 正课亦可：同版本 CPU 镜像，不加 --gpus / CUDA_VISIBLE_DEVICES
docker run --rm --entrypoint '' --gpus all -e CUDA_VISIBLE_DEVICES=-1 \
  --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/s100" \
  registry.d-robotics.cc/deliver/ai_toolchain_ubuntu_22_s100_s600_gpu:v3.7.0 \
  bash -c 'hb_compile --config config.yaml'                     # → build/resnet_s100.hbm
```

- 同一条 `hb_compile` 覆盖优化、校准、量化、编译；成功时日志末尾有 `Successfully compile the hbm model`，实测 **217.5 s**（约 3.6 分钟）。产物 `build/resnet_s100.hbm`（12 193 304 字节），中间产物含 `*_calibrated_model.onnx`、`*_quantized_model.bc` 等。
- S100P（`nash-m`）、S600（`nash-p`）用同一个工具、同一份 yaml，改 `march` 即可（yaml 文件头注明）；**本课只转了 S100，S100P 与 S600 没有转换、也没有演示**。

> **关于 CPU / GPU（工具链文档与本课实测）**
> S100/S600 OE V3.7.0 **同时提供 CPU Docker 与 GPU Docker**；单纯做 PTQ，用 CPU 镜像即可（例如 `run_docker.sh data/ cpu`）。GPU 镜像只是有可用 NVIDIA 显卡时的可选加速，**不是** S 系列做 PTQ 的前提。
>
> 本课演示沿用已录好的 GPU 镜像路径。在这台机器上，对 **GPU 镜像** 实测四种写法：
>
> | 写法（均在 GPU 镜像内） | 结果 |
> |---|---|
> | 不加 `--gpus` | 进程崩溃，退出码 139 |
> | `--gpus all` | 校准阶段报 `cudaErrorInvalidDevice`，退出码 255 |
> | `--gpus all -e CUDA_VISIBLE_DEVICES=0` | 同样退出码 255 |
> | `--gpus all -e CUDA_VISIBLE_DEVICES=-1` | **转换成功**，强制走 CPU |
>
> 上表只说明「误用/强行 GPU 镜像时」的现象，**不能**外推成「没有 GPU 就不能转」——正解是改用同版本 CPU 镜像。本课成功日志里有 14 次 `CUDA failure` / `EP Error` 与 `Falling back to ['CPUExecutionProvider']`：这是容器内试 GPU 未成功后自动回退 CPU 的提示，**不影响结果**，看最后是否 `Successfully compile the hbm model`。不要把回退讲成故障。本课没有在带可用 GPU 的电脑上转换，所以不比较 GPU 与 CPU 的耗时。

### 5.4 一页预告：为什么用 NV12 的配置

这里用的是**已发布的 NV12 配置**：因为产物要放回 Sample，而 Sample 只认 NV12 输入。同一个 ResNet 换成不带预处理的 feature map 输入是什么样，留给 2-05 对照着讲；自己的新模型怎么选输入方式，见 2-06。

---

## 6. 相似度检查，回到 Sample 上板验证（Part 4）

### 6.1 读相似度

**X5（`makertbin` 日志，实测）**

```text
Output      Cosine Similarity  L1 Distance  L2 Distance  Chebyshev Distance
logits      0.999941           0.118689     0.004645     0.535569
```

**S100（`hb_compile` 日志，实测）**

```text
| Output     | Calibrated Cosine | Quantized Cosine |
| logits     | 0.999913          | 0.999856         |
```

| | X5 | S100 |
|---|---|---|
| 输出 `logits` 余弦 | 0.999941 | Calibrated 0.999913 / Quantized 0.999856 |
| `GlobalAveragePool` 节点 | 0.997738 | 0.997083 / 0.995166 |
| 节点最低余弦 | 0.996568 | Quantized 0.973402 |


- S 系列文档对两列的定义：`Calibrated Cosine` 是优化后浮点模型与校准后模型对应节点的余弦；`Quantized Cosine` 是优化后浮点模型与量化后定点模型（`quantized_model.bc`）对应节点的余弦。X5 文档里的 `Cosine Similarity` 是原始浮点模型与量化模型在该节点输出上的余弦。（出处：S 系列「模型量化与编译」、X5「PTQ 转换步骤」，经 RDK 文档中心核对。）
- 两套文档都说明：余弦相似度只是指明量化后数据稳定性的一种参考，与模型精度没有明显的直接关联；一般情况下，输出节点相似度低于 0.8 就会有较明显的精度损失，完整精度要看模型精度分析。
- X5 与 S100 的表**格式不同、口径不同**（X5 只有一列 `Cosine Similarity`；S100 分 `Calibrated` / `Quantized` 两列；而且上面 §5.1 说明两边选的校准方法也不同），讲课时分开讲，不要把两个数字当成同一口径去比较「谁更好」。
- 两个输出的相似度都在 0.999 以上，远高于 0.8，没有触发需要排查的情况；但「相似度高」不等于「精度没掉」，最终以任务精度为准。

> 日志里还有编译器给的估算性能（X5：`FPS=428.67`、`latency = 2332.8 us`；S100：`FPS=2430.87`、`latency = 411.4 us`）。**这是编译器估算，不是板上实测**，讲课时一律叫「编译器估算」；下面 §6.4 的板测数字才是真实运行时间。X5 的 `checker` 表里也有一个估算 FPS，不引用。

### 6.2 产物重命名为发布名称

yaml 里 `output_model_file_prefix` 是 `resnet_x5` / `resnet_s100`，所以工具直接产出的是 `resnet_x5.bin` / `resnet_s100.hbm`。放回 Sample 之前改成发布命名规则（含 `bayese` / `nashe`、`224x224`、`nv12`）：

| 目标 | 工具产出 | 重命名后 | sha256（前 8 位…后 6 位） |
|---|---|---|---|
| X5 | `resnet_x5.bin` | `resnet18_bayese_224x224_nv12.bin` | `7f8fa575…c3374a` |
| S100 | `resnet_s100.hbm` | `resnet18_nashe_224x224_nv12.hbm` | `a506767b…635c77` |

只改文件名，内容不变。

注意：重命名**只改文件名**，不会改模型里记录的名字。所以用 `hrt_model_exec model_info` 看，自制的模型名是 `resnet_x5` / `resnet_s100`，发布制品是 `resnet18_224_x5` / `resnet18_224_s100`。另外，自制产物与发布制品**不是逐字节相同**（大小和 sha256 都不同：X5 发布制品 11 081 728 字节（取自上一课的记录）、自制 11 081 570 字节；S100 发布制品 12 193 864 字节（同）、自制 12 193 304 字节），所以数值是「接近」而不是「相同」。

### 6.3 把产物放回 Sample，上板验证

板上沿用上一课的做法：在 `/tmp/course_2-03/` 下准备仓库，把产物放到板上，**一次只看一块板**。

```bash
# 先核对产物没有损坏（两块板都 OK）
sha256sum -c SHA256SUMS.expected
```

> 本课是怎么把仓库和产物送到板上的：仓库在电脑上准备好（sparse + 浅克隆），产物也在电脑上转换，再用 `scp` 拷到板上。**这一次没有在板上重试 `git clone`**，所以不对板上能否访问 GitHub 下结论。正常做法仍然是在板上直接 `git clone`，`scp` 是备用。

**第 1 步：`model_info` 看输入输出**

```bash
hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin   # X5
hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm   # S100
```

| 板 | 自制产物 `model_info`（实测） |
|---|---|
| X5 | 模型名 `resnet_x5`；单输入 `data`，`HB_DNN_IMG_TYPE_NV12`，`(1,3,224,224)`，来源 `HB_DNN_INPUT_FROM_PYRAMID`，75 264 字节；输出 `logits (1,1000,1,1)` F32 |
| S100 | 模型名 `resnet_s100`；双输入 `data_y (1,224,224,1)` + `data_uv (1,112,112,2)` U8；输出 `logits` F32 |

输入结构与发布制品相同（X5：单个 NV12 张量；S100：Y 和 UV 分开），只有模型名不同。`--dry-run` 显示的 `input_protocol`：X5 `packed_nv12`，S100 `split_nv12`。


**第 2 步：`main.py` 看 Top-5**

```bash
# X5
python3 samples/vision/resnet/runtime/python/main.py --target x5 \
  --asset-id x5:resnet:resnet18_bayese_224x224_nv12.bin \
  --model-path /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG \
  --label-file datasets/imagenet/imagenet_classes.names

# S100
python3 samples/vision/resnet/runtime/python/main.py --target s100 \
  --asset-id s:resnet:s100/resnet18_nashe_224x224_nv12.hbm \
  --model-path /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG \
  --label-file datasets/imagenet/imagenet_classes.names
```

`--asset-id` 与 `--model-path` 要配对：asset-id 告诉程序按哪种输入协议准备数据，model-path 告诉它用哪个文件。自制产物沿用发布制品的 asset-id，只换 `--model-path`。


**白狼图的实测结果（自制 vs 发布制品）**

| 名次 | X5 自制 | X5 发布制品 | S100 自制 | S100 发布制品 |
|---|---|---|---|---|
| 1 | white wolf **0.997102** | white wolf 0.998090 | white wolf **0.998149** | white wolf 0.998109 |
| 2 | timber wolf 0.000710 | timber wolf（顺序同） | timber wolf 0.000555 | timber wolf 0.000565 |
| 3 | ice bear 0.000408 | ice bear（顺序同） | **Arctic fox** 0.000187 | ice bear 0.000185 |
| 4 | Arctic fox 0.000203 | Arctic fox（顺序同） | **ice bear** 0.000174 | Arctic fox 0.000137 |
| 5 | Samoyed 0.000096 | Samoyed（顺序同） | **coyote** 0.000063 | Samoyed 0.000087 |

斑马图（zebra）：X5 自制 Top-1 class 340 zebra **0.999962**（发布制品 0.999974）；S100 自制 **0.999976**（发布制品 0.999971）。

怎么读：

- **Top-1 都是 white wolf / zebra，分数在 0.997–0.9999**，自制产物通过验证。
- **X5**：自制与发布制品 Top-5 的类别与顺序完全一致。
- **S100**：前两名与发布制品一致；第 3–5 名分数都只有万分之一量级，自制与发布制品的顺序和个别类别略有不同——自制把 Arctic fox 排在 ice bear 前面，第 5 名是 coyote 而不是 Samoyed，分数差都小于 1e-4。自制产物的 Top-5 与**浮点 ONNX** 的 Top-5（270、269、279、296、272）完全一致。结论：**验证量化结果看 Top-1 和分数量级，不要要求「五个类别完全一致」**。造成这几名差异的具体原因，本课没有做对照实验，不下结论。

### 6.4 板测速度

```bash
hrt_model_exec perf --model_file <产物> --frame_count 200 --thread_num 1
```

| 板 | 自制产物，3 次平均延迟 | 自制产物，3 次 FPS（汇总行） | 发布制品，1 次 |
|---|---|---|---|
| X5 | 3.108 / 3.066 / 3.118 ms | 320.4 / 325.0 / 319.6 | 3.112 ms，320.1 FPS |
| S100 | 0.638 / 0.630 / 0.630 ms | 1524.2 / 1543.4 / 1541.5 | 0.641 ms，1513.8 FPS |


- 自制与发布制品的差别在单次运行的波动之内（X5 自制 3 次的范围是 3.066–3.118 ms，发布制品 3.112 ms；S100 自制 0.630–0.638 ms，发布制品 0.641 ms）；
- 单次测量有正常波动，页面上写区间或「约」；
- 两块板的数字**各自实测**，本课没有做公平的跨板对比实验，不要据此下「谁快几倍」的结论；
- `perf` 同一次运行会打印两个 FPS（线程行与汇总行），略有差别，讲课时选一个口径用到底（本讲义用汇总行）；
- 没有给 `--input_file` 时，`perf` 会打印一块 `[Warning]: These operators have range limitations …` 提示，是常规提示，不是错误。

### 6.5 评估：演示一下，说明怎么测（课件 43–45 页）

> **范围声明**：本课评估 = 演示 + 说明怎么测。下面实测的数字**全部来自 PC 上的演示子集**（200 张 / 1 834 张，只覆盖部分类别），**不代表完整 ImageNetV2 的精度**；板端评估**本课没有运行**，只给命令与参数含义，不给数字。

**口径**：ImageNetV2 **MatchedFrequency**，共 10 000 张、1 000 类、每类 10 张；**不是** ILSVRC2012（ImageNet-1k）验证集，数字不能与 ImageNet-1k 验证集的结果比较。本课只拿到其中 1 834 张（184 个类），标定图与这 1 834 张的 sha256 重叠为 0（只检查了这一部分）。

**Top-1 / Top-5**：对每张图的 1 000 维 logits 稳定排序取前 5 名（同分时编号小的在前）；第 1 名 = 标签算 Top-1 正确，标签在前 5 名里算 Top-5 正确；指标 = 正确张数 ÷ 总张数。

**两个脚本**：

| | FP32 ONNX 评估 | 板端评估 |
|---|---|---|
| 脚本 | `samples/vision/resnet/evaluator/evaluate.py` | `samples/vision/resnet/evaluator/evaluate_board.py` |
| 跑在哪 | 电脑，ONNX Runtime | 板上（X5 / S100），需要 `hbm_runtime` |
| 被评对象 | 自己导出的 `model.onnx`（FP32） | 自己编译的 `.bin`（X5）/ `.hbm`（S100） |
| 本课状态 | 已在演示子集上跑通 | **未运行**，只展示命令 |

**FP32 演示命令**（已跑；路径在页面上以 `<…>` 代替，`--provider CPUExecutionProvider --threads 4` 在页面上略去）：

```bash
python samples/vision/resnet/evaluator/evaluate.py \
  --model resnet18 --manifest <清单> --expected-images 200 \
  --export-dir <导出> --images-root <数据> --output <新目录>
jq -c '.metrics, .correct' evaluation.json
# {"top1":0.625,"top5":0.835}
# {"top1":125,"top5":167}
```

演示子集实测：200 张（124 类）Top-1 62.5%（125/200）、Top-5 83.5%（167/200）；1 834 张（184 类）Top-1 60.74%（1114/1834）、Top-5 81.52%（1495/1834）。页面标「演示子集」，**不与 README 的 59.35% 放在一起，也不据此说「复现成功/失败」**（样本小、类别有偏；200 张 Top-1 的 95% 区间约 55.6%–68.9%）。`evaluate.py` 在 200 张时终端不打印指标（进度每 500 张打印一次），所以页面用 `jq` 读 `evaluation.json`；`evaluation.json` 里的 `class_count` 是 1000（类别表大小），**不是**子集覆盖的类别数，页面不用这个字段。

**板端命令**（未运行，只展示命令与参数含义）：

```bash
python3 evaluate_board.py --target x5 --variant resnet18 \
  --model <自制 .bin> --model-sha256 <哈希> --campaign <配置> \
  --manifest <清单> --data-root <数据> --output <新目录>
# S100：--target s100，--model <自制 .hbm>，对应哈希；其余同 X5
```

- `--model-sha256` 与文件不符则拒绝运行；`--campaign` 提供预处理合同（尺寸、crop、mean/std）和期望张数；`--manifest` 张数必须一致；输出目录必须是新的。
- 仓库没有现成的 `campaign.json` 和 10 000 张 `manifest.json`（正式版由 `freeze.py` 生成，需要全部钉死的 checkpoint 和完整清单，本课不具备）；本课手工拼了一个最小演示 campaign（`DEMO-minimal-not-frozen`），只在 PC 上验证过输入校验，板端推理没跑。
- 仓库流程里没有「在 PC 上评估量化模型」的脚本；用工具链仿真评估**没有尝试**（不是「不可能」）。
- 自己在板上用演示子集实跑时，结果同样要标「演示子集」，不能当成完整 ImageNetV2 的精度。

Sample README 公布了 ResNet-18 的参考数字（**来自 README，不是本课实测**；ImageNetV2 不是 ILSVRC2012 验证集，数值不能和 ImageNet-1k 验证集的结果比较）：

| 目标 | FP32 Top-1 | 板端 Top-1 | FP32 Top-5 | 板端 Top-5 |
|---|---|---|---|---|
| X5 | 59.35% | 58.91% | 80.94% | 80.56% |
| S100 | 59.35% | 58.79% | 80.94% | 80.46% |

相似度 0.999 以上的模型，板端 Top-1 仍比 FP32 低约半个百分点：这正是「相似度只是参考，最终看任务精度」的例子。

---

## 7. 新手规则

课件第 46 页的「五条规则」就是下面前五条，课件、旁白与本讲义保持一致；后三条是补充提醒。

1. docker 镜像要加 `--entrypoint ''`，否则 `bash -c` 会报 126（`cannot execute binary file`）。
2. PTQ 纯 CPU 就能完成，GPU 只是可选加速；工具链同时提供 CPU 与 GPU 两种 Docker 镜像。本课演示日志里的 CUDA 提示可忽略（试 GPU 未成功后自动回退 CPU，共 14 次），看最后有没有 `Successfully compile the hbm model`。
3. 校准数据的预处理必须和部署一致：几何、颜色格式、归一化位置；注意 X5 的校准数据是原始 RGB，S100 的是已归一化的。
4. 产物是按目标 march 编译的，换板型要重新转换（S100P 要用 `nash-m` 另转一份），不要把 S100 的 `.hbm` 拿到 S100P 上用（RDK Studio 文档的常见问题写明：不同 RDK 板使用的 BPU 架构不同，hbm 模型不能跨板型使用）。
5. 验证看 Top-1 和分数量级，不要要求 Top-5 的低分类别顺序完全一致；余弦相似度只是参考：输出节点低于 0.8 要排查，最终看任务精度。
6. `$WORK` 放仓库外，不要把几十 MB 的中间产物写进 Sample 目录。
7. 板上只写 `/tmp/course_2-03/`；密码、密钥不要写进任何文件。
8. 重命名产物后，`model_info` 里的模型名不会变，别用模型名去判断用的是哪个文件。

---

## 8. 常见问题

**Q. `docker run` 报 `cannot execute binary file`（退出码 126）怎么办？**
A. 加 `--entrypoint ''`，再用 `bash -c '<命令>'`。（本课实测：不加时两个镜像都是 126，加上后正常。）

**Q. S100 转换报 `cudaErrorInvalidDevice`，或日志里一大堆 `CUDA failure`？**
A. 优先改用同版本 **CPU 镜像**（PTQ 不需要 GPU）。若仍在用 GPU 镜像：本课实测在 GPU 镜像内加 `-e CUDA_VISIBLE_DEVICES=-1` 可强制走 CPU 并成功（217.5 s）；日志里的 CUDA 提示是试 GPU 未成功后自动回退 CPU，不影响结果。注意：上表四种写法只针对 **GPU 镜像**——不加 `--gpus` 会崩（139），`=0` 失败（255），不能据此说「没 GPU 就不能转」。

**Q. X5 的 `checker` 为什么没有相似度？**
A. `checker` 只检查模型能不能转、算子落在哪；相似度在 `makertbin` 里算。

**Q. 自制产物和发布制品的 Top-5 为什么不完全一样？**
A. 校准数据、工具版本等任何不同都会让量化参数有细微差别。看 Top-1 与分数量级；本课 S100 的前两名与发布制品一致，第 3–5 名分数都在万分之一量级，顺序和个别类别略有不同。

**Q. 板上 `git clone` 失败怎么办？**
A. 主流程仍是板上直接 `git clone`；若当前网络访问不了 GitHub，在能访问的电脑上准备好仓库，用 `scp` 拷到板上的 `/tmp/course_2-03/`。

**Q. 系统镜像版本怎么写？**
A. 板上读 `/etc/version`：本课实测 X5 为 `3.5.0-beta`，S100 为 `4.0.5-Beta`，两者目前都是 Beta。

---

## 本课小结

- PTQ 五阶段：浮点模型 → 验证 → 校准数据 → 量化编译 → 评估；
- X5 用 `hb_mapper checker` + `makertbin` 产出 `.bin`，S100 用 `hb_compile` 产出 `.hbm`；
- yaml 里最关键的是 `march`、`nv12 / rgb`、`mean` / `scale`（归一化编进模型）和校准数据目录；
- 相似度（X5 `logits` 0.999941；S100 `logits` Quantized 0.999856）只是参考；
- 自制产物放回 Sample，在 X5 与 S100 上 Top-1 都是 white wolf（0.997102 / 0.998149），与发布制品在同一量级。

下一课（2-04）：以 YOLO 为例讲量化——检测模型的输出头和分类完全不同，后处理放在哪，再把校准方法、逐层/逐通道、int8/int16 混合精度和精度排查一次讲完。

---

## 完成检查

- [ ] 能说出 PTQ 五阶段与对应目录；
- [ ] 能读懂 yaml 里 `march`、`input_type_rt` / `input_type_train`、`mean_value` / `scale_value`、`cal_data_dir`；
- [ ] 能说明 X5 与 S 系列使用的镜像、命令和产物后缀；
- [ ] 能在日志里找到输出节点的相似度，并说出它为什么只是参考；
- [ ] 在至少一块板上用自制产物完成 `model_info` → `main.py` → 读 Top-1。

---

## 拓展练习

1. 把校准图改成 100 张或 400 张，重新转换，观察相似度和 Top-1 分数的变化。
2. 用 `hrt_model_exec model_info` 对比自制与发布制品，找出所有相同和不同的字段。
3. 把 S100 的 yaml 改成 `march: nash-m`，在 `hb_compile` 里转一遍（S100P 的板子上才能验证）。
4. 读 `export.json`，比较两张图的 PyTorch 与 ONNX 输出误差。

---

## 附录：命令速查

```bash
# ---- 电脑端（cwd = 仓库根目录；WORK、CAL、EVAL 为绝对路径目录）----
export REPO=$(pwd); export WORK=/abs/path/resnet-18

python3 utils/tools/classification/workflow.py fetch --model resnet18 --output $WORK/weights
python3 samples/vision/resnet/conversion/export.py --model resnet18 --source-dir $WORK/weights \
  --images samples/vision/resnet/test_data/white_wolf.JPEG samples/vision/resnet/test_data/zebra_cls.jpg \
  --opset 11 --simplify --output $WORK/export

python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform x5 \
  --manifest $CAL/manifest.json --images-root $CAL --expected-images 200 \
  --evaluation-manifest $EVAL/manifest.json --output $WORK/x5/calibration
python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform s100 \
  --manifest $CAL/manifest.json --images-root $CAL --expected-images 200 \
  --evaluation-manifest $EVAL/manifest.json --output $WORK/s100/calibration

# yaml 占位符
sed -e "s#@WORK@#$WORK#g" -e "s#@SIZE@#224#g" samples/vision/resnet/conversion/ptq_x5.yaml > $WORK/x5/config.yaml
sed -e "s#@WORK@#$WORK#g" -e "s#@TARGET@#s100#g" -e "s#@MARCH@#nash-e#g" -e "s#@SIZE@#224#g" \
  samples/vision/resnet/conversion/ptq_s.yaml > $WORK/s100/config.yaml

# X5（镜像 local/rdk-x5-oe:v1.2.8-server，cwd = $WORK/x5）
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/x5" \
  local/rdk-x5-oe:v1.2.8-server bash -c \
  'hb_mapper checker --model-type onnx --march bayes-e --model '"$WORK"'/export/model.onnx --input-shape data 1x3x224x224'
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/x5" \
  local/rdk-x5-oe:v1.2.8-server bash -c 'hb_mapper makertbin --config config.yaml --model-type onnx'

# S100（镜像 …_s100_s600_gpu:v3.7.0，cwd = $WORK/s100；本课演示：GPU 镜像 + CVD=-1；亦可用同版本 CPU 镜像）
docker run --rm --entrypoint '' --gpus all -e CUDA_VISIBLE_DEVICES=-1 --user "$(id -u):$(id -g)" --shm-size 15g \
  -v "$WORK:$WORK" -w "$WORK/s100" \
  registry.d-robotics.cc/deliver/ai_toolchain_ubuntu_22_s100_s600_gpu:v3.7.0 \
  bash -c 'hb_compile --config config.yaml'

# 重命名为发布名称
cp $WORK/x5/build/resnet_x5.bin     resnet18_bayese_224x224_nv12.bin
cp $WORK/s100/build/resnet_s100.hbm resnet18_nashe_224x224_nv12.hbm

# ---- 板端（只写 /tmp/course_2-03/）----
sha256sum -c SHA256SUMS.expected
hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin
python3 samples/vision/resnet/runtime/python/main.py --target x5 \
  --asset-id x5:resnet:resnet18_bayese_224x224_nv12.bin \
  --model-path /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG --label-file datasets/imagenet/imagenet_classes.names
hrt_model_exec perf --model_file /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin --frame_count 200 --thread_num 1

hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm
python3 samples/vision/resnet/runtime/python/main.py --target s100 \
  --asset-id s:resnet:s100/resnet18_nashe_224x224_nv12.hbm \
  --model-path /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG --label-file datasets/imagenet/imagenet_classes.names
hrt_model_exec perf --model_file /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm --frame_count 200 --thread_num 1
```

数字来源：本课在电脑上两套工具链转换日志与 RDK X5（X5U）、RDK S100 上的板端实测日志；Model Zoo main `7a97c178`。相似度的解释取自 S 系列文档中心「模型量化与编译」与 X5 文档中心「PTQ 转换步骤」。