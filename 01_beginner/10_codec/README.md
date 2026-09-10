# Lesson 10: Hardware Codec and RTSP Demo

[中文说明](README_cn.md)

This demo shows a complete hardware video codec loop on an RDK X5 or RDK S100:

```text
MIPI Camera -> NV12 -> Hardware Encoder -> H.264/H.265 -> RTSP
RTSP -> Hardware Decoder -> NV12 -> VPS -> HDMI Display
```

The server captures camera frames, encodes them with the RDK BSP, and publishes an RTSP stream. The client receives the stream, uses the BSP hardware decoder, and either displays the decoded video through HDMI or runs in headless mode.

## Requirements

- RDK X5 or RDK S100 with a supported RDK OS image
- BSP headers and `libspcdev`
- A supported MIPI camera
- CMake, a C++17 compiler, and GStreamer development packages
- An HDMI display for display mode; headless mode does not require one

Install the common build dependencies:

```bash
sudo apt update
sudo apt install -y build-essential cmake pkg-config \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libgstrtspserver-1.0-dev
```

## Build

Run the following commands on the RDK board:

```bash
cd ~/rdk-course-demos/01_beginner/10_codec
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
```

## Run

Start the RTSP server in the first terminal:

```bash
sudo ./build/codec_rtsp_server
```

Start the client in a second terminal. Stop the desktop service first if HDMI output is used:

```bash
sudo systemctl stop display-manager
sudo ./build/codec_rtsp_client \
  --url rtsp://127.0.0.1:8554/live \
  --display-width 800 --display-height 480
```

The display channel is selected automatically for X5 and S100. To test decoding without a display, use:

```bash
sudo ./build/codec_rtsp_client --headless --duration 30
```

Both programs use H.264 and 1920x1080 by default. Use `--codec h265` on both programs to test H.265, and run either program with `--help` to see all options. Press `Ctrl+C` to stop. If the desktop service was stopped, restore it with:

```bash
sudo systemctl start display-manager
```
