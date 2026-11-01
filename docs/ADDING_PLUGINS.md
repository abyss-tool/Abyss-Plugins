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
> **准入门槛**：新插件必须是「重」能力（原生工具链 / 独立进程 / 大型
> 框架）—— 轻量功能直接实现进主壳（ToolStatus.BUILT_IN），不建插件仓。
