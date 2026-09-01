#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a sine test tone as a standard 16-bit WAV, no dependencies.

The S100 loopback check needs a format-aligned tone to play while recording:

    python3 make_tone.py --freq 1000 --seconds 30 --out 1khz.wav
    aplay -Dhw:0,1 1khz.wav --period-size=1024 --buffer-size=1024

Keep the playback format aligned with the 8ch recording (same sample rate,
16-bit, 2ch playback on hw:0,1).
"""

import argparse
import math
import struct
import sys
import wave


def main():
    ap = argparse.ArgumentParser(
        description="Generate a sine tone wav for the S100 loopback check.")
    ap.add_argument("--freq", type=int, default=1000,
                    help="tone frequency in Hz (default 1000)")
    ap.add_argument("--seconds", type=float, default=30,
                    help="duration in seconds (default 30)")
    ap.add_argument("--rate", type=int, default=48000,
                    help="sample rate, keep aligned with your recording "
                         "(default 48000)")
    ap.add_argument("--out", default="1khz.wav", help="output wav path")
    args = ap.parse_args()

    n = int(args.rate * args.seconds)
    amplitude = 0.8 * 32767  # leave headroom, avoid clipping
    with wave.open(args.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(args.rate)
        frames = bytearray()
        for i in range(n):
            v = int(amplitude * math.sin(2 * math.pi * args.freq * i / args.rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))
    print("wrote {} ({} Hz, {}s, {} Hz, 2ch, 16-bit)".format(
        args.out, args.freq, args.seconds, args.rate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
