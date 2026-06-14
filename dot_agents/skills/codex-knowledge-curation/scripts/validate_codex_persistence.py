#!/usr/bin/env python3
"""Validate persisted Codex knowledge and block obvious runtime-state leaks."""

from __future__ import annotations

import re
import sys
from pathlib import Path


RESERVED = {"index.md", "log.md"}
BLOCKED_NAMES = {
    ".credentials.json",
    ".token_seed",
    "auth.json",
    "data.json",
    "history.jsonl",
    "hosts.yml",
    "installation_id",
    "keys.txt",
    "mondoo.yml",
}
BLOCKED_SUFFIXES = {
    ".db",
    ".db-shm",
    ".db-wal",
    ".kubeconfig",
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
    ".pyc",
    ".zip",
    ".xlsx",
    ".pdf",
}
BLOCKED_PARTS = {
    ".kube",
    "__pycache__",
    "Bitwarden CLI",
    "cache",
    "shell_snapshots",
    ".tmp",
}
SKIP_PARTS = {
    ".git",
}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"\b(?:OPENAI_API_KEY|CODEX_API_KEY|GITLAB_PERSONAL_ACCESS_TOKEN)\s*=\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\bgithub_token\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.IGNORECASE),
    re.compile(r"\btoken:\s*[A-Za-z0-9_\-]{16,}\b", re.IGNORECASE),
    re.compile(r"\bpassword:\s*['\"]?[A-Za-z0-9+/=_\-]{24,}['\"]?\s*$", re.IGNORECASE),
    re.compile(r"\bajs-synchrony-token\b", re.IGNORECASE),
    re.compile(r"\batl_token\b", re.IGNORECASE),
]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def has_frontmatter(text: str) -> tuple[bool, str]:
    if not text.startswith("---\n"):
        return False, ""
    end = text.find("\n---\n", 4)
    if end == -1:
        return False, ""
    return True, text[4:end]


def check_okf(root: Path) -> list[str]:
    errors: list[str] = []
    okf_root = root / "dot_codex" / "knowledge" / "okf"
    if not okf_root.exists():
        errors.append("missing OKF bundle: dot_codex/knowledge/okf")
        return errors

    for path in sorted(okf_root.rglob("*.md")):
        rel = path.relative_to(root)
        text = read_text(path)
        if text is None:
            errors.append(f"{rel}: not UTF-8")
            continue
        if path.name in RESERVED:
            if path.name == "log.md":
                for line_no, line in enumerate(text.splitlines(), 1):
                    if line.startswith("## ") and not re.match(r"## \d{4}-\d{2}-\d{2}$", line):
                        errors.append(f"{rel}:{line_no}: log date headings must use YYYY-MM-DD")
            if path.name == "index.md" and path == okf_root / "index.md":
                ok, frontmatter = has_frontmatter(text)
                if ok and 'okf_version: "0.1"' not in frontmatter:
                    errors.append(f"{rel}: root index frontmatter must declare okf_version 0.1")
            elif text.startswith("---\n"):
                errors.append(f"{rel}: reserved file must not have concept frontmatter")
            continue
        ok, frontmatter = has_frontmatter(text)
        if not ok:
            errors.append(f"{rel}: concept markdown missing YAML frontmatter")
            continue
        type_match = re.search(r"^type:\s*(.+?)\s*$", frontmatter, re.MULTILINE)
        if not type_match or not type_match.group(1).strip():
            errors.append(f"{rel}: concept frontmatter needs non-empty type")
    return errors


def check_persistence(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not (SKIP_PARTS & set(p.relative_to(root).parts))):
        rel = path.relative_to(root)
        parts = set(rel.parts)
        if path.name in BLOCKED_NAMES:
            errors.append(f"{rel}: blocked runtime/auth filename")
        if path.suffix in BLOCKED_SUFFIXES or any(str(path).endswith(s) for s in BLOCKED_SUFFIXES):
            errors.append(f"{rel}: blocked generated/binary suffix")
        if BLOCKED_PARTS & parts:
            errors.append(f"{rel}: blocked cache/runtime directory")
        text = read_text(path)
        if text is None:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: matches secret/session-token pattern {pattern.pattern}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = check_okf(root) + check_persistence(root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("codex persistence validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
