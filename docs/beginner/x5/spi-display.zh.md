# RDK X5 SPI 彩屏与动画显示

本课用 RDK X5 驱动一块两寸 ST7789 彩屏，先显示静态测试图，再运行弹跳小球动画。本页包含完整接线、环境准备、实验命令、预期结果和驱动代码解析，可以直接按顺序操作。

> **适用硬件：** RDK X5 + 2.0 寸 240 × 320 ST7789 SPI LCD，8 针接口为 VCC/GND/DIN/CLK/CS/DC/RST/BL。
>
> **配套代码：** [develop 分支](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi)。
>
> 本页管脚和默认参数适用于 **X5**。仓库中的 `README_S100.md` 属于另一块板卡。其他驱动芯片或分辨率的屏幕，需要另行核对初始化方式和尺寸参数。

## 本课实验效果

先运行 `rdk_x5_lcd_st7789.py`，显示渐变背景、色条、文字和时间戳；再运行 `lcd_animate.py`，显示弹跳小球、明暗变化的标题和持续更新的时钟。

![RDK X5 驱动 ST7789 运行小球动画的实拍](../../assets/images/beginner/rdk-x5-spi-lcd-animation.jpg){ width="280" }

先通过静态点亮和颜色检查，再进入动画实验，这样能把接线、初始化问题与刷新速度问题分开排查。

## SPI 信号与屏幕控制

SPI 是同步通信，主机通过 SCLK 提供时钟。MOSI 和 MISO 分别负责两个方向的数据传输，本实验只向屏幕写入，因此 **MISO 不接**。

| 信号 | 本课中的作用 |
| --- | --- |
| SCLK / CLK | X5 产生的时钟 |
| MOSI / DIN | X5 向屏幕发送数据 |
| MISO | 相反方向的数据传输，本实验不用 |
| CS | 片选，低电平选中屏幕 |
| DC | 低电平发送命令字节，高电平发送命令参数或像素数据 |
| RST | 硬件复位，拉低后再释放 |
| BL | 背光控制 |

SPI 用片选线选择设备，不使用 I2C 那样的设备地址。仓库驱动使用 **Mode 0**（`CPOL=0、CPHA=0`）、**每字 8 位**，默认 SPI 时钟为 **24 MHz**。SPI 通信通过 `spidev` 完成，DC、RST 和 BL 由 `Hobot.GPIO` 控制。

## 硬件与完整接线表

准备 RDK X5、上述 ST7789 模块，以及 8 根适配接头的杜邦线。

!!! warning "接线前关机断电"
    连接或调整杜邦线前，先关闭 X5 并断开电源。本课 VCC 接 **3.3V**，不要接 5V，并确保共地。下表全部使用 **BOARD 物理管脚编号**，对应代码里的 `GPIO.setmode(GPIO.BOARD)`。

| LCD 引脚 | RDK X5 物理管脚 | 功能 |
| --- | --- | --- |
| VCC | **1** 或 **17** | 3.3V 供电 |
| GND | **6** | 地，也可使用 9/14/20/25/30/34/39 |
| DIN / MOSI | **19** | SPI1_MOSI |
| CLK / SCLK | **23** | SPI1_SCLK |
| CS | **24** | SPI1_CSN1，对应 `/dev/spidev1.1` |
| DC | **22** | GPIO 输出，切换命令与数据 |
| RST | **31** | GPIO 输出，控制复位 |
| BL | **33** | GPIO 输出，控制背光 |

如果把 BL 直接接到 3.3V 常亮，运行下面**两个**实验时都加 `--no-bl`，跳过背光 GPIO 控制。

## 开启 SPI1

运行配置工具：

```bash
sudo srpi-config
```

进入 **3 Interface Options → I3 Peripheral bus config**，开启 SPI1 对应功能并重启。菜单名称可能随系统版本变化，以实际总线配置界面为准。

重启后检查设备节点：

```bash
ls -l /dev/spidev*
ls -l /dev/spidev1.1
```

本课明确使用 **`/dev/spidev1.1`**，对应代码里的 `spi.open(1, 1)`。第一个数字是总线号，第二个数字是片选号。只看到其他 spidev 节点还不够。

节点存在只说明 Linux 已提供这个接口，屏幕有没有接好、初始化是否正常，还要通过显示实验确认。

## 获取代码并检查依赖

首次下载课程代码时运行：

```bash
git clone --branch develop --single-branch https://github.com/D-Robotics/rdk-course-demos.git
cd rdk-course-demos/01_beginner/13_40pin_spi/code
ls rdk_x5_lcd_st7789.py lcd_animate.py
```

