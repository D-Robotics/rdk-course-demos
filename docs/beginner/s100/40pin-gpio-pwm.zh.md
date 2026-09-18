# RDK S100 40-pin GPIO 与 PWM

本文根据已录制课程的配套课件整理，保留原课件的接线、命令、实测结果和验证范围。

[原始课件](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/11_40pin_gpio_pwm/lesson-11-s100-zh.html)

用一只 LED 完成数字输出与硬件调光验证。

## 本课完成两项可见验证

同一只 LED，两次最小接线，分别验证开关量与连续亮度变化。

### GPIO 输出

Pin 37 周期性输出高低电平，LED 规律亮灭。

### PWM 调光

Pin 33 输出 48 kHz PWM，占空比连续变化。

### 证据闭环

接线照片、实拍视频和示例程序共同证明结果。

## 40-pin 接线边界

S100 数字 IO 使用 3.3V 逻辑。本课只从 J24 取信号和地，不使用独立电源。

- 断电接线，上电后不移动杜邦线
- LED 必须串联 330Ω 限流电阻
- GPIO 输出不得直接短接 3.3V 或 GND
- 本课使用 BOARD 物理编号
- 退出程序后调用 GPIO.cleanup()

## 数字输出只有两种状态

### HIGH

输出接近 3.3V，电流经过电阻和 LED。

### LOW

输出接近 0V，LED 熄灭。

### 周期切换

示例每秒切换一次电平，形成可见闪烁。

### 安全退出

Ctrl+C 结束，释放管脚状态。

## GPIO 实拍接线

J24 Pin 37 接 330Ω，再接 LED 长脚；LED 短脚回到 Pin 20 GND。

![RDK S100 GPIO LED wiring](../../assets/images/beginner/lesson-11-s100-045dc7326ed7.jpg)

Pin 37 → 330Ω → LED → Pin 20 GND

## 运行官方输出示例

进入板载示例目录后启动 simple\_out.py。程序直接使用 BOARD 编号。

### 执行命令

```text
sudo python3 /app/40pin_samples/simple_out.py
```

按 Ctrl+C 结束。

### 关键逻辑

```text
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37, HIGH / LOW)
```

输出每秒翻转一次。

## GPIO 验证链路

**断电**确认 Pin 37 与 GND

**上电**系统进入稳定桌面

**运行**启动 simple\_out.py

**观察**LED 周期亮灭

**退出**Ctrl+C 清理管脚

## 占空比决定平均亮度

### 频率

本例固定为 48 kHz，切换速度远高于肉眼分辨能力。

### 占空比

高电平所占比例越大，LED 平均亮度越高。

### 硬件通道

S100 40-pin 的 Pin 32 和 Pin 33 支持 LPWM。

### 可见结果

亮度从 25% 上升到 100%，随后下降。

## PWM 实拍接线

保持电阻、LED 和 GND 不变，只把信号线从 Pin 37 移到支持硬件 PWM 的 Pin 33。

![RDK S100 PWM LED wiring](../../assets/images/beginner/lesson-11-s100-ef15eb47c679.jpg)

Pin 33 → 330Ω → LED → Pin 20 GND

## 运行硬件 PWM 示例

simple\_pwm.py 使用 48 kHz，并按 5% 步进修改占空比。

### 执行命令

```text
sudo python3 /app/40pin_samples/simple_pwm.py
```

Pin 33 不得被其他功能占用。

### 关键参数

```text
GPIO.PWM(33, 48000)
ChangeDutyCycle(25 ... 100)
```

每 0.25 秒改变 5%。

## PWM 验证链路

**断电**把信号线移到 Pin 33

**上电**保持 330Ω 与 GND

**运行**启动 simple\_pwm.py

**观察**LED 渐亮再渐暗

**退出**停止 PWM 并 cleanup

## 两种输出解决不同问题

### GPIO

适合开关控制，只有 HIGH 与 LOW。

### PWM

适合调光、调速等平均功率控制。

### 共同验收

接线正确、现象可见、退出后资源释放。

## 没有现象时按顺序排查

优先检查物理连接，再看权限和管脚占用。

Step 1

断电核对 LED 极性、电阻和 GND。

Step 2

确认代码使用 BOARD 编号 37 或 33。

Step 3

检查是否以 sudo 运行，是否有其他进程占用管脚。

Step 4

结束旧程序并重新上电测试，不带电移动信号线。

## 完成

一只 LED 已完成 GPIO 闪烁与 PWM 调光两项 S100 40-pin 验证。

### 接线可复现

Pin 37 与 Pin 33 分别承担两项实验。

### 现象可见

亮灭与渐变都由实拍视频保留。

### 继续学习

下一课进入 UART 与 I2C 通信总线。
