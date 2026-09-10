# Lesson 10: Hardware Video Codec and 800×480 HDMI Display on RDK S100

This lesson uses two C++ programs to build a complete, observable codec loop on one RDK S100. The Server captures NV12 images from a MIPI camera, uses the S100 BSP hardware encoder to produce H.264, and publishes a local RTSP stream. The Client receives that stream through the loopback interface, restores NV12 with the S100 hardware decoder, scales it to 800×480 with VPS, and displays the live camera image over HDMI.

```text
Camera → ISP/VIO → NV12 → Hardware Encoder → H.264 → RTSP
       → RTSP Client → Hardware Decoder → NV12 → VPS 800×480 → HDMI Display
```

## Lesson task

| Item | Requirement |
| --- | --- |
| Board | RDK S100 |
| Camera | A MIPI camera supported by the S100 BSP; this lesson was tested with IMX219 |
| Camera and stream size | 1920×1080@30fps |
| Codec | H.264 at a target bitrate of 8000 kbit/s |
| RTSP URL | `rtsp://127.0.0.1:8554/live` |
| Decoder output | NV12 from the S100 hardware decoder |
| Display output | VPS scales 1920×1080 to 800×480, then outputs through HDMI channel 11 |
| Language | C++17 |
| Final result | The 800×480 HDMI screen continuously shows the live camera image |

The picture is accepted only on the board-connected screen. Run the Server and Client in two terminal sessions on the same S100, and keep the Client URL on `127.0.0.1`.

## What you will be able to do after this lesson

After completing this lesson, you will be able to:

1. Place Bayer RAW, NV12, H.264, RTP, and RTSP correctly in a video pipeline;
2. Explain why a camera stream is encoded for transport and decoded before display;
3. Open a MIPI camera and create an S100 hardware encoding channel through `libspcdev`;
4. Use GStreamer for H.264 RTP packetization, RTSP sessions, and RTP depacketization;
5. Restore NV12 frames with the S100 hardware decoder;
6. Scale 1920×1080 NV12 to 800×480 with VPS;
7. Output the decoded image through S100 HDMI channel 11;
8. Use logs to locate a fault in Camera, Encoder, RTSP, Decoder, VPS, or Display.

## Prerequisites

### Hardware

- One RDK S100;
- One S100 BSP-supported MIPI camera, with IMX219 1920×1080@30fps used by the commands below;
- The S100 camera expansion board and correctly installed camera ribbon cable;
- An HDMI screen that advertises an `800x480` display mode;
- An HDMI cable and the screen's power cable;
- Two terminal sessions that can operate the S100 at the same time.

!!! warning
    Power off the board before installing or adjusting a MIPI camera cable. Power the HDMI screen and select its HDMI input before booting the board so the display mode can be detected during startup.

### Check the board, codec driver, and HDMI

```bash
cat /proc/device-tree/model
cat /etc/version
uname -a
ls -l /dev/vpu /dev/jpu
```

The model must contain `RDK S100`, and both `/dev/vpu` and `/dev/jpu` must exist.

