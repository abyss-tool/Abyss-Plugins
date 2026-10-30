# 新插件接入流程

1. **建仓**：`Ultra-Guru/abyss-plugin-<name>`（kebab-case，id = 仓库名）；
2. **骨架**：复制任一现有插件仓（plugin.json / CHANGELOG.md / ROADMAP.md /
   patches/index.json / tools/validate_plugin.py / .github/workflows/plugin-ci.yml / LICENSE）；
3. **填写 manifest**：分类 ∈ {terminal, system, sandbox, disguise, media,
   automation, desktop, network, data, tools}；version/minApp 为合法 SemVer；
4. **过 CI**：插件仓 Plugin CI 全绿（清单 / 补丁通道 / changelog 三处一致）；
5. **入索引**：在本仓库 plugins.json 追加条目（字段与插件仓 plugin.json 零漂移），
   Hub CI 校验通过后合并；
6. **客户端**：App 插件中心即自动可见（无需发版 —— 索引是运行时拉取的）。
