# 入门篇：RDK 基础使用

**适用板卡** RDK X5、RDK S100

**课程目标** 完成系统烧录、启动检查、远程连接和常用外设操作，为后续的模型部署与机器人应用做好准备。

基础入门课程从认识 RDK 开始。通用基础课程介绍社区资源、产品和 RDK Studio。进入系统操作以后，请按照手中的开发板选择 RDK X5 或 RDK S100 课程，并沿着对应路线继续学习。

点击课程名称阅读讲义；配套资料列提供代码或课件。尚未发布的讲义单独列在各板卡课程表下方。

## 先认识 RDK

第一次接触 RDK 时，先花一点时间熟悉资料入口、产品区别和开发工具。后面遇到系统或硬件问题时，你会知道去哪里查文档，也能确认当前操作是否适用于自己的开发板。

| 课程讲义 | 配套资料 |
| --- | --- |
| [RDK 小课堂课程结构与学习方式](https://d-robotics.github.io/rdk-course-demos/zh/course-overview/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/00_course_overview) |
| [RDK 社区与生态](https://d-robotics.github.io/rdk-course-demos/zh/beginner/common/community-ecosystem/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/01_community_ecosystem) |
| [RDK 硬件全家桶](https://d-robotics.github.io/rdk-course-demos/zh/beginner/common/product-intro/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/02_product_intro) |
| [RDK Studio 介绍](https://d-robotics.github.io/rdk-course-demos/zh/beginner/common/rdk-studio/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/03_rdk_studio) |

## RDK X5 课程

使用 RDK X5 的学员从系统烧录开始，随后检查启动状态、建立远程连接，再依次完成摄像头、音频、显示、编解码和 40-pin 外设实验。

| 课程讲义 | 配套资料 |
| --- | --- |
| [烧录系统镜像](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/flash-system/) | — |
| [启动问题排查](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/boot-troubleshooting/) | — |
| [音频外设入门](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/audio/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| [编解码](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/codec/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| [40-pin 接口 GPIO 与 PWM](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/40pin-gpio-pwm/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| [40-pin UART 与 I2C](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/40pin-uart/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| [40-pin 接口 SPI](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/spi-display/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| [CAN 使用](https://d-robotics.github.io/rdk-course-demos/zh/beginner/x5/can/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |


**待发布讲义：** 远程连接、Camera 使用、显示模块使用。
## RDK S100 课程

使用 RDK S100 的学员沿着相同的任务顺序学习，但烧录方式、调试接口和部分硬件操作以 S100 课程为准。

| 课程讲义 | 配套资料 |
| --- | --- |
| [烧录系统镜像](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/flash-system/) | — |
| [启动问题排查](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/boot-troubleshooting/) | — |
| [远程连接](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/remote-connection/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/06_remote_connection) |
| [音频外设入门](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/audio/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/08_audio) |
| [编解码与 RTSP](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/codec/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/10_codec) |
| [40-pin 接口 GPIO 与 PWM](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/40pin-gpio-pwm/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/11_40pin_gpio_pwm) |
| [40-pin 接口 UART 与 I2C](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/40pin-uart-i2c/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/12_40pin_uart_i2c) |
| [40-pin 接口 SPI](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/40pin-spi/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/13_40pin_spi) |
| [CAN 使用](https://d-robotics.github.io/rdk-course-demos/zh/beginner/s100/can/) | [GitHub 资料](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/14_can) |

**待发布讲义：** Camera 使用、显示模块使用。
