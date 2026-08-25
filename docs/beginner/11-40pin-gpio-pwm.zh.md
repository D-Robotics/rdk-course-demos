# 第 11 课：RDK X5 40pin GPIO 与 PWM

## 1. 学习目标

完成本课后，你将能够：

1. 看懂 RDK X5 40pin 引脚图，并使用 BOARD 物理编号定位管脚
2. 使用 `Hobot.GPIO` 配置并读取 GPIO 输入
3. 说明轮询与中断的区别，认识上升沿、下降沿和双边沿
4. 理解 PWM 的频率、周期和占空比
5. 运行按键读取和舵机控制 Demo

---

## 2. 硬件清单

| 物品 | 数量 | 说明 |
|------|------|------|
| RDK X5 | 1 | 使用 40pin 排针 |
| 轻触按键 | 1 | 实验一读取按下和松开状态 |
| 10kΩ 电阻 | 1 | 作为按键输入的上拉电阻 |
| 舵机 | 1 | 常见 5V 小型舵机即可，使用前确认脉宽范围 |
| 稳压 5V 电源 | 1 | 独立给舵机供电 |
| 杜邦线、面包板 | 若干 | 用于完成接线 |

---

## 3. 认识 RDK X5 40pin

本课统一使用 **BOARD 编号**。BOARD 编号就是 40pin 排针上的物理位置：代码中的 `37` 表示物理 37 号脚，不是 BCM、CVM 或 SoC 编号。

![RDK X5 40pin 引脚功能对照图](../assets/images/beginner/rdk-x5-40pin-pinout.jpg)

本课只使用下面几个引脚：

| BOARD 编号 | 功能 | 本课用途 |
|-----------|------|----------|
| **Pin 17** | 3.3V | 按键输入上拉电源 |
| **Pin 33** | PWM7 | 舵机 PWM 信号 |
| **Pin 37** | GPIO26 | 读取按键状态 |
| **Pin 39** | GND | 按键接地、舵机电源共地 |

> **接线前请断电。** RDK X5 的 GPIO 使用 3.3V 逻辑，不能向 GPIO 输入 5V。舵机不要从 GPIO 信号脚取电，建议使用独立稳压 5V 电源，并将外部电源 GND 与 RDK X5 GND 相连。

---

## 4. GPIO、中断与 PWM

### 4.1 GPIO

GPIO（General Purpose Input/Output，通用输入输出）可以配置为输入或输出：

- **输入：**读取按键、传感器告警等 HIGH/LOW 状态
- **输出：**控制 LED、蜂鸣器、继电器等开关状态

本课的按键实验使用输入模式。按键松开时，10kΩ 电阻把 Pin 37 上拉为 HIGH；按下后 Pin 37 与 GND 导通，读取结果变为 LOW。

### 4.2 轮询与中断

**轮询**是程序不断调用 `GPIO.input()` 检查电平，写法简单直观；**中断**是在电平变化时通知程序，再执行预先注册的回调函数。

| 边沿 | 电平变化 | 按键上拉接线中的含义 |
|------|----------|----------------------|
| `GPIO.RISING` | LOW → HIGH | 按键松开 |
| `GPIO.FALLING` | HIGH → LOW | 按键按下 |
| `GPIO.BOTH` | 两个方向都检测 | 同时检测按下与松开 |

机械按键在按下和松开瞬间可能快速抖动，因此中断 API 通常配合 `bouncetime` 使用。回调函数应尽快结束，不要在回调中执行长时间阻塞任务。

### 4.3 PWM

PWM（Pulse Width Modulation，脉宽调制）是在固定频率下快速切换 HIGH 和 LOW，通过高电平持续时间控制外设。

```text
周期 T = 1 / 频率
占空比 = 高电平持续时间 / 周期时间 × 100%
```

舵机通常使用约 50Hz 的 PWM。50Hz 表示每秒 50 个周期，因此每个周期约为 20ms。改变占空比会改变高电平脉宽，从而改变舵机的目标位置。

`Hobot.GPIO` 只支持硬件 PWM，不提供软件模拟 PWM。RDK X5 默认使能 PWM3 组，本课使用其中的 BOARD Pin 33（PWM7）。

---

## 5. `Hobot.GPIO` Python API

### 5.1 检查环境

```bash
sudo python3
```

```python
import Hobot.GPIO as GPIO

print(GPIO.VERSION)
print(GPIO.model)
```

### 5.2 GPIO 基础命令

```python
import Hobot.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(37, GPIO.IN)
state = GPIO.input(37)

GPIO.cleanup()
```

| API | 作用 |
|-----|------|
| `GPIO.setmode(GPIO.BOARD)` | 使用 40pin 物理编号 |
| `GPIO.setup(pin, GPIO.IN)` | 将引脚配置为输入 |
| `GPIO.setup(pin, GPIO.OUT)` | 将引脚配置为输出 |
| `GPIO.input(pin)` | 读取 HIGH/LOW 电平 |
| `GPIO.output(pin, value)` | 输出 HIGH/LOW 电平 |
| `GPIO.gpio_function(pin)` | 查看引脚当前功能 |
| `GPIO.cleanup()` | 释放本程序使用的 GPIO 资源 |

### 5.3 中断 API

本课不增加第三个实验程序，下面的代码只用于认识中断 API：

```python
def button_pressed(channel):
    print("检测到按键，通道：", channel)

GPIO.add_event_detect(
    37,
    GPIO.FALLING,
    callback=button_pressed,
    bouncetime=200,
)

# 不再监听时执行
GPIO.remove_event_detect(37)
```

