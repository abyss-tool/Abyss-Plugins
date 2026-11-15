<div align="center">

# 🧩 Abyss-Plugins —— 深渊工具插件中心

### 三个引擎级插件的聚合索引 · 小功能内置主壳 · 引擎级能力插件化 · 独立 CI / 独立补丁通道

[![Hub CI](https://github.com/abyss-tool/Abyss-Plugins/actions/workflows/hub-ci.yml/badge.svg?branch=main)](https://github.com/abyss-tool/Abyss-Plugins/actions/workflows/hub-ci.yml)

</div>

---

## 这是什么

深渊工具（[abyss-tool/Abyss-Tools](https://github.com/abyss-tool/Abyss-Tools)）的插件生态中枢：
本仓库的 [`plugins.json`](plugins.json) 是 App「插件中心」页的**唯一数据源** ——
App 拉取该索引渲染插件列表；每个插件是独立仓库（独立 CI 门禁 + 独立补丁通道
`patches/index.json`）。

> **v0.8.0 承载形态定界：小功能内置，引擎级能力插件化。** v0.2 七个轻量
> 工具、v0.3 伪装四件套、**v0.8.0 六个重型插件（终端 / Python / 沙箱 /
> 媒体 / 网络 / 备份）**相继并入主壳 `ToolStatus.BUILT_IN`，对应仓库全部
> 归档。插件生态收缩为「自带完整引擎」的三个代表 —— 应用构建器（构建
> 底座）/ 病毒拦截（特征引擎）/ 虚拟机（QEMU）。框架预览期：APK 资产
> 自各自发布流水线起发布。

## 插件矩阵（三个引擎级插件）

| | 插件 | ID | 分类 | 说明 |
| --- | --- | --- | --- | --- |
| 🏗 | [应用构建器](https://github.com/abyss-tool/abyss-plugin-app-builder) | `abyss-plugin-app-builder` | 开发与构建 | 旗舰：Alpine+PRoot 三路径 APK 构建 · **Shizuku 独立授权** |
| 🦠 | [病毒拦截](https://github.com/abyss-tool/abyss-plugin-virus-guard) | `abyss-plugin-virus-guard` | 系统 | 🆕 v0.8.0：安装事件拦截 + ClamAV 级特征引擎 + VirusTotal 云查询 · **Shizuku 独立授权** |
| 🖳 | [虚拟机](https://github.com/abyss-tool/abyss-plugin-virtual-machine) | `abyss-plugin-virtual-machine` | 沙箱 | 🆕 v0.8.0：QEMU 级完整虚拟机（ARM/x86 镜像 + VNC）· **Shizuku 独立授权** |

> **已内置化（归档）**：`abyss-plugin-app-manager` / `abyss-plugin-shizuku-kit` /
> `abyss-plugin-automation` / `abyss-plugin-island` / `abyss-plugin-wallpaper` /
> `abyss-plugin-qr-craft`（v0.2）+ `abyss-plugin-disguise`（v0.3：伪装四件套）+
> **`abyss-plugin-terminal` / `abyss-plugin-python-lab` / `abyss-plugin-sandbox` /
> `abyss-plugin-media-lab` / `abyss-plugin-network-guard` / `abyss-plugin-backup`
> （v0.8.0 大内置化 —— 终端 / 脚本实验室 / 隔离空间 / 媒体实验室 /
> 流量审计 / 备份迁移，见主仓库 v0.8.1 发布说明）。

## 索引 schema（abyss-plugin-index-v1）

每个条目：`id / name / repo / category / version / minApp / summary / icon /
permissions / shizuku（可选，独立授权声明）/ apk / patchChannel / roadmap`。完整契约见开发仓
[docs/PLUGIN_SDK.md](https://github.com/abyss-tool/Abyss-Tools/blob/main/docs/PLUGIN_SDK.md)。

## 纪律

- 插件仓库先改先验（各自 CI），再同步本索引 —— 索引与仓库零漂移；
- `tools/validate_hub.py` 在 CI 中校验：至少 3 个引擎级插件 / id 唯一 / repo 形态 /
  SemVer / 补丁通道 URL 约定 / shizuku 声明形状（声明即 ownAuth=true +
  reason 必填）；
- 新插件接入流程见 [docs/ADDING_PLUGINS.md](docs/ADDING_PLUGINS.md)。

## 许可

受限许可（UGRL v1.0）—— 见 [LICENSE](LICENSE)。
