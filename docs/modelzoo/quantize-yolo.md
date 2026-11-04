# YOLO Quantization by Example

> Course: RDK Classroom · Chapter 2 Model Zoo · Lesson 4
>
> Boards covered: RDK X5, RDK S100 / S100P / S600 (RDK Model Zoo `main`; this lesson’s board measurements are **S600 + X5**)
>
> Course goal: Using YOLO detect, show how YOLO-specific toolchain opts (cut post-process, board-side decode, sensitive layers) cut compute and improve on-board running—covering output-head protocol, export cut-point and decode, one mapper into two toolchains, Softmax / int16, and accuracy triage—with commands you can follow
>
> Learning format: concepts + conversion README commands + on-board `model_info` / `main`. OE open-box points back to **2-03**; this lesson goes straight to mapper
>
> Video: **To be published**
>
> Slides: [Open English HTML slides on GitHub](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/04_quantize-yolo/lesson-2-04.html) · [中文课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/02_modelzoo/04_quantize-yolo/lesson-2-04.zh.html)

---

## Companion resources

| Resource | Purpose |
|---|---|
| [RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) | Conversion recipes, board runtime, reference artifacts |
| [`samples/vision/ultralytics_yolo/`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo) | Primary sample for this lesson |
| [`…/ultralytics_yolo/conversion`](https://github.com/D-Robotics/rdk_model_zoo/tree/main/samples/vision/ultralytics_yolo/conversion) | Export patch · mapper · Softmax config |
| [RDK Resource Center](https://developer.d-robotics.cc/rdk_doc_center/en) | Official manuals |
| [X5 OE docs](https://developer.d-robotics.cc/oe_x5_doc) | accuracy_tune / toolchain |
| [S OE docs](https://developer.d-robotics.cc/oe_s_doc) | accuracy_debug / toolchain |
| [hrt_model_exec](https://developer.d-robotics.cc/oe_s_doc/guide/ucp/runtime/tool_introduction/hrt_model_exec) | On-board `model_info` / `infer` |
| Lesson measurements | In-tree `board-tests/measured.json` |

!!! note "Figures"
    The four captions match the frozen 26-page deck. Hashed jpgs are not in the repo yet, so this note names the PLACEHOLDER files instead of linking missing images.

---

## 1. What problem does this lesson solve?

Lesson 2-03 finished a **full ResNet PTQ** and opened OE. Switching to detect usually stalls on:

1. **Output heads** — classify is one logits path; YOLO is three strides with cls + DFL. How do protocols pair?
2. **Cut & decode** — where does post-process live? Where does the export cut stop? How does board-side `decode_dfl` work?
3. **Mapper & sensitive layers** — how does one ONNX enter X5 and S toolchains? How do you write Softmax / int16?
4. **On-board triage** — large drop vs small drop; which numbers count?

This lesson’s spine: **heads → cut/decode → one mapper + sensitive layers → board-measured triage**. Value line to keep: **YOLO-specific opts → much less compute → better on-board running** (cut post-process, board-side `decode_dfl` filter-then-decode, raise sensitive layers—no invented latency/FPS; trust board measurements only).

> **Lesson route PLACEHOLDER** · `assets/lesson-2-04-en-PLACEHOLDER-route.jpg`

---

## 2. What you will be able to do

- State the lesson value in one line: YOLO-specific opts cut compute so detect runs better on board;
- Describe YOLO DFL detect vs classify (three cls + three DFL) and contrast YOLO26 direct-LTRB;
- Export with `export_monkey_patch` per the conversion README (X5 opset 11 / S opset 19), graph stopping at logits;
- Produce X5 `.bin` and S `.hbm` with one `mapper.py`, and write Softmax int8 / `--quantized int16`;
- On board, use `model_info` + `main.py` to check output tensor count and detection count;
- Triage accuracy drops: large → calib / preprocess / cut; small → Softmax / int16; **never put README mAP citations on slides**.

---

## 3. Output heads (slides p04–p07)

### 3.1 Contrast with classify

> **Head contrast PLACEHOLDER** · `assets/lesson-2-04-en-PLACEHOLDER-heads.jpg`

- Classify (e.g. ResNet): one feature path → one logits path; Softmax often in runtime.
- YOLO Detect (DFL): input 640 → backbone / neck → strides 8/16/32; each layer **cls logits + DFL 64 channels**.
- **Export cut-point**: six tensors stay in-graph; post-process never enters ONNX.

### 3.2 Shape table (NHWC · 80 classes · 640)

| Path | Meaning | valid shape |
|---|---|---|
| cls8 | stride8 class | 1×80×80×80 |
| DFL8 | stride8 box | 1×80×80×64 |
| cls16 | stride16 class | 1×40×40×80 |
| DFL16 | stride16 box | 1×40×40×64 |
| cls32 | stride32 class | 1×20×20×80 |
| DFL32 | stride32 box | 1×20×20×64 |

> Do not guess protocol from tensor count alone; follow the conversion README and runtime bindings.

### 3.3 Protocol differences

| Family | Contract |
|---|---|
| DFL (v5u/v8/v9/v10/11/12/13) | Three cls + three DFL (64 channels) |
| YOLO26 | direct-LTRB: three cls + three 4-channel boxes; **separate exporter** |

Artifacts are **not interchangeable**. Seg / pose / classify extend the detect protocol.

---

## 4. Cut & decode (slides p08–p11)

### 4.1 Five-step path

> **Cut & decode PLACEHOLDER** · `assets/lesson-2-04-en-PLACEHOLDER-cut.jpg`

1. Ultralytics `.pt` → `export_monkey_patch`
2. ONNX cut stops at cls / DFL logits (Softmax / dist2bbox / NMS stay out)
3. mapper compiles to `.bin` / `.hbm` **inside OE** (OE open-box → **2-03**)
4. Board `decode_dfl`: filter → expectation → xyxy
5. NMS per binding IoU → boxes

Filter before boxing; use Sigmoid monotonicity so you do not compute all ~8400 cells.

### 4.2 Export commands (README skeletons)

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

Run from the repo root; ONNX usually lands next to the weights.

### 4.3 Calibration & conversion layout

```bash
ls samples/vision/ultralytics_yolo/conversion/
# → export_monkey_patch.py  mapper.py
# → mapper_x5.py  mapper_s.py  config_x5.yaml
```

- Repo ships **no** calibration set; default `--cal-sample-num 20`—prepare **20–50** representative images.
- X5: raw RGB / NCHW; S: npy divided by 255.
- NMS defaults: X5 detect **0.70**; S detect **0.45**; S YOLOv10 has no NMS.

---

## 5. Mapper & sensitive layers (slides p12–p18)

> How to open OE / enter the container: **see 2-03**. This lesson has no OE open-box chapter—straight to mapper.

### 5.1 Two toolchains

| Side | Tool | march | Calib | Artifact |
|---|---|---|---|---|
| X5 | `hb_mapper makertbin` | bayes-e | raw RGB | `.bin` |
| S | `hb_compile` | nash-e / m / p | normalized npy | `.hbm` |

Shared: Softmax int8; `--quantized int16` when needed. Nash has **no O3**—use O0/O1/O2.

### 5.2 One mapper

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

Same name needs explicit `--overwrite`. S100 / S100P use `nash-e` / `nash-m`.

### 5.3 Softmax and int16

**X5** (`config_x5.yaml`):

```yaml
optimization: set_Softmax_input_int8, set_Softmax_output_int8
```

**S** (`quant_config`):

```yaml
quant_config: {"op_config": {"softmax": {"qtype": "int8"}}}
```

Still dropping? `--quantized int16` (whole-net precision ↑, slower/larger).

### 5.4 Default artifact names (ONNX stem=`yolo11n`, 640)

| Target | march | Filename |
|---|---|---|
| X5 | bayes-e | `yolo11n_bayese_640x640_nv12.bin` |
| S100 | nash-e | `yolo11n_nashe_640x640_nv12.hbm` |
| S100P | nash-m | `yolo11n_nashm_640x640_nv12.hbm` |
| S600 | nash-p | `yolo11n_nashp_640x640_nv12.hbm` |

Published names may include `_detect_`; follow `download_model` / measurements. `output-dir` only changes location.

---

## 6. On-board & accuracy triage (slides p19–p26)

### 6.1 model_info / main

Board writes only under `/tmp/course_2-04/`. Run `model_info` first, then `main.py` on `bus.jpg`.

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

X5 cross-family check can use yolov8n (`--platform x5 --family yolov8`). Always pass `--model-path` explicitly.

### 6.2 Board measurements (source: `board-tests/measured.json`)

Recorded at: 2026-11-02 11:14:31 (Asia/Shanghai). Model Zoo artifacts · `bus.jpg`.

| Board | Artifact | Output tensors | Dets | Notes (from measured) |
|---|---|---|---|---|
| S600 | `yolo11n_detect_nashp_640x640_nv12.hbm` | **6** | **5** | NMS default 0.45; persons 0.89/0.85/0.83/0.50 + bus 0.92 |
| X5U | `yolov8n_detect_bayese_640x640_nv12.bin` | **6** | **5** | NMS default 0.70; persons 0.86/0.84/0.82/0.36 + bus 0.85 |

**No README mAP on slides or in the main tables** (e.g. 36.77 / 35.74 / 35.72). Accuracy pages use det-count / tensor-count triage plus board measurements only.

### 6.3 Accuracy triage

> **Accuracy triage PLACEHOLDER** · `assets/lesson-2-04-en-PLACEHOLDER-triage.jpg`

1. **Float align** — exported ONNX ≈ training.
2. **Large drop** — check calib / preprocess / cut-point config.
3. **Small drop** — Softmax / `--quantized int16`.
4. **Re-measure** — `model_info` + `main`; then docs-center `accuracy_tune` / `accuracy_debug`.

Sensitivity-tool live commands follow the docs center (**pending docs**); this lesson only gives the triage route.

---

## 7. Takeaways

One value line: **YOLO-specific opts → much less compute → better on-board running** (cut post-process, board-side decode, raise sensitive layers). Then five lines:

1. Heads are multi-scale multi-tensor; protocol follows export and runtime bindings.
2. Cut stops at logits; `decode_dfl` is on board—filter before boxing.
3. One mapper: X5 → `.bin`, S → `.hbm`.
4. Softmax int8 separately; raise int16 if needed.
5. Accuracy drops: triage first; trust board measurements only.

---

## 8. Next lesson (2-05)

**Train your own YOLO + feature map / NV12**: train one YOLO, clear the path with feature map first, then switch to NV12—including a full OE hands-on.

---

## Appendix · Pending verification (no invented numbers)

| Item | Status |
|---|---|
| Self-converted YOLO similarity / evaluator mAP on PC | Pending board/docs (OE convert not re-run this round) |
| Self-converted vs Model Zoo box-by-box compare | Pending board (current measured.json = Model Zoo artifacts) |
| Auto-download when `--model-path` omitted | Pending board/docs (this lesson always passes `--model-path`) |
| Sensitivity-tool live commands | Pending docs (hmct-debugger / get_sensitivity_of_nodes → docs center) |
