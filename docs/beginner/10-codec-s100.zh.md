# 第 10 课：在 RDK S100 上完成硬件编解码与 800×480 HDMI 显示

本课使用两个 C++ 程序，在同一块 RDK S100 上完成一条完整、可观察的编解码闭环。Server 从 MIPI Camera 获取 NV12 图像，调用 S100 BSP 硬件编码器生成 H.264 码流并提供本机 RTSP 服务；Client 通过回环地址拉流，调用 S100 BSP 硬件解码器恢复 NV12，再由 VPS 缩放为 800×480，通过 HDMI 屏幕显示实时 Camera 画面。

```text
Camera → ISP/VIO → NV12 → Hardware Encoder → H.264 → RTSP
       → RTSP Client → Hardware Decoder → NV12 → VPS 800×480 → HDMI Display
```

## 本课任务

| 项目 | 本课要求 |
| --- | --- |
| 适用板卡 | RDK S100 |
| Camera | S100 BSP 支持的 MIPI Camera，本课实测使用 IMX219 |
| Camera 与码流分辨率 | 1920×1080@30fps |
| 编码格式 | H.264，目标码率 8000 kbit/s |
| RTSP 地址 | `rtsp://127.0.0.1:8554/live` |
| 解码输出 | S100 硬件解码器输出 NV12 |
| 显示输出 | VPS 将 1920×1080 缩放到 800×480，输出到 HDMI channel 11 |
| 开发语言 | C++17 |
| 最终结果 | 800×480 HDMI 屏幕连续显示 Camera 实时画面 |

本课只使用板端屏幕验收画面。Server 和 Client 分别运行在 S100 的两个终端中，Client 始终通过 `127.0.0.1` 访问本机 RTSP 服务。

## 完成本课后你能做到什么

完成本课后，你将能够：

1. 说明 Bayer RAW、NV12、H.264、RTP 和 RTSP 在视频链路中的位置；
2. 解释为什么 Camera 画面经过网络传输时通常需要编码，显示压缩码流时又必须解码；
3. 使用 `libspcdev` 打开 MIPI Camera，并创建 S100 硬件编码通道；
4. 使用 GStreamer 完成 H.264 的 RTP 打包、RTSP 会话和 RTP 解包；
5. 使用 S100 硬件解码器恢复 NV12 图像；
6. 使用 VPS 将 1920×1080 图像缩放为 800×480；
7. 使用 S100 HDMI channel 11 将解码画面显示到屏幕；
8. 根据日志判断故障位于 Camera、编码器、RTSP、解码器、VPS 还是 Display。

## 课前准备

### 硬件准备

- 一块 RDK S100；
- 一颗 S100 BSP 支持的 MIPI Camera，本课命令以 IMX219 1920×1080@30fps 为例；
- S100 Camera 扩展板及正确安装的 Camera 排线；
- 一块支持 `800x480` 显示模式的 HDMI 屏幕；
- HDMI 线和屏幕独立供电线；
- 两个能够同时操作 S100 的终端会话。

!!! warning
    安装或调整 MIPI Camera 排线前必须关闭开发板电源。HDMI 屏幕应先供电并切换到正确输入源，再启动开发板，以便系统读取显示模式。

### 检查板卡、编解码驱动与 HDMI

```bash
cat /proc/device-tree/model
cat /etc/version
uname -a
ls -l /dev/vpu /dev/jpu
```

型号应包含 `RDK S100`，并且 `/dev/vpu`、`/dev/jpu` 存在。

