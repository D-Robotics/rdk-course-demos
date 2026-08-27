# 第 8 课：RDK 音频外设入门

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

不接任何子板时，板载声卡独占 0 号：

```shell
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudio    ]: simple-card - duplex-audio
                      duplex-audio
```

对应设备节点 `pcmC0D0p`（播放）和 `pcmC0D0c`（录音），即 `hw:0,0`。

### 4.3 录音与播放

```shell
# 录 10 秒（-d 10），48kHz 双声道 24bit
arecord -Dhw:0,0 -c 2 -r 48000 -f S24_LE -t wav -d 10 /userdata/record1.wav

# 回放
aplay -D hw:0,0 /userdata/record1.wav
```

**成功标准：** 录制时终端输出 `Recording WAVE ...` 且无报错；播放时耳机里清楚听到刚才录下的声音。

> **录给观众听：** 录音文件可用 `scp` 下载到电脑播放，验证原始录音质量：
>
> ```shell
> scp sunrise@<板卡IP>:/userdata/record1.wav ./
> ```

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
root@ubuntu:~# cat /proc/asound/cards
 0 [duplexaudioi2s1]: simple-card - duplex-audio-i2s1   ← WM8960 HAT
                      duplex-audio-i2s1
 1 [duplexaudio    ]: simple-card - duplex-audio        ← 板载（降为 1 号）
                      duplex-audio
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

重启后 `cat /proc/asound/cards` 同样出现 `duplexaudioi2s1`（REV2 与 WM8960 注册名一致，靠配置项区分实际硬件）。

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

### 7.5 回采功能（进阶，本课不实操）

REV2 的回采信号映射在录音通道 7、8，需 8 通道录音并保持录放格式对齐（16k/8ch/16bit）。本课只讲概念与适用场景（算法侧分析播放信号），完整操作见官方文档 audio_echo_test 示例。

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
