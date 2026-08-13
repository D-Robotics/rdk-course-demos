# RDK 小课堂课程介绍

欢迎来到 RDK 开发课程。

本课程是一套面向 RDK 开发者的视频课程，主要通过 **讲解视频 + 配套讲义 + GitHub Demo** 的方式，帮助开发者系统学习 RDK 板卡的基础使用、外设验证、模型部署、TROS 开发、系统驱动调试以及具身智能应用开发。

其中：

- **讲解视频** 是课程主体，用于完整讲解概念、操作流程、实验演示和常见问题；
- **GitHub Pages 讲义** 是课程配套资料，用于整理命令、步骤、截图、排查方法和参考链接；
- **GitHub Demo** 是课程配套代码，用于存放脚本、示例工程和可复现实验；
- **官方文档** 是扩展参考资料，用于进一步查阅产品、系统、接口和软件栈细节。

建议学习时优先观看讲解视频，再结合讲义和 Demo 在板卡上完成实际操作。

---

# 课程适合谁

本课程适合以下开发者：

- 零基础开发者；
- 第一次接触 RDK 板卡，希望快速完成上手；
- 已有 Linux 基础，希望学习 RDK 外设、系统和工具链使用；
- 已有 AI / ROS / 机器人开发经验，希望在 RDK 上部署模型或构建应用；
- 希望基于 RDK 开发 Camera、Audio、CAN、40pin、编解码、TROS 或具身智能项目；
- 需要系统了解 RDK 课程体系、Demo 示例和开发资料入口的学习者。

---

# 推荐学习方式

建议按照以下顺序学习每节课程：

1. 观看讲解视频，先理解课程目标、实验流程和关键注意事项；
2. 打开 GitHub Pages 讲义，对照视频中的命令、步骤和截图进行操作；
3. 如果课程提供 GitHub Demo，下载或克隆 Demo 后在 RDK 板卡上运行；
4. 根据讲义中的“成功标准”和“常见问题排查”确认实验结果；
5. 完成拓展练习，尝试修改参数、替换设备或组合其他功能。

每节课程一般包含：

- 课程视频；
- 配套讲义；
- GitHub Demo；
- 官方参考文档；
- 实验环境说明；
- 操作流程；
- 成功标准；
- 常见问题排查；
- 拓展练习。

---

# 课程资源说明

## 讲解视频

讲解视频是本课程的核心内容。

视频中会重点讲解：

- 本节课要解决什么问题；
- 为什么需要掌握这个功能；
- 实验前需要准备哪些环境；
- 每一步命令或操作的作用；
- 正常结果应该是什么；
- 常见错误如何判断和排查；
- 该能力在真实项目中如何使用。

## GitHub Pages 讲义

