<div align="center">

# 🧩 Abyss-Plugins —— 深渊工具插件中心

### 十三个大插件仓库的聚合索引 · 独立仓库 / 独立 CI / 独立补丁通道

[![Hub CI](https://github.com/Ultra-Guru/Abyss-Plugins/actions/workflows/hub-ci.yml/badge.svg?branch=main)](https://github.com/Ultra-Guru/Abyss-Plugins/actions/workflows/hub-ci.yml)

</div>

---

## 这是什么

深渊工具（[Ultra-Guru/Abyss-Tools](https://github.com/Ultra-Guru/Abyss-Tools)）的插件生态中枢：
本仓库的 [`plugins.json`](plugins.json) 是 App「插件中心」页的**唯一数据源** ——
App 拉取该索引渲染插件列表；每个插件是独立仓库（独立 CI 门禁 + 独立补丁通道
`patches/index.json`）。

> 框架预览期（v0.1.0）：13 个插件仓库已建立骨架（manifest / 补丁通道 / CI），
> APK 资产自 v0.2 发布流水线起发布。

## 插件矩阵（13 个大插件）

| | 插件 | ID | 分类 | 版本 | 最低宿主 |
| --- | --- | --- | --- | --- | --- |
| 🖥 | [终端引擎](https://github.com/Ultra-Guru/abyss-plugin-terminal) | `abyss-plugin-terminal` | 终端 | v0.1.0 | v0.1.0 |
| 🐍 | [Python 游乐场](https://github.com/Ultra-Guru/abyss-plugin-python-lab) | `abyss-plugin-python-lab` | 终端 | v0.1.0 | v0.1.0 |
| 🛡 | [Shizuku 工具箱](https://github.com/Ultra-Guru/abyss-plugin-shizuku-kit) | `abyss-plugin-shizuku-kit` | 系统 | v0.1.0 | v0.1.0 |
| 📦 | [应用管理器](https://github.com/Ultra-Guru/abyss-plugin-app-manager) | `abyss-plugin-app-manager` | 系统 | v0.1.0 | v0.1.0 |
| 🧊 | [沙箱双开](https://github.com/Ultra-Guru/abyss-plugin-sandbox) | `abyss-plugin-sandbox` | 沙箱 | v0.1.0 | v0.1.0 |
| 🎭 | [设备伪装](https://github.com/Ultra-Guru/abyss-plugin-disguise) | `abyss-plugin-disguise` | 伪装 | v0.1.0 | v0.1.0 |
| 🎬 | [媒体实验室](https://github.com/Ultra-Guru/abyss-plugin-media-lab) | `abyss-plugin-media-lab` | 媒体 | v0.1.0 | v0.1.0 |
| ⚡ | [自动化编排](https://github.com/Ultra-Guru/abyss-plugin-automation) | `abyss-plugin-automation` | 自动化 | v0.1.0 | v0.1.0 |
| 🌊 | [灵动岛与悬浮球](https://github.com/Ultra-Guru/abyss-plugin-island) | `abyss-plugin-island` | 桌面 | v0.1.0 | v0.1.0 |
| 🖼 | [动态壁纸引擎](https://github.com/Ultra-Guru/abyss-plugin-wallpaper) | `abyss-plugin-wallpaper` | 桌面 | v0.1.0 | v0.1.0 |
| 📡 | [网络守护](https://github.com/Ultra-Guru/abyss-plugin-network-guard) | `abyss-plugin-network-guard` | 网络 | v0.1.0 | v0.1.0 |
| 🔳 | [二维码工坊](https://github.com/Ultra-Guru/abyss-plugin-qr-craft) | `abyss-plugin-qr-craft` | 工具 | v0.1.0 | v0.1.0 |
| 💾 | [备份迁移](https://github.com/Ultra-Guru/abyss-plugin-backup) | `abyss-plugin-backup` | 数据 | v0.1.0 | v0.1.0 |

## 索引 schema（abyss-plugin-index-v1）

每个条目：`id / name / repo / category / version / minApp / summary / icon /
permissions / apk / patchChannel / roadmap`。完整契约见开发仓
[docs/PLUGIN_SDK.md](https://github.com/Ultra-Guru/Abyss-Tools/blob/main/docs/PLUGIN_SDK.md)。

## 纪律

- 插件仓库先改先验（各自 CI），再同步本索引 —— 索引与仓库零漂移；
- `tools/validate_hub.py` 在 CI 中校验：至少 10 个插件 / id 唯一 / repo 形态 /
  SemVer / 补丁通道 URL 约定；
- 新插件接入流程见 [docs/ADDING_PLUGINS.md](docs/ADDING_PLUGINS.md)。

## 许可

受限许可（UGRL v1.0）—— 见 [LICENSE](LICENSE)。
