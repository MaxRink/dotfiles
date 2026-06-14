#!/bin/bash
# MCP Configuration Validator
# Validates .mcp.json structure and checks for common issues

set -euo pipefail

# Usage
if [ $# -eq 0 ]; then
  echo "Usage: $0 <path/to/.mcp.json>"
  echo ""
  echo "Validates MCP configuration file for:"
  echo "  - Valid JSON syntax"
  echo "  - Required fields per transport type"
  echo "  - Security best practices"
  echo "  - Path portability"
  exit 1
fi

MCP_FILE="$1"

if [ ! -f "$MCP_FILE" ]; then
  echo "Error: File not found: $MCP_FILE"
  exit 1
fi

echo "Validating MCP configuration: $MCP_FILE"
echo ""

error_count=0
warning_count=0

# Check 1: Valid JSON
echo "Checking JSON syntax..."
if ! jq empty "$MCP_FILE" 2>/dev/null; then
  echo "FAIL: Invalid JSON syntax"
  exit 1
fi
echo "OK: Valid JSON"

# Check 2: Has mcpServers key
echo ""
echo "Checking structure..."
if ! jq -e '.mcpServers' "$MCP_FILE" > /dev/null 2>&1; then
  echo "FAIL: Missing 'mcpServers' key at root"
  exit 1
fi
echo "OK: mcpServers key present"

# Check 3: Validate each server
echo ""
echo "Validating servers..."

for server in $(jq -r '.mcpServers | keys[]' "$MCP_FILE"); do
  echo ""
  echo "  Server: $server"

  # Get transport type (default: stdio)
  transport=$(jq -r ".mcpServers.\"$server\".type // \"stdio\"" "$MCP_FILE")
  echo "  Transport: $transport"

  if [ "$transport" = "stdio" ]; then
    # stdio: must have command
    command=$(jq -r ".mcpServers.\"$server\".command // empty" "$MCP_FILE")
    if [ -z "$command" ]; then
      echo "  FAIL: stdio server missing 'command' field"
      ((error_count++))
    else
      echo "  OK: command = $command"
    fi
  elif [ "$transport" = "sse" ] || [ "$transport" = "http" ]; then
    # sse/http: must have url
    url=$(jq -r ".mcpServers.\"$server\".url // empty" "$MCP_FILE")
    if [ -z "$url" ]; then
      echo "  FAIL: $transport server missing 'url' field"
      ((error_count++))
    else
      echo "  OK: url = $url"
      # Check for HTTPS
      if [[ "$url" == http://* ]]; then
        echo "  WARN: Using HTTP instead of HTTPS for remote server"
        ((warning_count++))
      fi
    fi
  else
    echo "  WARN: Unknown transport type '$transport' (expected: stdio, sse, http)"
    ((warning_count++))
  fi

  # Check for hardcoded paths
  server_json=$(jq -c ".mcpServers.\"$server\"" "$MCP_FILE")
  if echo "$server_json" | grep -qE '"/Users/|"/home/|"C:\\' 2>/dev/null; then
    echo "  WARN: Hardcoded absolute path detected. Use \${CLAUDE_PLUGIN_ROOT}"
    ((warning_count++))
  fi

  # Check for hardcoded secrets (basic check)
  if echo "$server_json" | grep -qiE '"(ghp_|sk-|Bearer [a-zA-Z0-9])' 2>/dev/null; then
    echo "  FAIL: Possible hardcoded secret detected. Use \${ENV_VAR} expansion"
    ((error_count++))
  fi

  # Check env vars use expansion
  env_values=$(jq -r ".mcpServers.\"$server\".env // {} | values[]" "$MCP_FILE" 2>/dev/null || true)
  for val in $env_values; do
    if [[ "$val" != *'${'* ]] && [[ ${#val} -gt 20 ]] && [[ "$val" != http* ]]; then
      echo "  WARN: env value '$val' may be a hardcoded secret. Consider using \${ENV_VAR}"
      ((warning_count++))
    fi
  done
done

echo ""
echo "---"
if [ $error_count -eq 0 ] && [ $warning_count -eq 0 ]; then
  echo "OK: All checks passed!"
  exit 0
elif [ $error_count -eq 0 ]; then
  echo "WARN: Passed with $warning_count warning(s)"
  exit 0
else
  echo "FAIL: $error_count error(s) and $warning_count warning(s)"
  exit 1
fi
