<!-- markdownlint-disable MD013 -->

# Lesson 02: Meet the RDK Hardware Portfolio

> Products: RDK X3, RDK X3 Module, RDK X5, RDK X5 Module, RDK S100, RDK S100P, RDK S100 SIP, RDK S600, and RDK S600 Module  
> Topic: RDK hardware products and key capabilities  
> Slides: [Open English HTML slides on GitHub](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/02_product_intro/rdk_hardware_family_en.html) · [中文课件源码](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/02_product_intro/rdk_hardware_family.html)

![RDK X3, RDK X5, RDK S100, and RDK S600 hardware lineup](https://raw.githubusercontent.com/D-Robotics/rdk-course-demos/develop/01_beginner/02_product_intro/images/rdk_family_lineup.jpg)

## Course goal

Meet four RDK hardware families and eight product forms. Understand their compute, vision, codec, connectivity, real-time control, and physical dimensions. Learn the hardware boundary between boards or development kits and Module or SIP forms.

This lesson focuses on hardware. Product selection is only mentioned to clarify form factors. Software setup, system configuration, and application development are covered in later lessons.

## 1. RDK hardware overview

The RDK portfolio scales from a 5 TOPS entry platform to a 560 TOPS embodied-AI platform. It covers learning and basic vision, mainstream robot perception, multi-camera real-time control, and edge large-model workloads.

Four capability layers define an RDK platform:

| Layer | Hardware to examine |
| --- | --- |
| Compute | CPU architecture, BPU performance, memory capacity and bandwidth, storage |
| Vision and media | Camera connectors, MIPI RX and lanes, ISP, H.264/H.265/MJPEG/JPEG codec |
| Connectivity and expansion | CAN/CAN FD, USB Host/Device, Ethernet, PCIe, 40-pin I/O |
| Real-time control | Cortex-R52+ MCU, MCU-domain CAN, UART, SPI, I2C, PWM, ADC, LIN |

> TOPS is only one compute metric. Actual model performance also depends on model architecture, precision, input size, concurrency, memory bandwidth, and software version.

## 2. Eight product forms

| Product | Form | Dimensions | Public date definition |
| --- | --- | --- | --- |
| RDK X3 | Full-featured board | 85×56×20 mm | Released Jun 2022; RDK X3 v2.0 in Jul 2023 |
| RDK X3 Module | Core module | 55×40 mm | Released May 2023 |
| RDK X5 | Mainstream robot development board | 85×56×20 mm | Released Sep 2024 |
| RDK X5 Module | Core module | 55×40 mm | First official TROS support in Apr 2025 |
| RDK S100 / S100P | 80 / 128 TOPS heterogeneous robot development kits | 120×121×51 mm | RDK S100 in-stock sale in Jun 2025 |
| RDK S100 SIP | Highly integrated product form | 65×65×4.75 mm | RDK S100 family, Jun 2025 |
| RDK S600 | Embodied AI development kit | 140×123×78 mm | Released for sale in Jun 2026 |
| RDK S600 Module | 699-pin B2B core module | 120×83 mm | V1.0.x design documents published in Jun 2026 |

Release, sale, first official software support, and design-document availability are different date definitions. They should not be treated as the same launch milestone.

## 3. Four hardware families

### RDK X3 family: learning and lightweight vision

Shared capabilities: 4×Cortex-A53, 5 TOPS, 2/4GB LPDDR4, and H.264/H.265/MJPEG up to 4K@60.

| Item | RDK X3 | RDK X3 Module |
| --- | --- | --- |
| Product form | Full-featured board | 55×40 mm core module |
| Vision I/O | Current docs list 1×MIPI CSI | 1×4-lane + 2×2-lane MIPI CSI |
| USB | 1×USB3 Host, 2×USB2 Host, 1×Micro USB Device | Native 1×USB3; physical ports depend on carrier |
| Hardware role | Learning, basic vision, and rapid validation | Compact products and custom carriers |

### RDK X5 family: mainstream robot vision

Shared capabilities: 8×Cortex-A55, 10 TOPS, up to 8GB LPDDR4, and H.264/H.265 up to 4K@60.

| Item | RDK X5 | RDK X5 Module |
| --- | --- | --- |
| Product form | 85×56×20 mm robot development board | 55×40 mm core module |
| Camera | 2×22-pin, each with 2-lane MIPI CSI | 2×4-lane, configurable as 4×2-lane |
| ISP | Current board documentation does not list independent throughput | 4K@60 with HDR, 3DNR, WDR, and PDAF |
| Key I/O | 1×CAN FD, 4×USB3 Host, GbE + PoE | USB, CAN, and network connectors depend on carrier |
| Hardware role | Ready for cameras, networking, and common peripherals | Custom dimensions, connectors, and product carriers |

### RDK S100 / S100P family: perception and real-time control

RDK S100 provides 6×Cortex-A78AE @1.5GHz, 12GB LPDDR5, and 80 TOPS. RDK S100P provides 6×Cortex-A78AE @2.0GHz, 24GB LPDDR5, and 128 TOPS. Both integrate 4×Cortex-R52+ MCUs, 2×ISP, and media capability up to 4K@90.

| Item | RDK S100 / S100P | RDK S100 SIP |
| --- | --- | --- |
| Product form | 120×121×51 mm heterogeneous development kit | 65×65×4.75 mm highly integrated compute unit |
| Model difference | S100: 1.5GHz, 12GB, 80 TOPS; S100P: 2.0GHz, 24GB, 128 TOPS | Product-oriented SIP form; not the S100P development-kit model |
| Vision | 3×4-lane MIPI signals and 2×ISP | Shares platform vision capability; refer to SIP pinout |
| Key I/O | 4×USB3 Host, 1×USB2 Device, 2×GbE | MIPI, USB, CAN, and MCU I/O depend on pinout and carrier |
| MCU expansion | 5×CAN FD plus I2C/SPI/UART/PWM/GPIO | Shares platform MCU capability; exposed I/O depends on design docs |
| Hardware role | Multi-camera perception and real-time control validation | Highly integrated robot product design |

### RDK S600 family: embodied AI and edge large models

Shared capabilities: 18×Cortex-A78AE, 560 TOPS, 6×Cortex-R52+ MCU, 32/64GB LPDDR5, 4×ISP, and aggregate H.264/H.265 throughput of 4K@240.

| Item | RDK S600 | RDK S600 Module |
| --- | --- | --- |
| Product form | 140×123×78 mm embodied-AI development kit | 120×83 mm, 699-pin B2B core module |
| Vision | Multi-camera MIPI and 4×ISP | 6×4-lane MIPI RX and 4×ISP |
| CAN and MCU | 4×main-domain CAN + 5×MCU CAN, plus MCU expansion | 4×main CAN; MCU domain provides CAN FD, LIN, PWM, ADC, and more |
| USB and network | 6×USB3 Host; 2×1GbE + 2×10GbE | Public native item: 1×USB2; network resources and ports depend on carrier |
| Hardware role | Embodied-AI system and advanced-algorithm validation | High-performance robot product integration |

## 4. Boards, development kits, Module, and SIP

- **Board or development kit:** USB-A, RJ45, CAN terminals, and camera connectors are already implemented for direct peripheral connection.
- **Module:** integrates the SoC, memory, storage, and key power circuits, then exposes native resources through board-to-board connectors. Final ports depend on the carrier.
- **SIP:** provides a higher level of integration. Product design must account for package, pinout, power, thermal, and reliability requirements.

Products in the same family may share a compute platform, but physical ports on a board must not be described as native Module or SIP I/O. Conversely, the maximum native resources of a Module or SIP do not mean a carrier can expose every resource at the same time.

## 5. Summary

1. RDK X3, RDK X5, RDK S100, and RDK S600 form four compute tiers.
2. Each family combines compute, vision, media, and connectivity.
3. RDK S100/S100P provide 80/128 TOPS; the RDK S100 and RDK S600 families add a dedicated real-time MCU domain.
4. Boards and kits simplify development and validation; Module and SIP forms enable compact product integration.

## References

- [D-Robotics Developer Documentation](https://developer.d-robotics.cc/en)
- [D-Robotics](https://d-robotics.cc/)
- [RDK X release notes](https://developer.d-robotics.cc/rdk_x_doc/en/Release_Note/release_note)
- [RDK S downloads](https://developer.d-robotics.cc/rdk_s_doc/en/Quick_start/download?p=RDK+S100&v=4.0.5)
Content updated in August 2026. For production design, refer to the current datasheet, pin list, hardware design guide, and official documentation.
