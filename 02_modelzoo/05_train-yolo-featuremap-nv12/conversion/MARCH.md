# 2-05 march 锁定（公开）

本课 conversion YAML 锁定：

| 板 | `march` | 依据（公开） |
|----|---------|--------------|
| X5 | `bayes-e` | Model Zoo `ultralytics_yolo` workflow / `config_x5` |
| S100 | `nash-e` | Model Zoo README_cn「S100 → nash-e」；`workflow.s_toolchain` 默认。公开 OE 检查页写明 S100 使用 `nash-e`：https://developer.d-robotics.cc/oe_s_doc/en/guide/ptq/ptq_tool/hb_compile/check.html 。本仓库没有重跑 `hb_compile --help` |

本课不录 S100P（`nash-m`）/ S600（`nash-p`）。

示例镜像名（可按本机标签调整）：

- X5 OE：`local/rdk-x5-oe:v1.2.8-server`
- S OE：`registry.d-robotics.cc/deliver/ai_toolchain_ubuntu_22_s100_s600_gpu:v3.7.0`
