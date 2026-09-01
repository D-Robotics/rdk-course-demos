#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""8-channel loopback analyzer for the Waveshare Audio Driver HAT REV2 on RDK S100.

Reads an 8-channel S16_LE WAV recorded with:

    arecord -Dhw:0,0 -c 8 -r 48000 -f S16_LE -t wav -d 30 ./8chn_capture.wav \
        --period-size=256 --buffer-size=1024

(played against a 1 kHz tone on hw:0,1, see make_tone.py) and reports, per
channel: peak, RMS, and the dominant frequency estimated from the zero-crossing
rate. It then prints PASS/FAIL verdicts:

  - mic capture OK   if any of ch1-ch4 carries signal above the RMS threshold
  - loopback OK      if any of ch7-ch8 carries signal above the threshold
                       AND its dominant frequency is close to the played tone

Pure standard library (wave + array + math) so it runs on the board itself.

Usage:
    python3 analyze_loopback.py 8chn_capture.wav
    python3 analyze_loopback.py 8chn_capture.wav --min-rms 200 --tone-freq 1000
"""

import argparse
import array
import math
import sys
import wave

BAR_WIDTH = 24
FREQ_TOLERANCE = 0.15  # dominant frequency must be within +/-15% of the tone


def read_wav(path):
    """Return (num_channels, sample_rate, list_of_per_channel_arrays)."""
    with wave.open(path, "rb") as w:
        nch = w.getnchannels()
        width = w.getsampwidth()
        rate = w.getframerate()
        nframes = w.getnframes()
        if width != 2:
            sys.exit("error: expected 16-bit PCM (S16_LE), got {}-bit. "
                     "Record with -f S16_LE.".format(width * 8))
        if nch != 8:
            sys.exit("error: expected 8 channels (arecord -c 8), got {}. "
                     "Loopback lives on ch7/ch8, which only exist in 8ch "
                     "recordings.".format(nch))
        raw = w.readframes(nframes)
    samples = array.array("h")
    samples.frombytes(raw)
    channels = [samples[c::nch] for c in range(nch)]
    return nch, rate, channels


def dominant_freq(samples, rate):
    """Estimate the dominant frequency via the zero-crossing rate.

    Good enough for a clean sine test tone, and dependency-free.
    """
    crossings = 0
    prev = samples[0]
    for s in samples[1:]:
        if (prev < 0) != (s < 0):
            crossings += 1
        prev = s
    duration = len(samples) / float(rate)
    if duration <= 0:
        return 0.0
    return crossings / (2.0 * duration)


def analyze(channels, rate):
    stats = []
    for ch in channels:
        n = len(ch)
        peak = 0
        acc = 0.0
        for s in ch:
            a = -s if s < 0 else s
            if a > peak:
                peak = a
            acc += s * s
        rms = math.sqrt(acc / n) if n else 0.0
        freq = dominant_freq(ch, rate)
        stats.append((peak, rms, freq))
    return stats


def bar(value, vmax):
    filled = int(BAR_WIDTH * value / vmax) if vmax > 0 else 0
    return "#" * filled


def main():
    ap = argparse.ArgumentParser(
        description="Analyze an 8ch capture from the S100 Audio Driver HAT "
                    "REV2 and verify mic + loopback channels.")
    ap.add_argument("wav", help="8ch S16_LE wav file (arecord -c 8 ...)")
    ap.add_argument("--min-rms", type=int, default=100,
                    help="RMS threshold for 'signal present' "
                         "(16-bit LSB, default 100)")
    ap.add_argument("--tone-freq", type=int, default=1000,
                    help="frequency of the tone played during capture "
                         "(Hz, default 1000)")
    args = ap.parse_args()

    nch, rate, channels = read_wav(args.wav)
    duration = len(channels[0]) / float(rate)
    stats = analyze(channels, rate)
    vmax = max(s[1] for s in stats) or 1

    print("file        : {}".format(args.wav))
    print("format      : {}ch / {} Hz / 16-bit / {:.1f}s".format(
        nch, rate, duration))
    print("threshold   : RMS >= {} ; tone = {} Hz (+/-{:.0f}%)".format(
        args.min_rms, args.tone_freq, FREQ_TOLERANCE * 100))
    print()
    print("channel   peak      RMS        est.freq    level")
    print("-" * 60)
    for i, (peak, rms, freq) in enumerate(stats, start=1):
        print("ch{}        {:6d}   {:8.1f}   {:7.0f} Hz   {}".format(
            i, peak, rms, freq, bar(rms, vmax)))
    print()

    mic = stats[0:4]
    loop = stats[6:8]
    mid = stats[4:6]

    failures = []

    if any(rms >= args.min_rms for _, rms, _ in mic):
        print("[PASS] mic capture      : signal on ch1-ch4")
    else:
        print("[FAIL] mic capture      : no signal on ch1-ch4")
        failures.append("mic")

    loop_ok = any(rms >= args.min_rms and
                  abs(freq - args.tone_freq) <= FREQ_TOLERANCE * args.tone_freq
                  for _, rms, freq in loop)
    if loop_ok:
        print("[PASS] loopback         : 1kHz reference on ch7-ch8")
    else:
        print("[FAIL] loopback         : expected ~{} Hz on ch7-ch8 "
              "while playing the tone".format(args.tone_freq))
        failures.append("loopback")

    quiet_mid = all(rms < args.min_rms for _, rms, _ in mid)
    print("[INFO] ch5-ch6          : {} (unused on this board, expected "
          "quiet)".format("quiet" if quiet_mid else "carrying signal"))

    print()
    if failures:
        print("Result: FAIL ({})".format(", ".join(failures)))
        print("Check the DIP switches first (40 PIN left / PCM right), then "
              "the four modprobe commands, then the recording/playback format "
              "alignment. See the handbook FAQ.")
        return 1
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
