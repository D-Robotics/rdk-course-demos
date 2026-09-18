# RDK S100 CAN 通信

本文根据已录制课程的配套课件整理，保留原课件的接线、命令、实测结果和验证范围。

[原始课件](https://github.com/D-Robotics/rdk-course-demos/blob/develop/01_beginner/14_can/lesson-14-s100-zh.html)

从机器人复位到 MCU 扩展板物理回环，验证完整 CAN 能力。

## 本课完成两条验证链路

机器人复位展示应用效果，MCU 扩展板回环证明 S100 的实体 CAN 收发路径。

### USB-CAN 应用

复用机器人 SDK 执行一次官方复位动作。

### MCU-CAN

通过扩展板连接 CAN6 发送端与 CAN5 接收端。

### 实测结果

12 次发送、12 次接收，ID 和 8 字节数据全部匹配。

## S100 的 CAN 经过 MCU 扩展链路

### Acore

Linux 用户态运行官方 CAN HAL 示例。

### MCU1

固件负责 IPC 与 CAN 通道转发。

### 扩展板

FPC 把主板与 MCU 接口扩展板连接。

### 收发器

CAN5 与 CAN6 提供实体差分总线接口。

## 从机器人应用到物理总线

**机器人**轻微偏离姿态

**USB-CAN**官方复位

**MCU1**running / alive

**CAN6→CAN5**三线物理闭环

**12/12**逐帧匹配

## S100 控制机器人完成复位

复用同一 robot\_py SDK、既有电机配置和默认姿态，不重新标定。

### 可见动作

腰部与多个关节从偏置姿态回到复位目标。

### 标准流程

init、读取、官方 reset、再次读取、deinit。

### 安全退出

SDK deinit 返回未初始化，四路 CAN 连接关闭。

## 机器人动作与扩展板测试各有边界

两段演示共同构成课程证据，但不混淆所用硬件。

- 复位动作证明 S100、USB-CAN、SDK 与执行器链路可工作
- 动作前后腰部反馈变化约 43.2 度
- 不把一次复位扩大为行走、舞蹈或全关节精度验收
- MCU 扩展板测试不连接机器人电机
- 实体 CAN 能力由 CAN6 到 CAN5 的物理回环单独证明

## MCU 扩展板 CAN 回环接线

CAN6 与 CAN5 之间连接 CAN\_H、CAN\_L 和 GND，并在两端接入 120Ω 终端电阻。

![RDK S100 MCU expansion board CAN wiring](../../assets/images/beginner/lesson-14-s100-381498824dc5.jpg)

CAN6 H/L/GND → CAN5 H/L/GND｜两端 120Ω｜1 Mbps

## 一帧数据如何穿过整条链路

**can\_send**Acore 示例

**IPC ch6**bypass 6

**CAN6**物理发送

**CAN5**物理接收

**IPC ch4**can\_get 输出

## 使用官方示例副本完成测试

原始 /app/Can 目录保持不变，代码、配置与日志都放在新项目隔离目录。

### 接收端

```text
sudo ./can_get
IPC instance 0 / channel 4
CAN5 RX
```

先启动接收，再发送帧。

### 发送端

```text
sudo ./can_send bypass 6
CAN6 TX @ 1 Mbps
```

发送 ID 0x131 的 8 字节经典 CAN 帧。

## 终端实时显示物理回环结果

录屏在同一次测试中展示 MCU 状态、发送帧、接收帧与最终 PASS。

### 发送

CAN6 连续发出 12 帧 ID 0x131。

### 接收

CAN5 返回完全相同的 8 字节载荷。

### 判定

12/12 全部匹配后输出 physical CAN PASS。

## S100 MCU-CAN 实测结果

### 方向

CAN6 TX → CAN5 RX

### 速率

1,000,000 bit/s

### 报文

ID 0x131 / 8 bytes

### 结果

12 发送 / 12 接收 / 全匹配

## 本次测试保留可复现状态

扩展板链路运行在隔离目录，原项目与系统服务不被改写。

- MCU1 使用 S100 4.0.5 官方 S100\_MCU\_DEBUG.elf
- 测试时 MCU1 为 running / alive
- 官方示例复制到 new\_project 后编译运行
- 测试结束无 canhal\_get 或 canhal\_send 残留进程
- SSH 保持启用，不修改网络或原项目目录

## 没有接收帧时这样排查

S100 的通道映射、终端匹配和方向都必须与当前固件一致。

Step 1

先确认 MCU1 为 running / alive，再检查官方固件版本。

Step 2

核对 CAN\_H 对 CAN\_H、CAN\_L 对 CAN\_L、GND 对 GND。

Step 3

确认两端各有 120Ω 终端，并使用 1 Mbps。

Step 4

当前固件实测方向为 CAN6 发送、CAN5 接收。

## RDK S100 CAN 验证完成

机器人应用与 MCU 扩展板物理回环共同说明 S100 的 CAN 开发能力。

### 应用可见

USB-CAN 驱动机器人完成官方复位。

### 链路完整

Acore、MCU、FPC、收发器和线缆均进入验证。

### 结果可复现

CAN6 到 CAN5 连续 12/12 帧匹配。
