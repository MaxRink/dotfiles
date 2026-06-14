#!/bin/bash

# Python Environment Validation Script
# Checks Python runtime, pip, venv, and recommended tools
# Exit codes: 0 = success, 1 = critical failure, 2 = warning

set -e

ERRORS=()
WARNINGS=()
INFO=()

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Python Environment Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Minimum versions
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=9
MIN_PIP_VERSION="20.0"

PYTHON_CMD=""

# ============================================
# Check 1: Python Runtime
# ============================================
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if 'python' is Python 3
    PYTHON_VERSION_CHECK=$(python -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo "0")
    if [ "$PYTHON_VERSION_CHECK" = "3" ]; then
        PYTHON_CMD="python"
    else
        ERRORS+=("Python 3 not found (only Python 2 detected)")
        ERRORS+=("  Install Python 3: https://www.python.org/downloads/")
    fi
else
    ERRORS+=("Python not found in PATH")
    ERRORS+=("  Install Python 3.9+: https://www.python.org/downloads/")
    ERRORS+=("  Or use pyenv: curl https://pyenv.run | bash")
fi

if [ -n "$PYTHON_CMD" ]; then
    PYTHON_FULL_VERSION=$($PYTHON_CMD --version 2>&1 | sed -E 's/Python ([0-9.]+).*/\1/')
    PYTHON_MAJOR=$(echo "$PYTHON_FULL_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_FULL_VERSION" | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt "$MIN_PYTHON_MAJOR" ]; then
        ERRORS+=("Python $PYTHON_FULL_VERSION is too old (minimum: Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR)")
    elif [ "$PYTHON_MAJOR" -eq "$MIN_PYTHON_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$MIN_PYTHON_MINOR" ]; then
        ERRORS+=("Python $PYTHON_FULL_VERSION is too old (minimum: Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR)")
        ERRORS+=("  Current: $PYTHON_FULL_VERSION")
        ERRORS+=("  Required: $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR or higher")
    else
        INFO+=("✓ Python: $PYTHON_FULL_VERSION")
    fi
fi

# ============================================
# Check 2: pip Package Manager
# ============================================
if [ -n "$PYTHON_CMD" ]; then
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        ERRORS+=("pip not available")
        ERRORS+=("  Install: $PYTHON_CMD -m ensurepip --upgrade")
        ERRORS+=("  Or: curl https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD")
    else
        PIP_VERSION=$($PYTHON_CMD -m pip --version 2>&1 | sed -E 's/pip ([0-9.]+).*/\1/')
        INFO+=("✓ pip: $PIP_VERSION")
    fi
fi

# ============================================
# Check 3: venv Module
# ============================================
if [ -n "$PYTHON_CMD" ]; then
    if ! $PYTHON_CMD -m venv --help &> /dev/null 2>&1; then
        ERRORS+=("venv module not available")

        # Provide OS-specific installation instructions
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            case "$ID" in
                ubuntu|debian)
                    ERRORS+=("  Install: sudo apt-get install python3-venv")
                    ;;
                centos|rhel|fedora)
                    ERRORS+=("  Install: sudo yum install python3-venv")
                    ;;
                *)
                    ERRORS+=("  Install: Check your package manager for python3-venv")
                    ;;
            esac
        else
            ERRORS+=("  Install: Check your package manager for python3-venv")
        fi
    else
        INFO+=("✓ venv module available")
    fi
fi

# ============================================
# Check 4: uv (Recommended Package Manager)
# ============================================
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | sed -E 's/uv ([0-9.]+).*/\1/')
    INFO+=("✓ uv: $UV_VERSION (recommended)")
else
    WARNINGS+=("⚠ uv not found (recommended for faster dependency management)")
    WARNINGS+=("  Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
    WARNINGS+=("  Or: pip install uv")
fi

# ============================================
# Optional Check: poetry
# ============================================
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version 2>&1 | sed -E 's/Poetry \(version ([0-9.]+)\).*/\1/')
    INFO+=("✓ poetry: $POETRY_VERSION")
fi

# ============================================
# Optional Check: Ruff (Linter/Formatter)
# ============================================
if command -v ruff &> /dev/null; then
    RUFF_VERSION=$(ruff --version 2>&1 | sed -E 's/ruff ([0-9.]+).*/\1/')
    INFO+=("✓ ruff: $RUFF_VERSION")
else
    WARNINGS+=("⚠ ruff not found (recommended for linting/formatting)")
    WARNINGS+=("  Install: pip install ruff")
fi

# ============================================
# Optional Check: mypy (Type Checker)
# ============================================
if [ -n "$PYTHON_CMD" ]; then
    if $PYTHON_CMD -m pip show mypy &> /dev/null; then
        MYPY_VERSION=$($PYTHON_CMD -m pip show mypy 2>&1 | grep Version | sed -E 's/Version: ([0-9.]+).*/\1/')
        INFO+=("✓ mypy: $MYPY_VERSION")
    else
        WARNINGS+=("⚠ mypy not found (recommended for type checking)")
        WARNINGS+=("  Install: pip install mypy")
    fi
fi

# ============================================
# Optional Check: pytest
# ============================================
if [ -n "$PYTHON_CMD" ]; then
    if $PYTHON_CMD -m pip show pytest &> /dev/null; then
        PYTEST_VERSION=$($PYTHON_CMD -m pip show pytest 2>&1 | grep Version | sed -E 's/Version: ([0-9.]+).*/\1/')
        INFO+=("✓ pytest: $PYTEST_VERSION")
    else
        WARNINGS+=("⚠ pytest not found (will be installed during setup)")
    fi
fi

# ============================================
# Print Results
# ============================================
echo ""

# Print info messages
for msg in "${INFO[@]}"; do
    echo "$msg"
done

echo ""

# Print warnings
if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "Warnings:"
    for warning in "${WARNINGS[@]}"; do
        echo "$warning"
    done
    echo ""
fi

# Print errors
if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✗ Environment Validation Failed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Issues found:"
    for error in "${ERRORS[@]}"; do
        echo "$error"
    done
    echo ""
    echo "Fix these issues and re-run code generation."
    exit 1
fi

# Success
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Python Environment Validated Successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#WARNINGS[@]} -gt 0 ]; then
    exit 2  # Success with warnings
else
    exit 0  # Complete success
fi
