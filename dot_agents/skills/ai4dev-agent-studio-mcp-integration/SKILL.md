---
name: ai4dev-agent-studio-mcp-integration
description: This skill should be used when the user asks to "add MCP server", "integrate MCP", "configure MCP in plugin", "use .mcp.json", "set up Model Context Protocol", "connect external service", mentions "${CLAUDE_PLUGIN_ROOT} with MCP", or discusses MCP server types (SSE, stdio, HTTP, WebSocket). Provides comprehensive guidance for integrating Model Context Protocol servers into Claude Code plugins for external tool and service integration.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/agent-studio/skills/mcp-integration by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# MCP Integration for Claude Code Plugins

## Overview

The Model Context Protocol (MCP) enables Claude Code plugins to integrate with external tools and services through a standardized interface.
MCP servers expose tools that Claude can call directly, extending its capabilities beyond built-in tools.

**Key concepts:**

- MCP servers provide tools, resources, and prompts to Claude Code
- Transport types: stdio (local processes), SSE/HTTP (remote servers)
- Configuration via `.mcp.json` or inline in `plugin.json`
- Path and variable expansion with `${CLAUDE_PLUGIN_ROOT}` and env vars
- Tools follow `mcp__<server>__<tool>` naming convention

## Transport Types

### stdio (Local Processes)

Run MCP servers as local processes communicating via stdin/stdout. Best for tools bundled with plugins.

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

### SSE / HTTP (Remote Servers)

Connect to hosted MCP servers via Server-Sent Events or HTTP streaming.

```json
{
  "mcpServers": {
    "remote-server": {
      "type": "sse",
      "url": "https://mcp.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

See `references/transport-types.md` for detailed transport configuration.

## Plugin MCP Configuration

### .mcp.json (Recommended)

Place `.mcp.json` at plugin root for MCP server definitions:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/tool.py"],
      "env": {
        "CONFIG_PATH": "${CLAUDE_PLUGIN_ROOT}/config.json"
      }
    }
  }
}
```

### Inline in plugin.json

For simple single-server configurations, define directly in the manifest:

```json
{
  "name": "my-plugin",
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/index.js"]
    }
  }
}
```

See `examples/plugin-mcp-json.json` for a complete inline example and `examples/stdio-server-config.json` for a standalone `.mcp.json` example.

## Path & Variable Expansion

### ${CLAUDE_PLUGIN_ROOT}

Always use `${CLAUDE_PLUGIN_ROOT}` for paths to plugin-bundled files:

```json
{
  "command": "python",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/tool.py"]
}
```

### Environment Variable Expansion

MCP configurations support environment variable expansion:

```json
{
  "env": {
    "API_KEY": "${API_KEY}",
    "DB_URL": "${DB_URL:-postgresql://localhost:5432/default}",
    "CONFIG": "${CLAUDE_PLUGIN_ROOT}/config.json"
  }
}
```

The `${VAR:-default}` syntax provides fallback values when variables are unset.

See `examples/env-variable-patterns.md` for comprehensive variable expansion patterns.

## MCP Tool Naming Convention

When MCP servers register tools, they appear in Claude Code as:

```text
mcp__<server-name>__<tool-name>
```

**Examples:**

- Server `github` with tool `create_issue` → `mcp__github__create_issue`
- Server `database` with tool `query` → `mcp__database__query`

Use this convention when:

- Writing hook matchers for MCP tools: `"matcher": "mcp__github__.*"`
- Referencing MCP tools in agent `tools` arrays
- Documenting available tools in skill content

## Installation Scopes

MCP servers can be configured at different scopes:

| Scope | Location | Applies To |
|-------|----------|------------|
| Local (project) | `.mcp.json` in project root | Current project only |
| Plugin | `.mcp.json` in plugin root | When plugin is enabled |
| User | `~/.claude/settings.json` | All sessions for user |
| Managed | Organization settings | All users in organization |

For plugins, always use plugin-scoped configuration with `${CLAUDE_PLUGIN_ROOT}` paths.

## CLI Commands

Manage MCP servers with the `claude mcp` CLI:

| Command | Purpose |
|---------|---------|
| `claude mcp add <name> -- <command> [args]` | Add stdio server |
| `claude mcp add --transport sse <name> <url>` | Add SSE server |
| `claude mcp list` | List configured servers |
| `claude mcp get <name>` | Show server details |
| `claude mcp remove <name>` | Remove a server |
| `claude mcp add -s user <name> -- <cmd>` | Add to user scope |

See `references/cli-commands.md` for detailed CLI usage with examples.

## Testing MCP Servers

### Verify Server Registration

After configuring an MCP server, verify it loads:

```bash
# Start Claude Code and check MCP status
claude
# Then use /mcp command to list servers and tools
```

### Test Tool Availability

In a Claude Code session, verify tools are accessible:

- Use `/mcp` to list all MCP servers and their tools
- Try calling a tool to verify connectivity
- Check `claude --debug` output for MCP registration logs

### Debug Connection Issues

```bash
# Run Claude in debug mode
claude --debug

# Look for MCP-related logs:
# - Server startup
# - Tool registration
# - Connection errors
```

Use `scripts/validate-mcp-config.sh` to validate `.mcp.json` configuration before testing.

## Quick Reference

| Topic | Detail |
|-------|--------|
| Config file | `.mcp.json` at plugin root |
| Inline config | `mcpServers` field in `plugin.json` |
| Path variable | `${CLAUDE_PLUGIN_ROOT}` |
| Env defaults | `${VAR:-fallback}` |
| Tool naming | `mcp__<server>__<tool>` |
| Hook matcher | `"matcher": "mcp__server__.*"` |
| CLI add | `claude mcp add <name> -- <cmd>` |
| CLI list | `claude mcp list` |
| Debug | `claude --debug` |
| Verify | `/mcp` in session |

## Additional Resources

### Reference Files

For detailed patterns and configuration, consult:

- **`references/transport-types.md`** - Detailed stdio/SSE/HTTP transport configuration
- **`references/cli-commands.md`** - Complete CLI command reference with examples
- **`references/plugin-mcp-patterns.md`** - Plugin-specific MCP patterns and best practices

### Example Files

Working examples in `examples/`:

- **`stdio-server-config.json`** - Complete .mcp.json example for stdio servers
- **`plugin-mcp-json.json`** - plugin.json with inline mcpServers example
- **`env-variable-patterns.md`** - Variable expansion patterns and fallbacks

### Utility Scripts

Development tools in `scripts/`:

- **`validate-mcp-config.sh`** - Validate .mcp.json structure and syntax

## Implementation Workflow

To integrate MCP servers into a plugin:

1. Choose transport type (stdio for bundled, SSE/HTTP for remote)
2. Create server implementation or identify remote endpoint
3. Configure in `.mcp.json` or `plugin.json`
4. Use `${CLAUDE_PLUGIN_ROOT}` for all plugin file paths
5. Set environment variables for secrets (never hardcode)
6. Validate with `scripts/validate-mcp-config.sh`
7. Test with `claude --debug` and `/mcp` command
8. Document required environment variables in plugin README
9. Add hook matchers for MCP tools if needed
