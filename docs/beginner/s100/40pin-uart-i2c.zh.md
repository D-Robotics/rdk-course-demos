# RDK S100 UART 与 I2C

本文根据已录制课程的配套课件整理，保留原课件的接线、命令、实测结果和验证范围。

[原始课件](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/12_40pin_uart_i2c/lesson-12-s100-zh.html)

用回环与 PCF8574T 完成两条最小通信链路。

## 两种总线，两类证据

UART 用发送接收一致性验收，I2C 用地址发现和数据回写验收。

### UART2

Pin 8 与 Pin 10 短接，AA55 发送后原样接收。

### I2C4

Pin 27 与 Pin 28 连接 PCF8574T，扫描到 0x20。

### 最小验证

不需要 USB-TTL、逻辑分析仪或外部电源。

## UART 与 I2C 的差别

### UART

点对点异步通信，使用 TX 与 RX。

### I2C

共享时钟与数据线，设备通过地址区分。

### 共同电平

S100 40-pin 数字接口为 3.3V。

### 共同目标

确认 Linux 设备节点到实体连线的完整链路。

## 先理解 SW6 复用关系

J24 的 I2C5 与 UART2 需要通过 SW6 的 40 PIN 拨码二选一。本课 UART 使用 UART2，I2C 则改用独立的 I2C4。

- 切换 SW6 前先断电
- UART2 对应物理 Pin 8 与 Pin 10
- I2C5 对应 Pin 3 与 Pin 5
- I2C4 对应 Pin 27 与 Pin 28
- 本次 I2C4 不受 UART2 拨码位置影响

## UART2 回环接线

只用一根杜邦线把 Pin 8 TXD 与 Pin 10 RXD 直接连接。回环不接 3.3V、5V 或 GND。

![RDK S100 UART2 loopback wiring](../../assets/images/beginner/lesson-12-s100-4fe94a26e6b1.jpg)

Pin 8 TXD ↔ Pin 10 RXD

## UART2 需要软硬件同时启用

S100 的 UART2 默认关闭。本次验证在保留恢复备份的前提下启用 uart2，并禁用复用的 i2c5。

Step 1

断电把 SW6 顶部 40 PIN 拨到 UART2。

Step 2

设备树设置 uart2 为 okay、i2c5 为 disabled。

Step 3

重启后确认 /dev/ttyS2 存在。

Step 4

连接 Pin 8 与 Pin 10，再运行回环程序。

## 发送 AA55 并检查回读

本次实测使用 /dev/ttyS2 与 921600 波特率，发送和接收内容完全一致。

### 设备节点

```text
ls -l /dev/ttyS2
```

存在后再开始测试。

### 回环结果

```text
TX: AA55
RX: AA55
STATUS: PASS
```

按字节比较，不只看程序是否启动。

## UART 回环证据

**打开**/dev/ttyS2

**配置**921600 8N1

**发送**AA55

**接收**AA55

**判定**逐字节一致 PASS

## I2C4 避免重复切换 SW6

I2C4 默认可用，物理 Pin 27 与 Pin 28 独立于 UART2。本次模块从 S100 的 3.3V 供电。

### 总线

/dev/i2c-4

### 供电

Pin 17 提供 3.3V，Pin 20 接地。

### 外设

PCF8574T 地址实测为 0x20。

## PCF8574T 四线接法

VCC、GND、SDA、SCL 四根线缺一不可。模块使用 3.3V 供电及 3.3V 逻辑。

![RDK S100 I2C4 PCF8574T wiring](../../assets/images/beginner/lesson-12-s100-d93ea463dec4.jpg)

Pin 17→VCC | Pin 20→GND | Pin 27→SDA | Pin 28→SCL

## 先扫描地址，再做读写

地址由模块 A0、A1、A2 配置决定，不能在未扫描前假定。

### 扫描总线

```text
sudo i2cdetect -y 4
```

本次找到 0x20，板载设备还包含 0x2F。

### 官方示例

```text
sudo python3 /app/40pin_samples/test_i2c.py
```

选择 i2c-4，再输入检测到的地址。

## I2C 读写证据

**枚举**确认 /dev/i2c-4

**扫描**发现 0x20

**读取**返回 0xFF

**回写**写回测试值

**判定**读写链路 PASS

## 通信失败的排查顺序

先确认复用和设备节点，再检查物理接线。

UART

无 /dev/ttyS2 时检查 SW6、设备树和重启结果。

Loop

TX 有发送但 RX 为空时核对 Pin 8 与 Pin 10。

I2C

扫描不到 0x20 时核对 3.3V、GND、SDA、SCL。

Address

不要把板载 0x2F 误认成 PCF8574T。

## 完成

UART2 回环与 I2C4 外设访问均已取得可重复的终端证据。

### UART2 PASS

AA55 发送与接收一致。

### I2C4 PASS

0x20 可发现、可读取、可回写。

### 下一课

使用两根线验证 SPI0 全双工回环。
