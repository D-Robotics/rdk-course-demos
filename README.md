# RDK Classroom

RDK Classroom 是面向海外开发者的 D-Robotics RDK 教程与实践平台。

教程网站使用 MkDocs Material 构建，发布在 GitHub Pages。教程正文统一维护在 `docs/` 下的 Markdown 文件中，代码示例维护在本仓库的课程目录中。

每次向 `develop` 分支推送 Markdown 或示例代码后，GitHub Actions 会自动构建并部署文档站。

文档站：<https://d-robotics.github.io/rdk-course-demos/>

本仓库不作为 RDK 官方手册或完整样例库使用。板卡能力、系统版本、接口说明和软件栈差异，请以 RDK 官方文档为准。

## 课程资源

- 讲解视频：课程主体，用于讲解概念、操作流程和实验演示
- GitHub Pages 教程：课程正文，用于整理步骤、命令、截图和参考链接
- 本仓库代码：课程中实际演示或引用到的代码
- 官方文档：板卡能力、系统接口和软件栈说明以官方文档为准

## 目录结构

```text
rdk-course-demos/
├── 01_beginner/            # 入门篇：RDK 的基础使用（共 14 课）
│   ├── 00_course_overview/       # 整个 RDK 小课堂的课程介绍与中英文页面源文件
│   ├── 01_community_ecosystem/   # 第 1 课：社区与生态入门
│   ├── 02_product_intro/         # 第 2 课：RDK 产品简介
│   ├── 03_rdk_studio/            # 第 3 课：RDK Studio 介绍
│   ├── 04_flash_system/          # 第 4 课：烧录说明
│   ├── 05_boot_troubleshooting/  # 第 5 课：启动说明与问题排查
│   ├── 06_remote_connection/     # 第 6 课：远程连接
│   ├── 07_camera/                # 第 7 课：Camera 使用
│   ├── 08_audio/                 # 第 8 课：音频使用
│   ├── 09_display/               # 第 9 课：显示模块使用
│   ├── 10_codec/                 # 第 10 课：编解码使用
│   ├── 11_40pin_gpio_pwm/        # 第 11 课：40pin 使用（1）
│   ├── 12_40pin_uart_i2c/        # 第 12 课：40pin 使用（2）
│   ├── 13_40pin_spi/             # 第 13 课：SPI 驱动屏幕（含点亮与动画 Demo）
│   └── 14_can/                   # 第 14 课：CAN 口使用
├── 02_modelzoo/            # 进阶篇：ModelZoo 开发指南
└── 03_tros/                # 进阶篇：TROS 开发指南
```

课程讲义维护在 `docs/`，可独立打开的中英文 HTML 页面和 Blueprint 保存在对应课程目录。没有配套代码的课程目录可以暂时保留为空目录占位。

## 使用方式

```bash
git clone https://github.com/D-Robotics/rdk-course-demos.git
cd rdk-course-demos
```

进入对应课程目录，根据 GitHub Pages 教程和课程视频运行配套代码。

## 维护原则

1. 本仓库只存放课程中实际用到的代码。
2. 每个目录对应一节课程或一个课程篇章。
3. 没有配套代码的课程不强行补充示例。
4. 代码以教学演示为主，不替代官方文档。
5. 板卡能力、接口说明和系统差异以 RDK 官方文档为准。
6. 每篇 Markdown 教程应给出对应代码目录和官方文档链接。
