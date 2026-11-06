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


def run_checker(checker: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(checker), *args],
        capture_output=True, text=True,
    )


def check_identity_gate() -> None:
    """Contract checks. A matching hash is not a blacklist, and a dark NV12 image is legal."""
    import hashlib

    checker = Path(__file__).resolve().parent / "check_fm_identity.py"
    shape = (1, 3, 8, 8)
    shape_arg = "1x3x8x8"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        def raw_file(name: str, values: np.ndarray) -> Path:
            path = root / name
            path.write_bytes(np.ascontiguousarray(values, dtype=np.float32).tobytes())
            return path

        def npy_file(name: str, values: np.ndarray) -> Path:
            path = root / name
            np.save(path, np.ascontiguousarray(values))
            return path

        unit = np.full(shape, 0.25, dtype=np.float32)
        wide = np.full(shape, 200.0, dtype=np.float32)
        dark = np.full(shape, 0.2, dtype=np.float32)
        fm = raw_file("fm.rgbchw", unit)
        old = raw_file("old.rgbchw", wide)
        nv12 = raw_file("nv12.rgbchw", wide)
        dark_nv12 = raw_file("dark.rgbchw", dark)
        s_nv12 = npy_file("s_nv12.npy", unit)

        rejected_domain = run_checker(checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(old))
        if rejected_domain.returncode == 0:
            raise AssertionError("0..255 featuremap file was accepted")
        current = run_checker(checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(fm))
        if current.returncode != 0:
            raise AssertionError(current.stderr or current.stdout)
        full = np.zeros((1, 3, 640, 640), dtype=np.float32)
        full_path = raw_file("full.rgbchw", full)
        full_ok = run_checker(checker, "--role", "x5-fm", "--cal", str(full_path))
        if full_ok.returncode != 0:
            raise AssertionError(full_ok.stderr or full_ok.stdout)

        historical = root / "historical.bin"
        historical.write_bytes(b"round3-aee-stand-in")
        historical_sha = hashlib.sha256(historical.read_bytes()).hexdigest()
        pinned = run_checker(
            checker, "--role", "x5-fm", "--model", str(historical),
            "--expect-sha256", historical_sha,
        )
        if pinned.returncode != 0 or "matches" not in pinned.stdout:
            raise AssertionError(pinned.stderr or pinned.stdout)
        wrong = run_checker(
            checker, "--role", "x5-fm", "--model", str(historical),
            "--expect-sha256", "0" * 64,
        )
        if wrong.returncode == 0:
            raise AssertionError("mismatched model sha was accepted")
        unpinned = run_checker(checker, "--role", "x5-fm", "--model", str(historical))
        if unpinned.returncode != 0 or "identity not pinned" not in unpinned.stdout:
            raise AssertionError(unpinned.stderr or unpinned.stdout)
        if "matches" in unpinned.stdout:
            raise AssertionError("unpinned run claimed an identity match")
        manifest = root / "manifest.json"
        manifest.write_text(json_dumps({"model_sha256": historical_sha}), encoding="utf-8")
        via_manifest = run_checker(
            checker, "--role", "x5-fm", "--model", str(historical), "--manifest", str(manifest),
        )
        if via_manifest.returncode != 0:
            raise AssertionError(via_manifest.stderr or via_manifest.stdout)

        nan = unit.copy()
        nan.flat[0] = np.nan
        nan_path = raw_file("nan.rgbchw", nan)
        if run_checker(checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(nan_path)).returncode == 0:
            raise AssertionError("NaN featuremap was accepted")
        empty_npy = root / "empty.npy"
        np.save(empty_npy, np.zeros((0,), dtype=np.float32))
        if run_checker(checker, "--role", "s100-fm", "--cal", str(empty_npy)).returncode == 0:
            raise AssertionError("empty npy was accepted")
        empty_raw = root / "empty.rgbchw"
        empty_raw.write_bytes(b"")
        if run_checker(checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(empty_raw)).returncode == 0:
            raise AssertionError("empty raw file was accepted")
        bad_dtype = npy_file("f64.npy", unit.astype(np.float64))
        if run_checker(checker, "--role", "s100-fm", "--shape", shape_arg, "--cal", str(bad_dtype)).returncode == 0:
            raise AssertionError("float64 npy was accepted")
        nhwc = np.transpose(unit, (0, 2, 3, 1))
        nhwc_path = npy_file("nhwc.npy", nhwc)
        if run_checker(checker, "--role", "s100-fm", "--shape", shape_arg, "--cal", str(nhwc_path)).returncode == 0:
            raise AssertionError("NHWC shape was accepted as NCHW")
        negative = unit.copy()
        negative.flat[0] = -0.01
        if run_checker(
            checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(raw_file("neg.rgbchw", negative)),
        ).returncode == 0:
            raise AssertionError("negative featuremap was accepted")
        if run_checker(checker, "--role", "x5-fm", "--shape", shape_arg, "--cal", str(npy_file("fm.npy", unit))).returncode == 0:
            raise AssertionError("npy container was accepted for x5-fm")

        if run_checker(checker, "--role", "x5-nv12", "--shape", shape_arg, "--cal", str(nv12)).returncode != 0:
            raise AssertionError("legal 0..255 X5 NV12 file was rejected")
        if run_checker(checker, "--role", "x5-nv12", "--shape", shape_arg, "--cal", str(dark_nv12)).returncode != 0:
            raise AssertionError("dark X5 NV12 image was rejected")
        bright = np.full(shape, 300.0, dtype=np.float32)
        if run_checker(
            checker, "--role", "x5-nv12", "--shape", shape_arg, "--cal", str(raw_file("hi.rgbchw", bright)),
        ).returncode == 0:
            raise AssertionError("X5 NV12 value above 255 was accepted")
        if run_checker(checker, "--role", "s100-nv12", "--shape", shape_arg, "--cal", str(s_nv12)).returncode != 0:
            raise AssertionError("legal S100 NV12 0..1 file was rejected")
        if run_checker(
            checker, "--role", "s100-nv12", "--shape", shape_arg, "--cal", str(npy_file("wide.npy", wide)),
        ).returncode == 0:
            raise AssertionError("0..255 file was accepted as S100 NV12")


def json_dumps(payload: dict[str, str]) -> str:
    import json
    return json.dumps(payload)


def main() -> int:
    check_yaml_text()
    check_files()
    check_cosine_does_not_prove_domain()
    check_identity_gate()
    print("cal domain file checks passed (OE compilers were not run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
