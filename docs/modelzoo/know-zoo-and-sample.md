# Meet RDK Model Zoo

> Course: RDK Classroom · Chapter 2 Model Zoo · Lesson 2
>
> Boards covered: RDK X5, RDK S100, RDK S100P, RDK S600 (RDK Model Zoo `main` branch, repository VERSION 2.0.0, commit baseline `7a97c178`; a shallow clone on the board may show `7a97c17` — same commit)
>
> Course goal: Understand how the main branch supports four boards with one codebase; read a Sample's directories, entry points, and interfaces; run ResNet-18 on X5 and S100 and read the Top-5 results
>
> Learning format: concept explanation + on-board hands-on (one board at a time). On the board, `git clone https://github.com/D-Robotics/rdk_model_zoo.git` is enough to run (working directory recommended: `/tmp/course_2-02/`). The board must allow login and reach `archive.d-robotics.cc` to download artifacts
>
> Video: [YouTube](https://youtu.be/kE8w3qjq010) · [Watch on Bilibili (in Chinese)](https://www.bilibili.com/video/BV1CYnd6SEUg/)
>
> Slides: [Open English HTML slides on GitHub](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/02_know-zoo-and-sample/lesson-2-02.html) · [Chinese slide source](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/02_know-zoo-and-sample/lesson-2-02.zh.html)

---

## Companion resources

| Resource | Purpose |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | The star of this lesson: Samples, artifact manifests, shared tools (`main`) |
| [ResNet Sample README](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/README.md) | Support matrix, quickstart, expected results, and performance references |
| [ResNet model artifacts](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/model/README.md) | Artifact list, download script, input protocols |
| [ResNet Python runtime](https://github.com/D-Robotics/rdk_model_zoo/blob/main/samples/vision/resnet/runtime/python/README.md) | `main.py` arguments, results, and integration examples |
| [Release manifests and board aliases](https://github.com/D-Robotics/rdk_model_zoo/tree/main/docs/release) | `models.yaml` (x5 / s) and `platforms.json` |
| [RDK documentation center](https://developer.d-robotics.cc/rdk_doc_center/) | Board manuals and algorithm toolchain docs |

On-board test environment: RDK X5 (SoC measured as X5U), RDK S100; Model Zoo `main` commit baseline `7a97c178` (a shallow clone on the board may show `7a97c17`).

---

## 1. What problem does this lesson solve?

Last lesson's takeaway: the BPU only runs quantized, compiled models; X5 uses `.bin`, the S series uses `.hbm`.

Once you have a model, how do you run it on the board? This lesson centers on three questions:

1. **One codebase, four boards**: how does `main` support X5, S100, S100P, and S600 at once?
2. **What is inside a Sample**: where are the directories, entry points, and interfaces?
3. **How to run it and read the results**: run ResNet-18 on X5 and S100 and read the Top-5.

---

## 2. What you will be able to do

- Pick a board with `--target x5|s100|s100p|s600|auto` and say how the artifact changes with the target;
- Read a Sample README support matrix, and preview on a computer with `--list-models` / `--dry-run`;
- Point to what `model/`, `conversion/`, `runtime/`, `evaluator/`, `test_data/`, and `tests/` each own;
- Follow the inference path `main.py → cli.py → ResNetClassifier.predict` (`preprocess → infer → postprocess`);
- On X5 and S100 complete: download artifact → `model_info` → run `main.py` → read Top-5;
- When switching boards, change only the target, download args, and artifact path, and avoid common pitfalls (mixed artifacts, target/hardware mismatch, missing deps, and so on).

---

## 3. What is Model Zoo (Part 1)

Model Zoo is D-Robotics' collection of **BPU model samples**. Each Sample usually contains:

| Content | Role |
|---|---|
| Converted models | Compiled `.bin` / `.hbm`, ready to download and use |
| On-board inference code | Python entry (some Samples also ship C++), with pre/post-processing already written |
| Conversion and evaluation | `conversion/` recipes; `evaluator/` dataset accuracy |

The current delivery line is the **`main` branch** (repository `VERSION` = 2.0.0). Historical `rdk_x5` and `rdk_s` branches remain, but new work targets `main`.

### 3.1 Four places in the repository

| Directory | What it holds |
|---|---|
| `samples/` | All Samples, by domain: vision, speech, llm, robotics, vla |
| `utils/` | Shared tools: image/label I/O, Runtime wrappers |
| `docs/release/` | Artifact manifests `models.yaml` (x5 / s) and `platforms.json` |
| `datasets/` | Evaluation data and class names, e.g. `imagenet/imagenet_classes.names` |

### 3.2 One codebase, four boards

There is only one copy of the Sample code. Tell the program which board to run on with `--target`:

- Explicit: `x5` / `s100` / `s100p` / `s600`
- `auto`: read the board identity (`/sys/class/boardinfo/soc_name` or `/sys/class/socinfo/soc_name`) and map it through `docs/release/platforms.json`

Once the target is set, the artifact is set (illustrative):

| target | march | ResNet-18 artifact (under `model/`) |
|---|---|---|
| x5 | bayes-e | `resnet18_bayese_224x224_nv12.bin` |
| s100 | nash-e | `s100/resnet18_nashe_224x224_nv12.hbm` |
| s100p | nash-m | `s100p/resnet18_nashm_224x224_nv12.hbm` |
| s600 | nash-p | `s600/resnet18_nashp_224x224_nv12.hbm` |

**The code does not change — only the target and the artifact do.** S100P must not use S100 files. The `model/` directory itself does not commit binaries; artifacts are fetched with `download.sh` from the Manifest.

Board identity aliases (`platforms.json`): X5 `socinfo_names` are `x5u` / `x5h` / `x5m`; the X5 SoC measured in this lesson is **X5U**.

---

## 4. Inside a Sample (Part 2)

### 4.1 Decide whether you can use it

Three steps that need no board — do them on a computer:

1. Read the README **support-matrix** (target × variant × language);
2. `python3 …/main.py --list-models --target <target>` lists artifact references in the manifest;
3. `--dry-run` only resolves the selection — it does not load a model or touch the on-board SDK.

Example (ResNet): ResNet-18 has Python artifacts on all four boards; C++ covers the S series only — X5 has no C++ runtime. YOLOv8 Detect is present for X5, S100, S100P, and S600 in the online Model Zoo catalog; not every model covers all four boards. Before you start, confirm platform and model on the cards or hardware filter of the [Model Zoo online catalog](https://d-robotics.github.io/rdk_model_zoo/) — that catalog is authoritative.

### 4.2 Six directories

Take `samples/vision/resnet/` as the example:

| Directory | What it owns |
|---|---|
| `model/` | Artifact acquisition (download script + README); no binaries checked in |
| `conversion/` | Export and quantization recipes (next lesson) |
| `runtime/` | On-board run code (`python/`, some Samples also `cpp/`) |
| `evaluator/` | Accuracy on a dataset |
| `test_data/` | Inputs you can run immediately (e.g. `white_wolf.JPEG`) |
| `tests/` | Behavior and numeric regressions |

Sample READMEs use fixed sections (`overview`, `support-matrix`, `prerequisites`, `quickstart`, `expected-results`, `directory`, `entry-points`, `license`, and so on). Learn one Sample and the others are easy to navigate.

### 4.3 Entry points and the shared interface

```text
main.py  →  cli.py  →  classify.py (ResNetClassifier)
                         predict() = preprocess → infer → postprocess
```

- `main.py`: parse args, build the model, call `predict`, print results;
- `cli.py`: args, artifact selection, listing, dry-run, result display;
- `ResNetClassifier`: pre/post on the CPU; `infer` goes to the BPU.

Swap to detection / segmentation Samples and the public interface names are still `preprocess` / `infer` / `postprocess` / `predict`.

### 4.4 Picking the right artifact

1. **manifest**: `docs/release/{x5,s}/models.yaml` — one line per artifact; download URL and format follow it (headers for this lesson's version: X5 `1.1.3`, S `1.1.2`).
2. **asset-id and model-path**: asset-id is the full name in the manifest; model-path is the local file — **they must pair**. Looking at the filename alone does not tell you the input protocol.
3. **Pre-run check**: if the requested target does not match the detected hardware, the run errors out instead of forcing it.

### 4.5 Two input protocols

| | RDK X5 | S100 / S100P / S600 |
|---|---|---|
| Protocol | packed NV12 (`--dry-run` field `packed_nv12`) | split NV12 (`split_nv12`) |
| Inputs | single tensor `data`, 1-D uint8; 224×224 → 75,264 bytes | `data_y (1,224,224,1)` + `data_uv (1,112,112,2)` |
| Artifact | `.bin` | `.hbm` |

You do not assemble this yourself; the Sample's preprocessing prepares data for the bound model. Check input tensors with `model_info`; check the input protocol with `--dry-run`.

---

## 5. On-board hands-on (Part 3)

> Working directory: write only under `/tmp/course_2-02/` on the board.  
> **Prep**: on the board, enter the working directory, run `git clone https://github.com/D-Robotics/rdk_model_zoo.git`, then enter the repo root for the rest. Artifact downloads go through `archive.d-robotics.cc`; `download.sh` works as expected.  
> Look at one board at a time. All commands run from the repository root.

### 5.0 Get the repository

```bash
cd /tmp/course_2-02
git clone https://github.com/D-Robotics/rdk_model_zoo.git
cd rdk_model_zoo
```

If the board cannot reach GitHub, clone on a computer and `scp` into `/tmp/course_2-02/` on the board.

### 5.1 Identify the board

```bash
cat /sys/class/boardinfo/soc_name \
  /sys/class/socinfo/soc_name \
  2>/dev/null | tr -d '\0'
```

Keep `2>/dev/null`: X5 has no `boardinfo`, S100 has no `socinfo`; without it you get a `No such file or directory` line.

| Board | Measured `soc_name` |
|---|---|
| X5 | **X5U** |
| S100 | **S100** |

X5 may also be X5H / X5M — trust what the board prints.

### 5.2 Download the artifact

```bash
bash samples/vision/resnet/model/download.sh x5 18
# or
bash samples/vision/resnet/model/download.sh s100 18
```

| Board | Artifact | Size (measured) |
|---|---|---|
| X5 | `samples/vision/resnet/model/resnet18_bayese_224x224_nv12.bin` | about **11.08 MB** (11 081 728 B) |
| S100 | `samples/vision/resnet/model/s100/resnet18_nashe_224x224_nv12.hbm` | about **12.19 MB** (12 193 864 B) |

### 5.3 Inspect model info

```bash
hrt_model_exec model_info --model_file <model file>
```

| Board | `model_info` highlights (measured) | `input_protocol` (`--dry-run`) |
|---|---|---|
| X5 | single input `data`, NV12, `(1,3,224,224)`, aligned 75,264 bytes | `packed_nv12` |
| S100 | dual inputs `data_y (1,224,224,1)` U8 + `data_uv (1,112,112,2)` U8 | `split_nv12` |

`model_info` description lines may include the build machine path — trim that line before sharing screenshots.

### 5.4 Run the Sample

Short form (artifact already in the default location; this lesson measured exit 0):

```bash
python3 samples/vision/resnet/runtime/python/main.py --target x5 --variant 18
python3 samples/vision/resnet/runtime/python/main.py --target s100 --variant 18
```

Default test image is the in-repo `white_wolf.JPEG`; labels are `datasets/imagenet/imagenet_classes.names`. Full form is in the Sample README (`--asset-id` + `--model-path` paired). Four ways (`--variant 18`, full form, `main.py` defaults, `run.sh`) produced matching Top-5 in this lesson; `--target auto` identified both X5 and S100 correctly.

### 5.5 How to read the results

Each line has three fields: `class` (ImageNet-1k id), `label`, and `score` (after softmax).

Measured Top-5 (repo commit baseline `7a97c178`; order matches the README expectation):

| Rank | Class | X5 score | S100 score |
|---|---|---|---|
| 1 | white wolf (class 270) | **0.998090** | **0.998109** |
| 2 | timber wolf | 0.000592 | 0.000565 |
| 3 | ice bear | 0.000189 | 0.000185 |
| 4 | Arctic fox | 0.000126 | 0.000137 |
| 5 | Samoyed | 0.000080 | 0.000087 |

README reference: for in-repo `white_wolf.JPEG`, Rank-1 is white wolf with X5 reference score 0.998; on ImageNetV2 MatchedFrequency, ResNet-18 Top-1 is FP32 59.35%, X5 on-board 58.91%, S100 on-board 58.79% (source: Sample README performance section).

### 5.6 Four steps to run a Sample (summary)

1. Download the artifact: `download.sh <target> 18`
2. `hrt_model_exec model_info`
3. `main.py --target <board>`
4. Read Top-5 and compare with the README

Switch boards: change only the target and the artifact — the four steps stay the same.

### 5.7 Optional: C++ (S series; measured on S100 in this lesson)

`bash samples/vision/resnet/runtime/cpp/run.sh` **defaults to `zebra_cls.jpg`** (Top-1 zebra). To see white wolf you must add:

```bash
bash samples/vision/resnet/runtime/cpp/run.sh \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG
```

X5 has no C++ runtime.

### 5.8 Extra: perf

Single `hrt_model_exec perf --frame_count 200 --thread_num 1` (no input file): X5 average about 3.144 ms / 316.6 FPS; S100 average about 0.628 ms / 1546.9 FPS. Single-run numbers fluctuate; magnitude can be compared with Sample README references (X5 2.740 ms, S100 0.631 ms).

---

## 6. Switching boards and pitfalls (Part 4)

### 6.1 Switch boards by changing three places

1. `--target`: `x5` → `s100` / `s100p` / `s600`, or `auto`
2. The first argument of `download.sh` in sync
3. S-series artifacts live under `s100/` / `s100p/` / `s600/` — the path follows

Test image, label file, and other args stay put.

### 6.2 Common pitfalls

When a run fails, check these five first.

| Pitfall | Note |
|---|---|
| S100P cannot use S100 artifacts | Different march (nash-m vs nash-e) |
| Target mismatches hardware | Pre-run check errors immediately |
| Old image missing PyYAML / Pillow | **May appear on old or slim images**; both boards in this lesson already had them — no deps installed |
| Inference does not auto-download | Run `download.sh` first |
| C++ defaults to zebra | White wolf needs `--test-img` |

---

## 7. Beginner rules

1. Read the support matrix first, then preview with `--list-models` / `--dry-run`.
2. Artifacts are named per board — do not reuse across boards.
3. Pair `asset-id` with `model-path`; the filename alone is not enough.
4. Get the repo on the board with `git clone`; write only under `/tmp/course_2-02/`.
5. Keep `2>/dev/null` when reading board identity.

---

## 8. FAQ

**Q. What if `git clone` on the board fails?**  
A. The main path is still cloning on the board. If the current network cannot reach GitHub, clone on a computer that can (sparse / shallow clone to shrink size), then `scp` into `/tmp/course_2-02/` — that is an optional fallback, not the default step.

**Q. Why does `git rev-parse --short HEAD` show `7a97c17` instead of `7a97c178`?**  
A. On shallow / sparse clones git may shorten to 7 hex digits; a full clone shows 8-digit `7a97c178`. Full hash is the same: `7a97c1780b0cfa131ff0007d662e255e5e41c12e`. Write it as **7a97c178**; the board may show `7a97c17` for the same commit.

**Q. Why keep `2>/dev/null`?**  
A. X5 has no `boardinfo`, S100 has no `socinfo`; with it each board prints cleanly, without it you get an extra error line.

**Q. How should system image versions be written?**  
A. Readable on the board from `/etc/version`: this lesson measured X5 as `3.5.0-beta`, S100 as `4.0.5-Beta` — both currently Beta.

---

## Lesson summary

- `main` picks the board with `--target`; one codebase maps to four boards' artifacts;
- A Sample has six directories; entry points are `main.py`, `cli.py`, and the model class;
- ResNet-18 ran on X5 (SoC X5U) and S100: Top-1 was white wolf on both (0.998090 / 0.998109).

Next lesson (2-03): quantize against a Sample — take ResNet from ONNX and calibration data to `.bin` / `.hbm`, walk through PTQ end to end, put the artifacts back into the Sample, and verify on the board with what you learned today.

---

## Completion checklist

- [ ] Can state how `--target` maps to artifact naming
- [ ] Can name what each of the six Sample directories owns
- [ ] On at least one board completed download → `model_info` → `main.py` → read Top-5
- [ ] Knows which three places to change when switching boards, and that the board gets the repo via `git clone`

---

## Stretch exercises

1. On the same board, repeat the four steps for ResNet-34 / 50 and compare with `--list-models`.
2. Dry-run with `--dry-run --target s600` and observe printed `asset_id` / `model_path_exists` (False before download).
3. (S100) Compare C++ default zebra output format with white wolf after adding `--test-img`.

---

## Appendix: command cheat sheet

```bash
# Get the repository (main path on the board)
cd /tmp/course_2-02
git clone https://github.com/D-Robotics/rdk_model_zoo.git
cd rdk_model_zoo

# Identity (keep 2>/dev/null)
cat /sys/class/boardinfo/soc_name /sys/class/socinfo/soc_name 2>/dev/null | tr -d '\0'

# Download
bash samples/vision/resnet/model/download.sh x5 18
bash samples/vision/resnet/model/download.sh s100 18

# Model info
hrt_model_exec model_info --model_file samples/vision/resnet/model/resnet18_bayese_224x224_nv12.bin
hrt_model_exec model_info --model_file samples/vision/resnet/model/s100/resnet18_nashe_224x224_nv12.hbm

# Preview (works on a computer)
python3 samples/vision/resnet/runtime/python/main.py --list-models --target auto
python3 samples/vision/resnet/runtime/python/main.py --dry-run --target x5
python3 samples/vision/resnet/runtime/python/main.py --dry-run --target s100

# Infer
python3 samples/vision/resnet/runtime/python/main.py --target x5 --variant 18
python3 samples/vision/resnet/runtime/python/main.py --target s100 --variant 18

# S100 C++ white wolf
bash samples/vision/resnet/runtime/cpp/run.sh \
  --test-img samples/vision/resnet/test_data/white_wolf.JPEG
```

Number sources: measured in this lesson on RDK X5 (X5U) and RDK S100 (Model Zoo main `7a97c178`); README reference values are from the Sample `README.md` performance / expected-results sections.
