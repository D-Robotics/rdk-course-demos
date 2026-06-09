# 第 12 课配套 Demo：SPI 屏幕点亮与动画显示

> **课程定位：** 40pin 外设实战 — 在掌握 GPIO / UART / I2C 基础后，通过 SPI 驱动 ST7789 屏幕，完成「接线 → 点亮 → 动画刷新」完整链路。  
> **适用硬件：** RDK X5 + 2.0 寸 240×320 SPI LCD（驱动 IC：ST7789）  
> **配套代码目录：** `[code/](./code/)`

---

## 效果展示

运行 `lcd_animate.py` 后，2.0 寸 SPI LCD 模块将显示弹跳小球动画，效果如下：

![SPI 屏幕动画 Demo 效果](./assets/lcd_animation_demo_thumb.jpg)

---

## 1. 学习目标

完成本课后，你将能够：

1. 理解 SPI 总线在 40pin 排针上的角色（SCLK / MOSI / CS）及 LCD 附加控制线（DC / RST / BL）
2. 按接线表完成 ST7789 模块与 RDK X5 的连接
3. 启用 SPI 接口并验证 `/dev/spidev1.1` 设备节点
4. 运行点亮测试，在屏幕上显示自检图案
5. 运行动画 Demo，理解「PIL 绘图 → RGB565 转换 → SPI 刷图」的循环流程

---

## 2. SPI 基础知识

### 2.1 什么是 SPI

**SPI（Serial Peripheral Interface，串行外设接口）** 是一种**主从、同步、全双工**的串行总线，由 Motorola 提出，常用于 MCU/SoC 与 Flash、传感器、显示屏等外设之间的高速通信。

典型拓扑：**一个主机（Master）** 通过共享总线连接 **一个或多个从机（Slave）**，每个从机用独立的 **CS（片选）** 线区分。

```text
  RDK X5 (Master)                    外设 (Slave)
  ───────────────                    ─────────────
  SCLK  ───────────────────────────  CLK   （时钟，主机产生）
  MOSI  ───────────────────────────  DIN   （主机出 → 从机入）
  MISO  ───────────────────────────  MISO  （从机出 → 主机入，LCD 通常不用）
  CS    ───────────────────────────  CS    （片选，低电平选中该设备）
```

### 2.2 四条核心信号线

| 信号 | 全称 | 方向 | 作用 |
|------|------|------|------|
| **SCLK** | Serial Clock | 主机 → 从机 | 时钟节拍，每来一个沿，传 1 bit 数据 |
| **MOSI** | Master Out Slave In | 主机 → 从机 | 主机发送数据（本课 LCD 的 DIN 即 MOSI） |
| **MISO** | Master In Slave Out | 从机 → 主机 | 从机回传数据（TFT 屏只写不读，本课不接） |
| **CS** | Chip Select | 主机 → 从机 | 片选，拉低表示「现在跟你通信」 |

**工作方式简述：** 主机拉低 CS → 在 SCLK 驱动下通过 MOSI 逐 bit 发出数据 → 从机在时钟沿采样。SPI 没有 I2C 那样的设备地址，靠 **CS 线数量** 区分多个从设备。

### 2.3 SPI 的四种模式

SPI 有 **Mode 0 ~ 3**，由 **CPOL**（时钟空闲电平）和 **CPHA**（数据采样沿）组合决定。RDK X5 与本课 ST7789 屏使用 **Mode 0**（CPOL=0, CPHA=0）：

- 空闲时 SCLK 为低电平
- 第一个时钟沿（上升沿）采样数据

代码中对应：`spi.mode = 0`（见 `rdk_x5_lcd_st7789.py`）。

### 2.4 本课 LCD 为何还要 GPIO？

带驱动 IC 的 TFT 屏不是「纯四线 SPI」，还需要几根 **GPIO 控制线**：

