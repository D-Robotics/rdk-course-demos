# RDK S100 启动问题排查

**目标** 找到 RDK S100 烧录后停在启动流程的哪个位置，并保存可供分析的调试日志。  
**预计用时** 5 分钟

镜像烧录成功不代表 S100 一定能够正常启动。先检查启动模式，再保存 Main 域的 Debug 输出，随后决定是否需要更换镜像。

## 检查启动模式

红色 `DOWNLOAD` 指示灯持续亮起，说明开发板仍处于 DFU 烧录模式。把 `SW2` 拨回正常启动位置，然后重新上电。如果 `DOWNLOAD` 已经熄灭，但橙色 `SYSTEM` 指示灯没有正常闪烁，再连接 Debug 串口。

## 连接 S100 Debug 串口

RDK S100 使用 USB Type-C `J16` 接口。J16 同时提供烧录、Main 域 Debug 和 MCU 域 Debug 通道。查看 Linux 启动输出时，需要选择 Main 域通道。

| 设置 | 参数 |
| --- | --- |
| 物理接口 | USB Type-C，J16 |
| Debug 通道 | Main 域 |
| 波特率 | 921600 |
| 数据格式 | 8 个数据位，1 个停止位，无校验 |
| 流控 | 关闭 |

1. 确认 `SW2` 位于正常启动位置，`DOWNLOAD` 指示灯已经熄灭。
2. 使用支持数据传输的 Type-C 线，把 `J16` 连接到主机。
3. 查看 J16 提供的串口设备，并选择 Main 域 Debug 通道。
4. 使用 `921600`、`8-N-1` 和关闭流控的参数打开串口。
5. 先开启终端日志保存，再给 S100 上电或按下复位键。

J16 会提供 Main 域和 MCU 域 Debug 通道，因此主机上出现多个串口设备是正常现象。如果没有出现串口设备，检查数据线以及 CH341 或 CH340 驱动。

## 根据日志判断位置

- **`DOWNLOAD` 持续亮起** 调整 `SW2` 位置并重新启动。
- **完全没有输出** 确认选择的是 Main 域通道，波特率为 `921600`。
- **早期启动停止** 检查 `SW2`、启动介质、烧录结果和第一条明确错误。
- **内核或文件系统报错** 保存第一条错误及其前后内容。
- **出现登录提示** S100 已经启动，继续检查显示、网络或应用程序。

## 提交排查信息

请提供硬件版本、镜像版本、烧录结果、供电方式、指示灯状态、J16 通道、串口参数、完整文本日志和复现步骤。

## 相关资料

- [课程代码与素材](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/05_boot_troubleshooting)
- [RDK S100 硬件文档](https://developer.d-robotics.cc/rdk_doc/rdk_s/Quick_start/hardware_introduction/rdk_s100/)
- [RDK 常见问题](https://developer.d-robotics.cc/rdk_doc/FAQ)
