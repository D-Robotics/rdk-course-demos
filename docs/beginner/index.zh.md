# 基础入门

先学习通用基础，再根据开发板选择 RDK X5 或 RDK S100 路径，完成系统与外设实践。已发布的讲义提供页面链接；规划中的主题仅链接到已有仓库目录。

## 通用基础

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [社区与生态](01-community-ecosystem.md) | RDK 社区、资料入口、NodeHub 应用案例补充入口、论坛使用规范 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/01_community_ecosystem) |
| 产品介绍 | 产品系列、硬件特性、Roadmap、典型使用场景 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/02_product_intro) |
| [RDK Studio](03-rdk-studio.md) | 认识面向 RDK 设备的 AI 原生开发工作台；使用 Moss 完成 X5 只读体检和 BPU YOLO 实时检测，并了解终端、文件、code-server、远程桌面、系统烧录与板端 Agent | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/03_rdk_studio) |

## RDK X5

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [系统烧录](04-flash-system-x5.md) | 系统镜像烧录、MiniBoot 更新、烧录后检查 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system) |
| [启动与问题排查](05-boot-troubleshooting-x5.md) | 启动流程、灯状态、启动日志、典型启动问题 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting) |
| 远程连接 | 串口连接、SSH、网络连接、VNC、远程开发 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/06_remote_connection) |
| Camera | USB Camera、MIPI Camera、C/Python 调用、TROS 快速使用 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/07_camera) |
| Audio | 板载 Earphone、音频板、USB 音频设备验证 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| 显示 | HDMI、DSI 显示模块、显示配置与效果验证 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/09_display) |
| 编解码 | 编码能力、解码能力、BSP 接口、RTSP 推流解码 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| GPIO 与 PWM | GPIO、PWM 基础、点灯、舵机控制 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| UART 与 I2C | 串口基础、串口收发 Demo、I2C 基础、I2C 读取温湿度传感器 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| [SPI](../hardware/spi-display.md) | SPI 基础、SPI 驱动屏幕 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| CAN | CAN FD 基础、can-utils、CAN 回环测试、CAN 电机控制 Demo、CAN 逻辑分析仪制作 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |

## RDK S100

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [系统烧录](04-flash-system-s100.md) | 系统镜像烧录、MiniBoot 更新、烧录后检查 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system) |
| [启动与问题排查](05-boot-troubleshooting-s100.md) | 启动流程、灯状态、启动日志、典型启动问题 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting) |
| 远程连接 | 串口连接、SSH、网络连接、VNC、远程开发 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/06_remote_connection) |
| Camera | USB Camera、MIPI Camera、C/Python 调用、TROS 快速使用 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/07_camera) |
| Audio | 板载 Earphone、音频板、USB 音频设备验证 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| 显示 | HDMI、DSI 显示模块、显示配置与效果验证 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/09_display) |
| 编解码 | 编码能力、解码能力、BSP 接口、RTSP 推流解码 | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| GPIO 与 PWM | GPIO、PWM 基础、点灯、舵机控制 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| UART 与 I2C | 串口基础、串口收发 Demo、I2C 基础、I2C 读取温湿度传感器 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| SPI | SPI 基础、SPI 驱动屏幕 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| CAN | CAN FD 基础、can-utils、CAN 回环测试、CAN 电机控制 Demo、CAN 逻辑分析仪制作 Demo | [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |
