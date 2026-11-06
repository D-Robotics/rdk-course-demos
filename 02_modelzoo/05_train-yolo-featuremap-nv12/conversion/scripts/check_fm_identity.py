#!/usr/bin/env python3
"""Check one calibration tensor and, when asked, one model file.

The public course repo does not contain remote_x5_fm_infer.sh or
push_artifacts_to_boards.sh. This checker does not deploy those scripts.

A model is identified only by --expect-sha256 or by --manifest. No hash is
built in as a bad file. A historical bin whose values were already correct
passes when the caller pins that hash, and fails when the caller pins a
different one. With neither flag, the command prints the sha256 and says
identity was not pinned. That is not a current-mainline check.

Calibration roles (default shape 1x3x640x640 float32 NCHW):

  x5-fm, s100-fm   no_preprocess. Values must be in [0, 1].
  x5-nv12          pre-scale RGB. Values must be in [0, 255]. A dark image
                   whose maximum is below 1 is still inside that range.
  s100-nv12        already divided by 255 once. Values must be in [0, 1].

X5 roles read a raw float32 file. S100 roles read a .npy file. --container
overrides that. --shape overrides the default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

DEFAULT_SHAPE = (1, 3, 640, 640)
ROLES = ("x5-fm", "s100-fm", "x5-nv12", "s100-nv12")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_shape(text: str) -> tuple[int, ...]:
    parts = tuple(int(item) for item in text.lower().replace(",", "x").split("x") if item)
    if len(parts) != 4 or any(item <= 0 for item in parts):
        raise SystemExit(f"--shape must be four positive sizes such as 1x3x640x640, got {text!r}")
    return parts


def manifest_value(document: object, key: str) -> str:
    current = document
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise SystemExit(f"manifest has no {key}")
        current = current[part]
    if not isinstance(current, str) or len(current) != 64:
        raise SystemExit(f"manifest key {key} is not a sha256 hex string")
    return current.lower()


def load_manifest(path: Path, key: str) -> str:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: manifest is not JSON ({exc})") from exc
    return manifest_value(document, key)


def container_for(role: str) -> str:
    return "npy" if role.startswith("s100-") else "raw"


def limits_for(role: str) -> tuple[float, float]:
    if role == "x5-nv12":
        return 0.0, 255.0
    return 0.0, 1.0


def load_tensor(path: Path, shape: tuple[int, ...], container: str) -> np.ndarray:
    raw = path.read_bytes()
    is_npy = raw.startswith(b"\x93NUMPY")
    if container == "raw" and is_npy:
        raise SystemExit(f"{path}: file is a NumPy array; this role expects raw float32")
    if container == "npy" and not is_npy:
        raise SystemExit(f"{path}: file is not a NumPy array; this role expects .npy float32")
    if container == "npy":
        try:
            values = np.load(path)
        except Exception as exc:
            raise SystemExit(f"{path}: cannot read npy ({exc})") from exc
        if values.size == 0:
            raise SystemExit(f"{path}: npy array is empty")
        if values.dtype != np.float32:
            raise SystemExit(f"{path}: dtype is {values.dtype}, expected float32")
        if tuple(int(item) for item in values.shape) != shape:
            raise SystemExit(f"{path}: shape {tuple(values.shape)} != {shape}")
        return values
    count = int(np.prod(shape, dtype=np.int64))
    if len(raw) != count * np.dtype(np.float32).itemsize:
        raise SystemExit(
            f"{path}: {len(raw)} bytes is not float32 {shape} "
            f"({count * np.dtype(np.float32).itemsize} bytes)"
        )
    return np.fromfile(path, dtype=np.float32).reshape(shape)


def check_cal(path: Path, role: str, shape: tuple[int, ...], container: str) -> None:
    values = load_tensor(path, shape, container)
    if not bool(np.isfinite(values).all()):
        raise SystemExit(f"{path}: values must be finite (no NaN or Inf)")
    lowest = float(values.min())
    highest = float(values.max())
    floor, ceiling = limits_for(role)
    if lowest < floor - 1e-6 or highest > ceiling + 1e-6:
        raise SystemExit(
            f"{path}: {role} values [{lowest:.6g}, {highest:.6g}] "
            f"are outside [{floor:g}, {ceiling:g}] for shape {shape}"
        )


def check_model(path: Path, expected: str | None) -> str:
    digest = sha256_file(path)
    if expected is None:
        print(f"model sha256: {digest}")
        print(
            "identity not pinned: no --expect-sha256 or --manifest. "
            "This run did not verify current-mainline identity."
        )
        return digest
    if digest != expected:
        raise SystemExit(f"{path}: sha256 {digest} != expected {expected}")
    print(f"model identity matches {digest}")
    return digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True, choices=ROLES)
    parser.add_argument("--cal", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--shape", default="1x3x640x640")
    parser.add_argument("--container", choices=("raw", "npy"))
    parser.add_argument("--expect-sha256")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-key", default="model_sha256")
    args = parser.parse_args(argv)
    if args.cal is None and args.model is None:
        raise SystemExit("pass --cal and/or --model")
    shape = parse_shape(args.shape)
    expected = args.expect_sha256.lower() if args.expect_sha256 else None
    if args.manifest is not None:
        from_manifest = load_manifest(args.manifest, args.manifest_key)
        if expected and expected != from_manifest:
            raise SystemExit("--expect-sha256 and --manifest name different hashes")
        expected = from_manifest
    if args.cal is not None:
        check_cal(args.cal, args.role, shape, args.container or container_for(args.role))
        print(f"cal ok: {args.cal} {args.role} {shape}")
    if args.model is not None:
        check_model(args.model, expected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
