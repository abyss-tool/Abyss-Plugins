#!/usr/bin/env python3
"""插件中心索引门禁：plugins.json 的完整性 / 唯一性 / 约定校验。

N-SEC-001（M1 起）：plugins.json 带 detached 签名（.minisig）时必须可被
内置公钥验过 —— 公钥唯一事实源 = 主仓 ChannelSignatureVerifier.kt
TRUSTED_KEYS（此处常量与其同步；轮换走双公钥：新增不替换）。签名缺失
= 首签落地前常态（sync_index.py 材料可用时幂等补签）→ 告警不阻断；
签名存在但验不过 → fail-closed（索引被改/公钥不匹配）。

hubVersion 0.4.0 增量（DC-100 §5 / SRS-102 FR-004 / ADR-100 D-4）：
  - 恰好 3 个活跃引擎级插件（虚拟机已收编归档，Linux 插件入位）；
  - depends 逐条校验：指向存在且未归档的 id、capability 必须命中被依赖
    方 provides[]、versionRange 合法区间形态、optional=false 时 reason 非空；
  - 瘦客户端（声明 depends 而无 provides）不得出现 shizuku 声明
    （授权收敛至 Linux 插件唯一持有方，APP-100 FR-001）；
  - provides / capabilities / assetChannel 形态校验；
  - 归档 id 一律拒收（含 abyss-plugin-virtual-machine）。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minisign_py

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REPO = re.compile(r"^abyss-tool/abyss-plugin-[a-z0-9]+(-[a-z0-9]+)*$")
CHANNEL = re.compile(
    r"^https://raw\.githubusercontent\.com/abyss-tool/abyss-plugin-[a-z0-9-]+/main/patches/index\.json$"
)
ASSET_CHANNEL = re.compile(
    r"^https://raw\.githubusercontent\.com/abyss-tool/abyss-plugin-[a-z0-9-]+/main/assets/index\.json$"
)
CAPABILITY_ID = re.compile(r"^[a-z0-9-]+-v[0-9]+$")
VERSION_RANGE = re.compile(r"^>=\d+\.\d+\.\d+(\s+<\d+\.\d+\.\d+)?$")
REQUIRED = ("id", "name", "repo", "category", "version", "minApp", "summary")
CATEGORIES = {"terminal", "system", "sandbox", "disguise", "media",
              "automation", "desktop", "network", "data", "tools", "dev"}
# 归档仓库（v0.8.0 大内置化 13 仓 + ADR-100 D-4 虚拟机收编）—— 不得再入位
ARCHIVED_IDS = {
    "abyss-plugin-terminal", "abyss-plugin-python-lab", "abyss-plugin-sandbox",
    "abyss-plugin-media-lab", "abyss-plugin-network-guard", "abyss-plugin-backup",
    "abyss-plugin-qr-craft", "abyss-plugin-island", "abyss-plugin-wallpaper",
    "abyss-plugin-shizuku-kit", "abyss-plugin-app-manager", "abyss-plugin-automation",
    "abyss-plugin-disguise", "abyss-plugin-virtual-machine",
}
ACTIVE_ENGINE_IDS = {
    "abyss-plugin-app-builder",   # 瘦客户端（构建编排）
    "abyss-plugin-virus-guard",   # 病毒特征引擎
    "abyss-plugin-linux",         # Linux 底座引擎（linux-runtime-v1 唯一提供方）
}

errors = []


def fail(msg):
    errors.append(msg)


# ── N-SEC-001：plugins.json detached 签名断言（存在必可验；缺失告警）──
TRUSTED_PUBKEYS = [
    """
    untrusted comment: Abyss-Tools manifest signing public key (meng4117222)
    RWRx16ORC4gsdxs6DsnctDYagiRptPX1NgFcVpQNYqh/BXGhPAHebh3B
    """,
]
_index = Path("plugins.json")
_sig = Path("plugins.json.minisig")
if _sig.exists():
    _raw = _index.read_bytes()
    _sig_text = _sig.read_text(encoding="utf-8")
    if not any(minisign_py.verify(pk, _sig_text, _raw) for pk in TRUSTED_PUBKEYS):
        fail("plugins.json.minisig 验签失败 —— 索引字节与签名不配对（公钥不匹配或索引被改）")
    else:
        print("[hub-ci] ✓ plugins.json detached 签名验签通过")
else:
    print("[hub-ci] ⚠ plugins.json.minisig 尚未产出 —— 首签落地前常态（sync_index.py "
          "在 RELEASE_SIGNING_KEY secret 配置后幂等补签；不阻断本轮门禁）")

data = json.loads(Path("plugins.json").read_text(encoding="utf-8"))
if data.get("schema") != "abyss-plugin-index-v1":
    fail("plugins.json.schema 应为 abyss-plugin-index-v1")
if data.get("hubVersion") != "0.4.0":
    fail(f"plugins.json.hubVersion 应为 0.4.0（v2 字段透传增量，DC-100 §4）→ {data.get('hubVersion')!r}")
plugins = data.get("plugins", [])
if len(plugins) != 3:
    fail(f"插件中心应恰好登记 3 个活跃引擎级插件（当前 {len(plugins)}）—— Linux 插件入位 / 虚拟机收编归档后的位次红线（SRS-102 FR-004）")

ids = set()
provides_map: dict[str, set[str]] = {}
for p in plugins:
    where = f"plugins.json[{p.get('id')}]"
    for field in REQUIRED:
        if not p.get(field):
            fail(f"{where}: 缺少必填字段 {field}")
    pid = p.get("id", "")
    if pid in ids:
        fail(f"{where}: id 重复")
    ids.add(pid)
    if pid in ARCHIVED_IDS:
        fail(f"{where}: 归档 id 不得再入位（HUB-014 / SRS-004 FR-005）")
    if pid not in ACTIVE_ENGINE_IDS:
        fail(f"{where}: 引擎级插件位次外的新条目需先过 SRS-102 承载形态评审 → {pid!r}")
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
    if p.get("apk") is not None:
        sha = p["apk"].get("sha256")
        if not isinstance(sha, str) or not re.match(r"^[0-9a-fA-F]{64}$", sha):
            fail(f"{where}: apk.sha256 缺失或非 64 位十六进制 → {sha!r}")
    shizuku = p.get("shizuku")
    if shizuku is not None:
        if not isinstance(shizuku, dict):
            fail(f"{where}: shizuku 应为对象（ownAuth + reason）")
        elif shizuku.get("ownAuth") is not True:
            fail(f"{where}: shizuku.ownAuth 声明即独立授权，必须为 true")
        elif not shizuku.get("reason") or len(shizuku.get("reason", "")) < 10:
            fail(f"{where}: shizuku.reason 缺失或过短 —— 需向用户解释单独授权原因")

    # ── v2 字段：minHost / provides / capabilities / assetChannel ────────
    min_host = p.get("minHost", 1)
    if not isinstance(min_host, int) or min_host < 1:
        fail(f"{where}: minHost 应为正整数 → {min_host!r}")
    provides = p.get("provides")
    if provides is not None:
        if not isinstance(provides, list) or not provides:
            fail(f"{where}: provides 应为非空数组")
        else:
            caps = set()
            for item in provides:
                if not isinstance(item, dict):
                    fail(f"{where}: provides 条目应为对象 → {item!r}")
                    continue
                cap = item.get("capability", "")
                if not CAPABILITY_ID.match(cap):
                    fail(f"{where}: provides.capability 形态非法 → {cap!r}")
                if cap in caps:
                    fail(f"{where}: provides.capability 重复 → {cap!r}")
                caps.add(cap)
                if item.get("since") is not None and not SEMVER.match(str(item.get("since"))):
                    fail(f"{where}: provides[{cap}].since 非法 SemVer → {item.get('since')!r}")
                if not isinstance(item.get("stable", True), bool):
                    fail(f"{where}: provides[{cap}].stable 应为布尔")
            provides_map[pid] = caps
    asset_channel = p.get("assetChannel")
    if asset_channel is not None and not ASSET_CHANNEL.match(asset_channel):
        fail(f"{where}: assetChannel 应为成员仓 assets/index.json 的 raw URL → {asset_channel!r}")
    capabilities = p.get("capabilities")
    if capabilities is not None and not isinstance(capabilities, dict):
        fail(f"{where}: capabilities 应为对象（能力 id → 描述）")
    if capabilities is not None and isinstance(capabilities, dict):
        for cap, desc in capabilities.items():
            if not CAPABILITY_ID.match(cap):
                fail(f"{where}: capabilities 键形态非法 → {cap!r}")
            if not isinstance(desc, dict):
                fail(f"{where}: capabilities[{cap}] 应为对象")
                continue
            if cap in provides_map.get(pid, set()):
                domains = desc.get("domains")
                if not isinstance(domains, list) or {"PROOT_USERLAND", "QEMU_VM"} - {d.get("id") for d in domains if isinstance(d, dict)}:
                    fail(f"{where}: capabilities[{cap}].domains 必须同时含 PROOT_USERLAND 与 QEMU_VM（A-1 双执行域假设）")
                auth = desc.get("auth")
                if not isinstance(auth, dict) or auth.get("mediator") != "PluginBroker":
                    fail(f"{where}: capabilities[{cap}].auth.mediator 必须为 PluginBroker（插件间永不直连）")
                ttl = auth.get("grantTtlSec") if isinstance(auth, dict) else None
                if not isinstance(ttl, int) or not (0 < ttl <= 300):
                    fail(f"{where}: capabilities[{cap}].auth.grantTtlSec 应 ≤300 → {ttl!r}")

# ── depends 逐条校验（依赖解析事实源，宿主运行时二次校验）────────────────
for p in plugins:
    where = f"plugins.json[{p.get('id')}]"
    depends = p.get("depends")
    if depends is None:
        continue
    if not isinstance(depends, list) or not depends:
        fail(f"{where}: depends 应为非空数组（或省略）")
        continue
    if p.get("provides"):
        fail(f"{where}: 提供方不得同时声明 depends（引擎角色单一化，当前无级联场景）")
    # 瘦客户端不得持有 Shizuku 授权（APP-100 FR-001 / LIN-005 FR-002）
    if p.get("shizuku") is not None:
        fail(f"{where}: 声明 depends 的瘦客户端不得出现 shizuku —— 授权收敛至 Linux 插件唯一持有方")
    for item in depends:
        if not isinstance(item, dict):
            fail(f"{where}: depends 条目应为对象 → {item!r}")
            continue
        dep_id = item.get("pluginId", "")
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)+$", dep_id):
            fail(f"{where}: depends[].pluginId 形态非法 → {dep_id!r}")
            continue
        if dep_id in ARCHIVED_IDS:
            fail(f"{where}: depends 指向归档 id → {dep_id}（索引 CI 直接拒收，DC-100 §3）")
        if dep_id not in ids:
            fail(f"{where}: depends 指向不存在的条目 → {dep_id}（E_DEP_MISSING）")
        cap = item.get("capability", "")
        if not CAPABILITY_ID.match(cap):
            fail(f"{where}: depends[{dep_id}].capability 形态非法 → {cap!r}")
        elif dep_id in provides_map and cap not in provides_map[dep_id]:
            fail(f"{where}: depends[{dep_id}].capability({cap}) 未命中被依赖方 provides → {sorted(provides_map[dep_id])}（E_CAPABILITY_MISMATCH）")
        vr = item.get("versionRange", "")
        if not VERSION_RANGE.match(vr):
            fail(f"{where}: depends[{dep_id}].versionRange 应为 SemVer 区间（如 >=0.2.0 <1.0.0）→ {vr!r}")
        if item.get("optional") is False and (not item.get("reason") or len(item.get("reason", "")) < 10):
            fail(f"{where}: depends[{dep_id}].optional=false 时 reason 必填且 ≥10 字符（DC-100 §3）")
        if item.get("optional") is True:
            fail(f"{where}: depends[{dep_id}].optional=true 仅为过渡期形态 —— 收口后一律 fail-closed（ADR-100 §5）")

if errors:
    print(f"[hub-ci] ✗ {len(errors)} 处校验失败：", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"[hub-ci] ✓ 插件索引校验通过（{len(plugins)} 个活跃引擎级插件 · hubVersion 0.4.0 · "
      f"依赖图无环且指向未归档 id）")