| 引脚 | 作用 |
|------|------|
| **DC**（Data/Command） | 低电平 = 发送命令字节；高电平 = 发送数据/像素 |
| **RST**（Reset） | 硬件复位，上电初始化前拉低再拉高 |
| **BL**（Backlight） | 背光开关，可接 GPIO 或直接接 3.3V 常亮 |

因此本课实战是 **「SPI 传数据 + GPIO 控模式」** 的典型组合。

### 2.5 SPI 与 I2C、UART 对比

| | SPI | I2C | UART |
|--|-----|-----|------|
| 线数 | 4+（含多路 CS） | 2（SDA + SCL） | 2（TX + RX） |
| 速度 | 通常 MHz 级，适合刷屏 | 通常 100k~400kHz | 通常 kbps~Mbps |
| 寻址 | 每设备一根 CS | 7 位地址 | 无地址，点对点 |
| 典型用途 | 显示屏、Flash、ADC | 温湿度传感器、IMU | 串口调试、模块通信 |

本课用 SPI 驱动 240×320 屏幕，一帧约 **150 KB** 像素数据，SPI 的高速批量传输能力是关键。

### 2.6 RDK X5 上的 SPI 资源

- 40pin 排针采用 **BOARD 物理编号**（与树莓派兼容，`GPIO.setmode(GPIO.BOARD)`）。
- 本课默认使用 **SPI1**，片选 **CS1** → 设备节点 **`/dev/spidev1.1`**（bus=1, device=1）。
- Python 通过 **`spidev`** 库访问内核 SPI 驱动；DC/RST/BL 通过 **`Hobot.GPIO`** 控制。

```text
  /dev/spidev1.1  ←→  spidev.SpiDev().open(1, 1)
       ↑                      ↑
   Pin 24 (CS1)          Python 用户态
```

---

## 3. 硬件清单


| 物品               | 说明                                               |
| ---------------- | ------------------------------------------------ |
| RDK X5 开发板       | 40pin 排针，BOARD 编号模式                              |
| 2.0 寸 SPI LCD 模块 | ST7789，240×320，8 针（VCC/GND/DIN/CLK/CS/DC/RST/BL） |
| 杜邦线              | 母对母或母对公，至少 8 根                                   |
| （可选）面包板          | 方便固定接线                                           |


---

## 4. 接线表

**务必在断电状态下接线。VCC 只接 3.3V，切勿接 5V。**


| LCD 丝印     | 功能     | RDK X5 40pin（BOARD 编号）           | 说明                       |
| ---------- | ------ | -------------------------------- | ------------------------ |
| VCC        | 电源     | **Pin 1** 或 **Pin 17**（3.3V）     | 勿接 5V                    |
| GND        | 地      | **Pin 6**（或 9/14/20/25/30/34/39） |                          |
| DIN / MOSI | SPI 数据 | **Pin 19**（SPI1_MOSI）            |                          |
| CLK / SCLK | SPI 时钟 | **Pin 23**（SPI1_SCLK）            |                          |
| CS         | 片选     | **Pin 24**（SPI1_CSN1）            | 对应 `/dev/spidev1.1`      |
| DC         | 数据/命令  | **Pin 22**                       | GPIO 输出                  |
| RST        | 复位     | **Pin 31**                       | GPIO 输出                  |
| BL         | 背光     | **Pin 33**                       | GPIO 输出；若 BL 已接 3.3V 可跳过 |


接线示意：

```text
  LCD 模块                         RDK X5 40pin
  ---------                        ------------
  VCC  --------------------------  Pin 1  (3.3V)
  GND  --------------------------  Pin 6  (GND)
  DIN  --------------------------  Pin 19 (SPI1_MOSI)
  CLK  --------------------------  Pin 23 (SPI1_SCLK)
  CS   --------------------------  Pin 24 (SPI1_CSN1)
  DC   --------------------------  Pin 22 (GPIO)
  RST  --------------------------  Pin 31 (GPIO)
  BL   --------------------------  Pin 33 (GPIO)
```

