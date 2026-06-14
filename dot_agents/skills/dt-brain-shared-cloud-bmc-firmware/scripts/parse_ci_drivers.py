#!/usr/bin/env python3
"""
Parse caas-image-builder .gitlab-ci.yml to extract the production
MLNX_OFED and DOCA driver versions used in the build matrix.

Used by hpe-firmware-versions.py and lenovo-firmware-versions.py to
automatically set the NIC firmware target versions without hardcoding.

Usage (standalone):
    python parse_ci_drivers.py /path/to/caas-image-builder/.gitlab-ci.yml

Returns JSON like:
    {
      "mlnx_ofed": "24.10-2.1.8.0",
      "doca": "2.9.3",
      "entries": [
        {"k8s": "1.32", "ubuntu": "24-04", "driver": "OFED 24.10-2.1.8.0"},
        ...
      ]
    }
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


def _sort_key_ofed(v: str) -> tuple:
    """Sort key for OFED versions like '24.10-2.1.8.0'."""
    try:
        parts = v.split("-", 1)
        maj_min = tuple(int(x) for x in parts[0].split("."))
        rest = tuple(int(x) for x in parts[1].split(".")) if len(parts) > 1 else ()
        return maj_min + rest
    except (ValueError, IndexError):
        return (0,)


def _sort_key_doca(v: str) -> tuple:
    """Sort key for DOCA versions like '2.9.3'."""
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def parse_ci_drivers(ci_config_path: str) -> dict:
    """
    Parse caas-image-builder .gitlab-ci.yml and return the highest
    MLNX_OFED and DOCA versions from the .matrix build matrix.

    Args:
        ci_config_path: Path to .gitlab-ci.yml

    Returns:
        dict with keys:
          - 'mlnx_ofed': highest OFED version string (e.g. "24.10-2.1.8.0")
          - 'doca':       highest DOCA version string (e.g. "2.9.3")
          - 'entries':    list of all matrix entries with k8s/ubuntu/driver fields
    """
    try:
        import yaml
        with open(ci_config_path) as f:
            ci = yaml.safe_load(f)
        matrix = (
            ci.get(".matrix", {})
            .get("parallel", {})
            .get("matrix", [])
        )
    except Exception:
        # Fallback: regex-based parsing (no PyYAML needed)
        matrix = _parse_matrix_regex(ci_config_path)

    ofed_versions = []
    doca_versions = []
    entries = []

    for entry in matrix:
        sw = entry.get("MELLANOX_SW", "")
        k8s = entry.get("K8S_VERSION", "?")
        ubuntu = entry.get("UBUNTU_VERSION", "?")
        entries.append({"k8s": k8s, "ubuntu": ubuntu, "driver": sw})

        if sw.startswith("OFED "):
            ofed_versions.append(sw[5:].strip())
        elif sw.startswith("DOCA "):
            doca_versions.append(sw[5:].strip())

    result = {"entries": entries}
    if ofed_versions:
        result["mlnx_ofed"] = sorted(ofed_versions, key=_sort_key_ofed)[-1]
    if doca_versions:
        result["doca"] = sorted(doca_versions, key=_sort_key_doca)[-1]

    return result


def _parse_matrix_regex(ci_config_path: str) -> list:
    """
    Regex-based fallback parser for the .matrix section in .gitlab-ci.yml.
    Looks for K8S_VERSION / UBUNTU_VERSION / MELLANOX_SW triplets.
    """
    text = Path(ci_config_path).read_text()
    entries = []

    # Find all blocks in .matrix: parallel: matrix: section
    # Each entry is a set of K8S_VERSION / UBUNTU_VERSION / MELLANOX_SW lines
    block_pattern = re.compile(
        r'K8S_VERSION:\s*"([^"]+)".*?'
        r'UBUNTU_VERSION:\s*"([^"]+)".*?'
        r'MELLANOX_SW:\s*"([^"]+)"',
        re.DOTALL,
    )
    for m in block_pattern.finditer(text):
        entries.append({
            "K8S_VERSION": m.group(1),
            "UBUNTU_VERSION": m.group(2),
            "MELLANOX_SW": m.group(3),
        })

    return entries


def find_ci_config(hint: Optional[str] = None) -> Optional[str]:
    """
    Find the caas-image-builder .gitlab-ci.yml file.

    Search order:
      1. Explicit path (hint argument)
      2. CAAS_IMAGE_BUILDER_PATH env variable
      3. Common relative paths from cwd
    """
    import os

    if hint:
        p = Path(hint)
        if p.is_file():
            return str(p)
        if p.is_dir():
            candidate = p / ".gitlab-ci.yml"
            if candidate.exists():
                return str(candidate)

    env_path = os.environ.get("CAAS_IMAGE_BUILDER_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return str(p)
        candidate = p / ".gitlab-ci.yml"
        if candidate.exists():
            return str(candidate)

    # Common locations relative to cwd
    candidates = [
        Path("../caas-image-builder/.gitlab-ci.yml"),
        Path("../../caas-image-builder/.gitlab-ci.yml"),
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())

    return None


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else find_ci_config()
    if not path:
        print("Usage: parse_ci_drivers.py /path/to/caas-image-builder/.gitlab-ci.yml", file=sys.stderr)
        sys.exit(1)

    result = parse_ci_drivers(path)
    print(json.dumps(result, indent=2))