已有仓库时，进入其 `develop` 分支下的 `code` 目录。两个 Python 文件必须放在一起，因为动画程序会导入驱动文件。

下面的实验命令都在这个 **`code` 目录**中执行。本课统一使用 `sudo python3` 访问 SPI 和 GPIO，先用同一个解释器检查依赖：

```bash
sudo python3 -c "import Hobot.GPIO, spidev; from PIL import Image; print('Dependencies OK')"
```

缺少 `spidev` 或 Pillow 时，安装系统包后重新检查：

```bash
sudo apt update
sudo apt install python3-spidev python3-pil
```

若缺少 `Hobot.GPIO`，先按当前 RDK X5 镜像说明恢复 GPIO 环境。只在用户的虚拟环境里安装依赖，不代表 `sudo python3` 也能导入。

## 实验一：静态点亮

核对接线并上电后运行：

```bash
sudo python3 rdk_x5_lcd_st7789.py --hold
```

终端应输出：

```text
LCD draw complete.
Holding. Press Ctrl+C to exit.
```

屏幕应显示渐变背景、顶部色条，中间有 `RDK X5`、`2.0 SPI LCD` 和 `ST7789 RGB565`，底部显示生成图片时的时间。

**`--hold` 只在画完一次后保持进程运行，不会刷新画面，也不会更新时间。** 按 `Ctrl+C` 退出后，再进行下一项测试。

### 红、绿、蓝纯色自检

依次运行，每次先按 `Ctrl+C` 退出，再执行下一条：

```bash
sudo python3 rdk_x5_lcd_st7789.py --solid red --hold
sudo python3 rdk_x5_lcd_st7789.py --solid green --hold
sudo python3 rdk_x5_lcd_st7789.py --solid blue --hold
```

若红蓝颠倒，加 `--rgb` 后重做三色自检。例如：

```bash
sudo python3 rdk_x5_lcd_st7789.py --solid red --rgb --hold
```

BL 已直接接到 3.3V 时使用：

```bash
sudo python3 rdk_x5_lcd_st7789.py --no-bl --hold
```

## 实验二：弹跳小球动画

静态图像和颜色都正常后，运行：

```bash
sudo python3 lcd_animate.py
```

终端应输出：

```text
Animation running. Press Ctrl+C to stop.
```

屏幕应显示深色渐变背景、地面线、带阴影的彩色弹跳小球，顶部 `RDK X5 LCD` 标题明暗变化，底部时钟持续更新。每一帧都由 Pillow 绘制，不需要外部图片文件。按 `Ctrl+C` 停止。

静态实验里确认需要的显示参数，也要带到动画命令中。例如，同时需要调整颜色顺序和跳过背光 GPIO 时：

```bash
sudo python3 lcd_animate.py --rgb --no-bl
```

### 比较帧率与 SPI 时钟

下面的命令分别运行：

```bash
# 降低目标帧率
sudo python3 lcd_animate.py --fps 15

# 降低 SPI 时钟，用于排查花屏
sudo python3 lcd_animate.py --speed 12000000

# 可选的更高时钟实验
sudo python3 lcd_animate.py --speed 40000000
```

默认 `--fps 30` 是**目标帧率**，不是实测或保证值。240 × 320 的 RGB565 图像每个像素占两字节，一整帧共 **153,600 字节，也就是 150 KiB**。默认 24 MHz 下，仅发送这些像素字节的理论下限就是 **51.2 ms**，还没计入绘图、转换和传输开销，因此无法在该时钟下达到每秒 30 次整屏刷新。

程序只有在一帧处理完仍有剩余时间时才等待。小球位置按帧更新，没有根据实际经过时间计算，所以实际帧率变化也会影响运动速度。40 MHz 仅作可选测试，出现花屏或条纹时先降速。

## 驱动如何把图像送到屏幕

完整程序见[ST7789 驱动](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/13_40pin_spi/code/rdk_x5_lcd_st7789.py)和[动画程序](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/13_40pin_spi/code/lcd_animate.py)。下面是源码节选，用于理解实现，不是单独运行的完整程序。

### 初始化与命令切换

`init()` 先执行硬件复位，再发送初始化命令、退出休眠、开启显示并清屏。`command()` 在发送命令字节时把 DC 拉低，发送参数时把 DC 拉高；需要等待的命令还会附带延时。

每次刷图前，`set_window()` 用 `0x2A` 和 `0x2B` 设置列、行范围，再用 `0x2C` 开始写入像素。

### RGB888 转换为 RGB565

