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
        train = expect / 255.0
        assert_close("x5 featuremap matches ONNX 0..1", x5_fm, train)
        assert_close("s100 featuremap matches ONNX 0..1", s_fm, train)
        assert_close("x5 and s100 featuremap share the 0..1 domain", x5_fm, s_fm)
        assert_close("x5 nv12 stays 0..255", x5_nv12, expect)
        assert_close("s100 nv12 stays a single /255", s_nv12, train)
        if np.allclose(x5_fm, x5_nv12):
            raise AssertionError("X5 featuremap must not reuse the NV12 0..255 file")
        if float(x5_fm.max()) > 1.0 or float(x5_nv12.max()) <= 1.0:
            raise AssertionError("X5 featuremap and X5 NV12 collapsed onto one domain")
        if np.allclose(s_nv12, train / 255.0):
            raise AssertionError("S100 NV12 file was divided by 255 twice")
        # Containers stay different: raw tofile versus npy, even when values match.
        x5_path = next((out / "cal_featuremap_x5_rgbchw").glob("*.rgbchw"))
        if x5_path.read_bytes()[:6] == b"\x93NUMPY":
            raise AssertionError("X5 featuremap must stay a raw .rgbchw, not an .npy")
        if not str(next((out / "cal_featuremap_s100_npy").glob("*.npy"))).endswith(".npy"):
            raise AssertionError("S100 featuremap suffix changed")
        jpg = next((out / "cal_images").glob("*.jpg"))
        bgr = cv2.imread(str(jpg))
        if bgr is None or bgr.shape[:2] != (HEIGHT, WIDTH):
            raise AssertionError("saved calibration JPG is missing or the wrong size")
        # JPEG is lossy; the tensor path above is the exact domain check.
        if int(np.abs(bgr.astype(np.int16) - np.array([40, 80, 200])).max()) > 8:
            raise AssertionError("saved calibration JPG is not the source BGR image")


def check_cosine_does_not_prove_domain() -> None:
    """A positive scale leaves cosine at 1 while the values change.

    This is why a high cosine between a wrong-domain bin and ORT is not a
    pass. The historical board figures are not re-run here.
    """
    values = np.array([1.11, -0.4, 0.2], dtype=np.float64)
    scaled = values * 255.0
    cosine = float(np.dot(values, scaled) / (np.linalg.norm(values) * np.linalg.norm(scaled)))
    if abs(cosine - 1.0) > 1e-9:
        raise AssertionError(f"expected cosine 1 for a positive scale, got {cosine}")
    if np.max(np.abs(scaled)) <= np.max(np.abs(values)):
        raise AssertionError("scaled vector should leave the original magnitude")


def check_identity_gate() -> None:
    """The public checker refuses the old 0..255 featuremap domain and the historical bin."""
    checker = Path(__file__).resolve().parent / "check_fm_identity.py"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        raw = np.full((1, 3, 2, 2), 200.0, dtype=np.float32)
        unit = raw / 255.0
        old_fm = root / "old.rgbchw"
        new_fm = root / "new.rgbchw"
        nv12 = root / "nv12.rgbchw"
        old_fm.write_bytes(raw.tobytes())
        new_fm.write_bytes(unit.tobytes())
        nv12.write_bytes(raw.tobytes())
        bad = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-fm", "--cal", str(old_fm)],
            capture_output=True, text=True,
        )
        if bad.returncode == 0:
            raise AssertionError("0..255 featuremap file was accepted")
        ok = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-fm", "--cal", str(new_fm)],
            capture_output=True, text=True,
        )
        if ok.returncode != 0:
            raise AssertionError(ok.stderr or ok.stdout)
        swapped = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-nv12", "--cal", str(new_fm)],
            capture_output=True, text=True,
        )
        if swapped.returncode == 0:
            raise AssertionError("0..1 file was accepted as X5 NV12")
        nv12_ok = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-nv12", "--cal", str(nv12)],
            capture_output=True, text=True,
        )
        if nv12_ok.returncode != 0:
            raise AssertionError(nv12_ok.stderr or nv12_ok.stdout)
        historical = root / "historical.bin"
        historical.write_bytes(b"not-the-mainline-bin")
        digest_proc = subprocess.run(
            ["sha256sum", str(historical)], capture_output=True, text=True, check=True,
        )
        digest = digest_proc.stdout.split()[0]
        rejected = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-fm", "--model", str(historical),
             "--expect-sha256", "0" * 64],
            capture_output=True, text=True,
        )
        if rejected.returncode == 0:
            raise AssertionError("mismatched model sha was accepted")
        pinned = subprocess.run(
            [sys.executable, str(checker), "--role", "x5-fm", "--model", str(historical),
             "--expect-sha256", digest],
            capture_output=True, text=True,
        )
        if pinned.returncode != 0:
            raise AssertionError(pinned.stderr or pinned.stdout)


def main() -> int:
    check_yaml_text()
    check_files()
    check_cosine_does_not_prove_domain()
    check_identity_gate()
    print("cal domain file checks passed (OE compilers were not run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
