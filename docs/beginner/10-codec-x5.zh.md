# 第 10 课：在 RDK X5 上完成硬件编解码与 800×480 HDMI 显示

本课使用两个 C++ 程序，在同一块 RDK X5 上完成一条完整、可观察的编解码闭环。Server 从 MIPI Camera 获取 NV12 图像，调用 X5 BSP 硬件编码器生成 H.264 码流并提供本机 RTSP 服务；Client 通过回环地址拉流，调用 X5 BSP 硬件解码器恢复 NV12，再由 VPS 缩放为 800×480，通过 HDMI 屏幕显示实时 Camera 画面。

```text
Camera → ISP/VIO → NV12 → Hardware Encoder → H.264 → RTSP
       → RTSP Client → Hardware Decoder → NV12 → VPS 800×480 → HDMI Display
```

## 本课任务

| 项目 | 本课要求 |
| --- | --- |
| 适用板卡 | RDK X5 4GB、RDK X5 8GB；RDK X5 Module 需配套支持 HDMI 和 Camera 的载板 |
| Camera | X5 BSP 支持的 MIPI Camera，本课以 IMX219 为例 |
| Camera 与码流分辨率 | 1920×1080@30fps |
| 编码格式 | H.264，目标码率 8000 kbit/s |
| RTSP 地址 | `rtsp://127.0.0.1:8554/live` |
| 解码输出 | X5 硬件解码器输出 NV12 |
| 显示输出 | VPS 将 1920×1080 缩放到 800×480，输出到 Display channel 1 |
| 开发语言 | C++17 |
| 最终结果 | 800×480 HDMI 屏幕连续显示 Camera 实时画面 |

本课只使用板端屏幕验收画面。Server 和 Client 分别运行在 X5 的两个终端中，Client 始终通过 `127.0.0.1` 访问本机 RTSP 服务。

## 完成本课后你能做到什么

完成本课后，你将能够：

1. 说明 Bayer RAW、NV12、H.264、RTP 和 RTSP 在视频链路中的位置；
2. 解释为什么 Camera 画面经过网络传输时通常需要编码，显示压缩码流时又必须解码；
3. 使用 `libspcdev` 打开 X5 MIPI Camera，并创建硬件编码通道；
4. 使用 GStreamer 完成 H.264 RTP 打包、RTSP 会话和 RTP 解包；
5. 使用 X5 硬件解码器恢复 NV12 图像；
6. 使用 VPS 将 1920×1080 图像缩放为 800×480；
7. 使用 X5 Display channel 1 将解码画面显示到 HDMI 屏幕；
8. 根据日志判断故障位于 Camera、编码器、RTSP、解码器、VPS 还是 Display。

## 课前准备

### 硬件准备

- 一块 RDK X5 4GB 或 8GB；
- 一颗 X5 BSP 支持的 MIPI Camera，本课命令以 IMX219 1920×1080@30fps 为例；
- 一块支持 `800x480` 显示模式的 HDMI 屏幕；
- HDMI 线和屏幕独立供电线；
- 两个能够同时操作 X5 的终端会话。

!!! warning
    安装或调整 MIPI Camera 排线前必须关闭开发板电源。HDMI 屏幕应先供电并切换到正确输入源，再启动开发板，以便系统读取显示模式。

### 检查板卡、系统与编解码驱动

```bash
cat /proc/device-tree/model
rdkos_info || cat /etc/version
uname -a
ls -l /dev/vpu /dev/jpu 2>/dev/null
```

型号应包含 `RDK X5`。如果系统使用其他编解码设备节点，应以当前 RDK OS 和 BSP 的设备节点为准。

### 检查 HDMI 与 800×480 模式

X5 的 DRM card 和 connector 编号可能随系统版本变化，因此先枚举：

```bash
for f in /sys/class/drm/card*-*/status; do
  echo "$f: $(cat "$f")"
done

for f in /sys/class/drm/card*-*/modes; do
  echo "--- $f"
  cat "$f"
done
```

至少一个 HDMI connector 应为 `connected`，并且对应的 modes 包含：

```text
800x480
```

如果已经确定 HDMI connector 路径，还可以读取实际 EDID：

```bash
wc -c < /sys/class/drm/card0-HDMI-A-1/edid
```

`stat -c '%s'` 对 sysfs EDID 属性可能显示 `0`，不能据此断定 EDID 为空。

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

### 在 X5 本机编译

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

应在 X5 4GB 本机重新执行 CMake 和链接，不要复制 S100 或其他架构环境中的可执行文件和动态库。

## 编解码链路的必要性

