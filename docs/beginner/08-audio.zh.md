# RDK 音频外设入门

> **课程定位：** 认识 RDK X5 上的四种音频硬件，掌握声卡侦察、录音与播放验证，理解声卡序号漂移与 Codec 路由配置。
>
> **适用硬件：** RDK X5
>
> **系统版本：** RDK OS 3.x 或更高
>
> **配套资料：** 视频讲解（录制中）/ 本讲义 / [官方音频文档](https://developer.d-robotics.cc/rdk_doc_center/)

---

## 1. 学习目标

完成本课后，你将能够：

1. 用三条命令查看当前系统里的声卡、序号和设备节点
2. 使用板载 3.5mm 耳机口完成一次「录音 → 播放」闭环
3. 即插即用 USB 扬声器，并在声卡序号变化时正确调整命令参数
4. 为 WM8960 Audio HAT 完成 srpi-config 配置和 tinymix 音频路由，实现三种播放模式
5. 为 Audio Driver HAT REV2 完成配置，录制 2 通道和 4 通道音频并回放
6. 排查「命令执行成功但没有声音」类问题

---

## 2. 准备材料

| 物品 | 数量 | 说明 |
|------|------|------|
| RDK X5 | 1 | 已完成烧录，可通过 SSH 连接 |
| 4 段式 3.5mm 耳机 | 1 | CTIA 标准，带 MIC；3 段式只能听不能录 |
| USB 扬声器 | 1 | USB-Audio 类驱动，即插即用 |
| 微雪 WM8960 Audio HAT | 1 | 40pin 接入，单 Codec |
| 微雪 Audio Driver HAT REV2 | 1 | 40pin 接入，双 Codec 四麦阵列；拨码开关全 OFF |

---

## 3. 音频系统全景：三条侦察命令

Linux 音频系统的底层框架叫 ALSA（Advanced Linux Sound Architecture）。你在 X5 上做的每一次录音和播放，最终都落到 ALSA 管理的三个层次上：

```text
声卡（Card）           —— 一块物理音频硬件 = 一个序号
  └─ PCM 设备（Device） —— 卡上的功能端点，分播放与录音
       └─ 设备节点（Node） —— /dev/snd/ 下的文件，程序实际打开的东西
```

举例：`pcmC0D1c` 的意思是「声卡 0、PCM 设备 1 的录音端点」（c = capture，p = playback）。理解这个命名规则，后面的命令参数就不再是玄学。

在接任何音频设备之前，先记住这三条命令，本课每一节都会用到：

```shell
# 1. 看系统里注册了哪些声卡（最重要的一条）
cat /proc/asound/cards

# 2. 看用户空间的设备节点
ls /dev/snd/

# 3. 看播放设备列表（录音用 arecord -l）
aplay -l
```

**侦察的意义：** 你操作 `-D hw:X,Y` 参数时，X 就是 `cat /proc/asound/cards` 里的声卡序号，Y 就是 `aplay -l` / `arecord -l` 里的设备号。先侦察再操作，参数永远有据可查。

### 序号漂移：为什么「昨天能跑今天失效」

ALSA 的声卡序号按注册顺序分配。USB 扬声器开机前插着，可能拿到 0 号；开机后插入，可能排在板载声卡后面。**同一个设备在不同时机下序号会漂移**，这是「命令昨天能跑今天失效」的最常见原因。

应对方法只有一条：**每次操作前重新侦察，以当次 `cat /proc/asound/cards` 的输出为准，不要相信记忆里的序号。** 本课第 5 节会现场演示一次漂移。

---

## 4. 板载 3.5mm 耳机口：最简闭环

### 4.1 硬件连接

X5 板载一个 3.5mm 耳机口，使用 **4 段式耳机**（CTIA 标准，带 MIC）。3 段式耳机缺少 MIC 段，只能听不能录。

耳机必须**完全插到底**。如果插得不深、金属部分露出来，程序照常运行但耳机无声——这是最常见的「假故障」。

### 4.2 侦察

不接任何子板时，板载声卡独占 0 号。依次用三条命令侦察：

```shell
# 1. 看声卡列表：确认板载声卡已注册
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudio    ]: simple-card - duplex-audio
                      duplex-audio

# 2. 看逻辑设备：确认播放与录音端点
root@ubuntu:~# cat /proc/asound/devices
  2: [ 0- 0]: digital audio playback
  3: [ 0- 0]: digital audio capture
  4: [ 0]   : control
 33:        : timer

# 3. 看用户空间的设备节点
root@ubuntu:~# ls /dev/snd/
by-path/   controlC0  pcmC0D0c   pcmC0D0p   timer
```

对应设备节点 `pcmC0D0p`（播放）和 `pcmC0D0c`（录音），即 `hw:0,0`。

### 4.3 录音与播放

```shell
# 录 10 秒（-d 10），48kHz 双声道 16bit
arecord -Dhw:0,0 -c 2 -r 48000 -f S16_LE -t wav -d 10 /userdata/record1.wav

# 回放
aplay -D hw:0,0 /userdata/record1.wav
```

**成功标准：** 录制时终端输出 `Recording WAVE ...` 且无报错；播放时耳机里清楚听到刚才录下的声音。

> **录给观众听：** 录音文件可用 `scp` 下载到电脑播放，验证原始录音质量：
>
> ```shell
> scp sunrise@<板卡IP>:/userdata/record1.wav ./
> ```

> **为什么用 16bit（S16_LE）而不是官方手册的 24bit（S24_LE）？** 见「4.4 录音格式陷阱」。

### 4.4 录音格式陷阱：S24_LE 为什么下载到电脑全是噪声

如果你照官方手册用 `-f S24_LE` 录了一段音频，在板子上用 `aplay` 回放是正常的；但把文件下载到电脑上播放，很可能全是噪声杂音。**这不是板卡录音坏了，而是格式本身的问题。**

**先看结论表：**

| ALSA 格式 | 每样本字节 | WAV 是否标准 | 电脑播放效果 |
|---|---|---|---|
| S16_LE | 2 字节 | 标准 16bit PCM | 正常 |
| S24_3LE | 3 字节 | 标准 24bit PCM | 正常 |
| **S24_LE（手册用的）** | **4 字节** | **非标准：头写 24bit、数据 4 字节** | **全是噪声/杂音** |
| S32_LE | 4 字节 | 标准 32bit PCM | 正常（个别老播放器不支持） |

**为什么会出现这个现象**

关键在于 ALSA 里 S24_LE 和 WAV 标准的 24bit 不是一回事：

- WAV 标准的 24bit = 每个样本 3 字节（打包存储），对应 ALSA 的 **S24_3LE**；
- ALSA 的 **S24_LE** = "24bit 装在 32bit 容器里"，每个样本占 4 字节（低 24bit 是有效数据，第 4 字节是符号扩展）。

`arecord -f S24_LE -t wav` 有个知名行为：它把 4 字节的样本原样写进文件，却在 WAV 头里把"每样本位数"写成 24bit。于是这个文件头和正文自相矛盾（头说 24bit→3 字节/样本，实际是 4 字节/样本）。

**为什么板子上回放正常？** 因为 `aplay` 和 `arecord` 用的是 ALSA 同一套约定：写的时候按 4 字节写、头标 24bit；读的时候也按 ALSA 的 S24_LE（4 字节）去理解。写错的 + 读错的刚好抵消，所以本地听是对的——这只是一种"往返自洽"，并不代表文件本身合法。

**为什么电脑上全是噪声？** Windows/Mac 的播放器（VLC、Audacity、浏览器等）严格按 WAV 标准读：头写着 24bit，就按 3 字节/样本切数据。而实际数据是 4 字节/样本，每读一帧就错位 1 字节，左右声道和采样完全错开 → 出来就是噪声杂音。这是 alsa-devel 邮件列表早已确认的 arecord 行为。

**结论：** 板载声卡按官方手册的 24 位录制时，下载到电脑播放会全是噪声。**我们录制 16 位（S16_LE）即可**——标准格式，板端、电脑端都能正常播放。

---

## 5. USB 扬声器：即插即用与序号漂移

### 5.1 接入与识别

USB 扬声器走标准 USB-Audio 类驱动，**即插即用，无需任何配置**。插入后直接侦察：

```shell
root@ubuntu:~# cat /proc/asound/cards
 0 [RC08          ]: USB-Audio - ROCWARE RC08      ← USB 声卡（示例）
                        ROCWARE RC08 at usb-xhci-hcd.2.auto-1.2, high speed
 1 [duplexaudio   ]: simple-card - duplex-audio    ← 板载声卡
                        duplex-audio
```

USB 扬声器此时是 0 号，播放命令：

```shell
aplay -D hw:0,0 /userdata/record1.wav
```

> 提示：不同型号扬声器显示的名称不同，以你自己的 `cat /proc/asound/cards` 输出为准。`lsusb` 可以进一步确认 USB 设备信息。

### 5.2 现场演示：序号漂移

保持 USB 扬声器插着，重启板卡，或者换一个 USB 口重新插入，再次侦察——你会看到 USB 声卡和板载声卡的序号**可能对调**。

此时如果还用记忆里的 `hw:0,0`，声音就会从错误的设备出来（或者报设备占用错误）。正确做法：重新看 `cat /proc/asound/cards`，如果 USB 扬声器变成了 1 号，命令就改为：

```shell
aplay -D hw:1,0 /userdata/record1.wav
```

**成功标准：** 声音从 USB 扬声器出来；无论序号怎么变，你都能通过侦察命令定位到它。

### 5.3 USB 声卡的录音与配置文件

USB 声卡（扬声器、麦克风一体设备或 USB 麦克风）的用法和板载一样，就是 `aplay` 播放、`arecord` 录音，指定它当次侦察到的序号即可：

```shell
# 录音（假设 USB 声卡当前是 1 号，用 S16_LE 标准格式）
arecord -Dhw:1,0 -c 2 -r 48000 -f S16_LE -t wav -d 10 /userdata/usb_record.wav

# 播放（序号以当次侦察为准）
aplay -D hw:1,0 /userdata/usb_record.wav
```

> 如果想让应用层（如桌面播放器、录音软件）能同时看到板载声卡和 USB 声卡，需要配置 PulseAudio。核心是编辑 `/etc/pulse/default.pa`，为 USB 声卡追加 `load-module module-alsa-sink/source`，并指定 `device=hw:X,Y`（X、Y 来自 `cat /proc/asound/cards` 和 `aplay -l`/`arecord -l` 的当次输出）。配置后重启板卡或重启 PulseAudio 服务生效。这一步属于进阶用法，本课演示直接用 ALSA 的 `-D` 指定设备，不依赖上层服务。

**USB 扬声器小结：** 它和板载 3.5mm 一样是"零配置"设备——即插即用，用 `aplay`/`arecord` 加 `-D hw:X,Y` 直接操作；唯一的坑是序号会漂移，所以每次操作前重新侦察。

---

## 6. WM8960 Audio HAT：配置路由才能出声

从这一节开始进入「需要配置」的硬件。WM8960 Audio HAT（微雪电子）通过 40pin 接入，采用 WM8960 Codec，支持双通道麦克风录音和音频播放。

### 6.1 硬件安装

断电状态下，将子板接入 X5 的 40pin header（注意方向，对齐插紧）。

### 6.2 软件配置（srpi-config）

```text
srpi-config
  → 3 Interface Options
    → I5 Audio
      → 选择 WM8960 Audio Driver HAT
```

按提示重启：

```shell
sync && reboot
```

### 6.3 重启后验证

```shell
# 1. 看声卡列表：出现 duplexaudioi2s1 = HAT 加载成功
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudioi2s1]: simple-card - duplex-audio-i2s1   ← WM8960 HAT
                      duplex-audio-i2s1
 1 [duplexaudio    ]: simple-card - duplex-audio        ← 板载（降为 1 号）
                      duplex-audio

# 2. 看逻辑设备：0 号卡对应播放 0-0、录音 0-1
root@ubuntu:~# cat /proc/asound/devices
  2: [ 0- 0]: digital audio playback
  3: [ 0- 1]: digital audio capture
  4: [ 0]   : control
  5: [ 1- 0]: digital audio playback
  6: [ 1- 0]: digital audio capture
  7: [ 1]   : control
 33:        : timer

# 3. 看设备节点：pcmC0D0p 播放、pcmC0D1c 录音
root@ubuntu:~# ls /dev/snd/
by-path  controlC0  controlC1  pcmC0D0p  pcmC0D1c  pcmC1D0c  pcmC1D0p  timer
```

`duplexaudioi2s1` 出现 = 驱动加载成功。此时：

- **HAT 是 0 号卡**：播放用 `pcmC0D0p`，录音用 `pcmC0D1c`；
- 板载声卡降为 1 号——又是一次序号漂移，侦察习惯再次发挥作用。

### 6.4 关键概念：为什么必须配路由

WM8960 内部有多条音频通路（输入→ADC、DAC→喇叭、DAC→耳机等），默认全部关闭。**不配路由时，`tinycap`/`tinyplay` 命令执行成功，但音频通路是断开的**——没有声音，也没有有效录音。

所以 WM8960 的每个使用场景，都遵循「先 `tinymix` 配路由 → 再 `tinycap`/`tinyplay` 操作」的顺序。

### 6.5 录音

**第一步：配输入路由与增益**

```shell
# 左右声道输入增益（有啸叫可降为 1）
tinymix -D 0 set 'Left Input Boost Mixer LINPUT1 Volume' 3
tinymix -D 0 set 'Right Input Boost Mixer RINPUT1 Volume' 3

# 录音音量
tinymix -D 0 set 'Capture Volume' 40 40
tinymix -D 0 set 'ADC PCM Capture Volume' 200 200

# 打开输入通路开关
tinymix -D 0 set 'Left Boost Mixer LINPUT1 Switch' 1
tinymix -D 0 set 'Right Boost Mixer RINPUT1 Switch' 1
tinymix -D 0 set 'Left Input Mixer Boost Switch' 1
tinymix -D 0 set 'Right Input Mixer Boost Switch' 1

# 打开录音开关
tinymix -D 0 set 'Capture Switch' 1 1
```

**第二步：录音（5 秒）**

```shell
tinycap ./2chn_test.wav -D 0 -d 0 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5
```

### 6.6 播放（三种模式）

**模式一：喇叭播放**

```shell
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Speaker DC Volume' 3
tinymix -D 0 set 'Speaker AC Volume' 3
tinymix -D 0 set 'Speaker Playback Volume' 127 127
tinymix -D 0 set 'Playback Volume' 255 255

tinyplay ./2chn_test.wav -D 0 -d 0
```

**模式二：耳机与喇叭同时播放**

```shell
tinymix -D 0 set 'Headphone Playback Volume' 80 80
tinymix -D 0 set 'Playback Volume' 220 220
tinymix -D 0 set 'Speaker DC Volume' 4
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1

tinyplay ./2chn_test.wav -D 0 -d 0
```

**模式三：仅耳机（喇叭静音）**

```shell
tinymix -D 0 set 'Headphone Playback Volume' 115 115
tinymix -D 0 set 'Speaker Playback Volume' 0 0
tinymix -D 0 set 'Playback Volume' 244 244
tinymix -D 0 set 'Speaker DC Volume' 4
tinymix -D 0 set 'Left Output Mixer PCM Playback Switch' 1
tinymix -D 0 set 'Right Output Mixer PCM Playback Switch' 1

tinyplay ./2chn_test.wav -D 0 -d 0
```

**成功标准：** 三种模式各自出声位置正确——模式一声源在喇叭，模式三在耳机且喇叭静音。

### 6.7 卸载

srpi-config → 3 Interface Options → I5 Audio → 选择 UNSET，然后断电拔板。

---

## 7. Audio Driver HAT REV2：多麦阵列与回采

### 7.1 硬件安装

断电接入 40pin header。**注意：3 个拨码开关必须全部拨到 OFF**，否则声卡不注册。

### 7.2 软件配置

```text
srpi-config
  → 3 Interface Options
    → I5 Audio
      → 选择 Audio Driver HAT V2
```

重启后 `cat /proc/asound/cards` 同样出现 `duplexaudioi2s1`（REV2 与 WM8960 注册名一致，靠配置项区分实际硬件）。三件套侦察输出与 WM8960 一节相同：0 号卡播放 `0-0`、录音 `0-1`，节点 `pcmC0D0p` / `pcmC0D1c`。

### 7.3 录音：2 通道与 4 通道

REV2 采用 ES7210+ES8156 双 Codec，支持环形 4 麦克风阵列。注意它的录音设备号是 **d 1**（与 WM8960 的 d 0 不同）：

```shell
# 2 通道录音
tinycap ./2chn_test.wav -D 0 -d 1 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5

# 4 通道录音（麦克阵列完整能力）
tinycap ./4chn_test.wav -D 0 -d 1 -c 4 -b 16 -r 48000 -p 512 -n 4 -t 5
```

### 7.4 播放

```shell
# 只支持 2 通道播放（不支持播放 4ch 文件）
tinyplay ./2chn_test.wav -D 0 -d 0
```

### 7.5 回采功能（讲义补充，视频不展开）

回采（echo / loopback）是把「播放通道的信号」同步采回来，供算法侧或应用侧分析播放内容的实际输出。REV2 的回采信号映射在录音通道 **7 和 8**，需要 8 通道录音，并保持录制与播放格式对齐。

#### 通道映射

| 通道 | 用途 |
|------|------|
| ch1–ch4 | 环形 4 路麦克风 |
| ch7–ch8 | 播放回采参考信号（PCB 回采通路） |

#### 为什么不能直接用 tinyplay 做回采

ES8156 播放 Codec 仅支持 2 通道，无法用 `tinyplay` 播放 8 通道 WAV 来做格式对齐的回采。所以官方在板端提供了 `/app/cdev_demo/audio_echo_test` 这个 C 示例，在应用层构造 8 通道 interleaved PCM 数据，一次性完成「录音 → 回放 → 同步采集 → 判定」。

#### 手动方式（两终端）

如果坚持用命令行手动回采，需要两个终端配合，并保证 8 通道格式完全对齐（16k/8ch/16bit）：

```shell
# 先录一段 8ch 数据，作为回采时的 playback 数据
tinycap ./8chn_echo_data.wav -D 0 -d 1 -c 8 -b 16 -r 16000 -p 256 -n 4 -t 5

# 终端 A：开启录制进程（时间留足，方便切到终端 B）
tinycap ./8chn_capture.wav -D 0 -d 1 -c 8 -b 16 -r 16000 -p 256 -n 4 -t 50

# 终端 B：同时启动格式对齐的 8 通道播放
tinyplay ./8chn_echo_data.wav -D 0 -d 0
```

录制完成后，用 Audacity 打开 `8chn_capture.wav`，查看第 7、8 通道的波形或频谱，验证回采是否正常。

#### 官方示例 audio_echo_test（推荐）

`/app/cdev_demo/audio_echo_test` 是官方 C 示例，无命令行参数，固定 8ch / 16kHz / 16bit，两阶段自动测试并输出 PASS/FAIL：

```shell
root@ubuntu:/app/cdev_demo/audio_echo_test# make
root@ubuntu:/app/cdev_demo/audio_echo_test# ./audio_echo_test
```

- **Phase 1**：提示 `speak into mic (5s)`，对着麦克风说话，生成 `record_first.wav`
- **Phase 2**：自动回放 Phase 1 录音并同步采集，生成 `audio_echo_test.wav`，输出各通道 peak 并判定

程序判定逻辑：ch7/ch8 峰值 ≥ 阈值 → `PASS: PCB loopback`（板载回采正常）；ch1–ch4 峰值 ≥ 阈值 → `PASS: wired loopback`（扬声器声音被麦克风拾取）；均不满足 → `FAIL`。

关键常量（定义在 `audio_echo_test.c` 中）：`CHANNELS=8`、`RATE=16000`、`FORMAT=S16_LE`、`CAPTURE_DEV=plughw:0,1`、`PLAYBACK_DEV=plughw:0,0`。修改采样率、通道数或设备节点时，必须保证 playback 与 capture 格式完全对齐。

**成功标准：** 4 通道录音文件生成且各通道有有效信号；2 通道文件能正常回放出声。

---

## 8. 常见问题排查

**Q1：插了设备但 `cat /proc/asound/cards` 里没有它？**

USB 设备：换口重插、查 `lsusb` 是否识别到硬件。HAT 子板：检查 srpi-config 配置项是否选对、是否重启过、拨码开关（REV2 必须全 OFF）。

**Q2：命令执行成功但没有声音？**

按顺序查四件事：① 目标声卡序号对不对（重新 `cat /proc/asound/cards`）；② 耳机是否插到底（3.5mm 场景）；③ WM8960 是否配了路由（第 6.4 节）；④ 播放文件格式与设备能力是否匹配（REV2 不能播 4ch）。

**Q3：WM8960 录音全是杂音/啸叫？**

输入增益过高。把 `LINPUT1/RINPUT1 Volume` 从 3 降到 1 再试。

**Q4：tinyalsa 的参数都是什么意思？**

`-D` 声卡号、`-d` PCM 设备号、`-c` 通道数、`-b` 位深、`-r` 采样率、`-p` period 大小、`-n` period 数量、`-t` 录音秒数。详见官方 FAQ「tinyalsa 参数含义」。

**Q5：想让 USB 声卡和子板声卡被上层服务（PulseAudio）同时管理？**

属于进阶配置，见官方 FAQ「音频子板与 USB 声卡共存」章节。

---

## 9. 总结

一图收束本课主线：

```text
侦察（cards → devices → nodes）
   ↓ 拿到声卡序号和设备号
播放（aplay / tinyplay -D hw:X,Y）
   ↓ 声音不对？回到侦察
录音（arecord / tinycap -D X -d Y）
   ↓ 没有有效波形？查路由（WM8960）
验证（耳朵听到 + 文件可回放）
```

- **四种硬件本质是三类设备：** 零配置（板载、USB）、单 Codec 需路由（WM8960）、双 Codec 多麦（REV2）；
- **序号漂移是常态，侦察是习惯。**

**拓展练习：** 用 WM8960 录一段自己的语音，通过 USB 扬声器播放出来（跨设备录放组合，巩固序号定位能力）。

---

## 10. 参考链接

- [RDK X5 音频应用官方文档](https://developer.d-robotics.cc/rdk_x_doc/03_Basic_Application/05_audio)（板载 Earphone、WM8960、Audio Driver HAT REV2、音频 FAQ 的原始出处）
- [微雪 WM8960 Audio HAT 产品页](https://www.waveshare.net/wiki/WM8960_Audio_HAT)
- [微雪 Audio Driver HAT 产品页](https://www.waveshare.net/shop/Audio-Driver-HAT.htm)
