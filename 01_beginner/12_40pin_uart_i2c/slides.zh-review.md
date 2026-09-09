# 视觉走查报告：slides.zh.html

生成时间：2026-09-09

输入：`blueprint.zh.json`

输出：`slides.zh.html`
文件大小：60.6 KB

## 文件与结构

- [pass] 文件存在且非空
- [pass] 文件大小处于 20–100 KB 范围
- [pass] UTF-8，无 BOM
- [pass] `<!doctype html>` 与 `</html>` 各出现一次
- [pass] `<title>` 有值
- [pass] HTML 含 10 张 slide，与 blueprint 的 10 张一致
- [pass] 封面使用 h1，其余 9 页使用 h2

## 视觉规范

- [pass] Logo 以 base64 内嵌一次
- [pass] `assets/` 外部引用为 0
- [pass] `ease-out-expo` 出现 9 次
- [pass] 包含 `text-wrap: balance`
- [pass] 包含 `prefers-reduced-motion`
- [pass] 包含 SF Pro 字体栈
- [pass] 所有标题不超过中文模板建议长度

## 反模式

- [pass] emoji 残留为 0
- [pass] Rockwell 字体残留为 0
- [pass] 模板占位文案残留为 0
- [pass] 未定义的 `next-card` 类残留为 0

## 内容顺序

- [pass] 开场与课程目标
- [pass] UART 原理与管脚
- [pass] UART 回环演示
- [pass] I2C 原理与 OLED 接线
- [pass] I2C 地址扫描与 OLED 点亮
- [pass] 排障、总结和下一课预告

## 人工浏览器检查

- [manual] 本地 `file://` 页面被浏览器自动化安全策略拦截，未绕过该限制
- [ ] 在 1920×1080 浏览器窗口中检查所有标题是否完整显示
- [ ] 使用左右方向键、Space、Home、End 测试翻页
- [ ] 检查卡片配色、SVG 图标和错峰动画

自动检查结果：通过。HTML 可以打开预览，发布前建议完成上述三项人工检查。
