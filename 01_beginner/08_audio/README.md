# RDK 音频外设入门

> **课程定位：** 认识 RDK X5 上的四种音频硬件（板载 3.5mm、USB 扬声器、WM8960 Audio HAT、Audio Driver HAT REV2），掌握声卡侦察、录音与播放验证，理解声卡序号漂移与 Codec 路由配置。
>
> **适用硬件：** RDK X5
>
> **在线讲义：** [RDK 音频外设入门](https://d-robotics.github.io/rdk-course-demos/zh/beginner/08-audio/)
>
> **官方文档：** [RDK 音频应用](https://developer.d-robotics.cc/rdk_doc_center/)

---

## 课程主线

四种音频硬件，本质是三类设备，按配置复杂度递增排列：

| 硬件 | 类型 | 配置要求 |
|------|------|----------|
| 板载 3.5mm（ES8326） | 零配置 | 4 段式耳机，插到底 |
| USB 扬声器 | 零配置 | 即插即用，注意序号漂移 |
| WM8960 Audio HAT | 单 Codec 需路由 | srpi-config 选型 + tinymix 路由 |
| Audio Driver HAT REV2 | 双 Codec 多麦 | 拨码全 OFF + srpi-config 选型 |

每一段都重复同一套侦察流程：**看声卡 → 看节点 → 看端点**，然后才执行录放操作。

## 硬件清单

| 物品 | 数量 | 说明 |
|------|------|------|
| RDK X5 | 1 | 已完成烧录，SSH 可连接 |
| 4 段式 3.5mm 耳机 | 1 | CTIA 标准，带 MIC |
| USB 扬声器 | 1 | 任意 USB-Audio 设备 |
| 微雪 WM8960 Audio HAT | 1 | 40pin 接入 |
| 微雪 Audio Driver HAT REV2 | 1 | 40pin 接入，拨码全 OFF |

> 接入或拔出 HAT 子板前务必断电。

## 关键命令速查

```shell
# 侦察三件套
cat /proc/asound/cards
ls /dev/snd/
aplay -l

# 板载 3.5mm 录放（不接子板时板载独占 0 号；录 16bit，标准格式）
arecord -Dhw:0,0 -c 2 -r 48000 -f S16_LE -t wav -d 10 /userdata/record1.wav
aplay -D hw:0,0 /userdata/record1.wav

# WM8960 录音（先配输入路由，见在线讲义 6.5 节）
tinycap ./2chn_test.wav -D 0 -d 0 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5
tinyplay ./2chn_test.wav -D 0 -d 0

# Audio Driver HAT REV2（注意录音设备号是 -d 1）
tinycap ./4chn_test.wav -D 0 -d 1 -c 4 -b 16 -r 48000 -p 512 -n 4 -t 5
```

完整命令清单（WM8960 三种播放模式全套路由、srpi-config 操作路径、常见问题排查）见在线讲义。

## S100 回采验证工具（可选）

适用板卡：RDK S100（Audio Driver HAT REV2）。本课为命令演示课，不做独立 Demo；这个小工具只补一件事——把「麦克风拾音、回采参考信号是否正常」自动判定出来，替代在 Audacity 里逐通道人工查看。

```shell
# 1. 生成 1kHz 测试音（板端即可，纯标准库）
python3 make_tone.py --freq 1000 --seconds 30 --out 1khz.wav

# 2. 终端 A：8 通道录音（period-size 满足 64 字节对齐）
arecord -Dhw:0,0 -c 8 -r 48000 -f S16_LE -t wav -d 30 ./8chn_capture.wav \
    --period-size=256 --buffer-size=1024

# 3. 终端 B：同时播放测试音
aplay -Dhw:0,1 1khz.wav --period-size=1024 --buffer-size=1024

# 4. 分析并判定
python3 analyze_loopback.py 8chn_capture.wav
```

判定逻辑：

| 通道 | 用途 | 判定条件 |
|------|------|----------|
| ch1–ch4 | 4 路模拟麦克风 | 任一通道 RMS ≥ 阈值 → `PASS: mic capture` |
| ch5–ch6 | 未使用 | 预期静音（仅提示） |
| ch7–ch8 | 播放回采参考 | RMS ≥ 阈值 且 主频 ≈ 播放音频率（±15%）→ `PASS: loopback` |

输出示例：

```text
channel   peak      RMS        est.freq    level
------------------------------------------------------------
ch1          8500     5665.5       364 Hz   #########
...
ch7         20000    14141.7      1000 Hz   ########################
ch8         20000    14141.7      1000 Hz   ########################

[PASS] mic capture      : signal on ch1-ch4
[PASS] loopback         : 1kHz reference on ch7-ch8

Result: PASS
```

两个脚本均为 Python 标准库实现，板端直接可跑（`python3` ≥ 3.6）；FAIL 时退出码为 1，可接入自动化脚本。

## 参考资料

- [RDK 音频外设入门（中文讲义）](https://d-robotics.github.io/rdk-course-demos/zh/beginner/08-audio/)
- [Audio Peripherals on RDK X5 (English handbook)](https://d-robotics.github.io/rdk-course-demos/beginner/08-audio/)
- [RDK X5 官方音频文档](https://developer.d-robotics.cc/rdk_doc_center/)
- [微雪 WM8960 Audio HAT 产品页](https://www.waveshare.net/wiki/WM8960_Audio_HAT)
- [微雪 Audio Driver HAT 产品页](https://www.waveshare.net/shop/Audio-Driver-HAT.htm)
