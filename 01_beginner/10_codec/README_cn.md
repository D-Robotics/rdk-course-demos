# 第十课：硬件编解码与 RTSP Demo

[English](README.md)

本 Demo 在 RDK X5 或 RDK S100 上演示完整的硬件视频编解码链路：

```text
MIPI Camera -> NV12 -> 硬件编码 -> H.264/H.265 -> RTSP
RTSP -> 硬件解码 -> NV12 -> VPS -> HDMI 显示
```

服务端采集摄像头画面，使用 RDK BSP 硬件编码器进行编码，并发布 RTSP 视频流；客户端接收视频流，使用 BSP 硬件解码器解码，然后通过 HDMI 显示，也可以使用无显示器模式运行。

## 环境要求

- 安装受支持 RDK OS 的 RDK X5 或 RDK S100
- BSP 头文件和 `libspcdev`
- RDK 支持的 MIPI 摄像头
- CMake、支持 C++17 的编译器及 GStreamer 开发包
- 使用显示模式时需要 HDMI 显示器；无显示器模式不需要

安装常用构建依赖：

```bash
sudo apt update
sudo apt install -y build-essential cmake pkg-config \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libgstrtspserver-1.0-dev
```

## 编译

请在 RDK 开发板上执行：

```bash
cd ~/rdk-course-demos/01_beginner/10_codec
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
```

## 运行

在第一个终端启动 RTSP 服务端：

```bash
sudo ./build/codec_rtsp_server
```

在第二个终端启动客户端。需要 HDMI 输出时，请先停止桌面服务：

```bash
sudo systemctl stop display-manager
sudo ./build/codec_rtsp_client \
  --url rtsp://127.0.0.1:8554/live \
  --display-width 800 --display-height 480
```

程序会自动为 X5 和 S100 选择对应的显示通道。若只测试解码、不使用显示器，可执行：

```bash
sudo ./build/codec_rtsp_client --headless --duration 30
```

服务端和客户端默认使用 H.264、1920x1080。测试 H.265 时，两端都需要添加 `--codec h265`。执行任一程序并添加 `--help` 可查看全部参数，按 `Ctrl+C` 停止程序。如停止过桌面服务，可使用以下命令恢复：

```bash
sudo systemctl start display-manager
```
