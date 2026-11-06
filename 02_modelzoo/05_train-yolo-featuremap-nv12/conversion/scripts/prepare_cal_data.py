#!/usr/bin/env python3
"""Prepare PTQ calibration tensors for 2-05.

Featuremap files match the Ultralytics ONNX input (float32 RGB NCHW, 0..1).
DetectionTrainer.preprocess_batch divides by 255 before the forward, and ONNX
export does not insert that Div. Both featuremap YAMLs stay norm_type
no_preprocess, so the file is the network input:

  X5 featuremap: (tensor / 255) -> raw float32 .rgbchw via tofile
  S100 featuremap: (tensor / 255) -> .npy via np.save

NV12 is a different contract and is not changed here:

  X5 NV12: 0..255 .rgbchw; YAML data_scale stays (HzPreprocess)
  S100 NV12: /255 .npy; YAML data_scale stays (inserted at the quantize stage)

Do not copy the NV12 file rule onto featuremap, and do not drop NV12 scale.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import cv2
import numpy as np

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def list_images(src: Path, limit: int) -> list[Path]:
    files = sorted(p for p in src.rglob("*") if p.suffix.lower() in IMAGE_EXTS)
    if not files:
        raise SystemExit(f"no images under {src}")
    return files[:limit]

def to_nchw(img_bgr, w: int, h: int) -> np.ndarray:
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    rgb = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_LINEAR)
    chw = np.transpose(rgb, (2, 0, 1))
    return np.expand_dims(chw, 0).astype(np.float32)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="dir of JPG/PNG")
    ap.add_argument("--out-root", required=True, help="course_2-05 workspace or conversion dir")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=640)
    ap.add_argument("--limit", type=int, default=32)
    args = ap.parse_args()
    src = Path(args.src).expanduser().resolve()
    root = Path(args.out_root).expanduser().resolve()
    dirs = {
        "images": root / "cal_images",
        "x5_fm": root / "cal_featuremap_x5_rgbchw",
        "s_fm": root / "cal_featuremap_s100_npy",
        "nv12": root / "cal_nv12_rgb_f32",
        "nv12_s": root / "cal_nv12_s100_npy",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
        # clear old tensors but keep README if any
        for old in d.glob("*"):
            if old.is_file() and old.suffix in {".rgbchw", ".npy", ".jpg", ".jpeg", ".png"}:
                old.unlink()

    imgs = list_images(src, args.limit)
    print(f"using {len(imgs)} images from {src}")
    for i, path in enumerate(imgs, 1):
        bgr = cv2.imread(str(path))
        if bgr is None:
            print(f"skip undecodable {path}")
            continue
        stem = f"{i:03d}_{path.stem}"
        # copy a small jpg set for NV12 image-based workflows / mapper --cal-images
        dst_jpg = dirs["images"] / f"{stem}.jpg"
        cv2.imwrite(str(dst_jpg), bgr)
        tensor = to_nchw(bgr, args.width, args.height)  # 0..255 float32 NCHW
        train_domain = tensor / 255.0  # ONNX / DetectionTrainer input, 0..1
        # X5 featuremap: same 0..1 values, still a raw .rgbchw. YAML stays no_preprocess.
        (dirs["x5_fm"] / f"{stem}.rgbchw").write_bytes(np.ascontiguousarray(train_domain).tobytes())
        # S100 featuremap: 0..1 .npy. YAML stays no_preprocess.
        np.save(str(dirs["s_fm"] / f"{stem}.npy"), train_domain)
        # X5 NV12: pre-scale 0..255. YAML data_scale is unchanged.
        (dirs["nv12"] / f"{stem}.rgbchw").write_bytes(tensor.tobytes())
        # S100 NV12: /255 once. YAML data_scale is unchanged; do not divide again.
        np.save(str(dirs["nv12_s"] / f"{stem}.npy"), train_domain)
        print(f"[{i}/{len(imgs)}] {path.name} -> {stem}")
    print("done:")
    for k, d in dirs.items():
        print(f"  {k}: {d} ({len(list(d.glob('*')))} files)")

if __name__ == "__main__":
    main()
