# Lesson 10: Hardware Video Codec and 800×480 HDMI Display on RDK X5

This lesson uses two C++ programs to build a complete, observable codec loop on one RDK X5. The Server captures NV12 images from a MIPI camera, produces H.264 with the X5 BSP hardware encoder, and publishes a local RTSP stream. The Client receives that stream through the loopback interface, restores NV12 with the X5 hardware decoder, scales it to 800×480 with VPS, and displays the live camera image over HDMI.

```text
Camera → ISP/VIO → NV12 → Hardware Encoder → H.264 → RTSP
       → RTSP Client → Hardware Decoder → NV12 → VPS 800×480 → HDMI Display
```

## Lesson task

| Item | Requirement |
| --- | --- |
| Board | RDK X5 4GB or 8GB; RDK X5 Module requires a carrier that exposes compatible Camera and HDMI interfaces |
| Camera | An X5 BSP-supported MIPI camera; this lesson uses IMX219 as the example |
| Camera and stream size | 1920×1080@30fps |
| Codec | H.264 at a target bitrate of 8000 kbit/s |
| RTSP URL | `rtsp://127.0.0.1:8554/live` |
| Decoder output | NV12 from the X5 hardware decoder |
| Display output | VPS scales 1920×1080 to 800×480, then outputs through Display channel 1 |
| Language | C++17 |
| Final result | The 800×480 HDMI screen continuously shows the live camera image |

Accept the picture only on the board-connected screen. Run the Server and Client in two terminal sessions on the same X5, and keep the Client URL on `127.0.0.1`.

## What you will be able to do after this lesson

After completing this lesson, you will be able to:

1. Place Bayer RAW, NV12, H.264, RTP, and RTSP correctly in a video pipeline;
2. Explain why a camera stream is encoded for transport and decoded before display;
3. Open an X5 MIPI camera and create a hardware encoding channel through `libspcdev`;
4. Use GStreamer for H.264 RTP packetization, RTSP sessions, and RTP depacketization;
5. Restore NV12 with the X5 hardware decoder;
6. Scale 1920×1080 NV12 to 800×480 with VPS;
7. Output the decoded image through X5 Display channel 1;
8. Use logs to locate faults in Camera, Encoder, RTSP, Decoder, VPS, or Display.

## Prerequisites

### Hardware

- One RDK X5 4GB or 8GB;
- One X5 BSP-supported MIPI camera, with IMX219 1920×1080@30fps used by the commands below;
- An HDMI screen that advertises an `800x480` display mode;
- An HDMI cable and the screen's power cable;
- Two terminal sessions that can operate the X5 at the same time.

!!! warning
    Power off the board before installing or adjusting a MIPI camera cable. Power the HDMI screen and select its HDMI input before booting the X5 so the display mode can be detected during startup.

### Check the board, system, and codec driver

```bash
cat /proc/device-tree/model
rdkos_info || cat /etc/version
uname -a
ls -l /dev/vpu /dev/jpu 2>/dev/null
```

The model must contain `RDK X5`. If a particular RDK OS release exposes different codec device nodes, use the nodes documented for that BSP release.

### Check HDMI and the 800×480 mode

DRM card and connector numbers may vary between X5 system releases, so enumerate them first:

```bash
for f in /sys/class/drm/card*-*/status; do
  echo "$f: $(cat "$f")"
done

for f in /sys/class/drm/card*-*/modes; do
  echo "--- $f"
  cat "$f"
done
```

At least one HDMI connector must be `connected`, and its mode list must contain:

```text
800x480
```

If the HDMI connector path is known, read the actual EDID data with:

```bash
wc -c < /sys/class/drm/card0-HDMI-A-1/edid
```

`stat -c '%s'` may return zero for a sysfs EDID attribute and must not be used as proof that EDID data is absent.

### Check the BSP development interface

```bash
test -f /usr/include/sp_codec.h && echo "sp_codec.h: ready"
ldconfig -p | grep libspcdev
```

