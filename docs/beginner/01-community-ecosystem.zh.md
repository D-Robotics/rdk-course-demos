# RDK 第一课：RDK 社区与生态入门

RDK 的资料不仅包括开发板手册，还包括源码仓库、模型示例、机器人开发文档、开发工具、应用案例和技术社区。

这一课不运行 Demo，也不讲具体硬件或算法。我们只完成一件事：建立一张清晰的 RDK 资源地图，让你遇到开发需求时，知道应该先去哪里找答案。

## 1. 本课要解决什么问题

刚开始使用 RDK 时，常见困难不是不会输入命令，而是不知道该从哪个入口开始：

- 想查看开发板接口、系统配置或快速入门步骤，应该看哪份手册？
- 想找示例源码或 BPU 模型，应该去 GitHub 还是 Model Zoo？
- 想开发机器人应用，TROS 手册和源码分别在哪里？
- 遇到问题需要反馈时，应该准备哪些信息？

本课围绕这四个问题，带你走完“找手册、找源码和模型、找 TROS、找反馈入口”的最短路径。

## 2. 完成本课后你能做到什么

完成本课后，你将能够：

1. 根据板卡系列找到 RDK X 系列或 RDK S 系列用户手册，并以 RDK X5 为例找到视频编解码 API 接口；
2. 在 D-Robotics GitHub 和 RDK Model Zoo 中识别官方仓库、选择对应板卡分支，并在操作前找到目标目录的 README；
3. 找到 TogetheROS.Bot（TROS）的官方手册和源码入口，理解两者的分工；
4. 找到论坛及发帖入口，并整理一份信息完整、便于复现的问题描述。

### 2.1 先认识八个关键词

在进入具体网站前，先建立下面八个概念。这里只要求理解它们各自负责什么，不需要记住实现细节。

| 关键词 | 含义 |
|---|---|
| RDK | Robotics Development Kit，面向机器人与智能应用开发的平台。 |
| BPU | Brain Processing Unit，RDK 板端的 AI 推理加速单元。 |
| RDK OS | 面向 RDK 板卡的 Linux 系统镜像，包含平台驱动与运行环境。 |
| miniboot | RDK 引导程序；排查启动和部分底层问题时需要关注其版本。 |
| TROS | TogetheROS.Bot，与 ROS 2 接口兼容的机器人应用平台。 |
| Model Zoo | 面向 RDK 与 BPU 的模型示例和工具集合。 |
| RDK Studio | 面向 RDK 设备的 AI 原生开发工作台。 |
| NodeHub | 用于了解已有方案和使用场景的应用案例补充入口。 |

## 3. 开始前准备

本课不要求连接开发板，只需要一台可以访问互联网的电脑和浏览器。

建议提前确认自己的板卡型号，例如 RDK X3、RDK X5、RDK S100 或 RDK S600。板卡系列会影响用户手册、Model Zoo 分支和示例代码的选择。

本课程的中英文讲义、页面原始内容与配套 Demo 均保存在 `rdk-course-demos` 仓库，并通过 GitHub Pages 发布：

