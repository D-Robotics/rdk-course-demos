# 为 RDK X5 烧录系统镜像

本讲介绍 RDK X5 的系统烧录流程。请使用明确支持 RDK X5 的镜像，并按照该软件版本对应的烧录说明操作。

## 烧录前的准备

1. 确认开发板是 RDK X5，并记录硬件版本。
2. 下载明确支持 RDK X5 的系统镜像。
3. 阅读当前镜像版本对应的 RDK X5 烧录说明。
4. 准备一根可靠的数据线和符合要求的电源适配器。
5. 安装烧录工具需要的主机驱动或命令行依赖。

## 烧录完成以后

重新给 X5 上电并观察指示灯。写入成功只能说明镜像已经保存到存储设备，开发板仍有可能在第一次启动时遇到问题。

如果 X5 没有显示输出或无法连接网络，先不要重复烧录。打开 [RDK X5 启动问题排查](05-boot-troubleshooting-x5.md)，先保存早期启动日志。

!!! note
    烧录工具、镜像布局和设备模式可能随版本变化。按键顺序和工具参数请以当前版本的 RDK X5 官方文档为准。

## 相关资料

- [课程代码与素材](https://github.com/D-Robotics/rdk-course-demos/tree/main/01_beginner/04_flash_system)
- [RDK X5 官方文档](https://developer.d-robotics.cc/rdk_doc/Quick_start/)
