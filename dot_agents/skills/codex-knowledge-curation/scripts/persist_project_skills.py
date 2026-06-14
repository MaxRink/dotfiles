#!/usr/bin/env python3
"""Import local project skills into dot_agents/skills with provenance metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path("/home/a92615428/git/devops.telekom.de")
REPO_ROOT = Path(__file__).resolve().parents[4]
TARGET_ROOT = REPO_ROOT / "dot_agents" / "skills"
MANIFEST_PATH = REPO_ROOT / "dot_agents" / "skills" / "imported-skills.json"

SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    ".worktrees",
    "__pycache__",
    "node_modules",
}
SKIP_FILE_SUFFIXES = {
    ".db",
    ".jsonl",
    ".lock",
    ".pyc",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
}
SKIP_FILE_NAMES = {
    ".DS_Store",
    ".credentials.json",
    "auth.json",
    "history.jsonl",
}
SOURCE_PREFIXES = [
    ("tcaas-psa/skill", ""),
    ("schiff/platform/clusters/.github/skills", "schiff-platform-clusters"),
    ("schiff/platform/infrastructure/k8s-agent/.opencode/skills", "schiff-k8s-agent"),
    ("cit/t-caas/tdi/clusters/.github/skills", "tcaas-tdi-clusters"),
    ("cit/t-caas/bm4x-operator/.github/skills", "tcaas-bm4x-operator"),
    ("devsecops-tools/public/compliscan/.github/skills", "compliscan"),
    ("tdi-caas/tools/dt-brain-shared/.claude/skills", "dt-brain-shared"),
    ("tdi-caas/tools/tcaas-agent-troubleshooter/skills", "tcaas-agent-troubleshooter"),
    ("tdi-caas/tools/tdi-cloudbrain/skills", "tdi-cloudbrain"),
    ("ai4developers/claude-code/claude-code-plugins", "ai4dev"),
    ("ai4developers/legacy-code-migration", "legacy-code-migration"),
    ("t-dci-cloud/netbox/netboxlabs/netbox-mcp-server/.claude/skills", "netbox-mcp-server"),
]
DIRECT_LOAD_EXCLUDE_PATTERNS = [
    "tdi-caas/tools/tdi-cloudbrain/template",
    "tdi-caas/tools/tdi-cloudbrain/plugins/template/skills/example-skill",
]
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
]


@dataclass(frozen=True)
class SkillSource:
    skill_dir: Path
    skill_md: Path
    rel_dir: Path
    target_name: str
    direct_load: bool
    skip_reason: str = ""


def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "skill"


def git_value(path: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(path), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return ""


def repo_root(path: Path) -> Path | None:
    top = git_value(path, ["rev-parse", "--show-toplevel"])
    return Path(top) if top else None


def source_prefix(rel_dir: Path) -> str:
    rel = rel_dir.as_posix()
    for prefix, label in SOURCE_PREFIXES:
        if rel == prefix or rel.startswith(prefix + "/"):
            if label:
                if label == "ai4dev":
                    parts = rel_dir.parts
                    try:
                        idx = parts.index("claude-code-plugins")
                        return slug(f"ai4dev-{parts[idx + 1]}")
                    except (ValueError, IndexError):
                        return label
                if label == "legacy-code-migration":
                    parts = rel_dir.parts
                    return slug("-".join(parts[: min(len(parts), 5)]))
                return label
            return ""
    parts = rel_dir.parts
    return slug("-".join(parts[: min(len(parts), 4)]))


def target_name_for(skill_dir: Path) -> str:
    rel_dir = skill_dir.relative_to(WORKSPACE)
    prefix = source_prefix(rel_dir)
    name = slug(skill_dir.name)
    return name if not prefix else slug(f"{prefix}-{name}")


def direct_load_decision(skill_dir: Path) -> tuple[bool, str]:
    rel = skill_dir.relative_to(WORKSPACE).as_posix()
    if any(rel == pattern or rel.startswith(pattern + "/") for pattern in DIRECT_LOAD_EXCLUDE_PATTERNS):
        return False, "template/example skill is recorded but not direct-loaded"
    skill_md = skill_dir / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "SKILL.md is not UTF-8"
    if not text.strip():
        return False, "SKILL.md is empty"
    return True, ""


def find_skills() -> list[SkillSource]:
    found: list[SkillSource] = []
    for skill_md in WORKSPACE.rglob("SKILL.md"):
        rel_parts = set(skill_md.relative_to(WORKSPACE).parts)
        if SKIP_PARTS & rel_parts:
            continue
        if "dotfiles" in rel_parts:
            continue
        skill_dir = skill_md.parent
        direct_load, skip_reason = direct_load_decision(skill_dir)
        found.append(
            SkillSource(
                skill_dir=skill_dir,
                skill_md=skill_md,
                rel_dir=skill_dir.relative_to(WORKSPACE),
                target_name=target_name_for(skill_dir),
                direct_load=direct_load,
                skip_reason=skip_reason,
            )
        )
    return sorted(found, key=lambda item: item.rel_dir.as_posix())


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def text_has_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def clean_text(text: str) -> str:
    lines = [line.rstrip(" \t") for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def description_from(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("'\"") or fallback
    for line in text.splitlines():
        if line.startswith("# "):
            return f"Imported local skill: {line[2:].strip()}"
    return fallback


def normalize_skill_md(text: str, source: SkillSource) -> str:
    description = description_from(text, f"Imported local skill from {source.rel_dir.as_posix()}.")
    description = description.replace("\n", " ").strip()
    if len(description) > 220:
        description = description[:217].rstrip() + "..."

    origin = (
        f"<!-- Imported from {source.rel_dir.as_posix()} by "
        "codex-knowledge-curation/scripts/persist_project_skills.py. -->\n\n"
    )
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            body = text[end + 5 :]
            frontmatter = text[4:end]
            lines = [line for line in frontmatter.splitlines() if not line.startswith("name:")]
            if not any(line.startswith("description:") for line in lines):
                lines.insert(0, f"description: {json.dumps(description)}")
            lines.insert(0, f"name: {source.target_name}")
            return clean_text("---\n" + "\n".join(lines).rstrip() + "\n---\n\n" + origin + body.lstrip())
    return clean_text(
        "---\n"
        f"name: {source.target_name}\n"
        f"description: {json.dumps(description)}\n"
        "---\n\n"
        + origin
        + text.lstrip()
    )


def should_copy_file(path: Path) -> tuple[bool, str]:
    if path.name in SKIP_FILE_NAMES:
        return False, "blocked filename"
    if path.suffix in SKIP_FILE_SUFFIXES:
        return False, "blocked suffix"
    if path.stat().st_size > 1_000_000:
        return False, "larger than 1MB"
    text = read_text(path)
    if text is not None and text_has_secret(text):
        return False, "secret-like token pattern"
    return True, ""


def copy_skill(source: SkillSource, apply: bool) -> dict[str, object]:
    target = TARGET_ROOT / source.target_name
    copied: list[str] = []
    skipped: list[dict[str, str]] = []
    if not source.direct_load:
        if apply and target.exists():
            shutil.rmtree(target)
        return {
            "source": source.rel_dir.as_posix(),
            "target": f"dot_agents/skills/{source.target_name}",
            "targetName": source.target_name,
            "status": "recorded_not_loaded",
            "reason": source.skip_reason,
        }
    if apply and target.exists():
        shutil.rmtree(target)
    for path in sorted(p for p in source.skill_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(source.skill_dir)
        if SKIP_PARTS & set(rel.parts):
            skipped.append({"path": rel.as_posix(), "reason": "blocked runtime/cache directory"})
            continue
        ok, reason = should_copy_file(path)
        if not ok:
            skipped.append({"path": rel.as_posix(), "reason": reason})
            continue
        if apply:
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if rel.as_posix() == "SKILL.md":
                text = read_text(path)
                if text is None:
                    skipped.append({"path": rel.as_posix(), "reason": "not UTF-8"})
                    continue
                out.write_text(normalize_skill_md(text, source), encoding="utf-8")
            else:
                text = read_text(path)
                if text is None:
                    shutil.copy2(path, out)
                else:
                    out.write_text(clean_text(text), encoding="utf-8")
                    shutil.copystat(path, out)
        copied.append(rel.as_posix())

    skill_text = read_text(source.skill_md) or ""
    digest = hashlib.sha256(skill_text.encode("utf-8", errors="ignore")).hexdigest()
    root = repo_root(source.skill_dir)
    remote = git_value(root, ["remote", "get-url", "origin"]) if root else ""
    commit = git_value(root, ["rev-parse", "HEAD"]) if root else ""
    return {
        "source": source.rel_dir.as_posix(),
        "target": f"dot_agents/skills/{source.target_name}",
        "targetName": source.target_name,
        "status": "loaded",
        "skillSha256": digest,
        "sourceRepo": str(root) if root else "",
        "sourceRemote": remote,
        "sourceCommit": commit,
        "copiedFileCount": len(copied),
        "skippedFileCount": len(skipped),
        "skippedFiles": skipped[:25],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="copy skills into dot_agents/skills")
    args = parser.parse_args()

    sources = find_skills()
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for source in sources:
        seen[source.target_name] = seen.get(source.target_name, 0) + 1
        if seen[source.target_name] > 1:
            duplicates.append(source.target_name)
    if duplicates:
        for item in sorted(set(duplicates)):
            print(f"duplicate target name: {item}")
        return 1

    rows = [copy_skill(source, args.apply) for source in sources]
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "workspace": str(WORKSPACE),
        "excludedPathParts": sorted(SKIP_PARTS),
        "skills": rows,
    }
    if args.apply:
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"skills discovered: {len(rows)}")
    print(f"skills direct-loaded: {len([row for row in rows if row.get('status') == 'loaded'])}")
    print(f"skills recorded only: {len([row for row in rows if row.get('status') == 'recorded_not_loaded'])}")
    print(f"manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
