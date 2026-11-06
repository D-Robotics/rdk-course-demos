#!/usr/bin/env python3
"""Fail fast on an X5/S100 featuremap file or a compiled artifact.

The public course repo does not contain remote_x5_fm_infer.sh or
push_artifacts_to_boards.sh. Run this checker yourself before those private
scripts. It does not deploy anything and it does not know a machine path.

Roles:
  x5-fm, s100-fm     no_preprocess input. Values must already be 0..1.
                     A file whose max is above 1 is the old 0..255 domain.
  x5-nv12            pre-scale RGB. The 0..1 featuremap rule is not applied.
                     A file whose max is at most 1 is refused, because that
                     is the featuremap file, not the X5 NV12 file.
  s100-nv12          already /255 once. A file whose max is above 1 was
                     prepared with the X5 NV12 rule and is refused.

Pass --expect-sha256 to pin a model file. The known historical X5 bin
aee69bc13281483525a62c38121e1612128aceb7d399d261af5cddcec0336b75 is refused
when you pass --model for role x5-fm.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np

HISTORICAL_X5_FM_BIN = (
    "aee69bc13281483525a62c38121e1612128aceb7d399d261af5cddcec0336b75"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_tensor(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    if raw.startswith(b"\x93NUMPY"):
        return np.load(path)
    data = np.fromfile(path, dtype=np.float32)
    if data.size == 0 or data.size % 3 != 0:
        raise SystemExit(f"{path}: not a float32 RGB tensor")
    return data


def check_cal(path: Path, role: str, *, allow_unit_nv12: bool) -> None:
    values = load_tensor(path)
    finite = np.isfinite(values)
    if not bool(finite.all()):
        raise SystemExit(f"{path}: calibration tensor has non-finite values")
    lowest = float(values.min())
    highest = float(values.max())
    if role in {"x5-fm", "s100-fm"}:
        if lowest < -1e-6 or highest > 1.0 + 1e-6:
            raise SystemExit(
                f"{path}: {role} max={highest:.4g}. no_preprocess requires "
                "0..1. This looks like the old 0..255 featuremap file."
            )
        return
    if role == "x5-nv12":
        if highest <= 1.0 and not allow_unit_nv12:
            raise SystemExit(
                f"{path}: x5-nv12 max={highest:.4g}. Refusing a 0..1 file. "
                "X5 NV12 keeps 0..255 and lets HzPreprocess scale it. "
                "Pass --allow-unit-nv12 only for a genuinely dark image."
            )
        return
    if role == "s100-nv12":
        if highest > 1.0 + 1e-6:
            raise SystemExit(
                f"{path}: s100-nv12 max={highest:.4g}. Do not reuse the "
                "X5 NV12 0..255 file here."
            )
        return
    raise SystemExit(f"unknown role {role}")


def check_model(path: Path, role: str, expect: str | None) -> str:
    digest = sha256(path)
    if role == "x5-fm" and digest == HISTORICAL_X5_FM_BIN:
        raise SystemExit(
            f"{path}: sha256 {digest} is the historical X5 featuremap bin "
            "(31.316 ms round). The current cast uses a different bin."
        )
    if expect and digest != expect.lower():
        raise SystemExit(f"{path}: sha256 {digest} != expected {expect.lower()}")
    return digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True, choices=("x5-fm", "s100-fm", "x5-nv12", "s100-nv12"))
    parser.add_argument("--cal", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--expect-sha256")
    parser.add_argument("--allow-unit-nv12", action="store_true")
    args = parser.parse_args(argv)
    if args.cal is None and args.model is None:
        raise SystemExit("pass --cal and/or --model")
    if args.cal is not None:
        check_cal(args.cal, args.role, allow_unit_nv12=args.allow_unit_nv12)
        print(f"cal ok: {args.cal}")
    if args.model is not None:
        digest = check_model(args.model, args.role, args.expect_sha256)
        print(f"model ok: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