### Camera 直接显示并不需要编解码

只在同一块 X5 上预览 Camera 时，最短路径是：

```text
Camera → ISP/VIO → NV12 → VPS → Display
```

这条路径不需要 H.264。本课增加 Encoder、RTSP 和 Decoder，是为了完整展示视频压缩、标准协议传输以及硬件解码的职责边界。

### 为什么需要编码

1920×1080 NV12 单帧大小为：

```text
1920 × 1080 × 3 / 2 = 3,110,400 bytes
```

以 30fps 连续传输时，原始数据量约为：

```text
3,110,400 × 30 ≈ 93.3 MB/s ≈ 746.5 Mbit/s
```

本课将其编码为约 8 Mbit/s 的 H.264，显著降低传输与存储带宽。编码器还会生成 SPS、PPS 和 IDR，供解码器建立参数和参考图像。

### 为什么需要解码

H.264 是压缩数据，不能直接作为图像送入 VPS 或 Display。Client 必须执行：

```text
RTP depay → H.264 Annex-B access unit → Hardware Decoder → NV12
```

得到 NV12 后，VPS 才能将 1920×1080 缩放成 800×480，再交给 Display 输出。

### 为什么使用本机 RTSP

- Server 与 Client 形成清晰的编码端和解码端；
- RTP 展示压缩码流的打包和重组；
- 结构可以直接扩展到跨设备传输；
- `127.0.0.1` 排除了外部网络波动，更适合课程首次验收。

## 编码能力与基础接口说明

### 本课验证的能力范围

本课不测试 X5 的极限并发能力，而是验证单路 1080p30 编解码和 800×480 显示闭环。

| 参数 | 本课设置 |
| --- | --- |
| Camera 输入 | IMX219，1920×1080@30fps |
| ISP/VIO 输出 | NV12，1920×1080 |
| 编码器 | X5 BSP H.264 硬件编码器 |
| 目标码率 | 8000 kbit/s |
| 码流格式 | H.264 Annex-B |
| RTSP/RTP | H.264 over RTP，RTSP/TCP |
| 解码器 | X5 BSP H.264 硬件解码器 |
| Display 输入 | VPS 输出 NV12，800×480 |

X5 编码输入宽高需要满足 BSP 对齐要求；本课的 1920×1080 已满足常用的 16 像素对齐约束。首个 IDR 附近的瞬时码率可能高于目标值，稳定运行后应接近 8 Mbit/s。

### 基础接口及职责边界

| 环节 | 关键接口或组件 | 作用 |
| --- | --- | --- |
| Camera/VIO | `sp_init_vio_module()`、`sp_open_camera_v2()` | 打开 Camera、ISP 和 NV12 输出 |
| 硬件编码 | `sp_init_encoder_module()`、`sp_start_encode()` | 创建 H.264 硬件编码通道 |
| 模块绑定 | `sp_module_bind()` | 建立 VIO → Encoder 板内通路 |
| 读取码流 | `sp_encoder_get_stream()` | 获取 H.264 Annex-B 码流 |
| RTSP Server | GStreamer `appsrc`、`h264parse`、`rtph264pay` | RTP 打包与 RTSP 服务 |
| RTSP Client | GStreamer `rtspsrc`、`rtph264depay`、`h264parse`、`appsink` | 拉流、RTP 解包和访问单元重组 |
| 硬件解码 | `sp_init_decoder_module()`、`sp_start_decode()`、`sp_decoder_set_image()` | 把访问单元送入 X5 VDEC |
| VPS | `sp_open_vps()` | 将 1920×1080 NV12 缩放成 800×480 |
| HDMI Display | `sp_start_display()` | 使用 X5 Display channel 1 输出画面 |

GStreamer 不承担图像解码。本课没有使用 `avdec_h264` 等软件解码器，真正的 H.264 解码发生在 X5 BSP 硬件解码通道中。

### 三组容易混淆的参数

| 参数 | 含义 |
| --- | --- |
| Server `--sensor-width/--sensor-height` | Camera RAW 输入尺寸 |
| Server/Client `--width/--height` | 编码和解码码流尺寸，本课为 1920×1080 |
| Client `--display-width/--display-height` | HDMI 屏幕尺寸，本课固定为 800×480 |

不要把 Client 的解码宽高改为 800×480。Server 产生的是 1920×1080 H.264，Decoder 也必须按 1920×1080 初始化，VPS 才负责最终缩放。

## BSP 接口使用指南（两个示例）

### 示例一：Camera → 硬件编码 → RTSP Server