---

## 5. 软件环境准备

### 5.1 启用 SPI

```bash
sudo srpi-config
# -> Interface Options -> SPI -> Enable -> Finish -> 重启
```

重启后确认设备节点：

```bash
ls -l /dev/spidev*
# 期望输出包含：/dev/spidev1.0  /dev/spidev1.1
```

### 5.2 检查 Python 依赖

```bash
pip3 show Hobot.GPIO spidev Pillow
```

若缺少 `spidev`：

```bash
pip3 install spidev
```

### 5.3 克隆课程代码

```bash
git clone https://github.com/D-Robotics/rdk-course-demos.git
cd rdk-course-demos/01_beginner/12_40pin_uart_i2c/code
```

### 5.4 权限说明

访问 SPI 与 GPIO 需要 root 权限，请使用 `sudo python3` 运行所有 Demo。

---

## 6. 代码结构

```text
12_40pin_uart_i2c/
├── README.md                  # 本讲义
└── code/
    ├── rdk_x5_lcd_st7789.py   # 核心驱动：ST7789 + spidev + GPIO
    └── lcd_animate.py         # 动画 Demo：弹跳小球 + 标题闪烁
```


| 文件                     | 作用                           |
| ---------------------- | ---------------------------- |
| `rdk_x5_lcd_st7789.py` | 底层驱动，提供 `ST7789` 类：初始化、清屏、刷图 |
| `lcd_animate.py`       | 应用层动画，循环绘制帧并刷新屏幕             |


---

## 7. 实验一：点亮屏幕

**目标：** 验证接线、SPI 通信、ST7789 初始化是否正常。

```bash
cd rdk-course-demos/01_beginner/12_40pin_uart_i2c/code
sudo python3 rdk_x5_lcd_st7789.py --hold
```

**预期效果：**

- 背光亮起
- 屏幕显示渐变背景、顶部色条
- 中央显示 `RDK X5 / 2.0 SPI LCD / ST7789 RGB565`
- 底部显示当前时间

按 `Ctrl+C` 退出。

**常用参数：**

```bash
# 纯色自检（快速验证 RGB565）
sudo python3 rdk_x5_lcd_st7789.py --solid red --hold
sudo python3 rdk_x5_lcd_st7789.py --solid green --hold
sudo python3 rdk_x5_lcd_st7789.py --solid blue --hold

# 背光已硬接 3.3V 时
sudo python3 rdk_x5_lcd_st7789.py --no-bl --hold

# 红蓝颜色对调时
sudo python3 rdk_x5_lcd_st7789.py --rgb --hold
```

---

## 8. 实验二：屏幕动画

**目标：** 在点亮基础上，理解帧循环刷新机制。

```bash
cd rdk-course-demos/01_beginner/12_40pin_uart_i2c/code
sudo python3 lcd_animate.py
```

**预期效果：**

- 深色渐变背景 + 地面线
- 彩色小球在屏幕内弹跳，碰边反弹
- 顶部标题 `RDK X5 LCD` 呼吸闪烁
- 底部实时时钟

![动画运行实拍](./assets/lcd_animation_demo_thumb.jpg)

按 `Ctrl+C` 停止动画。

**可调参数：**

```bash
# 降低帧率（便于观察每一帧）
sudo python3 lcd_animate.py --fps 15

# 提高 SPI 速度（线材质量好时可尝试，花屏则降速）
sudo python3 lcd_animate.py --speed 40000000
```

---

## 9. 驱动原理

### 9.1 发命令 vs 发数据（DC 线）

驱动通过 **DC 引脚** 区分 SPI 传输内容（详见 §2.4）：

1. `GPIO.output(dc, LOW)` → 发送 1 字节**命令**（如 `0x11` Sleep Out）
2. `GPIO.output(dc, HIGH)` → 发送**参数或像素数据**