- [中文课程讲义](https://d-robotics.github.io/rdk-course-demos/zh/)
- [英文课程讲义](https://d-robotics.github.io/rdk-course-demos/)
- [讲义与 Demo 源文件](https://github.com/D-Robotics/rdk-course-demos)

## 4. 先看资源地图

可以按照“要解决什么问题”来选择入口：

| 你的需求 | 优先入口 | 在这里找什么 |
|---|---|---|
| 查看板卡接口、系统安装、配置方法和常见问题 | RDK 资料中心与对应板卡用户手册 | 快速开始、系统配置、基础应用、FAQ |
| 查看开源项目和源码 | D-Robotics GitHub | 仓库、README、源文件、Issues |
| 查找 BPU 模型部署示例 | RDK Model Zoo | 板卡分支、模型目录、README |
| 开发 ROS 2 / TROS 机器人应用 | TROS 用户手册与 GitHub | 使用路径、功能包、源码、Issues |
| 进入面向 RDK 设备的开发工作台 | RDK Studio | 设备开发入口；第三课详细介绍 |
| 了解已有应用方案和使用场景 | NodeHub | 应用案例补充入口 |
| 提问、反馈问题或分享经验 | 地瓜机器人论坛 | 技术讨论、问题反馈、经验分享 |

记住一个简单原则：**先按板卡找手册，再按任务找源码或模型，最后带着完整信息去反馈问题。**

## 5. 任务一：按板卡找到官方手册

### 5.1 从资料中心选择板卡系列

打开 [RDK 资料中心](https://d-robotics.github.io/rdk_doc_center/)。在“RDK 用户手册”区域可以看到两个主要入口：

- **RDK X 系列用户手册**：面向 RDK X3、RDK X5、RDK X5 Module 等产品；
- **RDK S 系列用户手册**：面向 RDK S100、RDK S100P、RDK S600 等产品。

第一步不是搜索具体命令，而是先确认自己的板卡属于哪个系列，再进入对应手册。

### 5.2 以 RDK X5 查找编解码 API 接口

以 RDK X5 开发中查找视频编解码 API 为例，可以使用目录或搜索两种方式。

**通过目录查找：**

1. 在资料中心打开 **RDK X 系列用户手册**；
2. 确认页面当前产品为 **RDK X5**；
3. 在左侧目录进入 **3 基础应用开发 → 3.6 API 说明 → RDK X5 → Python 接口**；
4. 打开 **[Encoder 对象](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/multi_media_sp_dev_api/RDK_X3/pydev_multimedia_api_x3/object_encoder?v=3.5.0&p=RDK+X5)** 或 **[Decoder 对象](https://developer.d-robotics.cc/rdk_x_doc/Basic_Application/multi_media_sp_dev_api/RDK_X3/pydev_multimedia_api_x3/object_decoder?v=3.5.0&p=RDK+X5)**；
5. 在页面的 **API 参考** 中查看编码或解码相关接口。

**通过右上角搜索查找：**

1. 点击手册右上角的搜索框；
2. 输入 `Encoder`、`Decoder`、`编码`、`解码` 或具体接口名称；
3. 从搜索结果进入 **RDK X5 Python 接口**下的 Encoder 或 Decoder 对象页面；
4. 确认当前产品为 RDK X5，再查看 **API 参考**。

这次查找的重点不是记住某一个 API，而是掌握可重复的方法：

> 确认板卡系列和产品 → 进入 3.6 Python 接口或使用搜索 → 找到 Encoder / Decoder 对象 → 查看 API 参考

你可以用同样的方法继续查找系统烧录、远程登录、显示输出、网络配置或 40PIN 等主题。搜索结果较多时，先核对页面所属手册、板卡型号和章节位置，再使用其中的接口说明。

### 5.3 任务完成标准

如果你能做到下面两点，任务一就完成了：

- 能说明自己的板卡应该进入 RDK X 系列还是 RDK S 系列手册；
- 能通过目录或右上角搜索找到 RDK X5 Python 接口中的 Encoder 或 Decoder 对象及其 API 参考，并说明如何重复这条路径查找其他问题。

## 6. 任务二：找到源码和模型

### 6.1 D-Robotics GitHub 负责什么

[D-Robotics GitHub](https://github.com/D-Robotics) 是官方开源仓库入口。这里可以找到 RDK 文档源码、TROS 相关功能包、系统构建配置、模型示例和其他开源项目。

进入一个仓库后，先确认三件事：

1. 仓库名称和用途是否与当前任务一致；
2. 当前分支是否适合自己的板卡；
3. README 是否说明了依赖、目录结构和使用方法。

### 6.2 Model Zoo 负责什么

[RDK Model Zoo](https://github.com/D-Robotics/rdk_model_zoo) 是 D-Robotics 提供的 BPU 模型示例与工具集合，面向模型部署和智能应用开发。

Model Zoo 按硬件平台维护分支。进入仓库后，先根据板卡选择分支：

| 目标硬件 | 对应分支 | 示例入口 |
|---|---|---|
| RDK X5 | `rdk_x5` | `samples/vision/<sample>/README.md` |
| RDK X5 历史示例 | `rdk_x5_legacy` | 目标示例目录 README |
| RDK X3 | `rdk_x3` | `demos/<task>/<demo>/README.md` |
| RDK S 系列 | `rdk_s` | `samples/<domain>/<sample>/README.md` |

本课只需要掌握三步：

1. 打开官方仓库；
2. 选择与板卡对应的分支；
3. 进入目标示例目录，先阅读 README。

不要直接复制其他分支的命令。不同板卡分支的目录结构、系统要求和推理接口可能不同，目标目录的 README 才是当前示例的直接使用说明。

### 6.3 任务完成标准

如果你能在 Model Zoo 中选择自己的板卡分支，并找到一个目标目录的 README，任务二就完成了。本课不要求下载代码或运行模型。

## 7. 任务三：找到 TROS 手册与源码

TogetheROS.Bot，简称 TROS，是 D-Robotics 面向机器人应用开发提供的机器人操作系统，与 ROS 2 接口兼容，并针对 RDK 平台提供传感器接入、模型推理、图像处理、数据通信和可视化等能力。

TROS 的资料分为两个入口：

- [TROS 用户手册](https://developer.d-robotics.cc/tros_doc/tros)：用于了解概念、安装与使用路径、功能介绍和应用示例；
- [D-Robotics GitHub](https://github.com/D-Robotics)：用于查找具体功能包、源码、README 和 Issues。

需要查看具体功能包源码时，优先从 TROS 手册中的对应页面进入官方 GitHub 仓库，再阅读该仓库的 README 和 Issues。

任务三的判断方法很简单：

- 想先理解“是什么、怎么用”，看手册；
- 想查看“代码如何实现、有哪些问题”，看 GitHub 仓库、README 和 Issues。

本课不安装 TROS、不运行节点，也不展开功能包开发。

## 8. RDK Studio 与 NodeHub 补充入口

### 8.1 RDK Studio

[RDK Studio](https://d-robotics.github.io/rdk_studio_doc/) 是面向 RDK 设备的 AI 原生开发工作台，可以作为设备开发入口；第三课将专门介绍其使用方式。

### 8.2 NodeHub

[NodeHub](https://developer.d-robotics.cc/nodehub) 是应用案例的补充入口，可以用于了解已有方案和使用场景；本课不展开搜索和运行流程。

## 9. 遇到问题时如何反馈

### 9.1 选择反馈入口

常见反馈入口有两类：

- [地瓜机器人论坛](https://forum.d-robotics.cc/)：适合使用问题、环境问题、经验交流和案例分享；
- GitHub Issues：适合已经定位到具体开源仓库，并能确认问题与该仓库代码或文档直接相关的情况。

英文交流可以使用 [D-Robotics Forum](https://forum-en.d-robotics.cc/)。

### 9.2 论坛发帖入口

进入论坛后，先登录账号，再从论坛页面进入新建话题入口。选择与问题最接近的类别和标签即可。

本课只需要认识这个入口，不需要现场搜索、填写或发布帖子。

### 9.3 一个有效问题应包含什么

发帖前至少整理下面七项信息：

1. **板卡型号**：例如 RDK X5；
2. **系统或软件版本**：RDK OS、TROS、相关软件包或工具版本；
3. **复现步骤**：从什么状态开始，按什么顺序操作；
4. **预期结果**：你认为正常情况下应该出现什么；
5. **实际结果**：实际现象、错误信息或异常表现；
6. **关键日志**：尽量提供完整上下文，而不是只截最后一行；
7. **已做排查**：已经核对过哪些手册、版本、连接、配置或 Issues。

一个好标题应直接包含“板卡 + 任务 + 现象”，例如：

> RDK X5 调用视频编码接口时无法获取编码码流

这样的描述比“摄像头不能用，求助”更容易让其他开发者快速判断问题范围。

## 10. 如何判断本课完成

完成下面四项任务，说明你已经建立了 RDK 社区与生态的基础资源地图：

- [ ] 根据板卡系列进入正确用户手册，并找到一个具体主题；
- [ ] 在 Model Zoo 选择正确板卡分支，并找到目标目录 README；
- [ ] 分别找到 TROS 用户手册和源码入口；
- [ ] 找到论坛发帖入口，并能列出一个有效问题所需的七项信息。

## 11. 常见问题

### Q1：手册页面和我的板卡不一致怎么办？

先返回资料中心，重新确认 RDK X 系列或 RDK S 系列入口，再核对页面中的板卡型号。不要把其他系列或其他板卡的操作步骤直接套用到当前设备。

### Q2：Model Zoo 为什么不能直接使用默认页面里的命令？

Model Zoo 按板卡维护分支，不同分支的目录结构和接口可能不同。应先选择板卡分支，再阅读目标目录 README。

### Q3：TROS 手册和 GitHub 应该先看哪个？

第一次接触某项能力时先看手册，建立概念和使用路径；需要查看源码、修改功能或追踪问题时再进入 GitHub。

### Q4：NodeHub 和 Model Zoo 有什么区别？

NodeHub 是应用案例的补充入口，用于了解已有方案和使用场景；Model Zoo 聚焦 BPU 模型示例和模型部署流程。

### Q5：什么时候应该使用 GitHub Issues？

当问题已经明确对应某个官方开源仓库，并且你能够提供仓库、分支、版本、复现步骤和日志时，可以使用该仓库的 Issues。一般使用问题可以先在论坛反馈。

## 12. 本课小结

本课需要记住的不是一串网址，而是一套查找顺序：

1. **按板卡找手册**：先区分 RDK X 系列和 RDK S 系列；
2. **按任务找源码和模型**：GitHub 找开源项目，Model Zoo 找 BPU 模型示例；
3. **手册与源码配合使用**：TROS 手册讲使用路径，GitHub 提供功能包、源码和 Issues；
4. **补充入口适度使用**：RDK Studio 是设备开发入口，NodeHub 用于了解应用案例；
5. **带着完整信息反馈**：板卡、版本、步骤、预期、实际结果、日志和已做排查缺一不可。

下一课将介绍 **RDK 产品简介**，帮助你进一步理解不同 RDK 产品的定位和选择方式。

## 13. 拓展练习

1. 从资料中心进入自己板卡对应的用户手册，找到一个与你当前开发任务相关的主题；
2. 打开 Model Zoo，选择对应板卡分支，并记录一个示例目录及其 README 位置；
3. 打开 TROS 手册，再通过其中的源码链接找到一个 `hobot_*` 功能包；
4. 按附录模板，为一个假设问题写出标题和完整问题信息。

## 14. 附录

### 附录 A：问题信息模板

```text
标题：[板卡型号] + [任务] + [现象]

1. 板卡型号

2. 系统与软件版本

3. 参考的手册、仓库、分支或 README

4. 复现步骤

5. 预期结果

6. 实际结果

7. 关键日志或截图

8. 已做排查及结果
```

### 附录 B：核心资源速查

| 资源 | 地址 | 用途 |
|---|---|---|
| RDK 资料中心 | <https://d-robotics.github.io/rdk_doc_center/> | 进入各类官方手册 |
| RDK X 系列用户手册 | <https://developer.d-robotics.cc/rdk_x_doc/RDK> | X3、X5 等产品使用说明 |
| RDK S 系列用户手册 | <https://developer.d-robotics.cc/rdk_s_doc/RDK> | S100、S600 等产品使用说明 |
| D-Robotics GitHub | <https://github.com/D-Robotics> | 官方开源仓库入口 |
| RDK Model Zoo | <https://github.com/D-Robotics/rdk_model_zoo> | BPU 模型示例与工具 |
| TROS 用户手册 | <https://developer.d-robotics.cc/tros_doc/tros> | TROS 概念与使用路径 |
| RDK Studio | <https://d-robotics.github.io/rdk_studio_doc/> | 面向 RDK 设备的开发工作台 |
| NodeHub | <https://developer.d-robotics.cc/nodehub> | 应用案例补充入口 |
| 中文论坛 | <https://forum.d-robotics.cc/> | 中文技术交流与反馈 |
| 英文论坛 | <https://forum-en.d-robotics.cc/> | 英文技术交流与反馈 |
