#!/usr/bin/env python3
"""插件中心索引门禁：plugins.json 的完整性 / 唯一性 / 约定校验。"""
import json
import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REPO = re.compile(r"^abyss-tool/abyss-plugin-[a-z0-9]+(-[a-z0-9]+)*$")
CHANNEL = re.compile(
    r"^https://raw\.githubusercontent\.com/abyss-tool/abyss-plugin-[a-z0-9-]+/main/patches/index\.json$"
)
REQUIRED = ("id", "name", "repo", "category", "version", "minApp", "summary")
CATEGORIES = {"terminal", "system", "sandbox", "disguise", "media",
              "automation", "desktop", "network", "data", "tools", "dev"}

errors = []


def fail(msg):
    errors.append(msg)


data = json.loads(Path("plugins.json").read_text(encoding="utf-8"))
if data.get("schema") != "abyss-plugin-index-v1":
    fail("plugins.json.schema 应为 abyss-plugin-index-v1")
plugins = data.get("plugins", [])
if len(plugins) < 7:
    fail(f"插件中心至少登记 7 个大插件（当前 {len(plugins)}）—— v0.3 伪装四件套内置化后的体量红线（小功能内置主壳，只有重型能力独立成仓）")

ids = set()
for p in plugins:
    where = f"plugins.json[{p.get('id')}]"
    for field in REQUIRED:
        if not p.get(field):
            fail(f"{where}: 缺少必填字段 {field}")
    pid = p.get("id", "")
    if pid in ids:
        fail(f"{where}: id 重复")
    ids.add(pid)
    if not REPO.match(p.get("repo", "")):
        fail(f"{where}: repo 形态非法 → {p.get('repo')!r}")
    if not p.get("repo", "").endswith(pid):
        fail(f"{where}: repo 末段应等于插件 id")
    if p.get("category") not in CATEGORIES:
        fail(f"{where}: category 非法 → {p.get('category')!r}")
    for key in ("version", "minApp"):
        if not SEMVER.match(p.get(key, "")):
            fail(f"{where}: {key} 非法 SemVer → {p.get(key)!r}")
    if not CHANNEL.match(p.get("patchChannel", "")):
        fail(f"{where}: patchChannel 形态非法 → {p.get('patchChannel')!r}")
    if p.get("apk") is not None and not p["apk"].get("url"):
        fail(f"{where}: apk.url 缺失")
    shizuku = p.get("shizuku")
    if shizuku is not None:
        if not isinstance(shizuku, dict):
            fail(f"{where}: shizuku 应为对象（ownAuth + reason）")
        elif shizuku.get("ownAuth") is not True:
            fail(f"{where}: shizuku.ownAuth 声明即独立授权，必须为 true")
        elif not shizuku.get("reason"):
            fail(f"{where}: shizuku.reason 缺失 —— 需向用户解释单独授权原因")

if errors:
    print(f"[hub-ci] ✗ {len(errors)} 处校验失败：", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"[hub-ci] ✓ 插件索引校验通过（{len(plugins)} 个大插件）")
