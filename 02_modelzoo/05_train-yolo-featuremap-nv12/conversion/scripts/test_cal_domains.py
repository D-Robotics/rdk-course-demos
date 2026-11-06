#!/usr/bin/env python3
"""Check lesson 2-05 calibration files and YAML text.

This test proves what prepare_cal_data.py writes and what the four YAML
files still contain. It does not run hb_mapper or hb_compile, and a pass
here is not a quantization-accuracy result.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parent / "prepare_cal_data.py"
CONV = Path(__file__).resolve().parents[1]
WIDTH = 32
HEIGHT = 24


def write_bgr_png(path: Path, bgr: tuple[int, int, int]) -> None:
    import cv2

    image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    image[:, :] = bgr
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"failed to write {path}")


def load_rgbchw(path: Path) -> np.ndarray:
    raw = np.fromfile(path, dtype=np.float32)
    return raw.reshape(1, 3, HEIGHT, WIDTH)


def assert_close(name: str, got: np.ndarray, expect: np.ndarray) -> None:
    if got.shape != expect.shape or not np.allclose(got, expect):
        raise AssertionError(f"{name}: shape {got.shape} vs {expect.shape}")


def check_yaml_text() -> None:
    files = {
        "ptq_featuremap_x5.yaml": {
            "march": 'march: "bayes-e"',
            "rt": "input_type_rt: 'featuremap'",
            "train": "input_type_train: 'featuremap'",
            "norm": "norm_type: 'no_preprocess'",
            "cal": "cal_data_dir: './cal_featuremap_x5_rgbchw'",
        },
        "ptq_featuremap_s100.yaml": {
            "march": "march: 'nash-e'",
            "rt": "input_type_rt: 'featuremap'",
            "train": "input_type_train: 'featuremap'",
            "norm": "norm_type: 'no_preprocess'",
            "cal": "cal_data_dir: './cal_featuremap_s100_npy'",
        },
        "ptq_nv12_x5.yaml": {
            "march": 'march: "bayes-e"',
            "rt": "input_type_rt: 'nv12'",
            "train": "input_type_train: 'rgb'",
            "norm": "norm_type: 'data_scale'",
            "scale": "scale_value: 0.003921568627451",
            "cal": "cal_data_dir: './cal_nv12_rgb_f32'",
        },
        "ptq_nv12_s100.yaml": {
            "march": "march: 'nash-e'",
            "rt": "input_type_rt: 'nv12'",
            "train": "input_type_train: 'rgb'",
            "norm": "norm_type: 'data_scale'",
            "scale": "scale_value: 0.003921568627451",
            "cal": "cal_data_dir: './cal_nv12_s100_npy'",
        },
    }
    for name, required in files.items():
        text = (CONV / name).read_text(encoding="utf-8")
        if "data_mean_and_scale" in text:
            raise AssertionError(f"{name} must stay on data_scale, not data_mean_and_scale")
        for label, needle in required.items():
            if needle not in text:
                raise AssertionError(f"{name} missing {label}: {needle}")
    s100_nv12 = (CONV / "ptq_nv12_s100.yaml").read_text(encoding="utf-8")
    if "mean_value: ''" not in s100_nv12:
        raise AssertionError("S100 NV12 empty mean_value was changed")
    x5_fm = (CONV / "ptq_featuremap_x5.yaml").read_text(encoding="utf-8")
    if "scale_value" in x5_fm:
        raise AssertionError("X5 featuremap YAML unexpectedly gained a scale")


def check_files() -> None:
    import cv2

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = root / "src"
        out = root / "out"
        src.mkdir()
        # BGR (40, 80, 200) -> RGB (200, 80, 40) after the script's conversion.
        write_bgr_png(src / "swatch.png", (40, 80, 200))
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--src",
                str(src),
                "--out-root",
                str(out),
                "--width",
                str(WIDTH),
                "--height",
                str(HEIGHT),
                "--limit",
                "1",
            ],
            check=True,
        )
        x5_fm = load_rgbchw(next((out / "cal_featuremap_x5_rgbchw").glob("*.rgbchw")))
        x5_nv12 = load_rgbchw(next((out / "cal_nv12_rgb_f32").glob("*.rgbchw")))
        s_fm = np.load(next((out / "cal_featuremap_s100_npy").glob("*.npy")))
        s_nv12 = np.load(next((out / "cal_nv12_s100_npy").glob("*.npy")))
        expect = np.zeros((1, 3, HEIGHT, WIDTH), dtype=np.float32)
        expect[:, 0] = 200
        expect[:, 1] = 80
        expect[:, 2] = 40
        assert_close("x5 featuremap 0..255", x5_fm, expect)
        assert_close("x5 nv12 matches x5 featuremap bytes", x5_nv12, x5_fm)
        assert_close("s100 featuremap /255", s_fm, expect / 255.0)
        assert_close("s100 nv12 matches s100 featuremap", s_nv12, s_fm)
        if float(s_nv12.max()) > 1.0 or float(x5_nv12.max()) <= 1.0:
            raise AssertionError("NV12 files collapsed onto one numeric domain")
        # The script must not pre-apply the YAML scale on top of /255.
        if np.allclose(s_nv12, expect / 255.0 / 255.0):
            raise AssertionError("S100 NV12 file was divided by 255 twice")
        jpg = next((out / "cal_images").glob("*.jpg"))
        bgr = cv2.imread(str(jpg))
        if bgr is None or bgr.shape[:2] != (HEIGHT, WIDTH):
            raise AssertionError("saved calibration JPG is missing or the wrong size")
        # JPEG is lossy; the tensor path above is the exact domain check.
        if int(np.abs(bgr.astype(np.int16) - np.array([40, 80, 200])).max()) > 8:
            raise AssertionError("saved calibration JPG is not the source BGR image")


def main() -> int:
    check_yaml_text()
    check_files()
    print("cal domain file checks passed (OE compilers were not run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