`GPIO.wait_for_edge(channel, edge, timeout)` 可以阻塞等待一次边沿事件；`GPIO.add_event_detect()` 用于后台监听，配合 `callback` 在事件发生时执行函数。

### 5.4 PWM API

```python
pwm = GPIO.PWM(33, 50)
pwm.start(0)
pwm.ChangeDutyCycle(7.5)
pwm.stop()
GPIO.cleanup()
```

| API | 作用 |
|-----|------|
| `GPIO.PWM(pin, frequency)` | 在硬件 PWM 引脚上创建 PWM 对象 |
| `pwm.start(duty_cycle)` | 启动 PWM，并设置初始占空比 |
| `pwm.ChangeDutyCycle(duty_cycle)` | 修改占空比 |
| `pwm.stop()` | 停止 PWM 输出 |

---

## 6. 代码结构

```text
11_40pin_gpio_pwm/
├── README.md
├── assets/
│   └── rdk_x5_40pin_pinout.jpg
└── code/
    ├── read_button.py
    └── servo_pwm.py
```

两个 Demo 都使用固定引脚，不需要传入命令行参数。

---

## 7. 实验一：读取按键状态

### 7.1 接线

| 连接 | BOARD 引脚 |
|------|------------|
| 3.3V | Pin 17 |
| 按键输入 | Pin 37（GPIO26） |
| GND | Pin 39 |

```text
BOARD Pin 17（3.3V）── 10kΩ 电阻 ──┐
                                    ├── BOARD Pin 37（GPIO26 输入）
BOARD Pin 39（GND）── 轻触按键 ─────┘
```

按键松开时读取为 HIGH，按下时读取为 LOW。

### 7.2 运行

```bash
git clone https://github.com/D-Robotics/rdk-course-demos.git
cd rdk-course-demos/01_beginner/11_40pin_gpio_pwm/code
sudo python3 read_button.py
```

按下和松开按键，终端会输出：

```text
按键松开
按键按下
按键松开
```

程序每隔 50ms 读取一次，只在状态发生变化时打印。按 `Ctrl+C` 退出，程序会调用 `GPIO.cleanup()` 释放资源。

---

## 8. 实验二：PWM 控制舵机

### 8.1 接线

请先关闭 RDK X5 和舵机外部电源，再连接导线。

| 舵机导线 | 连接位置 | 说明 |
|----------|----------|------|
| 信号线（通常为橙色或黄色） | BOARD Pin 33（PWM7） | 只传输 PWM 信号 |
| 电源正极（通常为红色） | 外部稳压 5V | 不要连接 GPIO 信号脚 |
| 电源地（通常为棕色或黑色） | 外部电源 GND | 舵机电源地 |
| 共地线 | 外部电源 GND → BOARD Pin 39 | RDK X5 与舵机必须共地 |

```text
BOARD Pin 33（PWM7）──────── 舵机信号线
外部稳压 5V ─────────────── 舵机电源正极
外部电源 GND ────────────── 舵机电源地
外部电源 GND ────────────── BOARD Pin 39（GND）
```

### 8.2 运行

```bash
cd rdk-course-demos/01_beginner/11_40pin_gpio_pwm/code
sudo python3 servo_pwm.py
```

程序依次输出 5.0%、7.5%、10.0% 三个占空比，最后回到 7.5%。每个位置保持 1 秒。

不同舵机的脉宽范围可能不同。首次实验应保持安全范围；如果出现撞限位、持续抖动或异常发热，请立即断电并查阅舵机规格。

---

## 9. 系统预置示例

RDK OS 在 `/app/40pin_samples/` 中提供了基础示例，可以先用它们验证硬件和系统配置：

| 类别 | 示例 |
|------|------|
| GPIO 输入输出 | `simple_input.py`、`simple_out.py`、`button_led.py` |
| 边沿与中断 | `button_event.py`、`button_interrupt.py` |
| PWM | `simple_pwm.py` |
| 全引脚测试 | `test_all_pins.py`、`test_all_pins_input.py` |

```bash
cd /app/40pin_samples
ls
```

如果 `GPIO.PWM(33, 50)` 创建失败，请通过 `sudo srpi-config` 检查 PWM3 是否启用，修改后重启系统。

---

## 10. 常见问题

| 现象 | 可能原因 | 处理方法 |
|------|----------|----------|
| 按键一直显示按下 | Pin 37 与 GND 短接，或按键引脚接错 | 断电后重新核对按键方向和接线 |
| 按键未操作时状态不断变化 | Pin 37 悬空或 10kΩ 上拉电阻未接好 | 检查 Pin 17、Pin 37 和上拉电阻 |
| 舵机不动作 | 外部电源未开启、未共地或信号脚接错 | 检查外部 5V、Pin 39 共地和 Pin 33 |
| 舵机持续抖动 | 供电能力不足、频率不对或占空比超出范围 | 检查电源、50Hz 设置和舵机规格 |
| `Permission denied` | 当前用户没有 GPIO/PWM 权限 | 使用 `sudo python3` 运行 |
| PWM 对象创建失败 | PWM3 未启用或引脚复用冲突 | 使用 `sudo srpi-config` 检查 PWM3 后重启 |

---

## 11. 本课小结

- BOARD 编号对应 40pin 排针的物理位置
- `GPIO.input()` 用于读取 HIGH/LOW 电平
- 轮询是程序反复检查，中断是电平变化后通知程序
- PWM 使用频率和占空比控制脉冲；舵机需要独立供电并与 RDK X5 共地
- 程序退出前应执行 `pwm.stop()` 和 `GPIO.cleanup()`
