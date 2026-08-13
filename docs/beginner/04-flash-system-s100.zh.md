# 为 RDK S100 烧录系统镜像

本讲介绍 RDK S100 的系统烧录流程。请使用明确支持 RDK S100 的镜像，并按照该软件版本对应的烧录说明操作。

## 烧录前的准备

1. 确认开发板是 RDK S100，并记录硬件版本。
2. 下载明确支持 RDK S100 的系统镜像。
3. 阅读当前版本的 RDK S100 烧录说明，确认 `SW2` 应当拨到哪个位置。
4. 准备一根支持数据传输的 USB Type-C 线和符合要求的电源适配器。
5. 安装烧录工具需要的主机驱动或命令行依赖。

## 烧录完成以后

重新上电之前，把 `SW2` 拨回正常启动位置。红色 `DOWNLOAD` 指示灯持续亮起时，S100 仍处于 DFU 烧录模式，Linux 不会正常启动。

如果 `DOWNLOAD` 已经熄灭，但系统仍未正常启动，打开 [RDK S100 启动问题排查](05-boot-troubleshooting-s100.md)，先保存 Main 域启动日志，再决定是否重新烧录。

!!! note
    烧录工具、镜像布局和开关行为可能随版本变化。完整步骤请以当前版本的 RDK S100 官方文档为准。

## 相关资料

- [课程代码与素材](https://github.com/D-Robotics/rdk-course-demos/tree/develop/01_beginner/04_flash_system)
- [RDK S100 官方文档](https://developer.d-robotics.cc/rdk_doc/rdk_s/Quick_start/)
