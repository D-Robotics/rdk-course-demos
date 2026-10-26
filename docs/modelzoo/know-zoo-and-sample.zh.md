# 认识 RDK Model Zoo

> 所属章节：RDK 小课堂 · 第 2 章 Model Zoo · 第 2 课
>
> 适用板卡：RDK X5、RDK S100、RDK S100P、RDK S600（RDK Model Zoo `main` 分支，仓库 VERSION 2.0.0，提交口径 `7a97c178`；板上浅克隆可能显示 `7a97c17`，同一提交）
>
> 课程目标：理解 main 分支如何用一套代码同时支持四块板；读懂 Sample 的目录、入口和接口；在 X5 与 S100 上跑通 ResNet-18，并读懂 Top-5 结果
>
> 学习方式：概念讲解 + 上板实操（一次只演示一块板）。仓库在板上 `git clone https://github.com/D-Robotics/rdk_model_zoo.git` 后即可运行（工作目录建议 `/tmp/course_2-02/`）。板子需能登录，并能访问 `archive.d-robotics.cc` 以下载制品
>
> 配套课件：[查看中文 HTML 课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/02_know-zoo-and-sample/lesson-2-02.zh.html)

---

## 配套资源

| 资源 | 用途 |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | 本课主角：Sample、制品清单、共用工具（`main`） |
| [ResNet Sample README](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/README_cn.md) | 支持矩阵、快速体验、预期结果与性能参考值 |
| [ResNet 模型制品说明](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/model/README_cn.md) | 制品清单、下载脚本、输入协议 |
| [ResNet Python 运行说明](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/runtime/python/README_cn.md) | `main.py` 参数、结果与集成示例 |
| [发布制品清单与板卡别名](https://github.com/D-Robotics/rdk_model_zoo/tree/main/docs/release) | `models.yaml`（x5 / s）与 `platforms.json` |
| [RDK 文档资源中心](https://developer.d-robotics.cc/rdk_doc_center/) | 各板卡手册与算法工具链文档 |

板端实测环境：RDK X5（SoC 实测 X5U）、RDK S100；Model Zoo `main` 提交口径 `7a97c178`（板上浅克隆可能显示 `7a97c17`）。

---

## 1. 本课要解决什么问题

上一课结论：BPU 只跑量化、编译之后的模型；X5 用 `.bin`，S 系列用 `.hbm`。

拿到模型之后，怎么在板子上跑起来？本课围绕三个问题：

1. **一套代码四块板**：`main` 分支如何同时支持 X5、S100、S100P、S600？
2. **一个 Sample 有什么**：目录、入口和接口在哪里？
3. **怎么跑通并读懂**：在 X5 和 S100 上跑 ResNet-18，看 Top-5。

---

## 2. 完成本课后你能做到什么

- 用 `--target x5|s100|s100p|s600|auto` 选板，并说出制品如何随 target 变化；
- 读懂 Sample README 的支持矩阵，用 `--list-models` / `--dry-run` 在电脑上预演；
- 指出 `model/`、`conversion/`、`runtime/`、`evaluator/`、`test_data/`、`tests/` 各自管什么；
- 顺着 `main.py → cli.py → ResNetClassifier.predict`（`preprocess → infer → postprocess`）读推理路径；
- 在 X5 与 S100 上完成：下载制品 → `model_info` → 跑 `main.py` → 读 Top-5；
- 换板时只改 target、下载参数和制品路径，并避开常见坑（制品混用、target 与硬件不符、缺依赖等）。

---

## 3. Model Zoo 是什么（Part 1）

Model Zoo 是地瓜机器人维护的 **BPU 模型示例集合**。每个 Sample 里通常有：

| 内容 | 作用 |
|---|---|
| 转换好的模型 | 已编译的 `.bin` / `.hbm`，下载即用 |
| 板端推理代码 | Python（部分 Sample 另有 C++）入口，前后处理已写好 |
| 转换与评估 | `conversion/` 转换配方；`evaluator/` 数据集精度 |

当前交付线是 **`main` 分支**（仓库 `VERSION` = 2.0.0）。历史上的 `rdk_x5`、`rdk_s` 分支仍保留，但新开发以 `main` 为准。

### 3.1 仓库四个位置

| 目录 | 放什么 |
|---|---|
| `samples/` | 全部 Sample，按领域分：vision、speech、llm、robotics、vla |
| `utils/` | 共用工具：读图、读标签、Runtime 封装 |
| `docs/release/` | 制品清单 `models.yaml`（x5 / s）和 `platforms.json` |
| `datasets/` | 评估用数据和类别名，如 `imagenet/imagenet_classes.names` |

### 3.2 一套代码，四块板

Sample 代码只有一份。用 `--target` 告诉程序在哪块板上跑：

- 显式：`x5` / `s100` / `s100p` / `s600`
- `auto`：读板卡身份（`/sys/class/boardinfo/soc_name` 或 `/sys/class/socinfo/soc_name`），对照 `docs/release/platforms.json` 认出目标

目标定了，制品也就定了（示意）：

| target | march | ResNet-18 制品（`model/` 下） |
|---|---|---|
| x5 | bayes-e | `resnet18_bayese_224x224_nv12.bin` |
| s100 | nash-e | `s100/resnet18_nashe_224x224_nv12.hbm` |
| s100p | nash-m | `s100p/resnet18_nashm_224x224_nv12.hbm` |
| s600 | nash-p | `s600/resnet18_nashp_224x224_nv12.hbm` |

**代码不变，变的只有 target 和制品。** S100P 不能使用 S100 的文件。`model/` 目录本身不提交二进制，制品用 `download.sh` 按 Manifest 获取。

板卡身份别名（`platforms.json`）：X5 的 `socinfo_names` 为 `x5u` / `x5h` / `x5m`；本课 X5 实测 SoC 为 **X5U**。

---

## 4. 走进 Sample（Part 2）

### 4.1 先判断能不能用

三步都不需要板卡，在电脑上就能做：

1. 看 README 的 **support-matrix**（target × 变体 × 语言）；
2. `python3 …/main.py --list-models --target <目标>` 列出清单里的制品引用；
3. `--dry-run` 只解析选择，不加载模型、不触发板端 SDK。

示例（ResNet）：ResNet-18 在四块板上均有 Python 制品；C++ 只覆盖 S 系列，X5 无 C++ 运行时。YOLOv8 Detect 在 Model Zoo 在线模型目录上，X5、S100、S100P、S600 四块板都有；不是每个模型都覆盖四块板，动手前先在 [Model Zoo 在线模型目录](https://d-robotics.github.io/rdk_model_zoo/)的卡片标签或硬件平台筛选里确认平台与模型，以在线模型目录为准。

### 4.2 六个目录

以 `samples/vision/resnet/` 为例：

| 目录 | 管什么 |
|---|---|
| `model/` | 制品获取（下载脚本 + README），不放二进制 |
| `conversion/` | 导出与量化配方（下一课） |
| `runtime/` | 板上运行代码（`python/`，部分含 `cpp/`） |
| `evaluator/` | 数据集上算精度 |
| `test_data/` | 能直接跑的输入（如 `white_wolf.JPEG`） |
| `tests/` | 行为与数值回归 |

Sample README 使用固定小节（`overview`、`support-matrix`、`prerequisites`、`quickstart`、`expected-results`、`directory`、`entry-points`、`license` 等），学会一个，其他 Sample 就好找。

### 4.3 入口与统一接口

```text
main.py  →  cli.py  →  classify.py（ResNetClassifier）
                         predict() = preprocess → infer → postprocess
```

- `main.py`：取参数、构造模型、调用 `predict`、打印结果；
- `cli.py`：参数、制品选择、列清单、预演、结果展示；
- `ResNetClassifier`：前后处理在 CPU，`infer` 交给 BPU。

换成检测 / 分割等 Sample，公开接口名字仍是 `preprocess` / `infer` / `postprocess` / `predict`。

### 4.4 制品怎么选对

1. **manifest**：`docs/release/{x5,s}/models.yaml`，每个制品一行，下载地址和格式以它为准（本课对应版本头：X5 `1.1.3`，S `1.1.2`）。
2. **asset-id 与 model-path**：asset-id 是清单里的完整名字，model-path 是本地文件，**必须配对**——只看文件名分不出输入协议。
3. **运行前校验**：请求的 target 与检测到的硬件不一致，直接报错，不会硬跑。

### 4.5 两种输入协议

| | RDK X5 | S100 / S100P / S600 |
|---|---|---|
| 协议 | packed NV12（`--dry-run` 字段 `packed_nv12`） | split NV12（`split_nv12`） |
| 输入 | 单个张量 `data`，一维 uint8；224×224 → 75,264 字节 | `data_y (1,224,224,1)` + `data_uv (1,112,112,2)` |
| 制品 | `.bin` | `.hbm` |

你不用自己拼；Sample 的前处理会按绑定模型准备数据。输入张量用 `model_info` 核对；输入协议用 `--dry-run` 看。

---

## 5. 上板实操（Part 3）

> 工作目录约定：板上只写 `/tmp/course_2-02/`。  
> **准备**：在板上进入工作目录，执行 `git clone https://github.com/D-Robotics/rdk_model_zoo.git`，再进入仓库根目录即可后续操作。制品下载走 `archive.d-robotics.cc`，`download.sh` 正常。  
> 一次只看一块板。命令均在仓库根目录执行。

### 5.0 获取仓库

```bash
cd /tmp/course_2-02
git clone https://github.com/D-Robotics/rdk_model_zoo.git
cd rdk_model_zoo
```

如果板子网络访问不了 GitHub，也可以在电脑上 clone 后用 `scp` 拷到板上的 `/tmp/course_2-02/`。

### 5.1 认清板卡

```bash
cat /sys/class/boardinfo/soc_name \
  /sys/class/socinfo/soc_name \
  2>/dev/null | tr -d '\0'
```

保留 `2>/dev/null`：X5 没有 `boardinfo`，S100 没有 `socinfo`；去掉后会出现一行 `No such file or directory`。

| 板 | 实测 `soc_name` |
|---|---|
| X5 | **X5U** |
| S100 | **S100** |

X5 也可能是 X5H / X5M，以板上读数为准。

### 5.2 下载制品

```bash
bash samples/vision/resnet/model/download.sh x5 18
# 或
bash samples/vision/resnet/model/download.sh s100 18
```

| 板 | 制品 | 大小（实测） |
|---|---|---|
| X5 | `samples/vision/resnet/model/resnet18_bayese_224x224_nv12.bin` | 约 **11.08 MB**（11 081 728 B） |
| S100 | `samples/vision/resnet/model/s100/resnet18_nashe_224x224_nv12.hbm` | 约 **12.19 MB**（12 193 864 B） |

### 5.3 查看模型信息

```bash
hrt_model_exec model_info --model_file <模型文件>
```

| 板 | `model_info` 要点（实测） | `input_protocol`（`--dry-run`） |
|---|---|---|
| X5 | 单输入 `data`，NV12，`(1,3,224,224)`，aligned 75,264 字节 | `packed_nv12` |
| S100 | 双输入 `data_y (1,224,224,1)` U8 + `data_uv (1,112,112,2)` U8 | `split_nv12` |

`model_info` 的描述行可能带有构建机器的路径，截图分享前请留意（可裁掉该行）。

### 5.4 运行 Sample

短写法（制品已在默认位置时；本课实测 exit 0）：

```bash
python3 samples/vision/resnet/runtime/python/main.py --target x5 --variant 18
python3 samples/vision/resnet/runtime/python/main.py --target s100 --variant 18
```

默认测试图为随仓 `white_wolf.JPEG`，标签为 `datasets/imagenet/imagenet_classes.names`。完整写法见 Sample README（`--asset-id` + `--model-path` 配对）。四种方式（`--variant 18`、完整写法、`main.py` 默认参数、`run.sh`）在本课实测中 Top-5 一致；`--target auto` 在 X5、S100 上均可自动识别。

### 5.5 怎么读结果

每行三项：`class`（ImageNet-1k 编号）、`label`、`score`（softmax 后）。

实测 Top-5（仓库提交口径 `7a97c178`；顺序与 README 预期一致）：

| 名次 | 类别 | X5 分数 | S100 分数 |
|---|---|---|---|
| 1 | white wolf（class 270） | **0.998090** | **0.998109** |
| 2 | timber wolf | 0.000592 | 0.000565 |
| 3 | ice bear | 0.000189 | 0.000185 |
| 4 | Arctic fox | 0.000126 | 0.000137 |
| 5 | Samoyed | 0.000080 | 0.000087 |

README 参考值：随仓 `white_wolf.JPEG` 的 Rank-1 为 white wolf，X5 参考分数 0.998；ImageNetV2 MatchedFrequency 上 ResNet-18 Top-1：FP32 59.35%，X5 板端 58.91%，S100 板端 58.79%（来源：Sample README「性能数据」）。

### 5.6 跑 Sample 四步（小结）

1. 下载制品：`download.sh <target> 18`
2. `hrt_model_exec model_info`
3. `main.py --target <板卡>`
4. 读 Top-5，对照 README

换板：只改 target 和制品，四步不变。

### 5.7 可选：C++（S 系列；本课在 S100 上实测）

`bash samples/vision/resnet/runtime/cpp/run.sh` **默认输入是 `zebra_cls.jpg`**（Top-1 zebra）。要看 white wolf 必须加：

```bash
bash samples/vision/resnet/runtime/cpp/run.sh \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG
```

X5 无 C++ 运行时。

### 5.8 补充：perf

单次 `hrt_model_exec perf --frame_count 200 --thread_num 1`（无输入文件）：X5 平均约 3.144 ms / 316.6 FPS；S100 平均约 0.628 ms / 1546.9 FPS。属单次测量，数值随运行有波动；量级可对照 Sample README 参考值（X5 2.740 ms、S100 0.631 ms）。

---

## 6. 换板与避坑（Part 4）

### 6.1 换板只改三处

1. `--target`：`x5` → `s100` / `s100p` / `s600`，或 `auto`
2. `download.sh` 的第一个参数同步改
3. S 系列制品在 `s100/`、`s100p/`、`s600/` 子目录，路径跟着变

测试图片、标签文件和其他参数不用动。

### 6.2 常见坑

跑不起来时，先查这五项。

| 坑 | 说明 |
|---|---|
| S100P 不能用 S100 制品 | march 不同（nash-m vs nash-e） |
| target 与硬件不符 | 运行前校验直接报错 |
| 老镜像缺 PyYAML / Pillow | **老镜像或精简镜像可能出现**；两块板上都已经具备，未装任何依赖 |
| 推理不自动下载 | 先跑 `download.sh` |
| C++ 默认 zebra | 看白狼必须加 `--test-img` |

---

## 7. 新手规则

1. 先看支持矩阵，再用 `--list-models` / `--dry-run` 预演。
2. 制品按板卡命名，不跨板复用。
3. `asset-id` 与 `model-path` 配对；只看文件名不够。
4. 板上用 `git clone` 获取仓库；工作目录只写 `/tmp/course_2-02/`。
5. 读板卡身份时保留 `2>/dev/null`。

---

## 8. 常见问题

**Q. 板上 `git clone` 失败怎么办？**  
A. 主流程仍是板上直接 `git clone`。若当前网络访问不了 GitHub，可以在能访问的电脑上 clone（可用 sparse / 浅克隆减小体积），再 `scp` 到 `/tmp/course_2-02/`——这只是可选备选，不是默认步骤。

**Q. `git rev-parse --short HEAD` 为什么是 `7a97c17` 不是 `7a97c178`？**  
A. 浅克隆 / sparse 仓库下 git 可能缩成 7 位；完整克隆为 8 位 `7a97c178`。完整哈希相同：`7a97c1780b0cfa131ff0007d662e255e5e41c12e`。统一写作 **7a97c178**；板上可能显示 `7a97c17`，是同一提交。

**Q. 为什么要保留 `2>/dev/null`？**  
A. X5 无 `boardinfo`，S100 无 `socinfo`；保留后各自正常输出，去掉会多一行报错。

**Q. 系统镜像版本怎么写？**  
A. 板上可读 `/etc/version`：本课实测 X5 为 `3.5.0-beta`，S100 为 `4.0.5-Beta`，两者目前都是 Beta。

---

## 本课小结

- `main` 用 `--target` 选板，一套代码对应四块板的制品；
- Sample 六个目录，入口是 `main.py`、`cli.py` 与模型类；
- 在 X5（SoC X5U）与 S100 上跑通 ResNet-18：Top-1 均为 white wolf（0.998090 / 0.998109）。

下一课（2-03）：对照 Sample 量化——以 ResNet 为例，从 ONNX、校准数据到 `.bin` / `.hbm`，把 PTQ 完整走一遍，再把产物放回 Sample，用今天学的方法上板验证。

---

## 完成检查

- [ ] 能说出 `--target` 与制品命名的对应关系
- [ ] 能指出 Sample 六个目录各自职责
- [ ] 在至少一块板上完成下载 → `model_info` → `main.py` → 读 Top-5
- [ ] 知道换板改哪三处，以及板上用 `git clone` 获取仓库

---

## 拓展练习

1. 在同一块板上对 ResNet-34 / 50 重复四步，对照 `--list-models`。
2. 用 `--dry-run --target s600` 预演，观察打印出的 `asset_id`、`model_path_exists`（未下载时为 False）。
3. （S100）对比 C++ 默认 zebra 与加 `--test-img` 白狼的输出格式差异。

---

## 附录：命令速查

```bash
# 获取仓库（板上主流程）
cd /tmp/course_2-02
git clone https://github.com/D-Robotics/rdk_model_zoo.git
cd rdk_model_zoo

# 身份（保留 2>/dev/null）
cat /sys/class/boardinfo/soc_name /sys/class/socinfo/soc_name 2>/dev/null | tr -d '\0'

# 下载
bash samples/vision/resnet/model/download.sh x5 18
bash samples/vision/resnet/model/download.sh s100 18

# 模型信息
hrt_model_exec model_info --model_file samples/vision/resnet/model/resnet18_bayese_224x224_nv12.bin
hrt_model_exec model_info --model_file samples/vision/resnet/model/s100/resnet18_nashe_224x224_nv12.hbm

# 预演（可在电脑）
python3 samples/vision/resnet/runtime/python/main.py --list-models --target auto
python3 samples/vision/resnet/runtime/python/main.py --dry-run --target x5
python3 samples/vision/resnet/runtime/python/main.py --dry-run --target s100

# 推理
python3 samples/vision/resnet/runtime/python/main.py --target x5 --variant 18
python3 samples/vision/resnet/runtime/python/main.py --target s100 --variant 18

# S100 C++ 看白狼
bash samples/vision/resnet/runtime/cpp/run.sh \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG
```

数字来源：本课在 RDK X5（X5U）、RDK S100 上实测（Model Zoo main `7a97c178`）；README 参考值见 Sample `README_cn.md`「性能数据 / 预期结果」。