入口：[中文课程讲义](https://d-robotics.github.io/rdk-course-demos/zh/)｜[English Course Handbook](https://d-robotics.github.io/rdk-course-demos/)

GitHub Pages 讲义是视频课程的配套资料。

讲义主要用于：

- 存放课程命令；
- 整理实验步骤；
- 补充截图和结果说明；
- 记录常见问题；
- 汇总参考链接；
- 方便学习者复制命令并复现实验。

讲义不是孤立教程，建议配合讲解视频使用。

## GitHub Demo

入口：[rdk-course-demos](https://github.com/D-Robotics/rdk-course-demos)

GitHub Demo 用于存放课程配套代码和示例工程。

Demo 中可能包含：

- 一键检查脚本；
- 示例运行脚本；
- C / C++ 示例；
- Python 示例；
- ROS / TROS 示例；
- 模型推理 Demo；
- 配置文件；
- 示例输入输出数据。

课程讲义的原始 Markdown 和 GitHub Pages HTML 界面的原始内容也会放在 `rdk-course-demos` 仓库中。

## 官方文档

入口：[RDK 官方文档](https://developer.d-robotics.cc/rdk_doc_center/)

官方文档用于补充课程之外的完整说明，包括产品手册、系统文档、接口说明、Model Zoo 文档、TROS 文档等。

---

# 学习路径建议

如果你是第一次使用 RDK，建议按照下面顺序学习：

```text
入门篇：RDK 的基础使用
↓
进阶篇：ModelZoo 开发指南
↓
进阶篇：TROS 开发指南
↓
进阶篇：系统驱动开发指南
↓
高阶篇：大语言模型与具身指南
↓
开发者案例
```

如果你已经熟悉 Linux、ROS 或 AI 模型部署，也可以根据当前开发目标直接进入对应篇章。

---

# 课程目录

## 入门篇：RDK 的基础使用

本篇面向 RDK 新用户，重点解决“板卡如何启动、如何连接、如何确认外设、如何运行基础功能”的问题。

完成本篇后，你应能够独立完成 RDK 板卡的基础使用、常见外设验证和基础问题排查。

### 通用基础

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [社区与生态](beginner/01-community-ecosystem.md) | RDK 社区、资料入口、NodeHub 应用案例补充入口、论坛使用规范 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/01_community_ecosystem) |
| 产品介绍 | 产品系列、硬件特性、Roadmap、典型使用场景 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/02_product_intro) |
| [RDK Studio](beginner/03-rdk-studio.md) | 认识面向 RDK 设备的 AI 原生开发工作台；使用 Moss 完成 X5 只读体检和 BPU YOLO 实时检测，并了解终端、文件、code-server、远程桌面、系统烧录与板端 Agent | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/03_rdk_studio) |

### RDK X5

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [系统烧录](beginner/04-flash-system-x5.md) | 系统镜像烧录、MiniBoot 更新、烧录后检查 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system) |
| [启动与问题排查](beginner/05-boot-troubleshooting-x5.md) | 启动流程、灯状态、启动日志、典型启动问题 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting) |
| 远程连接 | 串口连接、SSH、网络连接、VNC、远程开发 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/06_remote_connection) |
| Camera | USB Camera、MIPI Camera、C/Python 调用、TROS 快速使用 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/07_camera) |
| Audio | 板载 Earphone、音频板、USB 音频设备验证 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| 显示 | HDMI、DSI 显示模块、显示配置与效果验证 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/09_display) |
| 编解码 | 编码能力、解码能力、BSP 接口、RTSP 推流解码 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| GPIO 与 PWM | GPIO、PWM 基础、点灯、舵机控制 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| UART 与 I2C | 串口基础、串口收发 Demo、I2C 基础、I2C 读取温湿度传感器 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| [SPI](hardware/spi-display.md) | SPI 基础、SPI 驱动屏幕 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| CAN | CAN FD 基础、can-utils、CAN 回环测试、CAN 电机控制 Demo、CAN 逻辑分析仪制作 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |

### RDK S100