### Install build and RTSP dependencies

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake pkg-config \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libgstrtspserver-1.0-dev \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad
```

Check the required GStreamer elements:

```bash
gst-inspect-1.0 appsrc
gst-inspect-1.0 appsink
gst-inspect-1.0 h264parse
gst-inspect-1.0 rtph264pay
gst-inspect-1.0 rtph264depay
gst-inspect-1.0 rtspsrc
```

### Build on the X5 itself

```bash
cd ~/rdk-course-demos/01_beginner/10_codec
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
```

Check the output:

```bash
ls -l build/codec_rtsp_server build/codec_rtsp_client
./build/codec_rtsp_server --help
./build/codec_rtsp_client --help
```

The build should finish with:

```text
Built target codec_rtsp_server
Built target codec_rtsp_client
```

Reconfigure and link on the X5 4GB itself. Do not copy executables or shared libraries from S100 or another architecture environment.

## Why the codec chain is necessary

### Direct camera display does not require a codec

For a local camera preview on the same X5, the shortest path is:

```text
Camera → ISP/VIO → NV12 → VPS → Display
```

That path does not require H.264. This lesson deliberately adds Encoder, RTSP, and Decoder to demonstrate compression, standards-based media transport, and hardware decoding as separate responsibilities.

### Why encoding is required

One 1920×1080 NV12 frame occupies:

```text
1920 × 1080 × 3 / 2 = 3,110,400 bytes
```

At 30fps, the uncompressed data rate is approximately:

```text
3,110,400 × 30 ≈ 93.3 MB/s ≈ 746.5 Mbit/s
```

The lesson compresses that image stream to roughly 8 Mbit/s of H.264. The hardware encoder also emits SPS, PPS, and IDR information required by the decoder.

### Why decoding is required

H.264 is compressed data and cannot be submitted to VPS or Display as an image. The Client must perform:

```text
RTP depay → H.264 Annex-B access unit → Hardware Decoder → NV12
```

VPS then converts the decoded 1920×1080 NV12 image to 800×480 for Display.

### Why local RTSP is used

- Server and Client form explicit encoding and decoding endpoints;
- RTP demonstrates packetization and access-unit reconstruction;
- The architecture can later be extended across devices;
- `127.0.0.1` removes external network variability during initial validation.

## Encoding capability and basic API overview

### Capability validated in this lesson

This lesson validates one 1080p30 codec stream and an 800×480 display path rather than the maximum concurrent capacity of the X5 codec subsystem.

| Parameter | Lesson setting |
| --- | --- |
| Camera input | IMX219, 1920×1080@30fps |
| ISP/VIO output | NV12, 1920×1080 |
| Encoder | X5 BSP H.264 hardware encoder |
| Target bitrate | 8000 kbit/s |
| Elementary stream | H.264 Annex-B |
| RTSP/RTP | H.264 over RTP through RTSP/TCP |
| Decoder | X5 BSP H.264 hardware decoder |
| Display input | NV12 scaled by VPS to 800×480 |

X5 encoder dimensions must satisfy BSP alignment requirements. The lesson's 1920×1080 setting satisfies the common 16-pixel alignment constraint. The instantaneous bitrate around an IDR may be higher than the configured target before settling near 8 Mbit/s.

### API responsibilities

| Stage | API or component | Responsibility |
| --- | --- | --- |
| Camera/VIO | `sp_init_vio_module()`, `sp_open_camera_v2()` | Open Camera, ISP, and NV12 output |
| Hardware encoding | `sp_init_encoder_module()`, `sp_start_encode()` | Create an H.264 hardware encoder |
| Module binding | `sp_module_bind()` | Connect VIO directly to Encoder |
| Encoded output | `sp_encoder_get_stream()` | Retrieve H.264 Annex-B data |
| RTSP Server | GStreamer `appsrc`, `h264parse`, `rtph264pay` | Packetize H.264 into RTP and expose RTSP |
| RTSP Client | GStreamer `rtspsrc`, `rtph264depay`, `h264parse`, `appsink` | Receive RTSP and reconstruct complete access units |
| Hardware decoding | `sp_init_decoder_module()`, `sp_start_decode()`, `sp_decoder_set_image()` | Submit H.264 access units to X5 VDEC |
| Scaling | `sp_open_vps()` | Scale 1920×1080 NV12 to 800×480 |
| HDMI display | `sp_start_display()` | Output through X5 Display channel 1 |

GStreamer does not decode the image in this lesson. No software decoder such as `avdec_h264` is used; decoding is performed by the X5 BSP hardware decoder.

### Parameters that must not be confused

| Parameter | Meaning |
| --- | --- |
| Server `--sensor-width/--sensor-height` | Camera RAW input size |
| Server/Client `--width/--height` | Encoded and decoded stream size, 1920×1080 in this lesson |
| Client `--display-width/--display-height` | HDMI output size, fixed to 800×480 in this lesson |

Do not change Client decode dimensions to 800×480. The decoder dimensions must match the Server's 1920×1080 H.264 stream; VPS performs the final resize.

## BSP API guide (two examples)

### Example 1: Camera → hardware encoding → RTSP Server

Open the first X5 terminal:

```bash
cd ~/rdk-course-demos/01_beginner/10_codec

