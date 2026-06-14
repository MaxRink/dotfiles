#!/bin/bash

# Java Environment Validation Script
# Checks Java runtime, compiler, JAVA_HOME, and build tools
# Exit codes: 0 = success, 1 = critical failure, 2 = warning

set -e

ERRORS=()
WARNINGS=()
INFO=()

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Java Environment Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Minimum versions
MIN_JAVA_VERSION=11
MIN_MAVEN_VERSION="3.6"
MIN_GRADLE_VERSION="7.0"

# ============================================
# Check 1: Java Runtime (JRE)
# ============================================
if ! command -v java &> /dev/null; then
    ERRORS+=("Java runtime (java) not found in PATH")
    ERRORS+=("  Install from: https://adoptium.net/")
    ERRORS+=("  Or use SDKMAN: curl -s https://get.sdkman.io | bash")
else
    JAVA_VERSION_OUTPUT=$(java -version 2>&1 | head -n 1)
    # Extract version number (handles both old "1.8.0" and new "11.0.1" formats)
    JAVA_VERSION=$(echo "$JAVA_VERSION_OUTPUT" | sed -E 's/.*version "?([0-9]+)\.?([0-9]+)?\.?([0-9]+)?.*"?.*/\1/')

    # Handle old format (1.8.0 -> 8)
    if [ "$JAVA_VERSION" = "1" ]; then
        JAVA_VERSION=$(echo "$JAVA_VERSION_OUTPUT" | sed -E 's/.*version "?1\.([0-9]+)\.?.*/\1/')
    fi

    if [ "$JAVA_VERSION" -lt "$MIN_JAVA_VERSION" ]; then
        ERRORS+=("Java version $JAVA_VERSION is too old (minimum: Java $MIN_JAVA_VERSION)")
        ERRORS+=("  Current: $JAVA_VERSION_OUTPUT")
        ERRORS+=("  Required: Java $MIN_JAVA_VERSION or higher")
    else
        JAVA_FULL_VERSION=$(echo "$JAVA_VERSION_OUTPUT" | sed -E 's/.*version "?([0-9.]+).*"?.*/\1/')
        INFO+=("✓ Java Runtime: $JAVA_FULL_VERSION")
    fi
fi

# ============================================
# Check 2: Java Compiler (JDK)
# ============================================
if ! command -v javac &> /dev/null; then
    ERRORS+=("Java compiler (javac) not found - JDK not installed (only JRE found)")
    ERRORS+=("  Install JDK from: https://adoptium.net/")
    ERRORS+=("  Or use SDKMAN: sdk install java 21-tem")
else
    JAVAC_VERSION=$(javac -version 2>&1 | sed -E 's/javac ([0-9.]+).*/\1/')
    INFO+=("✓ Java Compiler: javac $JAVAC_VERSION")
fi

# ============================================
# Check 3: JAVA_HOME Environment Variable
# ============================================
if [ -z "$JAVA_HOME" ]; then
    ERRORS+=("JAVA_HOME environment variable not set")
    ERRORS+=("  Add to ~/.bashrc or ~/.zshrc:")

    # Try to detect Java installation path
    if command -v java &> /dev/null; then
        JAVA_PATH=$(which java)
        # Try to resolve symlinks
        if command -v readlink &> /dev/null; then
            JAVA_REAL_PATH=$(readlink -f "$JAVA_PATH" 2>/dev/null || echo "$JAVA_PATH")
            SUGGESTED_JAVA_HOME=$(dirname $(dirname "$JAVA_REAL_PATH"))
            ERRORS+=("    export JAVA_HOME=$SUGGESTED_JAVA_HOME")
        else
            ERRORS+=("    export JAVA_HOME=/path/to/jdk")
        fi
    else
        ERRORS+=("    export JAVA_HOME=/path/to/jdk")
    fi

    ERRORS+=("    export PATH=\$JAVA_HOME/bin:\$PATH")
else
    # Verify JAVA_HOME points to a valid JDK
    if [ ! -d "$JAVA_HOME" ]; then
        ERRORS+=("JAVA_HOME points to non-existent directory: $JAVA_HOME")
    elif [ ! -f "$JAVA_HOME/bin/javac" ] && [ ! -f "$JAVA_HOME/bin/javac.exe" ]; then
        WARNINGS+=("JAVA_HOME may point to JRE instead of JDK (javac not found)")
        WARNINGS+=("  JAVA_HOME: $JAVA_HOME")
    else
        INFO+=("✓ JAVA_HOME: $JAVA_HOME")
    fi
fi

# ============================================
# Check 4: Build Tools (Maven or Gradle)
# ============================================
BUILD_TOOL_FOUND=false

if command -v mvn &> /dev/null; then
    MVN_VERSION=$(mvn -v 2>&1 | head -n 1 | sed -E 's/Apache Maven ([0-9.]+).*/\1/')
    MVN_MAJOR=$(echo "$MVN_VERSION" | cut -d'.' -f1)
    MVN_MINOR=$(echo "$MVN_VERSION" | cut -d'.' -f2)

    # Compare versions
    if [ "$MVN_MAJOR" -gt 3 ] || ([ "$MVN_MAJOR" -eq 3 ] && [ "$MVN_MINOR" -ge 6 ]); then
        INFO+=("✓ Maven: $MVN_VERSION")
        BUILD_TOOL_FOUND=true
    else
        WARNINGS+=("Maven version $MVN_VERSION is old (recommended: $MIN_MAVEN_VERSION+)")
        BUILD_TOOL_FOUND=true
    fi
fi

if command -v gradle &> /dev/null; then
    GRADLE_VERSION=$(gradle -v 2>&1 | grep "Gradle" | sed -E 's/Gradle ([0-9.]+).*/\1/')
    GRADLE_MAJOR=$(echo "$GRADLE_VERSION" | cut -d'.' -f1)

    if [ "$GRADLE_MAJOR" -ge 7 ]; then
        INFO+=("✓ Gradle: $GRADLE_VERSION")
        BUILD_TOOL_FOUND=true
    else
        WARNINGS+=("Gradle version $GRADLE_VERSION is old (recommended: $MIN_GRADLE_VERSION+)")
        BUILD_TOOL_FOUND=true
    fi
fi

if [ "$BUILD_TOOL_FOUND" = false ]; then
    ERRORS+=("Neither Maven nor Gradle found")
    ERRORS+=("  Install Maven: https://maven.apache.org/install.html")
    ERRORS+=("  Or Gradle: https://gradle.org/install/")
    ERRORS+=("  Or use SDKMAN: sdk install maven / sdk install gradle")
fi

# ============================================
# Optional Check: Spring Boot CLI
# ============================================
if command -v spring &> /dev/null; then
    SPRING_VERSION=$(spring --version 2>&1)
    INFO+=("✓ Spring Boot CLI: $SPRING_VERSION")
else
    WARNINGS+=("⚠ Spring Boot CLI not found (optional, useful for Spring projects)")
    WARNINGS+=("  Install: sdk install springboot")
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
echo "✓ Java Environment Validated Successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#WARNINGS[@]} -gt 0 ]; then
    exit 2  # Success with warnings
else
    exit 0  # Complete success
fi
