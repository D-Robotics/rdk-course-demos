# Audio Driver HAT on RDK S100

> **About this lesson:** Install the Audio Driver HAT REV2 on the RDK S100, load its drivers, identify the sound card, complete a record → playback loop, and go further with 8-channel capture and playback loopback (the AEC reference signal).
>
> **Target hardware:** RDK S100
>
> **System version:** RDK OS (S100)
>
> **Related resources:** Video walkthrough (in production) / This handbook / [Official audio documentation](https://developer.d-robotics.cc/rdk_doc_center/)

---

Adding "listening" and "speaking" to a robot usually starts with a 40pin audio HAT. On the RDK S100, new users rarely get stuck on the commands themselves — they get stuck on three things: the HAT is attached but no sound card appears; it is unclear which device number records and which plays; and the loopback signal that echo cancellation needs is nowhere to be found. This lesson walks the full path in order — recon first, then operate, then verify.

## 1. Learning Objectives

After completing this lesson, you will be able to:

1. Describe the role of each chip on the board (2× ES7210 for capture, 1× ES8156 for playback)
2. Complete the 40pin physical connection and DIP-switch switchover (40 PIN switch left, PCM switch right)
3. Load the audio drivers with `modprobe` and confirm card `s100snd2` via `cat /proc/asound/cards` and `ls /dev/snd/`
4. Complete a record → playback loop with `arecord` / `aplay`, and explain the device numbering: capture on `hw:0,0`, playback on `hw:0,1`
5. Query and adjust playback volume with `amixer`
6. Record 8 channels, locate the loopback signal on channels 7–8, and verify it in Audacity
7. Troubleshoot the three common failure classes: no card, device won't open, no sound

## 2. Required Materials

| Item | Qty | Notes |
|------|-----|-------|
| RDK S100 | 1 | Flashed and accessible via SSH |
| Waveshare Audio Driver HAT REV2 | 1 | 40pin attachment; 2× ES7210 + 1× ES8156 |
| Headphones or speaker | 1 | 3.5mm interface on the HAT |
| (Optional) Analog microphones | 4 | For the mic-array channels |

## 3. Audio System Overview: Reconnaissance First

The S100 audio module is built on the standard ALSA framework, with user-space tools from alsa-lib: `arecord`, `aplay`, and `amixer`. Every recording and playback operation ultimately goes through three layers:

```text
Card                     — one physical audio device = one number
  └─ PCM device          — functional endpoint on the card, playback or capture
       └─ Device node    — a file under /dev/snd/, what programs actually open
```

For example, `pcmC0D0c` means "card 0, PCM device 0, capture endpoint" (c = capture, p = playback). Once you understand this naming rule, the command parameters stop being guesswork.

Before touching any configuration, memorize these three commands — every section of this lesson uses them:

```shell
# 1. List registered sound cards (the most important one)
cat /proc/asound/cards

# 2. List device nodes in user space
ls /dev/snd/

# 3. List capture / playback devices
arecord -l
aplay -l
```

**Why reconnaissance matters:** when you use the `-D hw:X,Y` parameter, X is the card number from `cat /proc/asound/cards`, and Y is the device number from `arecord -l` / `aplay -l`. Reconnoiter first, then operate — your parameters always have a source.

### Device-Number Direction on the S100

Once the HAT is attached and its drivers are loaded, the S100 registers one sound card with two PCM endpoints:

| Device node | Meaning | hw argument | Used by |
|---|---|---|---|
| `pcmC0D0c` | card 0 · device 0 · capture | `hw:0,0` | `arecord` |
| `pcmC0D1p` | card 0 · device 1 · playback | `hw:0,1` | `aplay` |

Note the direction: **capture lives on `hw:0,0`, playback on `hw:0,1`.** Many tutorials assume "0,0 is playback" — copy that onto the S100 and the device simply won't open. Don't memorize the answer: check the trailing `c` / `p` in `ls /dev/snd/` every time, and the direction can never be wrong.

## 4. Meet the Audio HAT: Two Capture Codecs + One Playback Codec

The board used in this lesson is the Waveshare **Audio Driver HAT REV2**, attached to the S100 through the 40pin header. Its audio chips come in two groups:

| Chip | Count | I2C address | Role | Channels |
|---|---|---|---|---|
| ES7210 | 2 | 0x40 / 0x42 | Capture | Up to 8 ch: 4 analog mic inputs + 2 AEC loopback |
| ES8156 | 1 | 0x8 | Playback | 2 ch, to headphones or speaker |

Keep this division of labor in mind and every later observation lines up:

- Capture goes through the **ES7210** pair — 8-channel recording, the mic array, and loopback all live on the capture device;
- Playback goes through **ES8156**, 2 channels only, to headphones or a speaker;
- Four analog microphones pick up sound, and two channels capture "what the speaker actually plays" — that is exactly the reference signal echo-cancellation algorithms need.

## 5. Hardware Installation: 40pin Connection and the DIP Switches

### 5.1 Physical Connection

With the board powered off, align the HAT with the S100's 40pin header and press it in firmly.

### 5.2 DIP Switches: Pin-Function Switchover

**Key point: on the S100's 40pin header, the PCM audio pins are multiplexed with the PCIE Wi-Fi module pins.** A hardware DIP switch decides which function owns these pins. Before attaching the audio HAT, switch them to the PCM side:

```text
Upper "40 PIN" switch  →  slide LEFT
Lower "PCM" switch     →  slide RIGHT
```

Move both switches — flipping only one does not complete the switchover.

> **What happens if you get it wrong?** The pins remain connected to the Wi-Fi side. The HAT is physically attached but electrically disconnected — the drivers load fine, yet the card may never appear, or recordings come back all zeros. When "the HAT is attached but nothing happens," check the DIP switches first.

## 6. Driver Loading and Device Identification

### 6.1 Load the Drivers

On the S100, the sound card modules ship as kernel modules (ko) and are loaded dynamically:

```shell
modprobe hobot_cpudai_super
modprobe snd-soc-es8156
modprobe snd-soc-es7210
modprobe hobot_snd_super_ac_fdx_host
```

The four commands correspond to four stages of the driver chain: CPU DAI (I2S controller) → playback Codec → capture Codec → sound-card assembly. Only after the last one does the card exist.

### 6.2 Verify by Reconnaissance

```shell
# 1. Card list: s100snd2 appears = drivers loaded
root@ubuntu:~# cat /proc/asound/cards
 0 [s100snd2       ]: s100snd2 - s100snd2
                      s100snd2

# 2. Device nodes: one capture, one playback, one control
root@ubuntu:~# ls /dev/snd/
controlC0  pcmC0D0c  pcmC0D1p  timer
```

Map these against the direction table in section 3: `pcmC0D0c` → capture on `hw:0,0`; `pcmC0D1p` → playback on `hw:0,1`.

## 7. Record and Play: The Simplest Loop

### 7.1 Recording

```shell
# Record 5 seconds, 48kHz / 2ch / 16bit, saved as wav
arecord -Dhw:0,0 -c 2 -r 48000 -f S16_LE -t wav -d 5 test.wav
```

Parameter by parameter: `-D hw:0,0` device (from recon), `-c 2` channels, `-r 48000` sample rate, `-f S16_LE` sample format, `-t wav` file type, `-d 5` duration in seconds. Adjust the data format to your needs.

### 7.2 Playback

```shell
aplay -Dhw:0,1 test.wav
```

`aplay` parses the wav header to determine the format and feeds the driver, so the playback command does not need to repeat channels or sample rate.

**Success criteria:** the terminal prints `Recording WAVE ...` with no errors while recording; you clearly hear the recording during playback.

> **Why record in 16bit (S16_LE)?**
>
> If you record in 24bit (S24_LE), playback on the board with `aplay` sounds fine, but the file may be pure noise on your computer: ALSA's S24_LE means "24bit stored in a 32bit container" (4 bytes per sample), while the WAV standard's 24bit is 3 bytes per sample. `arecord` writes a file whose header says 24bit but whose data is 4 bytes per sample, so computer players slice it at 3 bytes and everything misaligns. The board round-trips consistently — that doesn't make the file standard. **Recording in 16bit (S16_LE) works everywhere.**

### 7.3 Volume Control (amixer)

```shell
# List all controls of the current codec and their values
amixer scontrols
amixer scontents

# Adjust playback volume (the DAC control, for example)
amixer sset 'DAC' 120
amixer sget 'DAC'
```

As always, confirm the target card first — in multi-card setups use `amixer -c 0 ...` so you adjust the right one.

## 8. Advanced: 8-Channel Capture and Loopback

### 8.1 What Loopback Is and Why You Need It

Loopback captures "the signal on the playback path" as a reference for algorithms such as echo cancellation (AEC). On this board, the loopback signal is mapped to **capture channels 7 and 8**.

| Channels | Purpose |
|---|---|
| ch1–ch4 | 4 analog microphones |
| ch7–ch8 | Playback loopback reference |

### 8.2 8-Channel Recording

```shell
arecord -Dhw:0,0 -c 8 -r 48000 -f S16_LE -t wav -d 5 ./8chn_test.wav --period-size=256 --buffer-size=1024
```

Watch `--period-size`: the S100 PDMA driver requires data sizes to be **64-byte aligned**, so the period-size value must satisfy this alignment or the transfer will not work properly.

### 8.3 Verify Loopback with Simultaneous Playback

The loopback records "what the playback path carries," so play while recording, and keep **channels, bit depth, and sample rate aligned on the same I2S** (this board fixes one I2S lane according to its DIP switches):

```shell
# Terminal A: start the 8-channel recording (leave enough time to switch to Terminal B)
arecord -Dhw:0,0 -c 8 -r 48000 -f S16_LE -t wav -d 30 ./8chn_capture.wav --period-size=256 --buffer-size=1024

# Terminal B: simultaneously play a format-aligned file (e.g. a homemade 1kHz sine wave)
aplay -Dhw:0,1 1khz.wav --period-size=1024 --buffer-size=1024
```

After recording, open `8chn_capture.wav` in an audio analysis tool such as Audacity:

- ch1–ch4 carry the sound picked up by the microphones → the mic path works;
- ch7–ch8 show the same 1kHz spectrum as the played content → loopback works.

**Success criteria:** the 8-channel file is generated; speaking into the mics produces waveforms on ch1–ch4, and playing audio produces the matching signal on ch7–ch8.

## 9. Troubleshooting

**Q1: The HAT is attached, but `cat /proc/asound/cards` shows no `s100snd2`?**

Check three things in order: ① the DIP switches — is the 40 PIN switch left and the PCM switch right; ② did all four `modprobe` commands run without errors; ③ does `dmesg` show a codec/I2S probe failure.

**Q2: Opening the device node fails?**

- `cannot open device ... No such file or directory`: the drivers didn't load, or the card/device numbers are wrong — go back to the recon commands;
- `cannot set hw params: Unknown error -22`: a parameter (rate/format/channels) exceeds the driver's supported range — use supported values;
- Opening the node hangs with no log output: ALSA allows each device to be opened only once at a time — check for a previous process that never exited.

**Q3: The command succeeds but there is no sound?**

Check in order: ① is the target card number right (recon again); ② did you use `hw:0,1` for playback (not 0,0); ③ is the volume turned to zero via `amixer`; ④ does the file format match the device capability.

**Q4: Crackling or choppy audio during record/playback?**

Most likely an xrun (underrun on playback / overrun on capture: the application can't keep up with the hardware). Try a larger period-size, or write recordings to faster storage to rule out IO bottlenecks; if it happens constantly, investigate the driver or application further.

**Q5: What do pcm_read/pcm_write return codes -5 / -32 / -16 mean?**

-5: DMA or interrupt trouble (check register configuration and the hardware link); -32: an xrun occurred; -16: the clock dropped or the hardware connection broke during recording (with the S100 acting as slave).

## 10. Summary

One through-line for the whole lesson:

```text
Hardware in place (40pin aligned + DIP switchover: 40PIN left / PCM right)
   ↓
Drivers loaded (modprobe ×4 → s100snd2 appears in cards)
   ↓ Recon (cards → /dev/snd → confirm D0c capture / D1p playback)
Record & play loop (arecord hw:0,0 → aplay hw:0,1)
   ↓
Advanced loopback (8ch capture, ch7/8 = playback reference, formats aligned)
   ↓
Verify (your ears + Audacity waveforms on every channel)
```

- **One board, three chips:** 2× ES7210 own capture (8ch including loopback), 1× ES8156 owns playback (2ch);
- **Pin multiplexing is the S100's signature trap:** the DIP switches decide whether the 40pin pins serve audio or Wi-Fi;
- **Parameters always have a source:** period-size must be 64-byte aligned; capture `hw:0,0` and playback `hw:0,1` are whatever `ls /dev/snd/` says.

**Extension exercise:** record 8 channels while speaking into the mics and playing music through the speaker, then compare the ch1–ch4 and ch7–ch8 waveforms in Audacity to see, concretely, what an AEC reference signal is.

## 11. References

- [RDK S100 Audio Guide (official docs · Basic Application)](https://developer.d-robotics.cc/rdk_s_doc/03_Basic_Application/02_audio) — source of arecord/aplay parameters, functional tests, and the loopback test
- [RDK S100 Audio Debugging Guide (official docs · Driver Development)](https://developer.d-robotics.cc/rdk_s_doc/07_Advanced_development/02_linux_development/04_driver_development_super/driver_audio) — source of driver loading, DIP switches, xrun and error-code troubleshooting
- [Waveshare Audio Driver HAT product page](https://www.waveshare.net/shop/Audio-Driver-HAT.htm)
