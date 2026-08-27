# Lesson 8: Audio Peripherals on RDK X5

This lesson covers four audio hardware options on the RDK X5: the onboard 3.5mm jack, a USB speaker, the WM8960 Audio HAT, and the Audio Driver HAT REV2. You will learn how to identify sound cards, record and play back audio, and understand card-number drift and Codec routing.

> **Target hardware:** RDK X5
>
> **System version:** RDK OS 3.x or later
>
> **Related resources:** Video walkthrough (in production) / This handbook / [Official audio documentation](https://developer.d-robotics.cc/rdk_doc_center/)

## 1. Learning Objectives

After completing this lesson, you will be able to:

1. Use three commands to list the sound cards, card numbers, and device nodes on your system
2. Complete a record → playback loop using the onboard 3.5mm jack
3. Use a USB speaker plug-and-play and adjust command parameters when card numbers change
4. Configure the WM8960 Audio HAT with srpi-config and tinymix routing to achieve three playback modes
5. Configure the Audio Driver HAT REV2, record 2-channel and 4-channel audio, and play it back
6. Troubleshoot the "command succeeds but no sound" class of problems

## 2. Required Materials

| Item | Qty | Notes |
|------|-----|-------|
| RDK X5 | 1 | Flashed and accessible via SSH |
| 4-conductor 3.5mm headset | 1 | CTIA standard with MIC; 3-conductor headsets can play but not record |
| USB speaker | 1 | USB-Audio class driver, plug-and-play |
| Waveshare WM8960 Audio HAT | 1 | 40pin attachment, single Codec |
| Waveshare Audio Driver HAT REV2 | 1 | 40pin attachment, dual-Codec 4-mic array; all DIP switches OFF |

## 3. Audio System Overview: Three Reconnaissance Commands

The underlying framework of the Linux audio system is ALSA (Advanced Linux Sound Architecture). Every recording and playback operation on the X5 ultimately goes through the three layers managed by ALSA:

```text
Card                     — one physical audio device = one number
  └─ PCM device          — functional endpoint on the card, playback or capture
       └─ Device node    — a file under /dev/snd/, what programs actually open
```

For example, `pcmC0D1c` means "card 0, PCM device 1, capture endpoint" (c = capture, p = playback). Once you understand this naming rule, the command parameters stop being guesswork.

Before connecting any audio device, memorize these three commands — every section of this lesson uses them:

```shell
# 1. List registered sound cards (the most important one)
cat /proc/asound/cards

# 2. List device nodes in user space
ls /dev/snd/

# 3. List playback devices (use arecord -l for capture)
aplay -l
```

**Why reconnaissance matters:** when you use the `-D hw:X,Y` parameter, X is the card number from `cat /proc/asound/cards`, and Y is the device number from `aplay -l` / `arecord -l`. Reconnoiter first, then operate — your parameters always have a source.

### Card-Number Drift: Why It Worked Yesterday but Fails Today

ALSA assigns card numbers in registration order. A USB speaker plugged in before boot may get number 0; plugged in after boot, it may end up after the onboard card. **The same device can drift to a different number depending on timing** — this is the most common cause of "it worked yesterday but fails today."

There is exactly one countermeasure: **reconnoiter before every operation and trust the current output of `cat /proc/asound/cards`, never the number you remember.** Section 5 demonstrates a live drift.

## 4. Onboard 3.5mm Jack: The Simplest Loop

### 4.1 Hardware Connection

The X5 has an onboard 3.5mm jack that works with a **4-conductor headset** (CTIA standard, with MIC). A 3-conductor headset lacks the MIC segment — it can play but not record.

The headset must be **fully plugged in**. If it is not inserted deep enough and metal is still visible, programs run normally but the headset stays silent — the most common "false failure."

### 4.2 Reconnaissance

With no HAT attached, the onboard card owns number 0. Reconnoiter with three commands in order:

```shell
# 1. List cards: confirm the onboard card is registered
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudio    ]: simple-card - duplex-audio
                      duplex-audio

# 2. List logical devices: confirm playback and capture endpoints
root@ubuntu:~# cat /proc/asound/devices
  2: [ 0- 0]: digital audio playback
  3: [ 0- 0]: digital audio capture
  4: [ 0]   : control
 33:        : timer

# 3. Inspect device nodes in user space
root@ubuntu:~# ls /dev/snd/
by-path/   controlC0  pcmC0D0c   pcmC0D0p   timer
```

The corresponding device nodes are `pcmC0D0p` (playback) and `pcmC0D0c` (capture), i.e. `hw:0,0`.

### 4.3 Record and Play

```shell
# Record 10 seconds (-d 10), 48kHz stereo 16-bit
arecord -Dhw:0,0 -c 2 -r 48000 -f S16_LE -t wav -d 10 /userdata/record1.wav

# Play back
aplay -D hw:0,0 /userdata/record1.wav
```

**Success criteria:** the terminal prints `Recording WAVE ...` without errors during recording, and you clearly hear your recording in the headset during playback.

> **Playback for your audience:** download the recording to your computer with `scp` to verify the original quality:
>
> ```shell
> scp sunrise@<board-ip>:/userdata/record1.wav ./
> ```

> **Why 16-bit (S16_LE) instead of the manual's 24-bit (S24_LE)?** See "4.4 The recording-format trap".

### 4.4 The Recording-Format Trap: Why S24_LE Turns to Noise on a PC

Record with the manual's `-f S24_LE` and it plays back fine on the board via `aplay`; download the same file to a computer and it is very likely pure noise. **This is not broken hardware — it is the format itself.**

**The summary table:**

| ALSA format | Bytes per sample | Standard WAV? | On a computer player |
|---|---|---|---|
| S16_LE | 2 bytes | Standard 16-bit PCM | Normal |
| S24_3LE | 3 bytes | Standard 24-bit PCM | Normal |
| **S24_LE (used by the manual)** | **4 bytes** | **Non-standard: header says 24-bit, data is 4 bytes** | **Noise/static** |
| S32_LE | 4 bytes | Standard 32-bit PCM | Normal (some older players refuse) |

**Why this happens**

The key is that ALSA's S24_LE and the WAV standard's 24-bit are not the same thing:

- WAV-standard 24-bit = 3 bytes per sample (packed), which corresponds to ALSA's **S24_3LE**;
- ALSA's **S24_LE** = "24 bits carried in a 32-bit container" — 4 bytes per sample (the low 24 bits hold valid data, the 4th byte is sign extension).

`arecord -f S24_LE -t wav` has a well-known behavior: it writes the 4-byte samples verbatim into the file, yet writes "24 bits per sample" into the WAV header. The header and the body now contradict each other (header says 24-bit → 3 bytes/sample, actual data is 4 bytes/sample).

**Why does it play back fine on the board?** Because `aplay` and `arecord` share the same ALSA convention: the writer stores 4 bytes and labels it 24-bit; the reader interprets it as ALSA's S24_LE (4 bytes). The write-side mistake and the read-side mistake cancel out, so local playback is correct — but this is only a "round-trip self-consistency", not a legally valid file.

**Why is it all noise on a computer?** Windows/Mac players (VLC, Audacity, browsers, etc.) strictly follow the WAV standard: the header says 24-bit, so they slice data at 3 bytes per sample. The actual data is 4 bytes per sample, so every frame is off by 1 byte — left/right channels and samples are completely misaligned → noise. This is a long-confirmed arecord behavior on the alsa-devel mailing list.

**Conclusion:** recording the onboard card at the manual's 24-bit yields noise when played on a computer. **Record at 16-bit (S16_LE)** — a standard format that plays correctly on both the board and a computer.

## 5. USB Speaker: Plug-and-Play and Card-Number Drift

### 5.1 Attach and Identify

USB speakers use the standard USB-Audio class driver — **plug-and-play, no configuration**. Reconnoiter right after plugging in:

```shell
root@ubuntu:~# cat /proc/asound/cards
 0 [RC08          ]: USB-Audio - ROCWARE RC08      ← USB sound card (example)
                        ROCWARE RC08 at usb-xhci-hcd.2.auto-1.2, high speed
 1 [duplexaudio   ]: simple-card - duplex-audio    ← onboard card
                        duplex-audio
```

The USB speaker is card 0 here, so playback is:

```shell
aplay -D hw:0,0 /userdata/record1.wav
```

> Note: different speaker models show different names. Trust your own `cat /proc/asound/cards` output. `lsusb` can further confirm the USB device information.

### 5.2 Live Demo: Card-Number Drift

Keep the USB speaker attached, reboot the board, or replug it into a different USB port, then reconnoiter again — the USB card and the onboard card **may have swapped numbers**.

If you keep using the `hw:0,0` you remember, sound comes out of the wrong device (or you get a device-busy error). The correct approach: check `cat /proc/asound/cards` again. If the USB speaker is now card 1, the command becomes:

```shell
aplay -D hw:1,0 /userdata/record1.wav
```

**Success criteria:** sound comes out of the USB speaker, and no matter how the numbers change, you can locate the device through reconnaissance.

### 5.3 USB Card Recording and the Config File

A USB card (speaker/mic combo or a USB microphone) works just like the onboard card — `aplay` to play, `arecord` to record, pointing at whatever number it got from that recon pass:

```shell
# Record (assuming the USB card is card 1 now, using standard S16_LE)
arecord -Dhw:1,0 -c 2 -r 48000 -f S16_LE -t wav -d 10 /userdata/usb_record.wav

# Play (number depends on the current recon)
aplay -D hw:1,0 /userdata/usb_record.wav
```

> To let upper-layer apps (desktop players, recording software) see the onboard card and the USB card at the same time, configure PulseAudio. The core is editing `/etc/pulse/default.pa` and appending `load-module module-alsa-sink/source` for the USB card, specifying `device=hw:X,Y` (X and Y come from the current output of `cat /proc/asound/cards` and `aplay -l`/`arecord -l`). Reboot or restart the PulseAudio service for it to take effect. This is an advanced step — the demo here talks to ALSA directly via `-D`, without the upper-layer service.

**USB speaker summary:** like the onboard 3.5mm, it is a "zero-config" device — plug-and-play, operated with `aplay`/`arecord` plus `-D hw:X,Y`. The only trap is card-number drift, so reconnoiter before every operation.

## 6. WM8960 Audio HAT: Configure Routing Before It Can Sound

From this section onward, hardware "requires configuration." The WM8960 Audio HAT (Waveshare) attaches via the 40pin header, uses a WM8960 Codec, and supports stereo microphone recording and audio playback.

### 6.1 Hardware Installation

With the board powered off, attach the HAT to the X5's 40pin header (mind the orientation; align and press firmly).

### 6.2 Software Configuration (srpi-config)

```text
srpi-config
  → 3 Interface Options
    → I5 Audio
      → select WM8960 Audio Driver HAT
```

Reboot as prompted:

```shell
sync && reboot
```

### 6.3 Verify After Reboot

```shell
# 1. List cards: duplexaudioi2s1 appearing = HAT loaded
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudioi2s1]: simple-card - duplex-audio-i2s1   ← WM8960 HAT
                      duplex-audio-i2s1
 1 [duplexaudio    ]: simple-card - duplex-audio        ← onboard (demoted to 1)
                      duplex-audio

# 2. List logical devices: card 0 = playback 0-0, capture 0-1
root@ubuntu:~# cat /proc/asound/devices
  2: [ 0- 0]: digital audio playback
  3: [ 0- 1]: digital audio capture
  4: [ 0]   : control
  5: [ 1- 0]: digital audio playback
  6: [ 1- 0]: digital audio capture
  7: [ 1]   : control
 33:        : timer

# 3. Inspect nodes: pcmC0D0p playback, pcmC0D1c capture
root@ubuntu:~# ls /dev/snd/
by-path  controlC0  controlC1  pcmC0D0p  pcmC0D1c  pcmC1D0c  pcmC1D0p  timer
```

The appearance of `duplexaudioi2s1` means the driver loaded successfully. Now:

- **The HAT is card 0**: playback uses `pcmC0D0p`, capture uses `pcmC0D1c`;
- the onboard card drops to number 1 — another round of card-number drift where the reconnaissance habit pays off again.

### 6.4 Key Concept: Why Routing Is Mandatory

The WM8960 contains multiple internal audio paths (input→ADC, DAC→speaker, DAC→headphone, etc.), all disabled by default. **Without routing configuration, `tinycap`/`tinyplay` commands execute successfully, but the audio path is disconnected** — no sound and no valid recording.

Every WM8960 use case therefore follows the order: "configure routing with `tinymix` first → then operate with `tinycap`/`tinyplay`."

### 6.5 Recording

**Step 1: configure input routing and gain**

```shell
# Left/right channel input gain (lower to 1 if it howls)
tinymix -D 0 set 'Left Input Boost Mixer LINPUT1 Volume' 3
tinymix -D 0 set 'Right Input Boost Mixer RINPUT1 Volume' 3

# Recording volume
tinymix -D 0 set 'Capture Volume' 40 40
tinymix -D 0 set 'ADC PCM Capture Volume' 200 200

# Open input path switches
tinymix -D 0 set 'Left Boost Mixer LINPUT1 Switch' 1
tinymix -D 0 set 'Right Boost Mixer RINPUT1 Switch' 1
tinymix -D 0 set 'Left Input Mixer Boost Switch' 1
tinymix -D 0 set 'Right Input Mixer Boost Switch' 1

# Open the capture switch
tinymix -D 0 set 'Capture Switch' 1 1
```

**Step 2: record (5 seconds)**

```shell
tinycap ./2chn_test.wav -D 0 -d 0 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5
```

### 6.6 Playback (Three Modes)

**Mode 1: speaker playback**

```shell
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Speaker DC Volume' 3
tinymix -D 0 set 'Speaker AC Volume' 3
tinymix -D 0 set 'Speaker Playback Volume' 127 127
tinymix -D 0 set 'Playback Volume' 255 255

tinyplay ./2chn_test.wav -D 0 -d 0
```

**Mode 2: headphone and speaker together**

```shell
tinymix -D 0 set 'Headphone Playback Volume' 80 80
tinymix -D 0 set 'Playback Volume' 220 220
tinymix -D 0 set 'Speaker DC Volume' 4
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1

tinyplay ./2chn_test.wav -D 0 -d 0
```

**Mode 3: headphone only (speaker muted)**

```shell
tinymix -D 0 set 'Headphone Playback Volume' 115 115
tinymix -D 0 set 'Speaker Playback Volume' 0 0
tinymix -D 0 set 'Playback Volume' 244 244
tinymix -D 0 set 'Speaker DC Volume' 4
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1

tinyplay ./2chn_test.wav -D 0 -d 0
```

**Success criteria:** each mode sounds from the right place — Mode 1 from the speaker, Mode 3 from the headset with the speaker silent.

### 6.7 Uninstall

srpi-config → 3 Interface Options → I5 Audio → select UNSET, then power off and remove the HAT.

## 7. Audio Driver HAT REV2: Mic Array and Loopback

### 7.1 Hardware Installation

Attach to the 40pin header with the board powered off. **Note: all 3 DIP switches must be OFF**, otherwise the sound card will not register.

### 7.2 Software Configuration

```text
srpi-config
  → 3 Interface Options
    → I5 Audio
      → select Audio Driver HAT V2
```

After reboot, `cat /proc/asound/cards` shows `duplexaudioi2s1` again (REV2 and WM8960 share the same registered name; the actual hardware is distinguished by the config selection). The three-command recon output is identical to the WM8960 section: card 0 = playback `0-0`, capture `0-1`, nodes `pcmC0D0p` / `pcmC0D1c`.

### 7.3 Recording: 2-Channel and 4-Channel

The REV2 uses an ES7210+ES8156 dual-Codec design and supports a ring of 4 microphones. Note that its capture device number is **d 1** (different from the WM8960's d 0):

```shell
# 2-channel recording
tinycap ./2chn_test.wav -D 0 -d 1 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5

# 4-channel recording (full mic-array capability)
tinycap ./4chn_test.wav -D 0 -d 1 -c 4 -b 16 -r 48000 -p 512 -n 4 -t 5
```

### 7.4 Playback

```shell
# 2-channel playback only (4-channel files are not supported)
tinyplay ./2chn_test.wav -D 0 -d 0
```

### 7.5 Loopback Capture (Advanced, Not Practiced Here)

The REV2's loopback signal maps to capture channels 7 and 8; it requires 8-channel recording with aligned record/playback formats (16k/8ch/16bit). This lesson only covers the concept and use cases (algorithm-side analysis of playback signals); see the official audio_echo_test example for the full procedure.

**Success criteria:** a 4-channel recording file is created with valid signals on all channels, and the 2-channel file plays back audibly.

## 8. Troubleshooting

**Q1: The device is plugged in but does not appear in `cat /proc/asound/cards`?**

USB devices: try another port and check `lsusb` for the hardware. HAT boards: verify the srpi-config selection, whether you rebooted, and the DIP switches (REV2 must be all OFF).

**Q2: The command succeeds but there is no sound?**

Check four things in order: ① Is the target card number correct (run `cat /proc/asound/cards` again)? ② Is the headset fully plugged in (3.5mm scenario)? ③ Did you configure WM8960 routing (Section 6.4)? ④ Does the file format match the device capability (REV2 cannot play 4ch)?

**Q3: WM8960 recordings are full of noise/howling?**

Input gain is too high. Lower `LINPUT1/RINPUT1 Volume` from 3 to 1 and try again.

**Q4: What do the tinyalsa parameters mean?**

`-D` card number, `-d` PCM device number, `-c` channels, `-b` bit depth, `-r` sample rate, `-p` period size, `-n` period count, `-t` recording seconds. See the official FAQ on tinyalsa parameters.

**Q5: Can a USB card and a HAT card be managed together by an upper-layer service (PulseAudio)?**

That is an advanced configuration; see the official FAQ section on audio HAT and USB card coexistence.

## 9. Summary

The lesson's through-line in one diagram:

```text
Reconnoiter (cards → devices → nodes)
   ↓ get the card number and device number
Play (aplay / tinyplay -D hw:X,Y)
   ↓ wrong sound? back to reconnaissance
Record (arecord / tinycap -D X -d Y)
   ↓ no valid waveform? check routing (WM8960)
Verify (your ears + a replayable file)
```

- **Four pieces of hardware are really three device classes:** zero-config (onboard, USB), single-Codec with routing (WM8960), dual-Codec multi-mic (REV2);
- **Card-number drift is the norm; reconnaissance is the habit.**

**Extension exercise:** record a clip of your own voice with the WM8960 and play it through the USB speaker (a cross-device record-play combination that reinforces card-locating skills).