检查 HDMI 连接和 800×480 模式：

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
cat /sys/class/drm/card0-HDMI-A-1/modes
wc -c < /sys/class/drm/card0-HDMI-A-1/edid
```

本课要求：

```text
status: connected
modes: 包含 800x480
EDID: 读取结果通常大于 0
```

`stat -c '%s' /sys/class/drm/card0-HDMI-A-1/edid` 可能始终显示 `0`，这是 sysfs 文件元数据的表现，不能据此判断 EDID 是否为空；应使用 `wc -c` 实际读取内容。

### 检查 BSP 开发接口

```bash
test -f /usr/include/sp_codec.h && echo "sp_codec.h: ready"
ldconfig -p | grep libspcdev
```

### 安装编译和 RTSP 依赖

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

检查本课需要的 GStreamer 元素：

```bash
gst-inspect-1.0 appsrc
gst-inspect-1.0 appsink
gst-inspect-1.0 h264parse
gst-inspect-1.0 rtph264pay
gst-inspect-1.0 rtph264depay
gst-inspect-1.0 rtspsrc
```

### 编译本课程序

```bash
cd ~/rdk-course-demos/01_beginner/10_codec
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
```

检查产物：

```bash
ls -l build/codec_rtsp_server build/codec_rtsp_client
./build/codec_rtsp_server --help
./build/codec_rtsp_client --help
```

构建输出应包含：

```text
Built target codec_rtsp_server
Built target codec_rtsp_client
```

## 编解码链路的必要性

### Camera 直接显示并不需要编解码

如果目标只是把同一块开发板上的 Camera 画面显示到 HDMI，最短链路可以是：

```text
Camera → ISP/VIO → NV12 → VPS → Display
```

这条链路不需要 H.264 编码和解码。本课有意增加编解码与 RTSP，是为了展示视频压缩、协议传输和硬件解码在真实视频系统中的作用。

### 为什么需要编码

ISP/VIO 输出的 1920×1080 NV12 单帧大小为：

```text
1920 × 1080 × 3 / 2 = 3,110,400 bytes
```

以 30fps 连续传输时，原始数据量约为：

```text
3,110,400 × 30 ≈ 93.3 MB/s ≈ 746.5 Mbit/s
```

本课将视频编码为约 8 Mbit/s 的 H.264 码流，显著降低传输和存储带宽。编码器还会生成 SPS、PPS 和 IDR 等解码所需信息，使视频能够按标准码流传输。

### 为什么需要解码

H.264 是压缩码流，不能作为 NV12 图像直接送入 VPS 或 Display。Client 必须先完成：

```text
RTP depay → H.264 Annex-B access unit → Hardware Decoder → NV12
```

得到 NV12 后，VPS 才能把 1920×1080 缩放成屏幕需要的 800×480，Display 再将图像送往 HDMI。

### 为什么仍然使用 RTSP

本课的 Server 与 Client 虽然运行在同一块 S100 上，但 RTSP 仍然具有教学价值：

- Server 与 Client 形成清晰的编码端和解码端边界；
- RTP 展示压缩视频如何被打包、传输和重新组装；
- 同一份结构可以扩展到跨设备视频传输；
- 使用 `127.0.0.1` 可以排除外部网络抖动，先验证编解码和显示本身。

## 编码能力与基础接口说明

### 本课验证的编码能力

本课不测试 S100 编解码器的极限并发能力，而是验证一条稳定、可重复的单路视频链路：

| 参数 | 本课设置 |
| --- | --- |
| Camera 输入 | IMX219，1920×1080@30fps |
| ISP/VIO 输出 | NV12，1920×1080 |
| 编码器 | S100 BSP H.264 硬件编码器 |
| 目标码率 | 8000 kbit/s |
| 码流格式 | H.264 Annex-B |
| RTSP/RTP | H.264 over RTP，RTSP TCP 控制与传输 |
| 解码器 | S100 BSP H.264 硬件解码器 |
| Display 输入 | VPS 输出的 NV12，800×480 |

首个 IDR 附近的瞬时码率可能高于 8 Mbit/s；稳定运行后，Server 日志中的实际码率应接近目标值。

### 基础接口及职责边界

| 环节 | 关键接口或组件 | 作用 |
| --- | --- | --- |
| Camera/VIO | `sp_init_vio_module()`、`sp_open_camera_v2()` | 打开 Camera、ISP 和 NV12 输出 |
| 硬件编码 | `sp_init_encoder_module()`、`sp_start_encode()` | 创建 H.264 硬件编码通道 |
| 模块绑定 | `sp_module_bind()` | 建立 VIO → Encoder 的板内数据通路 |
| 读取码流 | `sp_encoder_get_stream()` | 获取 H.264 Annex-B 编码数据 |
| RTSP Server | GStreamer `appsrc`、`h264parse`、`rtph264pay` | 将 H.264 打包成 RTP 并提供 RTSP 会话 |
| RTSP Client | GStreamer `rtspsrc`、`rtph264depay`、`h264parse`、`appsink` | 拉流、RTP 解包并输出完整 H.264 访问单元 |
| 硬件解码 | `sp_init_decoder_module()`、`sp_start_decode()`、`sp_decoder_set_image()` | 将 H.264 访问单元送入 S100 VDEC |
| VPS | `sp_open_vps()` | 将 1920×1080 NV12 缩放为 800×480 |
| HDMI Display | `sp_start_display()` | 使用 S100 HDMI channel 11 输出画面 |

GStreamer 不承担图像解码。本课没有使用 `avdec_h264` 等软件解码器；真正的 H.264 解码由 `sp_decoder_set_image()` 对应的 S100 硬件解码通道完成。

### 三组容易混淆的参数

| 参数 | 含义 |
| --- | --- |
| Server `--sensor-width/--sensor-height` | Camera RAW 输入尺寸 |
| Server/Client `--width/--height` | 编码和解码码流尺寸，本课为 1920×1080 |
| Client `--display-width/--display-height` | HDMI 显示尺寸，本课固定为 800×480 |

不能为了适配 800×480 屏幕而把 Client 的 `--width/--height` 改成 800×480；解码器尺寸必须与 Server 产生的 H.264 码流一致，缩放工作由 VPS 完成。

## BSP 接口使用指南

### 示例一：Camera → 硬件编码 → RTSP Server

打开第一个 S100 终端：

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

`--camera-index -1` 表示自动探测 Camera。初始化成功后应看到类似输出：

```text
[platform] model=D-Robotics RDK S100 ...
[0] INFO: Found sensor name:imx219-30fps ...
[camera] sensor=1920x1080 output=1920x1080 fps=30
[codec] h264 bitrate=8000 kbit/s
[rtsp] ready: rtsp://<board-ip>:8554/live
[rtsp] same-board client: rtsp://127.0.0.1:8554/live
```

Client 尚未连接时，日志中的 `no-client` 持续增加是正常现象。此时 Camera 与硬件编码器已经工作，只是编码数据尚未发布给 RTSP Client。

### 示例二：RTSP Client → 硬件解码 → VPS → 800×480 HDMI

保持示例一的 Server 持续运行。打开第二个 S100 终端，先检查 HDMI：

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
grep -x '800x480' /sys/class/drm/card0-HDMI-A-1/modes
```