打开第一个 X5 终端：

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
[platform] model=D-Robotics RDK X5 ...
[camera] sensor=1920x1080 output=1920x1080 fps=30
[codec] h264 bitrate=8000 kbit/s
[rtsp] ready: rtsp://<board-ip>:8554/live
[rtsp] same-board client: rtsp://127.0.0.1:8554/live
```

Client 尚未连接时，`no-client` 增加是正常现象。Client 连接后，`published` 应持续增加，`push-fail` 应保持为 0。

### 示例二：RTSP Client → 硬件解码 → VPS → 800×480 HDMI

保持示例一的 Server 运行。打开第二个 X5 终端，再次确认某个 HDMI connector 为 `connected` 且支持 `800x480`。

停止桌面显示服务：

```bash
sudo systemctl stop display-manager
```

在部分 X5 镜像中，实际服务是 `lightdm`；`display-manager` 是指向当前显示管理器的通用服务名。桌面消失属于正常现象。

运行 Client：

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

关键日志应包含：

```text
[platform] model=...RDK X5...
[codec] BSP hardware decoder=h264 size=1920x1080
[rtsp] linked H264 RTP pad
[sink] Decoder -> VPS -> Display 800x480 channel=1
[metrics] received=... rate=30.0 buffer/s ... submitted=...
```

根据 X5 BSP 版本，Display 初始化阶段可能显示 `Opened DRM device`、`DRM is available`、`sp_start_display success` 或等价信息。运行期间，800×480 HDMI 屏幕必须连续显示 Camera 画面。

等待 Client 的 30 秒测试自然结束后，再停止 Server。需要恢复桌面时执行：

```bash
sudo systemctl start display-manager
```

## 如何判断成功

不要只依据最后一行 `PASS`。当前 Client 的 `PASS` 证明 RTSP/RTP 码流已提交到硬件解码管线，并且 VPS、Display 与模块绑定初始化成功；最终验收还必须观察 HDMI 物理画面。

### Server 成功标准

- [ ] 识别到正确 Camera；
- [ ] 输出分辨率为 1920×1080，帧率为 30fps；
- [ ] 出现 `[rtsp] ready`；
- [ ] `encoded` 以约 30 chunk/s 增加；
- [ ] Client 连接后 `published` 持续增加；
- [ ] `push-fail=0`；
- [ ] H.264 SPS、PPS、IDR 均大于 0。

### Client 与 Display 成功标准

- [ ] HDMI connector 为 `connected`；
- [ ] Display/DRM 初始化成功；
- [ ] 日志显示 `Display 800x480 channel=1`；
- [ ] 出现 `linked H264 RTP pad`；
- [ ] `received` 和 `submitted` 以约 30 buffer/s 增加；
- [ ] 800×480 屏幕连续显示实时 Camera 画面；
- [ ] 画面方向、比例和颜色正常，没有持续黑屏或花屏；
- [ ] Client 在 30 秒后正常结束。

H.264 日志中的 `vps=0` 是正常现象；VPS NAL 仅属于 H.265，H.264 应检查 SPS、PPS 和 IDR。

## 常见问题与排查

### X5 4GB 上编译速度慢或内存紧张

使用：

```bash
cmake --build build -j2
```

不要默认使用 `-j$(nproc)`。本课只有少量 C++ 文件，`-j2` 足够并能降低编译峰值内存。

### `sp_open_camera_v2 failed`

关闭 X5 电源，检查 Camera 排线方向、接口位置和传感器型号；重新上电后确认没有其他程序占用 VIO。自动探测失败时，再根据实际 Camera 路由指定 `--camera-index`。

### `Fail to open vpu driver` 或硬件解码初始化失败

检查编解码设备节点、内核模块和 BSP 版本：

```bash
lsmod | grep -Ei 'vpu|jpu|video'
ls -l /dev/vpu /dev/jpu 2>/dev/null
dmesg | grep -Ei 'vpu|jpu|codec|decoder|encoder'
```

这类问题不应通过修改 RTSP URL 或屏幕参数解决。

### Client 提示 `Connection refused`

```bash
ss -ltnp | grep ':8554'
pgrep -a codec_rtsp_server
```

确认 Server 仍在运行，并且 Client 使用 `rtsp://127.0.0.1:8554/live`。

### Server 的 `no-client` 持续增加

Client 连接前属于正常现象。连接后应看到 `client media configured`、`rtsp-source=active`，并且 `published` 开始增加。

### HDMI connector 为 `disconnected`

关闭 X5，给屏幕供电并切换到 HDMI 输入，使用直连线缆，在 HDMI 已连接的状态下重新上电，然后再次枚举 `/sys/class/drm/card*-*/status`。

