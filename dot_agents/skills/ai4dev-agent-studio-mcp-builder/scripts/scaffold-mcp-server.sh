#!/bin/bash
# MCP Server Scaffolding Tool
# Creates a new MCP server project with boilerplate code and configuration.
#
# Usage:
#   scaffold-mcp-server.sh
#   scaffold-mcp-server.sh --language python --name my-server --output ./servers

set -euo pipefail

# --- Parse arguments or prompt interactively ---

LANGUAGE=""
SERVER_NAME=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --language|-l)
      LANGUAGE="$2"
      shift 2
      ;;
    --name|-n)
      SERVER_NAME="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --help|-h)
      echo "MCP Server Scaffolding Tool"
      echo ""
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --language, -l   Language: python or typescript"
      echo "  --name, -n       Server name (e.g., my-tools)"
      echo "  --output, -o     Output directory (default: current directory)"
      echo "  --help, -h       Show this help"
      echo ""
      echo "If options are not provided, the script will prompt interactively."
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Interactive prompts for missing values
if [ -z "$LANGUAGE" ]; then
  echo "Select language:"
  echo "  1) Python (FastMCP)"
  echo "  2) TypeScript (McpServer)"
  read -rp "Choice [1/2]: " choice
  case "$choice" in
    1|python|Python) LANGUAGE="python" ;;
    2|typescript|TypeScript|ts) LANGUAGE="typescript" ;;
    *)
      echo "Error: Invalid choice. Use 1 (Python) or 2 (TypeScript)."
      exit 1
      ;;
  esac
fi

if [ -z "$SERVER_NAME" ]; then
  read -rp "Server name (e.g., my-tools): " SERVER_NAME
  if [ -z "$SERVER_NAME" ]; then
    echo "Error: Server name is required."
    exit 1
  fi
fi

if [ -z "$OUTPUT_DIR" ]; then
  OUTPUT_DIR="."
fi

# Normalize language
LANGUAGE=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')
if [[ "$LANGUAGE" != "python" && "$LANGUAGE" != "typescript" ]]; then
  echo "Error: Language must be 'python' or 'typescript'."
  exit 1
fi

# --- Create project ---

PROJECT_DIR="${OUTPUT_DIR}/${SERVER_NAME}"

if [ -d "$PROJECT_DIR" ]; then
  echo "Error: Directory already exists: $PROJECT_DIR"
  exit 1
fi

mkdir -p "$PROJECT_DIR"
echo "Creating MCP server project: $PROJECT_DIR"

# --- Python scaffolding ---

if [ "$LANGUAGE" = "python" ]; then
  # Server file
  cat > "${PROJECT_DIR}/server.py" << 'PYEOF'
#!/usr/bin/env python3
"""MCP server: SERVER_NAME_PLACEHOLDER

Add tools, resources, and prompts below.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SERVER_NAME_PLACEHOLDER")


@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


@mcp.resource("config://info")
def get_info() -> str:
    """Return server information."""
    return '{"server": "SERVER_NAME_PLACEHOLDER", "version": "0.1.0"}'


if __name__ == "__main__":
    mcp.run()
PYEOF

  # Replace placeholder with actual name
  sed -i.bak "s/SERVER_NAME_PLACEHOLDER/${SERVER_NAME}/g" "${PROJECT_DIR}/server.py"
  rm -f "${PROJECT_DIR}/server.py.bak"

  # pyproject.toml
  cat > "${PROJECT_DIR}/pyproject.toml" << TOMLEOF
[project]
name = "${SERVER_NAME}"
version = "0.1.0"
description = "MCP server: ${SERVER_NAME}"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
TOMLEOF

  echo ""
  echo "Created Python MCP server:"
  echo "  ${PROJECT_DIR}/server.py"
  echo "  ${PROJECT_DIR}/pyproject.toml"
  echo ""
  echo "Next steps:"
  echo "  cd ${PROJECT_DIR}"
  echo "  pip install -e ."
  echo "  python server.py              # Test with stdio"
  echo ""
  echo "Add to .mcp.json:"
  echo "  {"
  echo "    \"mcpServers\": {"
  echo "      \"${SERVER_NAME}\": {"
  echo "        \"command\": \"python\","
  echo "        \"args\": [\"\${CLAUDE_PLUGIN_ROOT}/${SERVER_NAME}/server.py\"]"
  echo "      }"
  echo "    }"
  echo "  }"

fi

# --- TypeScript scaffolding ---

if [ "$LANGUAGE" = "typescript" ]; then
  # Server file
  cat > "${PROJECT_DIR}/server.ts" << 'TSEOF'
#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

const server = new McpServer({ name: "SERVER_NAME_PLACEHOLDER", version: "0.1.0" });

server.registerTool("hello", {
  description: "Say hello to someone",
  inputSchema: z.object({
    name: z.string().describe("Name of the person to greet"),
  }),
}, async ({ name }) => ({
  content: [{ type: "text" as const, text: `Hello, ${name}!` }],
}));

server.registerResource(
  "server-info",
  "config://info",
  { description: "Server information" },
  async (uri) => ({
    contents: [{
      uri: uri.href,
      text: JSON.stringify({ server: "SERVER_NAME_PLACEHOLDER", version: "0.1.0" }),
    }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
TSEOF

  # Replace placeholder with actual name
  sed -i.bak "s/SERVER_NAME_PLACEHOLDER/${SERVER_NAME}/g" "${PROJECT_DIR}/server.ts"
  rm -f "${PROJECT_DIR}/server.ts.bak"

  # package.json
  cat > "${PROJECT_DIR}/package.json" << PKGEOF
{
  "name": "${SERVER_NAME}",
  "version": "0.1.0",
  "description": "MCP server: ${SERVER_NAME}",
  "type": "module",
  "main": "dist/server.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "@modelcontextprotocol/server": "^2.0.0",
    "zod": "^3.25.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/node": "^22.0.0"
  }
}
PKGEOF

  # tsconfig.json
  cat > "${PROJECT_DIR}/tsconfig.json" << 'TSCEOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["server.ts"]
}
TSCEOF

  echo ""
  echo "Created TypeScript MCP server:"
  echo "  ${PROJECT_DIR}/server.ts"
  echo "  ${PROJECT_DIR}/package.json"
  echo "  ${PROJECT_DIR}/tsconfig.json"
  echo ""
  echo "Next steps:"
  echo "  cd ${PROJECT_DIR}"
  echo "  npm install"
  echo "  npm run build"
  echo "  npm start                     # Test with stdio"
  echo ""
  echo "Add to .mcp.json:"
  echo "  {"
  echo "    \"mcpServers\": {"
  echo "      \"${SERVER_NAME}\": {"
  echo "        \"command\": \"node\","
  echo "        \"args\": [\"\${CLAUDE_PLUGIN_ROOT}/${SERVER_NAME}/dist/server.js\"]"
  echo "      }"
  echo "    }"
  echo "  }"

fi

echo ""
echo "Done."
