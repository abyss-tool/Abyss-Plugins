#!/usr/bin/env python3
"""插件中心索引聚合器：从插件仓库群（abyss-plugin-*）重新生成 plugins.json。

数据源（每个成员仓库，main 分支）：
  1. 根 plugin.json          —— manifest（id / name / version / category / …）
  2. patches/index.json      —— 补丁通道（latest 版本，容忍缺失）
  3. GitHub Releases API     —— APK 资产（url / sizeBytes / digest 摘要）；
                                无发布 → apk 保持 null（框架预览期常态）

N-SEC-001（M1 起）：plugins.json 落盘后立即产出 detached 签名
`plugins.json.minisig`（与清单同 commit 原子上库）—— 私钥经
--seed-file（CI secret RELEASE_SIGNING_KEY 原文 base64 单行），公钥经
--pubkey-file（与客户端 TRUSTED_KEYS / 主仓 publisher_pubkey.py 提取值
一致）；索引有变化而签名材料缺失 → fail-closed 拒绝滚动。

聚合纪律：
  - 成员仓库清单是插件中心仓的注册表（本文件 REPOS）—— 新插件仓库加入
    时在此登记（docs/ADDING_PLUGINS.md 有全流程）；
  - 单个成员仓库拉取失败 → 保留旧索引条目并告警（不让一个坏仓库阻塞
    整个生态的索引滚动）；全部失败 → 非零退出；
  - 版本以插件仓库 plugin.json 为准（补丁通道 latest 仅用于交叉校验告警）；
  - 输出排序 (category, id) 稳定，字段与 PluginIndexEntry 契约一一对应。

凭据：GITHUB_TOKEN 环境变量（可选；API 读取公开仓库本可匿名，带上可避
免速率限制）。raw.githubusercontent.com 直读无需凭据。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minisign_py

ORG = "abyss-tool"
# v0.8.0 大内置化：原六个重型插件（terminal / python-lab / sandbox /
# media-lab / network-guard / backup）全部并入主壳内置路线，仓库已归档，
# 不再聚合；插件生态收缩为「自带完整引擎」的三个代表 ——
# 应用构建器（构建底座）/ 病毒拦截（特征引擎）/ 虚拟机（QEMU）。
REPOS = [
    "abyss-plugin-app-builder",
    "abyss-plugin-virus-guard",
    "abyss-plugin-virtual-machine",
]
INDEX_PATH = "plugins.json"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
UA = "abyss-plugin-hub-sync/1.0"


def http_get(url: str, accept: str = "application/vnd.github+json", retries: int = 3) -> bytes:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", accept)
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
            time.sleep(1.5 * (attempt + 1))
        except urllib.error.URLError as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET {url} 失败：{last}")


def fetch_json(url: str) -> dict:
    return json.loads(http_get(url).decode())


def raw(repo: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{ORG}/{repo}/main/{path}"


def latest_apk_asset(repo: str) -> dict | None:
    """该插件仓库最新 Release 的 APK 资产（无则 null）。"""
    try:
        release = fetch_json(f"https://api.github.com/repos/{ORG}/{repo}/releases/latest")
    except Exception:
        return None
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".apk"):
            digest = asset.get("digest") or ""
            sha = digest.split(":", 1)[1] if digest.startswith("sha256:") else None
            return {
                "url": asset.get("browser_download_url"),
                "sizeBytes": asset.get("size", 0),
                "sha256": sha,
            }
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="插件中心索引聚合（N-SEC-001 签名）")
    parser.add_argument("--seed-file", type=Path, default=None,
                        help="清单签名私钥（raw seed base64 单行；CI secret 原文）。"
                        "索引有变化时必填，缺失即 fail-closed 拒绝滚动")
    parser.add_argument("--pubkey-file", type=Path, default=None,
                        help="清单签名公钥文本（与客户端 TRUSTED_KEYS 一致）")
    args = parser.parse_args()

    old: dict = {}
    try:
        old = json.loads(open(INDEX_PATH, encoding="utf-8").read())
    except Exception:
        pass
    old_entries = {p.get("id"): p for p in old.get("plugins", [])}

    entries: list[dict] = []
    warnings: list[str] = []
    for repo in REPOS:
        try:
            manifest = fetch_json(raw(repo, "plugin.json"))
        except Exception as e:
            warnings.append(f"{repo}: plugin.json 拉取失败 → {e}（保留旧条目）")
            continue
        pid = manifest.get("id", repo)
        if pid != repo:
            warnings.append(f"{repo}: manifest.id({pid}) 与仓库名不一致")
        try:
            channel = fetch_json(raw(repo, "patches/index.json"))
            channel_latest = channel.get("latest")
        except Exception:
            channel_latest = None

        entry = {
            "id": pid,
            "name": manifest.get("name", pid),
            "repo": f"{ORG}/{repo}",
            "category": manifest.get("category", "tools"),
            "version": manifest.get("version", "0.0.0"),
            "minApp": manifest.get("minApp", "0.1.0"),
            "summary": manifest.get("summary", ""),
            "icon": manifest.get("icon"),
            "permissions": manifest.get("permissions", []),
            "apk": latest_apk_asset(repo),
            "patchChannel": raw(repo, "patches/index.json"),
            "roadmap": manifest.get("roadmap", []),
        }
        # Shizuku 独立授权声明透传（独立 APK 插件按 per-app 授权，宿主
        # 授权不继承 —— 客户端详情页据此展示单独授权引导）
        shizuku = manifest.get("shizuku")
        if isinstance(shizuku, dict):
            entry["shizuku"] = shizuku
        if channel_latest is not None and channel_latest != entry["version"]:
            warnings.append(
                f"{repo}: 补丁通道 latest({channel_latest}) 与 manifest 版本({entry['version']}) 不一致"
            )
        entries.append(entry)

    if not entries:
        print("[sync] ✗ 全部成员仓库拉取失败，保留现有索引", file=sys.stderr)
        sys.exit(1)

    entries.sort(key=lambda p: (p["category"], p["id"]))
    hub_version = old.get("hubVersion", "0.2.0")
    index = {
        "schema": "abyss-plugin-index-v1",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hubVersion": hub_version,
        "plugins": entries,
    }

    # ── 幂等写回：与现文件语义等价则不动（避免无意义的 CI 提交）────────
    def normalize(obj: dict) -> str:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)

    changed = normalize(index) != normalize(old)
    if not changed:
        print(f"[sync] 索引无变化（{len(entries)} 个插件），跳过提交")
        # ── N-SEC-001 补签：索引静止但清单尚未签名（首签落地前常态）——
        # 客户端对 plugins.json 先验签再解析，签名缺失 = 插件中心不可用。
        # 材料可用时补签（幂等：已有签名且仍验过则跳过，不产生空提交）。
        sig_path = Path(INDEX_PATH + ".minisig")
        if (args.seed_file and args.pubkey_file
                and Path(INDEX_PATH).exists() and not sig_path.exists()):
            try:
                seed, keynum, _ = minisign_py.load_seed(
                    args.seed_file.read_text(encoding="utf-8"),
                    args.pubkey_file.read_text(encoding="utf-8"),
                )
                pubkey_text = args.pubkey_file.read_text(encoding="utf-8")
                raw = Path(INDEX_PATH).read_bytes()
                sig = minisign_py.sign_message(
                    seed, keynum, raw,
                    "signature from abyss release key", "plugins.json")
                if not minisign_py.verify(pubkey_text, sig, raw):
                    print("[sync] ✗ 补签自验失败 —— 拒绝写入", file=sys.stderr)
                    sys.exit(1)
                sig_path.write_text(sig, encoding="ascii")
                print("[sync] ✓ 首签补齐：plugins.json.minisig 已产出（本 commit 一并上库）")
            except minisign_py.MinisignError as e:
                print(f"[sync] ⚠ 补签失败（索引未变更，保持无签名态）：{e}", file=sys.stderr)
    else:
        text = json.dumps(index, ensure_ascii=False, indent=2) + "\n"
        raw = text.encode("utf-8")
        # ── N-SEC-001：索引有变化 → 签名材料强制（fail-closed）────────
        if not args.seed_file or not args.pubkey_file:
            print("[sync] ✗ 索引有变化但缺清单签名材料（--seed-file/--pubkey-file，"
                  "CI secret RELEASE_SIGNING_KEY）—— N-SEC-001 强制签名，拒绝滚动",
                  file=sys.stderr)
            sys.exit(1)
        try:
            seed, keynum, _ = minisign_py.load_seed(
                args.seed_file.read_text(encoding="utf-8"),
                args.pubkey_file.read_text(encoding="utf-8"),
            )
        except minisign_py.MinisignError as e:
            print(f"[sync] ✗ 签名材料校验失败：{e}", file=sys.stderr)
            sys.exit(1)
        pubkey_text = args.pubkey_file.read_text(encoding="utf-8")
        sig = minisign_py.sign_message(
            seed, keynum, raw, "signature from abyss release key", "plugins.json")
        if not minisign_py.verify(pubkey_text, sig, raw):
            print("[sync] ✗ plugins.json.minisig 签名自验失败 —— 拒绝滚动", file=sys.stderr)
            sys.exit(1)
        with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        Path(INDEX_PATH + ".minisig").write_text(sig, encoding="ascii")
        print(f"[sync] plugins.json 已重新生成并签名（{len(entries)} 个插件，.minisig 同 commit 上库）")

    for w in warnings:
        print(f"[sync] ⚠ {w}", file=sys.stderr)
    apk_count = sum(1 for e in entries if e["apk"])
    print(f"[sync] ✓ 聚合完成：{len(entries)} 插件 · {apk_count} 个已发布 APK")


if __name__ == "__main__":
    main()