### HDMI 已连接，但仍显示桌面或黑屏

```bash
systemctl is-active display-manager
sudo systemctl stop display-manager
```

随后重新启动 Client。X5 官方直连显示示例同样要求在直接使用显示资源前停止桌面服务。

### Client 输出 PASS，但 800×480 屏幕仍黑

确认对应 HDMI connector 的 modes 包含 `800x480`，并检查：

```bash
systemctl is-active display-manager
dmesg | grep -Ei 'drm|hdmi|display|atomic|page.*flip|error'
```

Client 命令必须同时包含：

```text
--display-channel 1
--display-width 800
--display-height 480
```

不显式指定 800×480 时，X5 代码会在显示模式列表中优先匹配 1920×1080 码流尺寸，可能与本课小屏的原生模式不一致。

### RTSP 已连接，但 `submitted` 不增加

确认 Server 和 Client 的 codec、宽度和高度完全一致。H.264 解码开始前必须收到 SPS/PPS，并等待 IDR；正常情况下启动阶段允许有短暂缓存。

### Client 未到 30 秒就出现 `end of stream`

通常是第一个终端中的 Server 被提前停止。先等待 Client 自然结束，再停止 Server。

### PASS 后出现解码输出队列错误

如果错误只出现在 `[result] PASS` 之后，且运行期间画面正常，通常属于资源解绑和 Decoder 停止阶段的收尾告警。若运行期间反复出现并伴随黑屏，再检查 BSP 版本和解码输出队列。

### 8554 端口被占用

```bash
ss -ltnp | grep ':8554'
```

停止旧 Server，或者修改 Server 端口并同步更新 Client URL。

### CMake 找不到 GStreamer 或 RTSP Server

确认安装 `libgstreamer1.0-dev`、`libgstreamer-plugins-base1.0-dev` 和 `libgstrtspserver-1.0-dev`，随后重新运行 CMake。

## 本课小结

本课在一块 RDK X5 上完成了可见的硬件编解码闭环：Camera 经 ISP/VIO 产生 NV12，X5 硬件编码器将其压缩为 H.264，GStreamer 负责 RTP/RTSP，X5 硬件解码器恢复 NV12，VPS 将画面缩放为 800×480，最后通过 Display channel 1 输出到 HDMI 屏幕。

各层职责如下：

- BSP VIO 负责 Camera 与 NV12；
- BSP Encoder/Decoder 负责 H.264 硬件编解码；
- GStreamer 负责 RTSP/RTP，不负责图像解码；
- BSP VPS 负责 1920×1080 到 800×480 的缩放；
- BSP Display 负责 HDMI 输出。

## 拓展练习

1. 将 Server 码率从 8000 kbit/s 调整为 4000 kbit/s，比较实际码率和屏幕画质；
2. 将 Server 与 Client 同时切换为 H.265，并继续输出到 800×480 屏幕；
3. 保持 1920×1080 编解码，比较 1280×720 与 800×480 Display 输出；
4. 将 TCP 改为 UDP，比较启动速度和稳定性；
5. 增加硬件解码输出帧数和 Display 提交帧数统计，使 `PASS` 覆盖真实输出进度；
6. 在 X5 4GB 和 8GB 上分别记录 CPU、内存占用和实际帧率。

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
  --display-channel 1 \
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
| Server | `--bitrate` | `8000` | 目标码率，单位 kbit/s |
| Server | `--port` | `8554` | RTSP 监听端口 |
| Server | `--mount` | `/live` | RTSP 挂载路径 |
| Client | `--url` | `rtsp://127.0.0.1:8554/live` | 本机回环 RTSP URL |
| Client | `--width/--height` | `1920/1080` | 硬件解码尺寸 |
| Client | `--transport` | `tcp` | RTSP/RTP 传输方式 |
| Client | `--latency` | `100` | GStreamer 抖动缓冲，单位 ms |
| Client | `--vps-pipe-id` | `1` | Display 缩放使用的 VPS pipeline |
| Client | `--display-channel` | `1` | X5 视频显示层 |
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
- [RDK X3/X5 rtsp2display 示例](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/cdev_demo_sample/rtsp2display)
- [RDK X3/X5 Encoder API](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/encoder_api)
- [RDK X3/X5 Decoder API](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/decoder_api)
- [RDK X3/X5 Display API](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/multi_media_sp_dev_api/RDK_X3/cdev_multimedia_api_x3/display_api)
- [GStreamer RTSP Server](https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/)
