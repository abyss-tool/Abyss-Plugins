#!/usr/bin/env python3
"""插件中心索引门禁：plugins.json 的完整性 / 唯一性 / 约定校验。

N-SEC-001（M1 起）：plugins.json 必须带 detached 签名（.minisig）且可被
内置公钥验过 —— 公钥唯一事实源 = 主仓 ChannelSignatureVerifier.kt
TRUSTED_KEYS（此处常量与其同步；轮换走双公钥：新增不替换）。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minisign_py

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

# ── N-SEC-001：plugins.json detached 签名断言（存在 + 可验，fail-closed）
TRUSTED_PUBKEYS = [
    """
    untrusted comment: Abyss-Tools dev signing public key (M1, v0.10)
    RWSWn6+V/umBvAHNeSekC6UjX5Tg0me06vgXgEPeJ88ulrP82fR94AYZ
    """,
]
_index = Path("plugins.json")
_sig = Path("plugins.json.minisig")
if not _sig.exists():
    fail("plugins.json.minisig 缺失 —— N-SEC-001 起索引签名强制（sync_index.py 原子产出）")
else:
    _raw = _index.read_bytes()
    _sig_text = _sig.read_text(encoding="utf-8")
    if not any(minisign_py.verify(pk, _sig_text, _raw) for pk in TRUSTED_PUBKEYS):
        fail("plugins.json.minisig 验签失败 —— 索引字节与签名不配对（公钥不匹配或索引被改）")
    else:
        print("[hub-ci] ✓ plugins.json detached 签名验签通过")

plugins = data.get("plugins", [])
if len(plugins) < 3:
    fail(f"插件中心至少登记 3 个引擎级插件（当前 {len(plugins)}）—— v0.8.0 大内置化后的体量红线（六重型插件已并入主壳，只保留构建 / 病毒 / 虚拟机三个引擎级插件）")

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