| 主题 | 内容重点 | 配套资料 |
|---|---|---|
| [系统烧录](beginner/04-flash-system-s100.md) | 系统镜像烧录、MiniBoot 更新、烧录后检查 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system) |
| [启动与问题排查](beginner/05-boot-troubleshooting-s100.md) | 启动流程、灯状态、启动日志、典型启动问题 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting) |
| 远程连接 | 串口连接、SSH、网络连接、VNC、远程开发 | 视频 / 讲义 / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/06_remote_connection) |
| Camera | USB Camera、MIPI Camera、C/Python 调用、TROS 快速使用 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/07_camera) |
| Audio | 板载 Earphone、音频板、USB 音频设备验证 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| 显示 | HDMI、DSI 显示模块、显示配置与效果验证 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/09_display) |
| 编解码 | 编码能力、解码能力、BSP 接口、RTSP 推流解码 | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| GPIO 与 PWM | GPIO、PWM 基础、点灯、舵机控制 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| UART 与 I2C | 串口基础、串口收发 Demo、I2C 基础、I2C 读取温湿度传感器 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| SPI | SPI 基础、SPI 驱动屏幕 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| CAN | CAN FD 基础、can-utils、CAN 回环测试、CAN 电机控制 Demo、CAN 逻辑分析仪制作 Demo | 视频 / 讲义 / Demo / [GitHub](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |

---

## ModelZoo 与 RoboGo 开发指南

本篇面向希望在 RDK 上运行 AI 模型的开发者，重点讲解模型准备、模型转换、模型部署和典型视觉任务 Demo，同时讲解如何使用 Robogo 云平台进行模型训练和转化操作。

完成本篇后，你应能够理解 RDK Model Zoo 的基本结构，并能基于已有 Demo 完成模型推理实验，同时能够学会 Robogo 云平台的使用，进行模型的云端训练与转化。

| 主题 | 本课主要解决的问题 | 配套资料 |
|---|---|---|
| ModelZoo 使用指南 | 了解官方 Model Zoo 仓库、支持模型、分支说明、快速运行已有 Sample | 视频 / 讲义 / GitHub 代码 |
| ModelZoo Sample 结构说明 | 讲解典型 Sample 中 conversion、model、runtime、evaluator、test_data 等目录的作用 | 视频 / 讲义 |
| 算法工具链与量化环境准备 | 介绍本地工具链、Docker 环境、RoboGo 云桌面 / 云主机 / 在线量化环境的使用方式 | 视频 / 讲义 |
| ResNet 分类模型训练与量化 | 以 ResNet 为例，完成分类模型训练、模型导出、量化、校验和板端推理验证（云 + 本地） | 视频 / 讲义 / GitHub 代码 |
| YOLO 检测模型训练与量化 | 以 YOLO 为例，完成检测模型训练、ONNX 导出、量化、校验和板端推理验证（云 + 本地） | 视频 / 讲义 / GitHub 代码 |
| Featuremap 模型量化说明 | 以需要配置 Featuremap 的模型为例，说明 Featuremap 配置方式、适用场景和常见问题（云 + 本地） | 视频 / 讲义 |
| 板端 Python Runtime 推理 | 讲解 hbm_runtime 的模型加载、输入构造、推理执行、输出解析和结果可视化 | 视频 / 讲义 / GitHub 代码 |
| 板端 C/C++ Runtime 推理 | 讲解 C/C++ 推理接口、模型加载、前处理、BPU 推理、后处理和编译运行方式 | 视频 / 讲义 / GitHub 代码 |
| YOLO 后处理与 Demo 改造 | 以 YOLO Runtime 为例，讲解检测框解析、阈值设置、NMS、类别映射和自定义模型适配 | 视频 / 讲义 / GitHub 代码 |
| ModelZoo 开发共建 | 讲解新 Sample 的目录规范、命名规则、README 要求、测试数据、运行脚本和提交方式 | 视频 / 讲义 |

---

## TROS 开发指南

本篇面向 ROS / TROS 开发者，重点讲解 RDK 上的机器人应用开发流程。

完成本篇后，你应能够运行 TROS 示例，理解节点、话题、服务、参数的基本使用，并完成 Camera、感知、控制等基础实验。

---

## 系统驱动开发指南

本篇面向需要进行外设适配、底层调试和系统集成的开发者。

完成本篇后，你应能够理解 RDK 常见接口的系统层使用方式，并能进行基础驱动调试和日志分析。

---

## 大语言模型与具身智能

本篇面向希望在 RDK 上构建智能体、语音交互、机器人感知与控制应用的开发者。

完成本篇后，你应能够理解 RDK 在具身智能应用中的角色，并能组合语音、视觉、ROS/TROS 和大模型能力完成基础项目。

---

## 开发者案例

本篇用于沉淀真实项目案例、社区开发者作品和典型应用方案。

---

# 建设说明

本课程仍在持续建设中，课程名称、讲解顺序、视频内容、讲义内容和 Demo 示例会根据 RDK 产品能力、官方文档更新和开发者反馈持续调整。

课程内容按照“先完成讲义，再生成或更新 HTML，最后准备录制材料”的顺序制作。讲义负责沉淀课程事实，HTML 负责在线呈现，录制材料以已经确认的讲义和页面为依据。

讲义原始 Markdown 与 HTML 界面的原始内容都会放在 `rdk-course-demos` 仓库中。