停止桌面显示服务，让 BSP Display 使用 DRM/GBM：

```bash
sudo systemctl stop display-manager
```

桌面消失属于正常现象。随后运行 Client：

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

关键日志应包含：

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

运行期间，800×480 HDMI 屏幕应连续显示 Camera 实时画面。等待 Client 的 30 秒测试自然结束，再停止 Server；如果先停止 Server，Client 会提前收到 RTSP EOS。

测试结束后如需恢复桌面：

```bash
sudo systemctl start display-manager
```

## 如何判断成功

不要只根据最后一行 `PASS` 判断屏幕显示成功。当前 Client 的 `PASS` 能证明 RTSP/RTP 数据已送入硬件解码管线、Display 和模块绑定初始化成功，但最终验收还必须观察 HDMI 屏幕。

### Server 成功标准

- 日志识别到正确的 Camera，例如 `imx219-30fps`；
- 出现 `[camera] sensor=1920x1080 output=1920x1080 fps=30`；
- 出现 `[rtsp] ready`；
- `encoded` 以约 30 chunk/s 增加；
- Client 连接后，`published` 持续增加；
- `push-fail` 保持为 0；
- H.264 的 SPS、PPS 和 IDR 计数均大于 0。

### Client 与 Display 成功标准

- DRM 报告 HDMI connector 为 `Connected`；
- 日志显示 `DRM is available, using GBM for rendering`；
- `Renderer::init completed successfully`；
- 日志显示 `Display 800x480 channel=11`；
- `linked H264 RTP pad`；
- `received` 和 `submitted` 以约 30 buffer/s 增加；
- 800×480 屏幕连续显示 Camera 画面；
- 画面方向、比例和颜色正常，没有持续黑屏、花屏或明显撕裂；
- 30 秒结束时 Client 正常退出。

H.264 日志中的 `NAL(vps/sps/pps/idr)` 第一项 `vps=0` 是正常的，因为 VPS 只用于 H.265；H.264 验收重点是 SPS、PPS 和 IDR。

