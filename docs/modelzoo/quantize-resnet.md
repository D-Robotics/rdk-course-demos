# ResNet Quantization Hands-on

> Course: RDK Classroom · Chapter 2 Model Zoo · Lesson 3
>
> Boards covered: RDK X5 (`bayes-e`, `hb_mapper` → `.bin`) and RDK S100 (`nash-e`, `hb_compile` → `.hbm`); S100P (`nash-m`) and S600 (`nash-p`) also use `hb_compile` and are only mentioned in the text. RDK Model Zoo `main` branch, repository VERSION 2.0.0, commit `7a97c178`
>
> Course goal: Using `samples/vision/resnet/conversion` as the reference, run one complete PTQ (post-training quantization) of ResNet-18 on your computer: export ONNX → prepare calibration data → write the yaml → convert once with the X5 toolchain and once with the S-series toolchain → read the similarity → put the artifacts back into the Sample and verify them on RDK X5 and RDK S100
>
> Learning format: concept explanation + conversion on the computer + verification on the board (one board at a time)
>
> Video: <!-- TODO: add the video link after publishing -->**Coming soon**
>
> Slides: [Open English HTML slides on GitHub](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/03_quantize-resnet/lesson-2-03.html) · [中文课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/03_quantize-resnet/lesson-2-03.zh.html)

---

## Companion resources