sudo ./build/codec_rtsp_server \
  --codec h264 \
  --width 1920 \
  --height 1080 \
  --sensor-width 1920 \
  --sensor-height 1080 \
  --fps 30 \
  --bitrate 8000 \
  --camera-index -1 \
  --pipe-id 0 \
  --port 8554 \
  --mount /live
```

`--camera-index -1` enables camera auto-detection. Successful initialization includes output similar to:

```text
[platform] model=D-Robotics RDK X5 ...
[camera] sensor=1920x1080 output=1920x1080 fps=30
[codec] h264 bitrate=8000 kbit/s
[rtsp] ready: rtsp://<board-ip>:8554/live
[rtsp] same-board client: rtsp://127.0.0.1:8554/live
```

Before a Client connects, a growing `no-client` count is expected. After connection, `published` must grow while `push-fail` remains zero.

### Example 2: RTSP Client → hardware decoding → VPS → 800×480 HDMI

Keep Example 1 running. In a second X5 terminal, verify that an HDMI connector is `connected` and that its mode list includes `800x480`.

Stop the desktop display service:

```bash
sudo systemctl stop display-manager
```

Some X5 images use `lightdm`; `display-manager` is the generic service alias for the active display manager. The desktop disappearing is expected.

Start the Client:

```bash
cd ~/rdk-course-demos/01_beginner/10_codec

sudo ./build/codec_rtsp_client \
  --url rtsp://127.0.0.1:8554/live \
  --codec h264 \
  --width 1920 \
  --height 1080 \
  --transport tcp \
  --latency 100 \
  --vps-pipe-id 1 \
  --display-channel 1 \
  --display-width 800 \
  --display-height 480 \
  --duration 30