Pillow 提供的 RGB 图像每个通道占八位。RGB565 使用五位红、六位绿、五位蓝，驱动将一个像素打包为两个字节，高字节先发送：

```python
def rgb888_to_rgb565(image: Image.Image) -> bytes:
    out = bytearray(image.width * image.height * 2)
    i = 0
    for r, g, b in image.getdata():
        value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        out[i] = (value >> 8) & 0xFF
        out[i + 1] = value & 0xFF
        i += 2
    return bytes(out)
```

### 设置窗口并分块刷图

下面的 `show()` 方法位于 `ST7789` 类中：

```python
def show(self, image: Image.Image) -> None:
    if image.size != (self.width, self.height):
        image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
    payload = rgb888_to_rgb565(image.convert("RGB"))
    self.set_window(0, 0, self.width - 1, self.height - 1)
    GPIO.output(self.dc_pin, GPIO.HIGH)
    for start in range(0, len(payload), 4096):
        self.spi.writebytes2(payload[start : start + 4096])
```

它在必要时调整图像尺寸，再转换为 RGB565，设置全屏写入窗口，把 DC 拉高，最后以每块最多 4,096 字节发送。

动画程序每轮先更新小球位置，再调用 `make_frame()` 绘制图像，通过 `lcd.show(frame)` 刷到屏幕，最后根据目标帧间隔决定是否等待。

## 默认参数速查

| 设置 | 默认值 | 参数 |
| --- | --- | --- |
| SPI 总线 / 片选 | 1 / 1 | `--bus 1 --device 1` |
| 图像尺寸 | 240 × 320 | `--width 240 --height 320` |
| DC / RST / BL | 22 / 31 / 33 | `--dc 22 --rst 31 --bl 33` |
| SPI 时钟 | 24 MHz | `--speed 24000000` |
| SPI 模式 / 字长 | Mode 0 / 8 位 | 驱动内设置 |
| 旋转 | 0° | `--rotation 0`，也支持 90、180、270 |
| X / Y 偏移 | 0 / 0 | `--x-offset 0 --y-offset 0` |
| 颜色顺序 | BGR 标志开启 | `--rgb` 清除该标志 |
| 动画目标帧率 | 30 fps | `--fps 30`，仅动画程序 |
| 静态画面保持 | 默认关闭 | `--hold`，仅静态测试 |

当前驱动**不会因为旋转而自动交换宽高**。尝试 90° 或 270° 时，要结合实际面板核对尺寸与偏移，检查是否裁切。第一次实验先使用默认方向。

## 常见问题排查

| 现象 | 检查与处理 |
| --- | --- |
| 没有 `/dev/spidev1.1` | 开启 SPI1 并重启；确认 bus=1、device=1，CS 接物理 Pin 24。 |
| 背光不亮 | 断电后核对 VCC、GND 和 BL；默认 BL 接 Pin 33，直接接 3.3V 时加 `--no-bl`。 |
| 背光亮但没有图像 | 核对 MOSI=19、CLK=23、CS=24、DC=22、RST=31、设备节点和 ST7789 面板型号。 |
| 红蓝颠倒 | 加 `--rgb` 后重新进行三色自检。 |
| 花屏、条纹 | 先用 `--speed 12000000` 降速，再检查接线。 |
| 画面裁切或偏移 | 核对面板尺寸、旋转角度和 X/Y 偏移。 |
| `Permission denied` | 按本课使用 `sudo python3`，并检查设备权限。 |
| Python 导入失败 | 使用运行 Demo 的同一个解释器重新检查依赖。 |
| 静态图时间不动 | `--hold` 的正常行为；需要连续更新请运行 `lcd_animate.py`。 |
| 动画达不到目标帧率 | 计入绘图、颜色转换和 SPI 传输耗时；fps 参数只设置目标值。 |

系统自带的 `/app/40pin_samples/test_spi.py` 是另一项基础总线测试。运行前先查看它使用的设备节点、接线和验证方式。它不能替代 ST7789 初始化，也不会完成本课的两个显示实验。

## 课堂练习与资料

1. 不看接线表填写八根线的连接位置，再对照检查后上电。
2. 分别进行三色自检，观察 `--rgb` 对颜色的影响。
3. 比较不同目标帧率与 SPI 时钟下的动画效果。
4. 修改 `ball_r`、`gravity`，或 `make_frame()` 中的标题，然后重新运行动画。

- [完整代码与 README](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi)
- [中英文 SPI 原理动画源码与导出说明](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/13_40pin_spi/SPI_ANIMATIONS.md)
- [上一课：UART 与 I2C](40pin-uart.md)