| Resource | Purpose |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | The star of this lesson: `samples/vision/resnet/conversion/` (`export.py`, `ptq_x5.yaml`, `ptq_s.yaml`) and `utils/tools/classification/workflow.py` |
| [ResNet Sample README](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/README.md) | Support matrix, entry to the conversion recipe, reference accuracy |
| [S series: the hb_compile tool](https://developer.d-robotics.cc/oe_s_doc/en/guide/ptq/ptq_tool/hb_compile) | Conversion tool for S100 / S100P / S600 |
| [S series: model quantization and compilation](https://developer.d-robotics.cc/oe_s_doc/en/guide/ptq/ptq_usage/quantize_compile) | The conversion flow and how to read the similarity information |
| [X5: hb_mapper checker](https://developer.d-robotics.cc/oe_x5_doc/en/oe_mapper/source/ptq/ptq_tool/hb_mapper/hb_mapper_checker.html) | X5 checking tool |
| [X5: hb_mapper makertbin](https://developer.d-robotics.cc/oe_x5_doc/en/oe_mapper/source/ptq/ptq_tool/hb_mapper/hb_mapper_makertbin.html) | X5 conversion tool |
| [X5: PTQ conversion steps](https://developer.d-robotics.cc/oe_x5_doc/en/oe_mapper/source/ptq/ptq_usage/ptq_usage.html) | Overview of the X5 flow |
| [RDK documentation center](https://developer.d-robotics.cc/rdk_doc_center/) | Board manuals and toolchain release notes; for toolchain versions, follow the toolchain documentation |

Test environment: x86_64 Linux + Docker on the computer; RDK X5 (SoC X5U) and RDK S100 on the board side; Model Zoo `main` at commit `7a97c178`.

---

## 1. What problem does this lesson solve?

In the last lesson you ran the Sample on the board: download the released artifact → `model_info` → `main.py` → read the Top-5. That `.bin` / `.hbm` had been converted by someone else.

If you want to put **your own model** into a Sample, or want to know how the released artifacts are produced, you have to run the conversion yourself. In this lesson we take the same ResNet-18 and, following the Sample's `conversion/` directory, do three things:

1. **Turn the floating-point model into ONNX, then prepare calibration data**;
2. **Write the yaml and convert once in each toolchain, X5 and S series**, and learn to read the similarity;
3. **Put the artifacts back into the Sample, verify them on the board**, and compare them with the released artifacts.

---

## 2. What You Will Be Able to Do

- Name the five PTQ stages (floating-point model → validation → calibration data → quantization and compilation → evaluation) and which directory each step lives in;
- Read `ptq_x5.yaml` / `ptq_s.yaml`: `march`, `input_type_rt: nv12` vs. `input_type_train: rgb`, `norm_type` + `mean_value` / `scale_value` (normalization compiled into the model), `input_space_and_range: bt601_video`, `cal_data_dir`, `calibration_type`, and the compiler parameters;
- Tell apart the tools and images of the X5 (`hb_mapper checker` + `makertbin`, X5 OE image, produces `.bin`) and the S series (`hb_compile`, S OE image, produces `.hbm`);
- Understand `Cosine Similarity` (X5) and `Calibrated Cosine` / `Quantized Cosine` (S series) in the logs, and know that cosine similarity is only a reference — task accuracy is what counts;
- Rename the artifacts to the release names and verify white wolf on the X5 and the S100 with the method from the last lesson.

---

## 3. The PTQ big picture and the conversion environment (Part 1)

### 3.1 Conversion has to solve two things

1. **Input data handling**: at runtime on the board the input is NV12 (`input_type_rt: nv12`); during training it was RGB (`input_type_train: rgb`). Subtracting the mean and dividing by the standard deviation is not done on the board but **compiled into the model**: the yaml's `mean_value` / `scale_value` correspond to the common ImageNet `mean = [0.485, 0.456, 0.406] × 255` and `scale = 1 / (255 × std)`.
2. **Model optimization and compilation**: turn the ONNX into an INT8 model the BPU can run, using the calibration data to decide each layer's quantization parameters.

The five PTQ stages and their directories (the Sample's `conversion/`):

| Stage | What it does | In this lesson |
|---|---|---|
| Floating-point model | Get the weights, export ONNX | `workflow.py fetch`, `export.py` |
| Validation | Compare with PyTorch, tool check | `export.json`, `hb_mapper checker` |
| Calibration data | A batch of representative inputs | `workflow.py calibrate` |
| Quantization and compilation | Calibrate + quantize + compile | `hb_mapper makertbin` / `hb_compile` |
| Evaluation | Compare accuracy on a dataset | `evaluator/` (this lesson demos a subset and explains how to measure; no full run) |


### 3.2 The two toolchain images

Both toolchains are installed inside Docker images; you do not need to install the OE directly on your computer:

| | X5 | S series (S100 / S100P / S600) |
|---|---|---|
| Image | `local/rdk-x5-oe:v1.2.8-server` (X5 also has CPU/GPU images; this lesson uses a local server image) | Demo in this lesson: `…_s100_s600_gpu:v3.7.0`; the same version also has `…_s100_s600_cpu:v3.7.0` (`run_docker.sh data/ cpu`) |
| Conversion commands | `hb_mapper checker`, `hb_mapper makertbin` | `hb_compile` |
| Final artifact | `.bin` | `.hbm` |
| Measured tool versions | hb_mapper 1.24.3, hbdk 3.49.15, horizon_nn 1.1.0 | hb_compile 3.5.3, hbdk4 4.7.5, hmct 2.6.5 |

> The repository README lists the X5 image as `…/ai_toolchain_ubuntu_20_x5_gpu:v1.2.8`; this lesson uses the locally available `local/rdk-x5-oe:v1.2.8-server`, whose tool versions match (hb_mapper 1.24.3, same version number v1.2.8). We did not compare the two images file by file, so we draw no conclusion about whether they are identical. For toolchain versions, always follow the toolchain documentation.

### 3.3 How to write docker run

```bash
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g \
  -v "$WORK:$WORK" -w "$WORK/x5" local/rdk-x5-oe:v1.2.8-server \
  bash -c '<command>'
```

- `--entrypoint ''`: running `docker run … bash -c '…'` directly failed in our tests with `cannot execute binary file` (exit code 126); with `--entrypoint ''` it works — **this is a pitfall we actually hit**;
- `-v "$WORK:$WORK"`: mount the working directory at the same path, so absolute paths in the yaml are the same inside and outside the container;
- If you have an NVIDIA GPU, `--gpus all` is an optional speed-up and is **not** required for the S series; for PTQ the CPU image of the same version is enough (see §5.3). The demo in this lesson keeps the measured path of the GPU image + `-e CUDA_VISIBLE_DEVICES=-1`.

### 3.4 Working directory

Put `$WORK` **outside the repository**, for example `~/work/course_2-03/resnet-18`, with `weights/`, `export/`, `x5/` and `s100/` under it. Conversion outputs are large (intermediate ONNX files of tens of MB); do not put them in the Sample directory.

---

## 4. ONNX and calibration data (Part 2)

### 4.1 Export ONNX

```bash
# cwd: repository root (rdk_model_zoo)
python3 utils/tools/classification/workflow.py fetch --model resnet18 --output $WORK/weights

python3 samples/vision/resnet/conversion/export.py --model resnet18 \
  --source-dir $WORK/weights \
  --images samples/vision/resnet/test_data/white_wolf.JPEG samples/vision/resnet/test_data/zebra_cls.jpg \
  --opset 11 --simplify --output $WORK/export
```

- `fetch` downloads timm weights at a fixed revision (`timm/resnet18.a1_in1k`), so everyone gets the same weights;
- `export.py --opset 11 --simplify` writes `model.onnx` (input `data` float32 `[1,3,224,224]`, output `logits` `[1,1000]`) and `export.json`;
- During export, two test images are compared against PyTorch: measured maximum absolute error **9.5e-06** (white_wolf) and **6.2e-06** (zebra); the Top-5 of the white wolf image is 270, 269, 279, 296, 272;
- The model has 11 689 512 parameters and 1 814 073 344 Conv / Linear multiply-accumulates.

> Source of the numbers: the export log on the computer and `export.json` from this lesson. Download took about 27.6 s, export about 3.2 s.


### 4.2 Calibration data

Calibration gives the tool a batch of "representative inputs". The Sample's recipe: a fixed set of 200 images, preprocessed with "resize the short side to 235 + 224 center crop" (the same geometry as at runtime; resizing uses antialiased bicubic).

```bash
# Run once for X5 and once for S100 (this lesson only does these two targets)
python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform x5 \
  --manifest $CAL/manifest.json --images-root $CAL \
  --expected-images 200 --evaluation-manifest $EVAL/manifest.json \
  --output $WORK/x5/calibration
python3 utils/tools/classification/workflow.py calibrate --model resnet18 --platform s100 \
  --manifest $CAL/manifest.json --images-root $CAL \
  --expected-images 200 --evaluation-manifest $EVAL/manifest.json \
  --output $WORK/s100/calibration
```

The two targets write **different content** (source: the Sample's `conversion/README_cn.md`):

| | X5 | S100 |
|---|---|---|
| File | `.rgb`: headerless little-endian float32, **raw [0,255] RGB** (the calibration loader converts it to NV12) | `.npy`: float32, **already normalized for the ONNX input** |
| Size per image (measured) | 602 112 bytes (224×224×3×4) | 602 240 bytes (the same data + a 128-byte `.npy` header) |
| `cal_data_type` in the yaml | `float32` | `float32` (the S100 log notes this parameter is deprecated and suggests npy) |

> Measured: 200 images per target, about 1.3 s each; the 200 X5 images total 115 MB.
>
> **About the calibration image source**: the calibration images in this lesson come from one shard of the `detection-datasets/coco` dataset on Hugging Face (40 shards in total, one chosen with seed 42), from which 200 images are drawn with seed 42; the manifest records each image's sha256. We did not check whether these are the same calibration images used for the released artifacts, so small differences between your own numbers and the released artifacts are normal.
>
> **`--evaluation-manifest`**: the script uses it to check that "calibration images must not appear in the evaluation set". This lesson only downloaded the first 1 834 images of ImageNetV2 (the full set is 10 000), so the check covers only that part, and this time we **cannot** claim "no overlap between calibration images and the evaluation set"; we also did not use it for accuracy evaluation in this lesson.

**Key point**: calibration data must match the deployment preprocessing — geometry (resize + crop), color format and where normalization happens must all be the same, otherwise the calibrated quantization parameters will not fit the real input.

---

## 5. Write the yaml and compile: X5 and S series (Part 3)

### 5.1 Reading the yaml field by field

The Sample's `ptq_x5.yaml` / `ptq_s.yaml` use placeholders (`@WORK@`, `@SIZE@`, `@TARGET@`, `@MARCH@`); fill in the actual paths with `sed`:

```bash
export SIZE=224
sed -e "s#@WORK@#$WORK#g" -e "s#@SIZE@#$SIZE#g" \
  $REPO/samples/vision/resnet/conversion/ptq_x5.yaml > $WORK/x5/config.yaml
sed -e "s#@WORK@#$WORK#g" -e "s#@TARGET@#s100#g" -e "s#@MARCH@#nash-e#g" -e "s#@SIZE@#$SIZE#g" \
  $REPO/samples/vision/resnet/conversion/ptq_s.yaml > $WORK/s100/config.yaml
```

The X5 yaml actually used in this lesson (excerpt, paths replaced with `$WORK`):

```yaml
model_parameters:
  onnx_model: $WORK/export/model.onnx
  march: bayes-e
  working_dir: $WORK/x5/build
  output_model_file_prefix: resnet_x5
input_parameters:
  input_name: data
  input_type_rt: nv12            # input at runtime on the board
  input_type_train: rgb          # input during training
  input_layout_train: NCHW
  input_shape: 1x3x224x224
  norm_type: data_mean_and_scale # normalization compiled into the model
  mean_value: 123.675 116.28 103.53
  scale_value: 0.0171247538317 0.0175070028011 0.0174291938998
  input_space_and_range: bt601_video   # OpenCV's I420→NV12 is BT.601, limited range
calibration_parameters:
  cal_data_dir: $WORK/x5/calibration/data
  cal_data_type: float32
  calibration_type: default
  preprocess_on: false           # calibration data is already preprocessed
compiler_parameters:
  optimize_level: O3
  compile_mode: latency
  core_num: 1
  input_source:
    data: pyramid
```

| Field | Meaning |
|---|---|
| `march` | Target architecture: `bayes-e` for X5; `nash-e` for S100 (`nash-m` for S100P, `nash-p` for S600) |
| `input_type_rt` / `input_type_train` | `nv12` at runtime, `rgb` in training; the tool adds the color conversion in front of the model |
| `norm_type` + `mean_value` / `scale_value` | Compile "subtract the mean, multiply by scale" into the model, so the board doesn't need to do it |
| `input_space_and_range` | `bt601_video`: the color space and range of NV12, which must match the runtime preprocessing |
| `cal_data_dir` | Directory of the calibration data |
| `calibration_type: default` | With `default`, the tool searches automatically among candidates (listed below); this lesson uses the default and leaves comparing calibration methods to the next lesson |
| `optimize_level` / `compile_mode` / `core_num` | Compiler parameters: `O3` for X5 and `O2` for S100 in this lesson; both use `compile_mode: latency` and `core_num: 1` |
| `input_source` (X5) | `data: pyramid`: the input comes from the pyramid, matching `HB_DNN_INPUT_FROM_PYRAMID` in `model_info` |

The S100 yaml has the same structure; the main differences are `march: nash-e`, `optimize_level: O2`, `.npy` calibration data, and a set of extra options that are empty by default (`debug_mode`, `output_nodes`, etc.). The S100 log has two WARNINGs: `norm_type` is deprecated (whether to normalize is decided by whether `mean` / `scale` / `std` are filled in), and `cal_data_type` is deprecated (npy is suggested instead); this lesson uses the Sample's yaml as is.

> Note: the header of the Sample's yaml states that its compiler parameters are exactly the ones used for the released artifacts; only the paths and placeholders differ.

**What does `calibration_type: default` actually choose?** With `default`, both toolchains search automatically over the same set of candidates (measured from the logs): the `max` and `kl` methods, `max_percentile` at 0.99995 and 1.0, with `per_channel` and `asymmetric` each tried on and off; the target is a model-level cosine similarity of 0.995. The two sides chose differently:

| | X5 | S100 |
|---|---|---|
| Choice in the log | `Select max-percentile:percentile=0.99995 method` | `Select kl:num_bin=1024,max_num_bin=16384 method` |

So with "the same yaml style + the same data", different toolchains can pick different quantization methods; this is one reason the similarities of the two sides cannot be compared directly.

### 5.2 X5: `hb_mapper checker` + `makertbin`

```bash
# Run inside the X5 image, cwd = $WORK/x5
hb_mapper checker --model-type onnx --march bayes-e \
  --model $WORK/export/model.onnx --input-shape data 1x3x224x224

hb_mapper makertbin --config config.yaml --model-type onnx      # → build/resnet_x5.bin
```

- `checker` first checks which operators in the model can go to the BPU and which fall back to the CPU; measured 5.7 s. Its similarity column shows `--` — **checker does not compute similarity**.
- `makertbin` does calibration, quantization and compilation; measured **32.8 s**. When finished it writes `build/resnet_x5.bin` (11 081 570 bytes) plus a set of intermediate files (`*_original_float_model.onnx`, `*_optimized_float_model.onnx`, `*_calibrated_model.onnx`, `*_quantized_model.onnx`, `*_quant_info.json`).
- The log of the whole run is in `hb_mapper_makertbin.log`.

### 5.3 S series: `hb_compile` (demonstrated on S100)

```bash
# Demo path in this lesson (GPU image + forced CPU); cwd = $WORK/s100
# Also fine: the CPU image of the same version, without --gpus / CUDA_VISIBLE_DEVICES
docker run --rm --entrypoint '' --gpus all -e CUDA_VISIBLE_DEVICES=-1 \
  --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/s100" \
  registry.d-robotics.cc/deliver/ai_toolchain_ubuntu_22_s100_s600_gpu:v3.7.0 \
  bash -c 'hb_compile --config config.yaml'                     # → build/resnet_s100.hbm
```

- One `hb_compile` command covers optimization, calibration, quantization and compilation; on success the log ends with `Successfully compile the hbm model`; measured **217.5 s** (about 3.6 minutes). The artifact is `build/resnet_s100.hbm` (12 193 304 bytes); intermediate files include `*_calibrated_model.onnx`, `*_quantized_model.bc`, etc.
- S100P (`nash-m`) and S600 (`nash-p`) use the same tool and the same yaml; just change `march` (as noted in the yaml header); **this lesson only converted for S100 — S100P and S600 were neither converted nor demonstrated**.

> **About CPU / GPU (toolchain documentation and our measurements)**
> S100/S600 OE V3.7.0 **provides both a CPU Docker and a GPU Docker**; for PTQ alone, the CPU image is enough (e.g. `run_docker.sh data/ cpu`). The GPU image is only an optional speed-up when a usable NVIDIA GPU is present; it is **not** a prerequisite for PTQ on the S series.
>
> The demo in this lesson keeps the GPU-image path that was recorded. On this machine, we tested four ways of running the **GPU image**:
>
> | Variant (all inside the GPU image) | Result |
> |---|---|
> | Without `--gpus` | Process crashes, exit code 139 |
> | `--gpus all` | `cudaErrorInvalidDevice` during calibration, exit code 255 |
> | `--gpus all -e CUDA_VISIBLE_DEVICES=0` | Same, exit code 255 |
> | `--gpus all -e CUDA_VISIBLE_DEVICES=-1` | **Conversion succeeds**, forced onto the CPU |
>
> The table above only shows what happens "when the GPU image is misused or GPU is forced"; it **cannot** be extended to "you can't convert without a GPU" — the right fix is to use the CPU image of the same version. The successful log in this lesson contains 14 `CUDA failure` / `EP Error` messages and `Falling back to ['CPUExecutionProvider']`: these mean the container tried the GPU, failed, and automatically fell back to the CPU; they **do not affect the result** — look for `Successfully compile the hbm model` at the end. Don't describe the fallback as a failure. We did not convert on a computer with a usable GPU, so we do not compare GPU and CPU times.

### 5.4 A one-page preview: why the NV12 configuration

We use the **released NV12 configuration** here because the artifacts go back into the Sample, and the Sample only accepts NV12 input. What the same ResNet looks like with a feature-map input without preprocessing is covered side by side in 2-05; how to choose the input type for your own new model is in 2-06.

---

## 6. Similarity check, then back to the Sample for on-board verification (Part 4)

### 6.1 Reading the similarity

**X5 (`makertbin` log, measured)**

```text
Output      Cosine Similarity  L1 Distance  L2 Distance  Chebyshev Distance
logits      0.999941           0.118689     0.004645     0.535569
```

**S100 (`hb_compile` log, measured)**

```text
| Output     | Calibrated Cosine | Quantized Cosine |
| logits     | 0.999913          | 0.999856         |
```

| | X5 | S100 |
|---|---|---|
| Cosine of output `logits` | 0.999941 | Calibrated 0.999913 / Quantized 0.999856 |
| `GlobalAveragePool` node | 0.997738 | 0.997083 / 0.995166 |
| Lowest node cosine | 0.996568 | Quantized 0.973402 |


- How the S-series documentation defines the two columns: `Calibrated Cosine` is the cosine between corresponding nodes of the optimized floating-point model and the calibrated model; `Quantized Cosine` is the cosine between corresponding nodes of the optimized floating-point model and the quantized fixed-point model (`quantized_model.bc`). In the X5 documentation, `Cosine Similarity` is the cosine between the original floating-point model and the quantized model at that node's output. (Sources: S series "Model quantization and compilation" and X5 "PTQ conversion steps", checked against the RDK documentation center.)
- Both documents state that cosine similarity is only a reference indicating the stability of the quantized data and has no clear direct relationship with model accuracy; in general, an output-node similarity below 0.8 means a noticeable accuracy loss, and full accuracy needs a model accuracy analysis.
- The X5 and S100 tables have **different formats and different definitions** (X5 has a single `Cosine Similarity` column; S100 has two columns, `Calibrated` / `Quantized`; and, as §5.1 explains, the two sides chose different calibration methods). Explain them separately, and don't compare the two numbers as if they were the same measure to decide "which is better".
- Both output similarities are above 0.999, far above 0.8, so nothing triggered further investigation; but "high similarity" does not mean "no accuracy loss" — task accuracy is what counts.

> The logs also contain the compiler's performance estimates (X5: `FPS=428.67`, `latency = 2332.8 us`; S100: `FPS=2430.87`, `latency = 411.4 us`). **These are compiler estimates, not on-board measurements**; always call them "compiler estimates" when teaching. The board numbers in §6.4 below are the real run times. The X5 `checker` table also has an estimated FPS, which we do not quote.

### 6.2 Rename the artifacts to the release names

The yaml's `output_model_file_prefix` is `resnet_x5` / `resnet_s100`, so the tools directly produce `resnet_x5.bin` / `resnet_s100.hbm`. Before putting them back into the Sample, rename them following the release naming rule (with `bayese` / `nashe`, `224x224`, `nv12`):

| Target | Tool output | Renamed to | sha256 (first 8 … last 6) |
|---|---|---|---|
| X5 | `resnet_x5.bin` | `resnet18_bayese_224x224_nv12.bin` | `7f8fa575…c3374a` |
| S100 | `resnet_s100.hbm` | `resnet18_nashe_224x224_nv12.hbm` | `a506767b…635c77` |

Only the file name changes; the content stays the same.

Note: renaming **only changes the file name**, not the name recorded inside the model. So in `hrt_model_exec model_info`, your own models are named `resnet_x5` / `resnet_s100`, while the released artifacts are `resnet18_224_x5` / `resnet18_224_s100`. Also, your own artifacts and the released ones are **not byte-for-byte identical** (both size and sha256 differ: X5 released artifact 11 081 728 bytes (from the last lesson's records), own 11 081 570 bytes; S100 released artifact 12 193 864 bytes (same source), own 12 193 304 bytes), so the numbers are "close", not "identical".

### 6.3 Put the artifacts back into the Sample and verify on the board

On the board, follow the last lesson's approach: prepare the repository under `/tmp/course_2-03/`, copy the artifacts onto the board, and **look at one board at a time**.

```bash
# First check that the artifacts are not corrupted (OK on both boards)
sha256sum -c SHA256SUMS.expected
```

> How we got the repository and the artifacts onto the board in this lesson: the repository was prepared on the computer (sparse + shallow clone), the artifacts were converted on the computer, and both were copied to the board with `scp`. **This time we did not retry `git clone` on the board**, so we draw no conclusion about whether the board can reach GitHub. The normal way is still to `git clone` directly on the board; `scp` is the fallback.

**Step 1: check inputs and outputs with `model_info`**

```bash
hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_bayese_224x224_nv12.bin   # X5
hrt_model_exec model_info --model_file /tmp/course_2-03/own/resnet18_nashe_224x224_nv12.hbm   # S100
```

| Board | `model_info` of your own artifact (measured) |
|---|---|
| X5 | Model name `resnet_x5`; single input `data`, `HB_DNN_IMG_TYPE_NV12`, `(1,3,224,224)`, source `HB_DNN_INPUT_FROM_PYRAMID`, 75 264 bytes; output `logits (1,1000,1,1)` F32 |
| S100 | Model name `resnet_s100`; two inputs `data_y (1,224,224,1)` + `data_uv (1,112,112,2)` U8; output `logits` F32 |

The input structure is the same as the released artifacts (X5: a single NV12 tensor; S100: Y and UV separate); only the model name differs. The `input_protocol` shown by `--dry-run`: X5 `packed_nv12`, S100 `split_nv12`.


**Step 2: check the Top-5 with `main.py`**

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

`--asset-id` and `--model-path` must be paired: the asset-id tells the program which input protocol to prepare the data for, and the model-path tells it which file to use. Your own artifact keeps the released artifact's asset-id; only `--model-path` changes.


**Measured results on the white wolf image (own vs. released)**

| Rank | X5 own | X5 released | S100 own | S100 released |
|---|---|---|---|---|
| 1 | white wolf **0.997102** | white wolf 0.998090 | white wolf **0.998149** | white wolf 0.998109 |
| 2 | timber wolf 0.000710 | timber wolf (same order) | timber wolf 0.000555 | timber wolf 0.000565 |
| 3 | ice bear 0.000408 | ice bear (same order) | **Arctic fox** 0.000187 | ice bear 0.000185 |
| 4 | Arctic fox 0.000203 | Arctic fox (same order) | **ice bear** 0.000174 | Arctic fox 0.000137 |
| 5 | Samoyed 0.000096 | Samoyed (same order) | **coyote** 0.000063 | Samoyed 0.000087 |

Zebra image: X5 own Top-1 class 340 zebra **0.999962** (released 0.999974); S100 own **0.999976** (released 0.999971).

How to read it:

- **Top-1 is white wolf / zebra everywhere, with scores of 0.997–0.9999**; your own artifacts pass verification.
- **X5**: the Top-5 classes and order of your own artifact and the released artifact are exactly the same.
- **S100**: the first two match the released artifact; ranks 3–5 all score only around one in ten thousand, and the order and a few classes differ slightly between own and released — the own artifact ranks Arctic fox above ice bear, and rank 5 is coyote instead of Samoyed, all with score differences below 1e-4. The own artifact's Top-5 is exactly the same as the **floating-point ONNX** Top-5 (270, 269, 279, 296, 272). Conclusion: **when verifying a quantization result, look at the Top-1 and the order of magnitude of the scores; don't require "all five classes to match"**. We did no controlled experiment on the cause of the differences in these ranks, so we draw no conclusion.

### 6.4 Board speed

```bash
hrt_model_exec perf --model_file <artifact> --frame_count 200 --thread_num 1
```

| Board | Own artifact, latency of 3 runs | Own artifact, FPS of 3 runs (summary line) | Released artifact, 1 run |
|---|---|---|---|
| X5 | 3.108 / 3.066 / 3.118 ms | 320.4 / 325.0 / 319.6 | 3.112 ms, 320.1 FPS |
| S100 | 0.638 / 0.630 / 0.630 ms | 1524.2 / 1543.4 / 1541.5 | 0.641 ms, 1513.8 FPS |


- The difference between own and released artifacts is within the run-to-run variation (X5 own over 3 runs: 3.066–3.118 ms, released 3.112 ms; S100 own 0.630–0.638 ms, released 0.641 ms);
- Single measurements vary normally; write a range or "about" on the page;
- The numbers for the two boards were **measured separately**; we did not run a fair cross-board comparison in this lesson, so don't conclude "which is how many times faster" from them;
- One `perf` run prints two FPS values (the thread line and the summary line), which differ slightly; pick one and use it consistently when teaching (these notes use the summary line);
- Without `--input_file`, `perf` prints a `[Warning]: These operators have range limitations …` block; it is a routine notice, not an error.

### 6.5 Evaluation: a demo, and how to measure (slides 43–45)

> **Scope**: evaluation in this lesson = a demo + an explanation of how to measure. All measured numbers below **come from demo subsets on the PC** (200 / 1 834 images, covering only some classes) and **do not represent accuracy on the full ImageNetV2**; board-side evaluation was **not run in this lesson** — we only give the commands and what the parameters mean, no numbers.

**Definition**: ImageNetV2 **MatchedFrequency**: 10 000 images, 1 000 classes, 10 images per class; it is **not** the ILSVRC2012 (ImageNet-1k) validation set, and its numbers cannot be compared with ImageNet-1k validation results. This lesson only obtained 1 834 of the images (184 classes); the sha256 overlap between the calibration images and these 1 834 images is 0 (only this part was checked).

**Top-1 / Top-5**: for each image, stably sort the 1 000-dimensional logits and take the top 5 (on ties, the smaller index comes first); rank 1 = label counts as Top-1 correct, label among the top 5 counts as Top-5 correct; metric = number correct ÷ total.

**Two scripts**:

| | FP32 ONNX evaluation | Board-side evaluation |
|---|---|---|
| Script | `samples/vision/resnet/evaluator/evaluate.py` | `samples/vision/resnet/evaluator/evaluate_board.py` |
| Runs on | Computer, ONNX Runtime | Board (X5 / S100), needs `hbm_runtime` |
| Evaluates | Your exported `model.onnx` (FP32) | Your compiled `.bin` (X5) / `.hbm` (S100) |
| Status in this lesson | Run on the demo subsets | **Not run**, command shown only |

**FP32 demo command** (run; paths shown as `<…>` on the page, `--provider CPUExecutionProvider --threads 4` omitted on the page):

```bash
python samples/vision/resnet/evaluator/evaluate.py \
  --model resnet18 --manifest <manifest> --expected-images 200 \
  --export-dir <export> --images-root <data> --output <new-dir>
jq -c '.metrics, .correct' evaluation.json
# {"top1":0.625,"top5":0.835}
# {"top1":125,"top5":167}
```

Measured on the demo subsets: 200 images (124 classes) Top-1 62.5% (125/200), Top-5 83.5% (167/200); 1 834 images (184 classes) Top-1 60.74% (1114/1834), Top-5 81.52% (1495/1834). The page labels them "demo subset", **does not put them next to the README's 59.35%, and does not use them to claim "reproduced / failed to reproduce"** (small sample, biased classes; the 95% interval of the 200-image Top-1 is about 55.6%–68.9%). With 200 images, `evaluate.py` does not print the metrics in the terminal (progress is printed every 500 images), so the page reads `evaluation.json` with `jq`; `class_count` in `evaluation.json` is 1000 (the size of the class list), **not** the number of classes covered by the subset, so the page does not use that field.

**Board-side command** (not run; command and parameter meanings only):

```bash
python3 evaluate_board.py --target x5 --variant resnet18 \
  --model <own .bin> --model-sha256 <hash> --campaign <config> \
  --manifest <manifest> --data-root <data> --output <new-dir>
# S100: --target s100, --model <own .hbm>, the matching hash; otherwise the same as X5
```

- If `--model-sha256` does not match the file, it refuses to run; `--campaign` provides the preprocessing contract (size, crop, mean/std) and the expected image count; the `--manifest` image count must match; the output directory must be new.
- The repository has no ready-made `campaign.json` or 10 000-image `manifest.json` (the frozen versions are generated by `freeze.py`, which needs all pinned checkpoints and the full manifest, which this lesson does not have); this lesson hand-assembled a minimal demo campaign (`DEMO-minimal-not-frozen`), only verified the input checks on the PC, and did not run board-side inference.
- The repository flow has no script for "evaluating the quantized model on the PC"; evaluating with toolchain simulation was **not tried** (not "impossible").
- If you run it on the board yourself with a demo subset, label the result "demo subset" as well; it is not the accuracy on the full ImageNetV2.

The Sample README publishes reference numbers for ResNet-18 (**from the README, not measured in this lesson**; ImageNetV2 is not the ILSVRC2012 validation set, and its numbers cannot be compared with ImageNet-1k validation results):

| Target | FP32 Top-1 | Board Top-1 | FP32 Top-5 | Board Top-5 |
|---|---|---|---|---|
| X5 | 59.35% | 58.91% | 80.94% | 80.56% |
| S100 | 59.35% | 58.79% | 80.94% | 80.46% |

A model with similarity above 0.999 still has a board Top-1 about half a percentage point below FP32: exactly an example of "similarity is only a reference; task accuracy is what counts".

---

## 7. Rules for beginners

The "five rules" on slide 46 are the first five below; the slides, the narration and these notes are kept consistent. The last three are extra reminders.

1. Add `--entrypoint ''` to the docker image, otherwise `bash -c` fails with 126 (`cannot execute binary file`).
2. PTQ can be done on the CPU alone; the GPU is only an optional speed-up, and the toolchain provides both CPU and GPU Docker images. The CUDA messages in this lesson's demo log can be ignored (the container tried the GPU, failed, and fell back to the CPU, 14 times in total); check whether `Successfully compile the hbm model` appears at the end.
3. Calibration preprocessing must match deployment: geometry, color format and where normalization happens; note that X5 calibration data is raw RGB, while S100 calibration data is already normalized.
4. Artifacts are compiled for the target march; changing board types requires a new conversion (S100P needs a separate conversion with `nash-m`). Don't use an S100 `.hbm` on an S100P (the RDK Studio documentation FAQ states that different RDK boards use different BPU architectures, and hbm models cannot be used across board types).
5. For verification, look at the Top-1 and the order of magnitude of the scores; don't require the low-score Top-5 classes to be in exactly the same order. Cosine similarity is only a reference: investigate if an output node is below 0.8, and task accuracy is what counts in the end.
6. Keep `$WORK` outside the repository; don't write tens of MB of intermediate files into the Sample directory.
7. On the board, write only to `/tmp/course_2-03/`; never put passwords or keys into any file.
8. After renaming an artifact, the model name in `model_info` does not change, so don't use the model name to tell which file you are using.

---

## 8. Frequently Asked Questions

**Q. `docker run` fails with `cannot execute binary file` (exit code 126). What should I do?**
A. Add `--entrypoint ''` and use `bash -c '<command>'`. (Measured in this lesson: without it both images give 126; with it they work.)

**Q. The S100 conversion fails with `cudaErrorInvalidDevice`, or the log is full of `CUDA failure`?**
A. Prefer the **CPU image** of the same version (PTQ does not need a GPU). If you are still using the GPU image: in this lesson, adding `-e CUDA_VISIBLE_DEVICES=-1` inside the GPU image forced the CPU and succeeded (217.5 s); the CUDA messages in the log mean the GPU was tried, failed, and the run fell back to the CPU, and they do not affect the result. Note: the four variants in the table above apply only to the **GPU image** — without `--gpus` it crashes (139), with `=0` it fails (255) — and they do not mean "you can't convert without a GPU".

**Q. Why does the X5 `checker` show no similarity?**
A. `checker` only checks whether the model can be converted and where operators land; similarity is computed in `makertbin`.

**Q. Why is the Top-5 of my own artifact not exactly the same as the released one?**
A. Any difference in calibration data, tool versions, etc. makes the quantization parameters differ slightly. Look at the Top-1 and the order of magnitude of the scores; in this lesson the first two S100 ranks match the released artifact, and ranks 3–5 all score around one in ten thousand, with slight differences in order and a few classes.

**Q. What if `git clone` fails on the board?**
A. The main flow is still to `git clone` directly on the board; if the current network cannot reach GitHub, prepare the repository on a computer that can, and copy it to `/tmp/course_2-03/` on the board with `scp`.

**Q. How should I state the system image version?**
A. Read `/etc/version` on the board: measured in this lesson, X5 is `3.5.0-beta` and S100 is `4.0.5-Beta`; both are currently Beta.

---

## Lesson Summary

- Five PTQ stages: floating-point model → validation → calibration data → quantization and compilation → evaluation;
- X5 uses `hb_mapper checker` + `makertbin` to produce `.bin`; S100 uses `hb_compile` to produce `.hbm`;
- The most important parts of the yaml are `march`, `nv12 / rgb`, `mean` / `scale` (normalization compiled into the model) and the calibration data directory;
- Similarity (X5 `logits` 0.999941; S100 `logits` Quantized 0.999856) is only a reference;
- Put your own artifacts back into the Sample: on both X5 and S100 the Top-1 is white wolf (0.997102 / 0.998149), in the same range as the released artifacts.

Next lesson (2-04): quantization using YOLO as the example — a detection model's output head is completely different from classification, where does the post-processing go, and then calibration methods, per-layer / per-channel, int8/int16 mixed precision and accuracy debugging, all in one go.

---

## Completion Checklist

- [ ] I can name the five PTQ stages and their directories;
- [ ] I can read `march`, `input_type_rt` / `input_type_train`, `mean_value` / `scale_value` and `cal_data_dir` in the yaml;
- [ ] I can explain the images, commands and artifact suffixes used by the X5 and the S series;
- [ ] I can find the output-node similarity in the log and explain why it is only a reference;
- [ ] On at least one board, I completed `model_info` → `main.py` → reading the Top-1 with my own artifact.

---

## Extension Exercises

1. Change the calibration set to 100 or 400 images, convert again, and observe how the similarity and the Top-1 score change.
2. Use `hrt_model_exec model_info` to compare your own and the released artifacts, and find all fields that are the same and different.
3. Change the S100 yaml to `march: nash-m` and convert it with `hb_compile` (it can only be verified on an S100P board).
4. Read `export.json` and compare the PyTorch vs. ONNX output errors of the two images.

---

## Appendix: Command Quick Reference

```bash
# ---- On the computer (cwd = repository root; WORK, CAL, EVAL are absolute directories) ----
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

# yaml placeholders
sed -e "s#@WORK@#$WORK#g" -e "s#@SIZE@#224#g" samples/vision/resnet/conversion/ptq_x5.yaml > $WORK/x5/config.yaml
sed -e "s#@WORK@#$WORK#g" -e "s#@TARGET@#s100#g" -e "s#@MARCH@#nash-e#g" -e "s#@SIZE@#224#g" \
  samples/vision/resnet/conversion/ptq_s.yaml > $WORK/s100/config.yaml

# X5 (image local/rdk-x5-oe:v1.2.8-server, cwd = $WORK/x5)
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/x5" \
  local/rdk-x5-oe:v1.2.8-server bash -c \
  'hb_mapper checker --model-type onnx --march bayes-e --model '"$WORK"'/export/model.onnx --input-shape data 1x3x224x224'
docker run --rm --entrypoint '' --user "$(id -u):$(id -g)" --shm-size 15g -v "$WORK:$WORK" -w "$WORK/x5" \
  local/rdk-x5-oe:v1.2.8-server bash -c 'hb_mapper makertbin --config config.yaml --model-type onnx'

# S100 (image …_s100_s600_gpu:v3.7.0, cwd = $WORK/s100; demo: GPU image + CVD=-1; the CPU image of the same version also works)
docker run --rm --entrypoint '' --gpus all -e CUDA_VISIBLE_DEVICES=-1 --user "$(id -u):$(id -g)" --shm-size 15g \
  -v "$WORK:$WORK" -w "$WORK/s100" \
  registry.d-robotics.cc/deliver/ai_toolchain_ubuntu_22_s100_s600_gpu:v3.7.0 \
  bash -c 'hb_compile --config config.yaml'

# Rename to the release names
cp $WORK/x5/build/resnet_x5.bin     resnet18_bayese_224x224_nv12.bin
cp $WORK/s100/build/resnet_s100.hbm resnet18_nashe_224x224_nv12.hbm

# ---- On the board (write only to /tmp/course_2-03/) ----
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

Sources of the numbers: this lesson's conversion logs from both toolchains on the computer and on-board measurement logs from RDK X5 (X5U) and RDK S100; Model Zoo main `7a97c178`. The interpretation of similarity is taken from "Model quantization and compilation" in the S-series documentation and "PTQ conversion steps" in the X5 documentation.
