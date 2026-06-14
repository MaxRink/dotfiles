#!/usr/bin/env bash
#
# Cross-Platform Python Launcher for Dependency Map Generator
#
# This script automatically detects the correct Python command (python vs python3)
# and verifies Python 3.10+ is installed before executing generate_dependency_map.py.
#
# Usage:
#   bash run_dependency_map.sh [generate_dependency_map.py arguments]
#
# Example:
#   bash run_dependency_map.sh --phase1-analysis results/NBM/phase1/analysis.json \
#                              --phase1-deps results/NBM/phase1/dependency-graph.json \
#                              --output results/NBM/phase2/dependency_map.md \
#                              --feature NBM
#

set -e  # Exit on error

# Function to detect the correct Python command
detect_python() {
    local python_cmd=""
    local python_version=""

    # Try python3 first (preferred on Unix systems)
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
    # Try python (common on Windows, may be Python 2 on old Unix)
    elif command -v python &> /dev/null; then
        # Verify it's Python 3.x, not 2.x
        local py_major=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null || echo "0")
        if [ "$py_major" = "3" ]; then
            python_cmd="python"
            python_version=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
        else
            echo "ERROR: Python not found or only Python 2.x detected" >&2
            echo "" >&2
            echo "Python 3.10+ is REQUIRED for dependency map generation." >&2
            echo "" >&2
            echo "Installation instructions:" >&2
            echo "  Windows: https://python.org/downloads" >&2
            echo "           During installation, check 'Add Python to PATH'" >&2
            echo "" >&2
            echo "  macOS:   brew install python3" >&2
            echo "           OR download from https://python.org/downloads" >&2
            echo "" >&2
            echo "  Linux (Ubuntu/Debian):" >&2
            echo "           sudo apt update && sudo apt install python3" >&2
            echo "" >&2
            echo "  Linux (RHEL/CentOS):" >&2
            echo "           sudo yum install python3" >&2
            echo "" >&2
            exit 1
        fi
    else
        echo "ERROR: Python not found" >&2
        echo "" >&2
        echo "Python 3.10+ is REQUIRED for dependency map generation." >&2
        echo "" >&2
        echo "Installation instructions:" >&2
        echo "  Windows: https://python.org/downloads" >&2
        echo "           During installation, check 'Add Python to PATH'" >&2
        echo "" >&2
        echo "  macOS:   brew install python3" >&2
        echo "           OR download from https://python.org/downloads" >&2
        echo "" >&2
        echo "  Linux (Ubuntu/Debian):" >&2
        echo "           sudo apt update && sudo apt install python3" >&2
        echo "" >&2
        echo "  Linux (RHEL/CentOS):" >&2
        echo "           sudo yum install python3" >&2
        echo "" >&2
        exit 1
    fi

    # Verify Python version is 3.10+
    local version_check=$($python_cmd -c '
import sys
v = sys.version_info
if v.major == 3 and v.minor >= 10:
    print("OK")
else:
    print(f"FAIL:{v.major}.{v.minor}")
' 2>/dev/null || echo "FAIL:unknown")

    if [[ $version_check == FAIL:* ]]; then
        local detected_version="${version_check#FAIL:}"
        echo "ERROR: Python $python_version detected, but Python 3.10+ required" >&2
        echo "" >&2
        echo "Dependency Map Generator requires Python 3.10 or higher." >&2
        echo "This is due to modern type hints and dataclasses features." >&2
        echo "" >&2
        echo "Current version: Python $python_version" >&2
        echo "Required: Python 3.10.0 or higher" >&2
        echo "" >&2
        echo "Please upgrade Python:" >&2
        echo "  https://python.org/downloads" >&2
        echo "" >&2
        exit 1
    fi

    echo "$python_cmd"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect the correct Python command
PYTHON_CMD=$(detect_python)

# Execute generate_dependency_map.py with all arguments passed to this script
exec "$PYTHON_CMD" "$SCRIPT_DIR/generate_dependency_map.py" "$@"