Check HDMI status and the required display mode:

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
cat /sys/class/drm/card0-HDMI-A-1/modes
wc -c < /sys/class/drm/card0-HDMI-A-1/edid
```

For this lesson, expect:

```text
status: connected
modes: contains 800x480
EDID: the actual read normally returns more than 0 bytes
```

`stat -c '%s'` may report zero for a sysfs EDID attribute even when it contains data. Use `wc -c` to read the attribute instead of treating the metadata size as the EDID length.

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

Check the GStreamer elements used by this lesson:

```bash
gst-inspect-1.0 appsrc
gst-inspect-1.0 appsink
gst-inspect-1.0 h264parse
gst-inspect-1.0 rtph264pay
gst-inspect-1.0 rtph264depay
gst-inspect-1.0 rtspsrc
```

### Build the lesson programs

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

## Why the codec chain is necessary

### Direct camera display does not require a codec

If the only objective is to show a local camera on a local display, the shortest path is:

```text
Camera → ISP/VIO → NV12 → VPS → Display
```

H.264 encoding and decoding are not required for that path. This lesson intentionally adds codec and RTSP stages to demonstrate compression, media transport, and hardware decoding in a realistic video architecture.

### Why encoding is required

One 1920×1080 NV12 frame occupies:

```text
1920 × 1080 × 3 / 2 = 3,110,400 bytes
```

At 30fps, the uncompressed data rate is approximately:

```text
3,110,400 × 30 ≈ 93.3 MB/s ≈ 746.5 Mbit/s
```

The lesson compresses that image stream to roughly 8 Mbit/s of H.264. The encoder also inserts SPS, PPS, and IDR information required for standards-compliant decoding.

### Why decoding is required

H.264 is a compressed elementary stream, not an NV12 image that VPS or Display can consume. The Client must first perform:

```text
RTP depay → H.264 Annex-B access unit → Hardware Decoder → NV12
```

VPS can then scale the decoded 1920×1080 NV12 frame to the screen's 800×480 resolution, and Display can send it to HDMI.

### Why RTSP is still used on one board

Although both processes run on one S100, local RTSP remains useful because it:

- Separates the encoding endpoint from the decoding endpoint;
- Demonstrates RTP packetization and access-unit reconstruction;
- Preserves an architecture that can later be extended across devices;
- Uses `127.0.0.1` to remove external network variability during initial validation.

## Encoding capability and basic API overview

### Capability validated in this lesson

This lesson validates one stable stream rather than the maximum concurrent capacity of the S100 codec subsystem.

| Parameter | Lesson setting |
| --- | --- |
| Camera input | IMX219, 1920×1080@30fps |
| ISP/VIO output | NV12, 1920×1080 |
| Encoder | S100 BSP H.264 hardware encoder |
| Target bitrate | 8000 kbit/s |
| Elementary stream | H.264 Annex-B |
| RTSP/RTP | H.264 over RTP, transported through RTSP/TCP |
| Decoder | S100 BSP H.264 hardware decoder |
| Display input | NV12 scaled by VPS to 800×480 |

The instantaneous bitrate around an IDR may exceed 8 Mbit/s. After startup, the measured Server bitrate should settle close to the configured target.

### API responsibilities

| Stage | API or component | Responsibility |
| --- | --- | --- |
| Camera/VIO | `sp_init_vio_module()`, `sp_open_camera_v2()` | Open the sensor, ISP, and NV12 output |
| Hardware encoding | `sp_init_encoder_module()`, `sp_start_encode()` | Create an H.264 hardware encoding channel |
| Module binding | `sp_module_bind()` | Connect VIO directly to Encoder |
| Encoded output | `sp_encoder_get_stream()` | Retrieve H.264 Annex-B data |
| RTSP Server | GStreamer `appsrc`, `h264parse`, `rtph264pay` | Packetize H.264 into RTP and expose an RTSP session |
| RTSP Client | GStreamer `rtspsrc`, `rtph264depay`, `h264parse`, `appsink` | Receive RTSP and reconstruct complete H.264 access units |
| Hardware decoding | `sp_init_decoder_module()`, `sp_start_decode()`, `sp_decoder_set_image()` | Submit access units to the S100 VDEC hardware |
| Scaling | `sp_open_vps()` | Scale 1920×1080 NV12 to 800×480 |
| HDMI display | `sp_start_display()` | Output through S100 HDMI channel 11 |

GStreamer does not decode the picture in this lesson. No software decoder such as `avdec_h264` is used; image decoding is performed by the S100 hardware channel receiving data through `sp_decoder_set_image()`.

### Parameters that must not be confused

| Parameter | Meaning |
| --- | --- |
| Server `--sensor-width/--sensor-height` | Camera RAW input size |
| Server/Client `--width/--height` | Encoded and decoded stream size, 1920×1080 in this lesson |
| Client `--display-width/--display-height` | HDMI output size, fixed to 800×480 in this lesson |

Do not change the Client decode dimensions to 800×480 just because the screen is 800×480. Decoder dimensions must match the Server's H.264 stream; VPS performs the resize.

## BSP API guide (two examples)

### Example 1: Camera → hardware encoding → RTSP Server

Open the first S100 terminal:

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

`--camera-index -1` enables camera auto-detection. A successful startup includes output similar to:

```text
[platform] model=D-Robotics RDK S100 ...
[0] INFO: Found sensor name:imx219-30fps ...
[camera] sensor=1920x1080 output=1920x1080 fps=30
[codec] h264 bitrate=8000 kbit/s
[rtsp] ready: rtsp://<board-ip>:8554/live
[rtsp] same-board client: rtsp://127.0.0.1:8554/live
```

Before a Client connects, a growing `no-client` counter is expected. Camera capture and hardware encoding are already active; the encoded data simply has no RTSP consumer yet.

### Example 2: RTSP Client → hardware decoding → VPS → 800×480 HDMI

Keep the Server running. In a second S100 terminal, verify HDMI first:

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
grep -x '800x480' /sys/class/drm/card0-HDMI-A-1/modes
```