```

Important log lines include:

```text
[platform] model=...RDK X5...
[codec] BSP hardware decoder=h264 size=1920x1080
[rtsp] linked H264 RTP pad
[sink] Decoder -> VPS -> Display 800x480 channel=1
[metrics] received=... rate=30.0 buffer/s ... submitted=...
```

Depending on the X5 BSP version, Display initialization may report `Opened DRM device`, `DRM is available`, `sp_start_display success`, or equivalent output. During the run, the 800×480 HDMI screen must continuously show the live camera image.

Let the Client finish its 30-second test before stopping the Server. Restore the desktop when required:

```bash
sudo systemctl start display-manager
```

## How to determine success

Do not accept the lesson only because the final line says `PASS`. The current Client uses `PASS` to report that RTSP/RTP data was submitted to the decoder pipeline and that VPS, Display, and module binding initialized. Final acceptance also requires a visible HDMI image.

### Server acceptance criteria

- [ ] The expected camera is detected;
- [ ] Camera output is 1920×1080 at 30fps;
- [ ] `[rtsp] ready` appears;
- [ ] `encoded` grows at approximately 30 chunks/s;
- [ ] `published` grows after the Client connects;
- [ ] `push-fail=0`;
- [ ] H.264 SPS, PPS, and IDR counters are nonzero.

### Client and Display acceptance criteria

- [ ] An HDMI connector is `connected`;
- [ ] Display/DRM initialization succeeds;
- [ ] The sink reports `Display 800x480 channel=1`;
- [ ] `linked H264 RTP pad` appears;
- [ ] `received` and `submitted` grow at approximately 30 buffers/s;
- [ ] The 800×480 screen continuously shows the live camera image;
- [ ] Orientation, aspect ratio, and color are correct without persistent black output or corruption;
- [ ] The Client exits normally after 30 seconds.

For H.264, `vps=0` in `NAL(vps/sps/pps/idr)` is expected. VPS NAL units belong to H.265; validate SPS, PPS, and IDR for H.264.

## Troubleshooting

### Build is slow or memory pressure is high on X5 4GB

Use:

```bash
cmake --build build -j2
```

Avoid defaulting to `-j$(nproc)`. This lesson has only a few C++ files, and `-j2` keeps peak build memory lower.

### `sp_open_camera_v2 failed`

Power off the X5, verify ribbon orientation, connector choice, and sensor support, then reboot and ensure no other process owns VIO. Use an explicit `--camera-index` only after identifying the actual camera route.

### `Fail to open vpu driver` or decoder initialization fails

```bash
lsmod | grep -Ei 'vpu|jpu|video'
ls -l /dev/vpu /dev/jpu 2>/dev/null
dmesg | grep -Ei 'vpu|jpu|codec|decoder|encoder'
```

This is a device-driver or BSP issue and should not be addressed by changing the RTSP URL or screen dimensions.

### Client reports `Connection refused`

```bash
ss -ltnp | grep ':8554'
pgrep -a codec_rtsp_server
```

Keep the Server running and use the exact URL `rtsp://127.0.0.1:8554/live`.

### Server `no-client` keeps increasing

This is normal before the Client connects. After connection, expect `client media configured`, `rtsp-source=active`, and a growing `published` count.

### HDMI connector is `disconnected`

Power off the X5, power the screen and select HDMI input, use a direct cable, boot with HDMI already connected, and enumerate `/sys/class/drm/card*-*/status` again.

### HDMI is connected but the desktop or a black screen remains

```bash
systemctl is-active display-manager
sudo systemctl stop display-manager
```

Restart the Client afterward. Official direct-display examples for X5 also stop the desktop service before taking direct control of display resources.

### Client reports PASS but the 800×480 screen remains black

Confirm that the connected HDMI connector advertises `800x480`, then inspect:

```bash
systemctl is-active display-manager
dmesg | grep -Ei 'drm|hdmi|display|atomic|page.*flip|error'
```

The Client command must include all three overrides:

```text
--display-channel 1
--display-width 800
--display-height 480
```

Without an explicit display size, the X5 code may prefer the 1920×1080 mode that matches the stream rather than the native 800×480 mode of the lesson screen.

### RTSP links but `submitted` does not grow

Use the same codec and 1920×1080 dimensions on both endpoints. H.264 requires SPS/PPS and an IDR before normal decoding can begin; a short startup buffer is expected.

### Client reaches `end of stream` before 30 seconds

The Server was usually stopped first. Leave it running until the Client finishes naturally.

### A decoder-output queue error appears after PASS

If it appears only after `[result] PASS` and playback was correct, it is normally a shutdown-time warning while modules are unbound and Decoder is stopped. Investigate further if it repeats during playback or accompanies a black screen.

### Port 8554 is already in use

```bash
ss -ltnp | grep ':8554'
```

Stop the previous Server, or select another Server port and update the Client URL.

### CMake cannot find GStreamer or RTSP Server

Install `libgstreamer1.0-dev`, `libgstreamer-plugins-base1.0-dev`, and `libgstrtspserver-1.0-dev`, then rerun CMake configuration and build.

## Lesson summary

This lesson completed a visible hardware codec loop on one RDK X5. Camera and ISP/VIO produced NV12; the X5 hardware encoder compressed it to H.264; GStreamer handled RTP/RTSP; the X5 hardware decoder restored NV12; VPS scaled the image to 800×480; and Display channel 1 sent it to the HDMI screen.

The responsibilities are explicit:

