# 新插件接入流程

1. **建仓**：`abyss-tool/abyss-plugin-<name>`（kebab-case，id = 仓库名）；
2. **骨架**：复制任一现有插件仓（plugin.json / CHANGELOG.md / ROADMAP.md /
   patches/index.json / tools/validate_plugin.py /
   tools/make_patch.py / tools/publish_patch.py /
   .github/workflows/plugin-ci.yml /
   .github/workflows/patch-release.yml / LICENSE）；
3. **填写 manifest**：分类 ∈ {terminal, system, sandbox, disguise, media,
   automation, desktop, network, data, tools, dev}；version/minApp 为合法
   SemVer；独立 APK 且需要 Shizuku 的插件必须声明
   `"shizuku": {"ownAuth": true, "reason": "…"}`（Shizuku 授权 per-app，
   不继承宿主 —— 客户端详情页会展示单独授权引导）；
4. **过 CI**：插件仓 Plugin CI 全绿（清单 / 补丁通道 / changelog 三处一致）；
5. **入索引**：在本仓库 `tools/sync_index.py` 的 `REPOS` 注册表登记新仓库名，
   运行 `python3 tools/sync_index.py`（或触发 Sync Index 工作流）——
   plugins.json 自动聚合生成，Hub CI 校验通过后合并；
6. **客户端**：App 插件中心即自动可见（无需发版 —— 索引是运行时拉取的）；
7. **后续发布**：插件仓 Actions → Patch Release 发布数据补丁，本仓
   Sync Index（每日 12:00 UTC / 手动）自动把新版本汇入索引；APK 资产
   上架 GitHub Release 后亦会被聚合器自动探测并填入 `apk` 字段。

> 索引聚合器（`sync-index.yml`）同时拉取各仓 plugin.json、补丁通道与
> Releases APK 资产 —— 单仓故障保留旧条目并告警，不阻塞生态滚动。
>
> **准入门槛（v0.8.0 收紧）**：新插件必须「自带完整引擎」（构建底座 /
> 病毒特征引擎 / 整机虚拟机级别）—— 其余能力一律直接实现进主壳
> （ToolStatus.BUILT_IN），不建插件仓。

## 带依赖的新插件（HOST_API v2 · hubVersion 0.4.0 起）

消费其它插件能力的插件（瘦客户端，如应用构建器）在 7 步之外追加：

8. **声明 depends**：`plugin.json` 的 `depends[]` 逐条写明
   `pluginId` / `capability` / `versionRange`（如 `>=0.2.0 <1.0.0`）/
   `optional: false` / `reason`（≥10 字符人话）；`minHost` 必须为 2
   （依赖解析与能力绑定需 v2 宿主）；
9. **不得声明 shizuku**：消费方不持有 Shizuku 授权 —— 引擎与授权都在
   被依赖插件内（当前唯一授权持有方 = abyss-plugin-linux）；
10. **不自带引擎**：仓库静态扫描 0 文件含底座实现关键字
    （`proot` / `rootfs` / `qemu` / `ptrace` / `ILinuxRuntime` /
    `rikka.shizuku`），运行环境经宿主 PluginBroker 中介获取受限
    `ILinuxSession` 代理（永不直连，ARC-102）。

Hub CI 会对以上 3 条逐项校验：depends 指向存在且未归档的 id、
capability 命中被依赖方 `provides[]`、声明 depends 的瘦客户端无
shizuku 声明（`validate_hub.py`）。

## 归档与承接（HUB-014 / ADR-100 D-4）

插件仓归档（如 2026-11-22 的 `abyss-plugin-virtual-machine`）：

1. 停止一切补丁发布（`patches/index.json` 保持现状不再滚动）；
2. 本仓 `sync_index.py` 的 `REPOS` 移除该仓 —— 索引条目随下轮聚合消失；
3. `validate_hub.py` 的 `ARCHIVED_IDS` 登记该 id —— 再次出现即红灯；
4. GitHub 仓库设置 `archived=true`（转只读）；
5. 发布归档公告（指明能力去向，如 `QEMU_VM 执行域 → abyss-plugin-linux`，
   规格承接 `LIN-002` / `DC-102`）。

归档能力不得复活为插件（SRS-004 FR-005）。
