<div align="center">

# 🧩 Abyss-Plugins —— 深渊工具插件中心

### 八个重型大插件的聚合索引 · 小功能内置主壳 · 大功能插件化 · 独立 CI / 独立补丁通道

[![Hub CI](https://github.com/abyss-tool/Abyss-Plugins/actions/workflows/hub-ci.yml/badge.svg?branch=main)](https://github.com/abyss-tool/Abyss-Plugins/actions/workflows/hub-ci.yml)

</div>

---

## 这是什么

深渊工具（[abyss-tool/Abyss-Tools](https://github.com/abyss-tool/Abyss-Tools)）的插件生态中枢：
本仓库的 [`plugins.json`](plugins.json) 是 App「插件中心」页的**唯一数据源** ——
App 拉取该索引渲染插件列表；每个插件是独立仓库（独立 CI 门禁 + 独立补丁通道
`patches/index.json`）。

> **v0.2 承载形态定界：小功能内置，大功能插件化。** 轻量工具（应用管理 /
> Shizuku 面板 / 任务蓝图 / 自动化 / 灵动岛 / 壁纸 / 二维码）已并入主壳
> `ToolStatus.BUILT_IN`，不再占据插件中心位次（原六仓已归档）；只有「重」的
> 能力（原生工具链 / 独立进程 / 大型框架）才独立成仓。框架预览期：APK 资产
> 自 v0.2 发布流水线起发布。

## 插件矩阵（八个大插件）

| | 插件 | ID | 分类 | 说明 |
| --- | --- | --- | --- | --- |
| 🏗 | [应用构建器](https://github.com/abyss-tool/abyss-plugin-app-builder) | `abyss-plugin-app-builder` | 开发与构建 | 🆕 旗舰：Alpine+PRoot 三路径 APK 构建 · **Shizuku 独立授权** |
| 🖥 | [终端引擎](https://github.com/abyss-tool/abyss-plugin-terminal) | `abyss-plugin-terminal` | 终端 | Termux 血统内置 Linux 终端 |
| 🐍 | [Python 游乐场](https://github.com/abyss-tool/abyss-plugin-python-lab) | `abyss-plugin-python-lab` | 终端 | Chaquopy 脚本引擎 |
| 🧊 | [沙箱双开](https://github.com/abyss-tool/abyss-plugin-sandbox) | `abyss-plugin-sandbox` | 沙箱 | VirtualApp 血统虚拟空间 |
| 🎭 | [设备伪装](https://github.com/abyss-tool/abyss-plugin-disguise) | `abyss-plugin-disguise` | 伪装 | 沙箱 Hook 层伪造数据 |
| 🎬 | [媒体实验室](https://github.com/abyss-tool/abyss-plugin-media-lab) | `abyss-plugin-media-lab` | 媒体 | FFmpeg 批量剪辑 |
| 📡 | [网络守护](https://github.com/abyss-tool/abyss-plugin-network-guard) | `abyss-plugin-network-guard` | 网络 | VpnService 流量审计 |
| 💾 | [备份迁移](https://github.com/abyss-tool/abyss-plugin-backup) | `abyss-plugin-backup` | 数据 | 应用数据备份与跨设备迁移 |

> **已内置化（归档）**：`abyss-plugin-app-manager` / `abyss-plugin-shizuku-kit` /
> `abyss-plugin-automation` / `abyss-plugin-island` / `abyss-plugin-wallpaper` /
> `abyss-plugin-qr-craft` —— 能力并入主壳内置路线，见主仓库 v0.2.0 发布说明。

## 索引 schema（abyss-plugin-index-v1）

每个条目：`id / name / repo / category / version / minApp / summary / icon /
permissions / shizuku（可选，独立授权声明）/ apk / patchChannel / roadmap`。完整契约见开发仓
[docs/PLUGIN_SDK.md](https://github.com/abyss-tool/Abyss-Tools/blob/main/docs/PLUGIN_SDK.md)。

## 纪律

- 插件仓库先改先验（各自 CI），再同步本索引 —— 索引与仓库零漂移；
- `tools/validate_hub.py` 在 CI 中校验：至少 8 个插件 / id 唯一 / repo 形态 /
  SemVer / 补丁通道 URL 约定 / shizuku 声明形状（声明即 ownAuth=true +
  reason 必填）；
- 新插件接入流程见 [docs/ADDING_PLUGINS.md](docs/ADDING_PLUGINS.md)。

## 许可

受限许可（UGRL v1.0）—— 见 [LICENSE](LICENSE)。