## 常见问题与排查

### 自动探测时出现其他传感器 Chip ID 警告

`--camera-index -1` 会依次探测多个传感器。只要随后出现：

```text
Found sensor name:imx219-30fps
```

并且 Camera、编码器成功初始化，其他未连接传感器的 Chip ID 警告可以忽略。

### `sp_open_camera_v2 failed`

1. 关闭 S100 电源；
2. 检查 Camera 与扩展板排线方向；
3. 确认 Camera 型号受当前 BSP 支持；
4. 重新上电；
5. 确认没有其他程序占用 Camera/VIO；
6. 仍失败时再尝试显式指定正确的 `--camera-index`。

### `Fail to open vpu driver` 或 `/dev/vpu` 不存在

这表示硬件编解码驱动没有准备好，问题位于 BSP、内核模块或设备节点，不是 RTSP 参数，也不是 Camera 扩展板本身。检查：

```bash
lsmod | grep -E 'hobot_vpu|hobot_jpu|hobot_videosys'
ls -l /dev/vpu /dev/jpu
dmesg | grep -Ei 'vpu|jpu|codec'
```

### Client 提示 `Connection refused`

确认 Server 仍在第一个终端运行：

```bash
ss -ltnp | grep ':8554'
pgrep -a codec_rtsp_server
```

同时确认 Client URL 完整匹配：

```text
rtsp://127.0.0.1:8554/live
```

### Server 的 `no-client` 持续增加

在 Client 尚未连接时属于正常现象。Client 成功连接后应出现：

```text
[rtsp] client media configured
rtsp-source=active
```

并且 `published` 开始增加。