- BSP VIO owns Camera and NV12 production;
- BSP Encoder and Decoder own H.264 hardware processing;
- GStreamer owns RTSP/RTP, not image decoding;
- BSP VPS owns the 1920×1080 to 800×480 resize;
- BSP Display owns HDMI output.

## Extension exercises

1. Change Server bitrate from 8000 to 4000 kbit/s and compare measured bitrate and screen quality;
2. Switch both endpoints to H.265 while retaining 800×480 output;
3. Keep 1920×1080 codec dimensions and compare 1280×720 and 800×480 Display output;
4. Change TCP to UDP and compare startup and stability;
5. Add decoded-frame and Display-submission counters so `PASS` covers real output progress;
6. Record CPU load, memory use, and actual frame rate on X5 4GB and 8GB.

## Appendix

### Appendix A: Complete run sequence

Terminal 1:

```bash
cd ~/rdk-course-demos/01_beginner/10_codec

sudo ./build/codec_rtsp_server \
  --codec h264 \
  --width 1920 --height 1080 \
  --sensor-width 1920 --sensor-height 1080 \
  --fps 30 --bitrate 8000 \
  --camera-index -1 --pipe-id 0 \
  --port 8554 --mount /live
```

Terminal 2:

```bash
sudo systemctl stop display-manager

cd ~/rdk-course-demos/01_beginner/10_codec

sudo ./build/codec_rtsp_client \
  --url rtsp://127.0.0.1:8554/live \
  --codec h264 \
  --width 1920 --height 1080 \
  --transport tcp --latency 100 \
  --vps-pipe-id 1 \
  --display-channel 1 \
  --display-width 800 --display-height 480 \
  --duration 30
```

Restore the desktop:

```bash
sudo systemctl start display-manager
```

### Appendix B: Parameter reference

| Program | Parameter | Lesson value | Meaning |
| --- | --- | --- | --- |
| Server | `--camera-index` | `-1` | Auto-detect the camera |
| Server | `--pipe-id` | `0` | Camera VIO pipeline |
| Server | `--width/--height` | `1920/1080` | Encoded stream dimensions |
| Server | `--fps` | `30` | Camera and RTP frame rate |
| Server | `--bitrate` | `8000` | Target bitrate in kbit/s |
| Server | `--port` | `8554` | RTSP listening port |
| Server | `--mount` | `/live` | RTSP mount path |
| Client | `--url` | `rtsp://127.0.0.1:8554/live` | Local loopback RTSP URL |
| Client | `--width/--height` | `1920/1080` | Hardware decode dimensions |
| Client | `--transport` | `tcp` | RTSP/RTP transport |
| Client | `--latency` | `100` | GStreamer jitter buffer in ms |
| Client | `--vps-pipe-id` | `1` | VPS pipeline used for Display scaling |
| Client | `--display-channel` | `1` | X5 video display layer |
| Client | `--display-width/--display-height` | `800/480` | Lesson screen dimensions |

### Appendix C: Source-to-API map

| File | Main responsibility |
| --- | --- |
| `src/codec_rtsp_server.cpp` | Camera, hardware encoding, RTSP Server, and encoding metrics |
| `src/codec_rtsp_client.cpp` | RTSP Client, RTP depay, decoder input, and runtime metrics |
| `src/codec_common.cpp` | Platform detection, VPS, Display, module binding, and NAL metrics |
| `src/codec_common.hpp` | Shared types, display configuration, and metrics |
| `CMakeLists.txt` | C++17, `libspcdev`, GStreamer, and threading linkage |

### Appendix D: References

- [Lesson source](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec)
- [RDK X3/X5 rtsp2display example](https://developer.d-robotics.cc/rdk_x_doc/en/Basic_Application/cdev_demo_sample/rtsp2display)
- [RDK X3/X5 Encoder API](https://developer.d-robotics.cc/rdk_x_doc/en/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/encoder_api)
- [RDK X3/X5 Decoder API](https://developer.d-robotics.cc/rdk_x_doc/en/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/decoder_api)
- [RDK X3/X5 Display API](https://developer.d-robotics.cc/rdk_x_doc/en/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/display_api)
- [GStreamer RTSP Server](https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/)