Stop the desktop display service so the BSP Display path can use DRM/GBM:

```bash
sudo systemctl stop display-manager
```

The desktop disappearing is expected. Start the Client:

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
  --display-channel 11 \
  --display-width 800 \
  --display-height 480 \
  --duration 30
```

Important log lines include:

```text
[platform] model=D-Robotics RDK S100 ...
DRM is available, using GBM for rendering.
Using requested connector: type (11), id (...)
Initializing HDMI display.
Mode 0: 800x480 @ 60Hz
Renderer::init completed successfully
[codec] BSP hardware decoder=h264 size=1920x1080
[rtsp] linked H264 RTP pad
[sink] Decoder -> VPS -> Display 800x480 channel=11
[metrics] received=... rate=30.0 buffer/s ... submitted=...
```

The HDMI screen must continuously show the live camera image. Let the 30-second Client test finish before stopping the Server; stopping the Server first causes an early RTSP EOS.

Restore the desktop after testing when needed:

```bash
sudo systemctl start display-manager
```

## How to determine success

Do not accept the lesson only because the last line says `PASS`. In the current Client, `PASS` proves that RTSP/RTP data was submitted to the decoder pipeline and that Display and module binding initialized. Final acceptance also requires a visible HDMI image.

### Server acceptance criteria

- [ ] The expected camera is detected, for example `imx219-30fps`;
- [ ] The log contains `[camera] sensor=1920x1080 output=1920x1080 fps=30`;
- [ ] The log contains `[rtsp] ready`;
- [ ] `encoded` grows at approximately 30 chunks/s;
- [ ] `published` grows after the Client connects;
- [ ] `push-fail` stays at zero;
- [ ] H.264 SPS, PPS, and IDR counters are nonzero.

### Client and Display acceptance criteria

- [ ] DRM reports the HDMI connector as `Connected`;
- [ ] The renderer initializes through DRM/GBM;
- [ ] `Renderer::init completed successfully` appears;
- [ ] The sink reports `Display 800x480 channel=11`;
- [ ] `linked H264 RTP pad` appears;
- [ ] `received` and `submitted` grow at approximately 30 buffers/s;
- [ ] The 800×480 screen continuously shows the camera image;
- [ ] Orientation, aspect ratio, and color are correct, without persistent black output or corruption;
- [ ] The Client exits normally after 30 seconds.

For H.264, `NAL(vps/sps/pps/idr)` reporting `vps=0` is expected because VPS NAL units belong to H.265. Validate SPS, PPS, and IDR for H.264.

## Troubleshooting

### Auto-detection prints chip-ID warnings for other sensors

`--camera-index -1` probes several sensor drivers. Warnings for absent sensors are harmless when the log later reports:

```text
Found sensor name:imx219-30fps
```

and Camera and Encoder initialization succeed.

### `sp_open_camera_v2 failed`

Power off the board, verify the camera expansion board and ribbon orientation, confirm BSP sensor support, reboot, and ensure no other process owns Camera/VIO. Use an explicit `--camera-index` only after identifying the correct sensor route.

### `Fail to open vpu driver` or `/dev/vpu` is missing

The codec driver is not ready. This is a BSP, kernel-module, or device-node problem rather than an RTSP or camera-expansion parameter problem.

```bash
lsmod | grep -E 'hobot_vpu|hobot_jpu|hobot_videosys'
ls -l /dev/vpu /dev/jpu
dmesg | grep -Ei 'vpu|jpu|codec'
```

### Client reports `Connection refused`

```bash
ss -ltnp | grep ':8554'
pgrep -a codec_rtsp_server
```

Keep the Server running and verify the exact URL `rtsp://127.0.0.1:8554/live`.