### HDMI 状态为 `disconnected`

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
```

若结果为 `disconnected`：

1. 关闭 S100；
2. 给屏幕独立供电并选择 HDMI 输入；
3. 使用直连 HDMI 线；
4. 先连接屏幕，再给 S100 上电；
5. 启动后重新检查状态和 modes。

### HDMI 已连接，但屏幕仍显示桌面或黑屏

确认已经停止桌面服务：

```bash
systemctl is-active display-manager
sudo systemctl stop display-manager
```

随后重新启动 Client。日志应选择 GBM/DRM，而不是继续由桌面系统占用显示设备。

### HDMI 已连接、Client 输出 PASS，但屏幕仍黑

依次确认：

```bash
cat /sys/class/drm/card0-HDMI-A-1/status
grep -x '800x480' /sys/class/drm/card0-HDMI-A-1/modes
systemctl is-active display-manager
dmesg | grep -Ei 'drm|hdmi|idu|lt9611|atomic|page.*flip|error'
```

本课命令必须同时包含：

```text
--display-channel 11
--display-width 800
--display-height 480
```

如果不指定显示尺寸，当前 BSP 可能从 modes 中选择 1920×1080，而不是本课屏幕的 800×480 原生模式。

### RTSP 已连接，但 `submitted` 不增加

确认 Server 与 Client 都使用 `--codec h264`，并且两端 `--width 1920 --height 1080` 一致。Client 必须先收到 SPS/PPS 和 IDR，才能开始正确解码。

### Client 未到 30 秒就出现 `end of stream`

通常是 Server 被提前停止。应保持第一个终端中的 Server 运行，等待 Client 自然结束后再按 `Ctrl+C` 停止 Server。

### PASS 后出现 `hb_mm_mc_dequeue_output_buffer failed`

如果错误只发生在 `[result] PASS` 之后，并且运行期间画面正常，它通常来自退出时解绑 Display、停止 VPS 和关闭 Decoder 的收尾过程，不影响本次运行结果。若该错误在运行过程中反复出现并伴随黑屏，则需要进一步检查解码器输出队列和 BSP 版本。

### 8554 端口被占用

```bash
ss -ltnp | grep ':8554'
```

停止旧的 `codec_rtsp_server`，或者让 Server 使用其他端口，并同步修改 Client URL。

### CMake 找不到 GStreamer RTSP Server

确认安装：

```bash
sudo apt install -y \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libgstrtspserver-1.0-dev
```

然后重新执行 CMake 配置和构建。

## 本课小结

本课在一块 RDK S100 上完成了可见的硬件编解码闭环：Camera 经 ISP/VIO 产生 NV12，S100 硬件编码器将其压缩为 H.264，GStreamer 负责 RTP/RTSP，S100 硬件解码器恢复 NV12，VPS 将画面缩放为 800×480，最后由 HDMI channel 11 输出到屏幕。

这条链路明确划分了各层职责：

- BSP VIO 负责 Camera 与 NV12；
- BSP Encoder/Decoder 负责 H.264 硬件编解码；
- GStreamer 负责 RTSP/RTP，不负责图像解码；
- BSP VPS 负责 1920×1080 到 800×480 的缩放；
- BSP Display 负责 HDMI 输出。

完成本课后，你不仅能运行 Demo，也能根据每一层的日志定位 Camera、编码、传输、解码和显示问题。

## 拓展练习

1. 将 Server 码率从 8000 kbit/s 调整为 4000 kbit/s，比较日志中的实际码率和屏幕画面质量；
2. 将 Server 与 Client 同时切换为 H.265，观察 VPS/SPS/PPS/IDR 统计，并继续输出到 800×480 屏幕；
3. 在保持 1920×1080 编解码的前提下，分别尝试 1280×720 和 800×480 Display 输出，比较 VPS 缩放效果；
4. 将 `--transport tcp` 改为 `--transport udp`，比较画面启动速度与稳定性；
5. 修改 Client，增加“硬件解码输出帧数”和“Display 提交帧数”统计，使 `PASS` 同时覆盖解码和显示阶段；
6. 修改 Client，使其优先选择 HDMI 的原生或首选模式，并保留 `--display-width/--display-height` 作为显式覆盖参数。

## 附录

### 附录 A：完整运行顺序

终端一：

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

终端二：

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

恢复桌面：

```bash
sudo systemctl start display-manager
```

### 附录 B：关键参数速查

| 程序 | 参数 | 本课值 | 说明 |
| --- | --- | --- | --- |
| Server | `--camera-index` | `-1` | 自动探测 Camera |
| Server | `--pipe-id` | `0` | Camera VIO pipeline |
| Server | `--width/--height` | `1920/1080` | 编码码流尺寸 |
| Server | `--fps` | `30` | Camera 与 RTP 帧率 |
| Server | `--bitrate` | `8000` | 编码目标码率，单位 kbit/s |
| Server | `--port` | `8554` | RTSP 监听端口 |
| Server | `--mount` | `/live` | RTSP 挂载路径 |
| Client | `--url` | `rtsp://127.0.0.1:8554/live` | 本机回环 RTSP 地址 |
| Client | `--width/--height` | `1920/1080` | 硬件解码尺寸 |
| Client | `--transport` | `tcp` | RTSP/RTP 传输方式 |
| Client | `--latency` | `100` | GStreamer 抖动缓冲，单位 ms |
| Client | `--vps-pipe-id` | `1` | Display 缩放使用的 VPS pipeline |
| Client | `--display-channel` | `11` | S100 HDMI 输出 |
| Client | `--display-width/--display-height` | `800/480` | 本课屏幕输出尺寸 |

### 附录 C：源码与 BSP 接口对应关系

| 文件 | 主要职责 |
| --- | --- |
| `src/codec_rtsp_server.cpp` | Camera、硬件编码、RTSP Server、编码指标 |
| `src/codec_rtsp_client.cpp` | RTSP Client、RTP depay、硬件解码输入、运行指标 |
| `src/codec_common.cpp` | 平台识别、VPS、Display、模块绑定和 NAL 统计 |
| `src/codec_common.hpp` | 公共类型、显示配置和指标结构 |
| `CMakeLists.txt` | C++17、`libspcdev`、GStreamer 和线程库链接 |

### 附录 D：参考资料

- [课程代码与素材](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec)
- [RDK S100 C/C++ 多媒体参考示例](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/cdev_demo)
- [RDK Encoder API](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/multi_media_api/cdev/encoder_api)
- [RDK Decoder API](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/multi_media_api/cdev/decoder_api)
- [RDK VIO API](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/multi_media_api/cdev/vio_api)
- [RDK Display API](https://developer.d-robotics.cc/rdk_s_doc/Basic_Application/multi_media/multi_media_api/cdev/display_api)
- [GStreamer RTSP Server](https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/)
