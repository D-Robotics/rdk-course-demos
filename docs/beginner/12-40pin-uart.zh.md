# 第 12 课：RDK X5 40pin UART 串口通信

本课使用 RDK X5 40pin 排针上的 UART1，完成串口参数设置、硬件回环测试和 Python 数据收发。

> **适用硬件：** RDK X5
>
> **代码与完整讲义：** [第 12 课课程目录](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c)
>
> **飞书讲义：** [第 12 课　40pin 使用（2）UART 串口通信](https://horizonrobotics.feishu.cn/docx/Qjdhd8j7yoxWlSxsGJec4DojnGc)

## 1. 学习目标

完成本课后，你将能够：

1. 说明 UART 中 TX、RX 和 GND 的作用
2. 找到 RDK X5 UART1 对应的 BOARD 物理引脚
3. 说明波特率和 8N1 的含义
4. 运行系统预置示例，完成串口回环测试
5. 使用 Python `serial` API 发送和接收数据

## 2. UART 串口基础

UART（Universal Asynchronous Receiver/Transmitter，通用异步收发器）通过串行方式传输数据。发送端使用 TX 输出数据，接收端使用 RX 接收数据。

UART 没有共享时钟线，因此通信两端必须使用相同的参数：

| 参数 | 本课设置 | 说明 |
|------|----------|------|
| 波特率 | 115200 | 每秒传输的符号数量 |
| 数据位 | 8 | 每帧包含 8 位有效数据 |
| 校验 | None | 不使用奇偶校验 |
| 停止位 | 1 | 每帧使用 1 个停止位 |
| 流控 | None | 本实验不使用 RTS 和 CTS |

上面的配置通常写成 **115200 8N1，无流控**。两端只要有一项参数不同，就可能出现乱码或收不到数据。

连接真实外设时，RDK TX 要接外设 RX，RDK RX 要接外设 TX，两端还必须连接公共 GND。

## 3. RDK X5 UART1 引脚

RDK X5 默认在 40pin 接口上启用 UART1，使用 BOARD Pin 8 和 Pin 10，IO 电平为 3.3V。

![RDK X5 40pin 引脚功能对照图](../assets/images/beginner/rdk-x5-40pin-pinout.jpg)

| BOARD 引脚 | 信号 | 本课用途 |
|-----------|------|----------|
| **Pin 8** | UART1_TXD | RDK 发送数据 |
| **Pin 10** | UART1_RXD | RDK 接收数据 |
| **Pin 6** | GND | 连接外设公共地 |

> **接线前请断电。** UART1 使用 3.3V TTL 电平。不要把 RS-232 接口或 5V 串口信号直接接入 40pin。

## 4. 查看串口设备与配置

查看已经启用的串口设备：

```bash
ls -l /dev/ttyS*
```

RDK X5 的 40pin UART1 通常对应 `/dev/ttyS1`。`/dev/ttyS0` 是系统调试串口，不用于本课实验。

UART1 默认启用。如果 Pin 8 和 Pin 10 没有串口功能，可以检查复用配置：

```bash
sudo srpi-config
```

选择 **3 Interface Options**，进入 **I3 Peripheral bus config**，确认对应串口显示为 `okay`。修改后保存配置并重启开发板。

检查 pyserial：

```bash
python3 -c "import serial; print(serial.VERSION)"
```

如果出现 `ModuleNotFoundError`，运行：

```bash
python3 -m pip install pyserial
```

## 5. 系统回环实验

开发板断电后，用一根杜邦线连接 BOARD Pin 8（UART1_TXD）和 BOARD Pin 10（UART1_RXD）。回环实验不需要连接 3.3V 或 5V 引脚。

上电后运行系统预置示例：

```bash
python3 /app/40pin_samples/test_serial.py
```

设备名输入 `/dev/ttyS1`，波特率输入 `115200`。接线正确时，终端会显示：

```text
Starting demo now! Press CTRL+C to exit
Send: AA55
Recv: AA55
```

发送和接收内容一致，说明 UART1 的发送、接收和通信参数都能正常工作。

## 6. 运行课程 Demo

课程 Demo 固定使用 `/dev/ttyS1` 和 115200，不需要传入命令行参数。

```bash
git clone https://github.com/D-Robotics/rdk-course-demos.git
cd rdk-course-demos/01_beginner/12_40pin_uart_i2c/code
python3 uart_loopback.py
```

程序每秒发送一次 `AA55`，再读取 4 个字节：

```text
发送 AA55
接收 AA55
```

按 `Ctrl+C` 退出，程序会关闭串口设备。

## 7. Python `serial` API

| API | 作用 |
|-----|------|
| `serial.Serial("/dev/ttyS1", 115200, timeout=1)` | 打开 UART1，设置波特率和超时 |
| `ser.write(data)` | 发送 bytes 类型的数据 |
| `ser.read(size)` | 读取指定数量的字节 |
| `ser.readline()` | 读取一行数据 |
| `ser.close()` | 关闭串口并释放设备 |

`write()` 接收 bytes。字符串发送前需要使用 `encode()`，收到 bytes 后可以使用 `decode()` 转回字符串。

## 8. 连接真实串口模块

| RDK X5 | 串口外设 |
|--------|----------|
| BOARD Pin 8（UART1_TXD） | RX |
| BOARD Pin 10（UART1_RXD） | TX |
| BOARD Pin 6（GND） | GND |

外设是否由开发板供电，要根据外设手册单独确认。优先让外设使用自己的合规电源，两端保持共地。

## 9. 常见问题

| 现象 | 可能原因 | 处理方法 |
|------|----------|----------|
| 找不到 `/dev/ttyS1` | UART 功能未启用 | 使用 `srpi-config` 检查串口并重启 |
| 打开串口时 `Permission denied` | 当前用户没有设备权限 | 检查权限，必要时使用 `sudo python3` |
| 发送后没有接收 | 回环线未连通，或真实外设 TX/RX 未交叉 | 断电后重新核对接线 |
| 收到乱码 | 两端通信参数不同 | 核对波特率、数据位、校验和停止位 |
| 数据不稳定 | 没有共地或电平不兼容 | 检查 GND 和 3.3V TTL 电平 |

## 10. 本课小结

- RDK X5 默认在 BOARD Pin 8 和 Pin 10 上启用 UART1
- UART1 使用 3.3V TTL 电平，真实外设需要 TX/RX 交叉并共地
- 本课统一使用 115200、8N1 和无流控
- 40pin UART1 通常对应 `/dev/ttyS1`，不要误用 `/dev/ttyS0`
- 先完成 TXD 与 RXD 回环测试，再连接真实串口外设
- Python 通过 `serial.Serial()`、`write()`、`read()` 和 `close()` 完成串口收发

## 参考资料

- [RDK 官方 UART 使用说明](https://d-robotics.github.io/rdk_doc/en/Basic_Application/01_40pin_user_sample/uart/)
- [RDK X5 40pin GPIO 定义](https://developer.d-robotics.cc/rdk_doc/en/Basic_Application/01_40pin_user_sample/40pin_define/)
