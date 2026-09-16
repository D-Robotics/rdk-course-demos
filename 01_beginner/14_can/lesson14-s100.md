# RDK S100 第14课 CAN 通信

- 适用板卡：RDK S100
- 课程目标：通过机器人应用与板卡 CAN 回环建立两层可复现证据。

## 演示一：机器人应用

复用已部署的 USB-CAN、官方 SDK 和默认复位流程，记录可见动作。

## 演示二：板卡 CAN

S100 使用 MCU 扩展板完成 CAN6 到 CAN5 的 1 Mbps 物理回环，12 帧逐帧匹配。

## 验收边界

机器人动作、内部回环和物理回环分别按实际硬件范围表述，不把单项结果扩大为未测试能力。

## 官方资料

- 中文：https://developer.d-robotics.cc/rdk_s_doc/Advanced_development/mcu_development/mcu_can
- English: https://developer.d-robotics.cc/rdk_s_doc/en/Advanced_development/mcu_development/mcu_can
