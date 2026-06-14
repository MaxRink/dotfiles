#!/usr/bin/env python3
"""Wrapper script for generating .drawio diagrams.

Handles imports and path setup so diagram scripts only need to contain
the diagram logic itself. All drawio_utils symbols are pre-imported.

Usage:
    .venv/bin/python .claude/skills/core-drawio/scripts/generate_drawio.py <script.py>

The script.py has access to:
    - DiagramBuilder, STATUS_COLORS, ARCH_COLORS (from drawio_utils)
    - xml.etree.ElementTree as ET
    - sys, os
"""

import sys
import os
import runpy

# Make drawio_utils importable
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

from drawio_utils import DiagramBuilder, STATUS_COLORS, ARCH_COLORS  # noqa: F401
import xml.etree.ElementTree as ET  # noqa: F401

if len(sys.argv) < 2:
    print("Usage: generate_drawio.py <script.py>")
    print()
    print("The script has access to: DiagramBuilder, STATUS_COLORS, ARCH_COLORS, ET")
    sys.exit(1)

script_path = sys.argv[1]
if not os.path.exists(script_path):
    print(f"Error: {script_path} not found")
    sys.exit(1)

# Inject drawio_utils symbols into the script's namespace
script_globals = {
    "__name__": "__main__",
    "__file__": os.path.abspath(script_path),
    "DiagramBuilder": DiagramBuilder,
    "STATUS_COLORS": STATUS_COLORS,
    "ARCH_COLORS": ARCH_COLORS,
    "ET": ET,
    "sys": sys,
    "os": os,
}

with open(script_path) as f:
    code = compile(f.read(), script_path, "exec")
    exec(code, script_globals)
