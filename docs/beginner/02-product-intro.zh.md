<!-- markdownlint-disable MD013 -->

# 第 2 课：认识 RDK 硬件全家桶

> 适用产品：RDK X3、RDK X3 Module、RDK X5、RDK X5 Module、RDK S100、RDK S100P、RDK S100 SIP、RDK S600、RDK S600 Module  
> 课程主题：RDK 硬件产品与关键能力介绍  
> 配套课件：[查看中文 HTML 课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/02_product_intro/rdk_hardware_family.html) · [English slide source](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/02_product_intro/rdk_hardware_family_en.html)

![RDK X3、RDK X5、RDK S100 与 RDK S600 系列硬件实物合照](https://raw.githubusercontent.com/D-Robotics/rdk-course-demos/develop/01_beginner/02_product_intro/images/rdk_family_lineup.jpg)

## 课程目标

认识 RDK X3、RDK X5、RDK S100、RDK S600 四个硬件系列及八种具体产品形态，理解它们的计算、影像、编解码、通信接口、实时控制与尺寸信息，并分清开发板/开发套件和 Module/SIP 的硬件边界。

本课以硬件介绍为主。选型只作为理解产品形态的补充，软件安装、系统配置与算法开发将在后续课程中展开。

## 一、RDK 硬件全景

RDK 硬件从 5 TOPS 的入门平台延伸到 560 TOPS 的具身智能平台，覆盖基础视觉、主流机器人感知、多摄实时控制和端侧大模型等不同计算层级。

理解一款 RDK，建议同时看四层能力：

| 能力层 | 需要关注的硬件 |
| --- | --- |
| 计算 | CPU 架构、BPU 算力、内存容量与带宽、存储 |
| 影像与媒体 | Camera 连接器、MIPI RX/Lane、ISP、H.264/H.265/MJPEG/JPEG Codec |
| 通信与扩展 | CAN/CAN FD、USB Host/Device、以太网、PCIe、40-pin |
| 实时控制 | Cortex-R52+ MCU、MCU 域 CAN、UART、SPI、I2C、PWM、ADC、LIN |

> TOPS 是算力指标之一，不能单独代表模型实际性能。比较平台时还需要结合模型、精度、输入尺寸、并发、内存带宽和软件版本。

## 二、八种产品形态

| 产品 | 形态 | 尺寸 | 公开时间口径 |
| --- | --- | --- | --- |
| RDK X3 | 全功能开发板 | 85×56×20 mm | 2022-06 发布；2023-07 RDK X3 v2.0 上线 |
| RDK X3 Module | 核心模组 | 55×40 mm | 2023-05 正式发布 |
| RDK X5 | 主流机器人开发板 | 85×56×20 mm | 2024-09 正式发布 |
| RDK X5 Module | 核心模组 | 55×40 mm | 2025-04 首次进入官方 TROS 支持 |
| RDK S100 / S100P | 80 / 128 TOPS 异构机器人开发套件 | 120×121×51 mm | RDK S100 于 2025-06 现货开售 |
| RDK S100 SIP | 产品化高集成形态 | 65×65×4.75 mm | 与 RDK S100 同系列，2025-06 |
| RDK S600 | 具身智能开发套件 | 140×123×78 mm | 2026-06 正式发售 |
| RDK S600 Module | 699-pin B2B 核心模组 | 120×83 mm | 2026-06 公开 V1.0.x 设计资料 |

发布、开售、首次进入官方软件支持和设计资料公开是不同时间口径，不能直接视为相同含义的“上市日期”。

## 三、四个硬件系列

### RDK X3 系列：教学与轻量视觉

系列共同能力：4×Cortex-A53、5 TOPS、2/4GB LPDDR4，H.264/H.265/MJPEG 最高 4K@60。

| 对比项 | RDK X3 | RDK X3 Module |
| --- | --- | --- |
| 产品形态 | 全功能开发板 | 55×40 mm 核心模组 |
| 影像接口 | 当前资料列 1×MIPI CSI | 1×4-lane + 2×2-lane MIPI CSI |
| USB | 1×USB3 Host、2×USB2 Host、1×Micro USB Device | 原生 1×USB3，物理端口由载板决定 |
| 硬件定位 | 课程、基础视觉和快速验证 | 紧凑产品与定制载板集成 |

### RDK X5 系列：主流机器人视觉

系列共同能力：8×Cortex-A55、10 TOPS、最高 8GB LPDDR4，H.264/H.265 最高 4K@60。

| 对比项 | RDK X5 | RDK X5 Module |
| --- | --- | --- |
| 产品形态 | 85×56×20 mm 机器人开发板 | 55×40 mm 核心模组 |
| Camera | 2×22-pin，每口对应 2-lane MIPI CSI | 2×4-lane，可配置为 4×2-lane |
| ISP | 当前开发板公开手册未单列独立吞吐 | 4K@60，支持 HDR、3DNR、WDR、PDAF |
| 关键接口 | 1×CAN FD、4×USB3 Host、GbE + PoE | USB、CAN、网络连接器由载板完成 |
| 硬件定位 | 开箱连接相机、网络和常见外设 | 自定义尺寸、连接器和产品载板 |

### RDK S100 / S100P 系列：感知与实时控制

RDK S100 为 6×Cortex-A78AE @1.5GHz、12GB LPDDR5、80 TOPS；RDK S100P 为 6×Cortex-A78AE @2.0GHz、24GB LPDDR5、128 TOPS。两者均集成 4×Cortex-R52+ MCU、2×ISP，媒体能力最高 4K@90。

| 对比项 | RDK S100 / S100P | RDK S100 SIP |
| --- | --- | --- |
| 产品形态 | 120×121×51 mm 异构开发套件 | 65×65×4.75 mm 高集成计算单元 |
| 型号差异 | S100：1.5GHz、12GB、80 TOPS；S100P：2.0GHz、24GB、128 TOPS | 产品化 SIP 形态，不等同于 S100P 开发套件型号 |
| 影像 | 3×4-lane MIPI 信号、2×ISP | 共享平台影像能力，以 SIP Pinout 为准 |
| 关键接口 | 4×USB3 Host、1×USB2 Device、2×GbE | MIPI、USB、CAN 和 MCU IO 由 Pinout 与载板决定 |
| MCU 扩展 | 覆盖 5 路 CAN FD 及 I2C/SPI/UART/PWM/GPIO | 共享平台 MCU 能力，实际引出以设计资料为准 |
| 硬件定位 | 多摄感知和实时控制系统验证 | 高集成机器人产品设计 |

### RDK S600 系列：具身智能与端侧大模型

系列共同能力：18×Cortex-A78AE、560 TOPS、6×Cortex-R52+ MCU、32/64GB LPDDR5、4×ISP，H.264/H.265 总计 4K@240。

| 对比项 | RDK S600 | RDK S600 Module |
| --- | --- | --- |
| 产品形态 | 140×123×78 mm 具身智能开发套件 | 120×83 mm、699-pin B2B 核心模组 |
| 影像 | 多路 MIPI、4×ISP | 6×4-lane MIPI RX、4×ISP |
| CAN 与 MCU | 4×主域 CAN + 5×MCU CAN，并提供 MCU 扩展 | 主域 4×CAN；MCU 域提供 CAN FD、LIN、PWM、ADC 等资源 |
| USB 与网络 | 6×USB3 Host；2×1GbE + 2×10GbE | 原生公开项为 1×USB2；网络资源和端口由载板决定 |
| 硬件定位 | 具身智能整机与高阶算法验证 | 高性能机器人商业化集成 |

## 四、开发板、开发套件、Module 与 SIP

- **开发板或开发套件**：USB-A、RJ45、CAN 端子和相机连接器已经完成板级设计，适合直接连接外设和搭建系统。
- **Module**：集成 SoC、内存、存储和关键电源电路，通过连接器引出原生资源；最终端口由载板决定。
- **SIP**：集成程度更高，产品设计需要重点核对封装、Pinout、电源、散热和可靠性。

同系列产品可以共享计算平台，但开发板上的物理端口不能直接写成 Module/SIP 的原生接口。反过来，Module/SIP 的最大原生资源也不等于载板能够同时做出的全部物理端口。

## 五、本课小结

1. RDK X3、RDK X5、RDK S100、RDK S600 构成四个计算层级；
2. 各系列都需要同时理解计算、影像、媒体和通信接口；
3. RDK S100/S100P 提供 80/128 TOPS，RDK S100 与 RDK S600 系列进一步加入实时 MCU 域；
4. 开发板/套件用于快速开发和验证，Module/SIP 面向紧凑集成和产品化。

## 参考资料

- [D-Robotics 官方资料中心](https://developer.d-robotics.cc/)
- [D-Robotics 产品官网](https://d-robotics.cc/)
- [RDK X 系列发布记录](https://developer.d-robotics.cc/rdk_x_doc/en/Release_Note/release_note)
- [RDK S 系列资源汇总](https://developer.d-robotics.cc/rdk_s_doc/en/Quick_start/download?p=RDK+S100&v=4.0.5)
资料更新时间：2026 年 8 月。正式设计请以当前 Datasheet、Pinlist、硬件设计指南和官方资料中心为准。