刷一整屏时：`set_window()` 设定写入区域后，DC 保持 HIGH，SPI 连续写入 RGB565 像素块。

### 9.2 驱动工作流程

```text
hard_reset()  ->  RST 拉低/拉高，芯片复位
init()        ->  发送 ST7789 寄存器初始化序列
set_window()  ->  设置显存写入区域 (0x2A/0x2B/0x2C)
show(image)   ->  PIL RGB888 -> RGB565 -> SPI 分块写入
```

### 9.3 颜色格式 RGB565

屏幕配置为 16 位色，每个像素占 2 字节：

- 红色 5 位 + 绿色 6 位 + 蓝色 5 位
- 一帧 240x320 画面约 150 KB 数据

### 9.4 动画本质

动画 Demo 并不依赖外部图片，而是：

1. 用 PIL 在内存中绘制一帧 `Image`
2. 调用 `lcd.show(frame)` 刷到屏幕
3. 更新物理量（小球坐标、颜色相位）
4. 按 `--fps` 控制刷新间隔

---

## 10. 故障排查


| 现象                     | 可能原因          | 处理方法                                 |
| ---------------------- | ------------- | ------------------------------------ |
| 找不到 `/dev/spidev1.1`   | SPI 未启用       | `sudo srpi-config` 开启 SPI 并重启        |
| 背光不亮                   | BL 未接或接错      | 检查 Pin 33；或 BL 直接接 3.3V 后加 `--no-bl` |
| 白屏/黑屏无图案               | RST/DC/CS 接错  | 核对 Pin 22/24/31                      |
| 花屏、条纹                  | SPI 速度过高      | `--speed 12000000` 降速                |
| 红蓝颜色反了                 | BGR/RGB 位设置   | 加 `--rgb` 参数                         |
| 画面偏移/裁切                | GRAM 窗口与面板不一致 | 调 `--x-offset` / `--y-offset`        |
| Permission denied      | 权限不足          | 使用 `sudo python3`                    |
| certificate / HTTPS 报错 | 系统时间错误        | `sudo date -s "2026-06-09 12:00:00"` |


---

## 11. 课堂练习

1. **连线考核：** 不看讲义，填写 DIN/CLK/CS/DC/RST/BL 对应的 BOARD 编号。
2. **纯色验证：** 分别运行 `--solid red/green/blue`，确认三色显示正确。
3. **改速实验：** 将 `--speed` 从 24M 逐步提高到 40M，记录开始花屏的阈值。
4. **改动画：** 修改 `lcd_animate.py` 中的 `ball_r` 或 `gravity`，观察弹跳效果变化。
5. **（选做）** 在 `make_frame()` 中把标题改成自己的名字，重新运行动画。

---

## 12. 与课程体系的衔接


| 已学内容            | 本课关联                    |
| --------------- | ----------------------- |
| 第 11 课 GPIO/PWM | DC/RST/BL 本质是 GPIO 输出   |
| 第 12 课 UART/I2C | 对比 SPI 的高速批量传输特性        |
| 第 13 课 SPI 深入   | 本 Demo 即为 SPI 驱动屏幕的实战入口 |


**官方参考示例：**

```bash
cd /app/40pin_samples
sudo python3 test_spi.py
```

---

## 附录：默认参数速查


| 参数              | 默认值          | CLI 选项                    |
| --------------- | ------------ | ------------------------- |
| SPI bus         | 1            | `--bus 1`                 |
| SPI device (CS) | 1            | `--device 1`              |
| 分辨率             | 240x320      | `--width` / `--height`    |
| DC / RST / BL   | 22 / 31 / 33 | `--dc` `--rst` `--bl`     |
| SPI 时钟          | 24 MHz       | `--speed`                 |
| 旋转              | 0 度          | `--rotation 0/90/180/270` |
| 动画帧率            | 30 fps       | `--fps 30`                |