### Server `no-client` keeps increasing

This is normal before the Client connects. After connection, expect `client media configured`, `rtsp-source=active`, and a growing `published` count.

### HDMI status is `disconnected`

Power off the S100, power and select the HDMI input on the screen, use a direct HDMI cable, connect it before boot, and then check `status` and `modes` again.

### HDMI is connected but the desktop or a black image remains

```bash
systemctl is-active display-manager
sudo systemctl stop display-manager
```

Restart the Client after stopping the desktop service. The Display path should select DRM/GBM.

### Client says PASS but the screen remains black

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
grep -x '800x480' /sys/class/drm/card0-HDMI-A-1/modes
systemctl is-active display-manager
dmesg | grep -Ei 'drm|hdmi|idu|lt9611|atomic|page.*flip|error'
```

Confirm that all three display overrides are present:

```text
--display-channel 11
--display-width 800
--display-height 480
```

Without the explicit display size, this BSP may select 1920×1080 instead of the lesson screen's native 800×480 mode.

### RTSP links but `submitted` does not grow

Use `--codec h264` and `--width 1920 --height 1080` on both endpoints. The Client must receive SPS/PPS and then an IDR before normal decoding begins.

### Client reaches `end of stream` before 30 seconds

The Server was usually stopped first. Leave it running until the Client finishes naturally.

### `hb_mm_mc_dequeue_output_buffer failed` appears after PASS

If it appears only after `[result] PASS` and the picture was correct during the run, it is a shutdown-time warning while Display, VPS, and Decoder are being unbound and stopped. Investigate further only if the error repeats during playback or accompanies a black screen.

### Port 8554 is already in use

```bash
ss -ltnp | grep ':8554'
```

Stop the old Server or select another port and update the Client URL accordingly.

### CMake cannot find GStreamer RTSP Server

Install `libgstreamer1.0-dev`, `libgstreamer-plugins-base1.0-dev`, and `libgstrtspserver-1.0-dev`, then rerun CMake configuration and build.

## Lesson summary

This lesson completed a visible codec loop on one RDK S100. Camera and ISP/VIO produced NV12; the S100 hardware encoder compressed it to H.264; GStreamer handled RTP/RTSP; the S100 hardware decoder restored NV12; VPS scaled the frame to 800×480; and HDMI channel 11 displayed it.

The responsibilities are now explicit:

- BSP VIO owns Camera and NV12 production;
- BSP Encoder and Decoder own H.264 hardware processing;
- GStreamer owns RTSP/RTP, not image decoding;
- BSP VPS owns the 1920×1080 to 800×480 resize;
- BSP Display owns HDMI output.

## Extension exercises

1. Change Server bitrate from 8000 to 4000 kbit/s and compare measured bitrate and screen quality;
2. Switch both endpoints to H.265 and verify VPS/SPS/PPS/IDR while retaining 800×480 output;
3. Keep 1920×1080 codec dimensions but compare 1280×720 and 800×480 Display outputs;
4. Change `--transport tcp` to `--transport udp` and compare startup and stability;
5. Add hardware-decoded and Display-submitted frame counters so `PASS` covers actual output progress;
6. Add preferred-mode selection while keeping explicit display-size overrides.

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
  --display-channel 11 \
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
| Client | `--display-channel` | `11` | S100 HDMI output |
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
- [RDK S100 C/C++ multimedia examples](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/cdev_demo)
- [RDK Encoder API](https://developer.d-robotics.cc/rdk_s_doc/en/Basic_Application/multi_media/multi_media_api/cdev/encoder_api)
- [RDK Decoder API](https://developer.d-robotics.cc/rdk_s_doc/en/Basic_Application/multi_media/multi_media_api/cdev/decoder_api)
- [RDK VIO API](https://developer.d-robotics.cc/rdk_s_doc/en/Basic_Application/multi_media/multi_media_api/cdev/vio_api)
- [RDK Display API](https://developer.d-robotics.cc/rdk_s_doc/en/Basic_Application/multi_media/multi_media_api/cdev/display_api)
- [GStreamer RTSP Server](https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/)
