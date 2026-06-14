# Plugin MCP Patterns

Best practices and common patterns for integrating MCP servers into Claude Code plugins.

## Pattern 1: Bundled stdio Server

Package an MCP server with the plugin for self-contained functionality.

### Structure

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── servers/
│   ├── my-server.js
│   └── package.json
└── skills/
    └── my-skill/
        └── SKILL.md
```

### .mcp.json

```json
{
  "mcpServers": {
    "my-plugin-tools": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/my-server.js"],
      "env": {
        "CONFIG_PATH": "${CLAUDE_PLUGIN_ROOT}/config/defaults.json"
      }
    }
  }
}
```

### Key Considerations

- Bundle all server dependencies (or document installation steps)
- Use `${CLAUDE_PLUGIN_ROOT}` for all paths
- Pass configuration via environment variables
- Document any system requirements (Node.js version, Python, etc.)

## Pattern 2: External Service Integration

Connect to a remote API via MCP.

### .mcp.json

```json
{
  "mcpServers": {
    "external-api": {
      "type": "sse",
      "url": "https://mcp.service.com/sse",
      "headers": {
        "Authorization": "Bearer ${SERVICE_API_KEY}"
      }
    }
  }
}
```

### Key Considerations

- Always use HTTPS for remote connections
- Never hardcode API keys or tokens
- Document required environment variables in README
- Provide setup instructions for obtaining credentials
- Consider fallback behavior when service is unavailable

## Pattern 3: Multiple Servers

Plugin providing multiple MCP servers for different purposes.

### .mcp.json

```json
{
  "mcpServers": {
    "plugin-db": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/db-server.py"],
      "env": {
        "DB_URL": "${DB_URL:-sqlite:///local.db}"
      }
    },
    "plugin-api": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/api-server.js"],
      "env": {
        "API_BASE": "${API_BASE_URL}"
      }
    }
  }
}
```

### Key Considerations

- Use descriptive server names with plugin prefix to avoid conflicts
- Each server can use a different runtime
- Configure servers independently
- Document which tools come from which server

## Pattern 4: Hook + MCP Integration

Use hooks to validate or augment MCP tool calls.

### hooks/hooks.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__my-plugin-tools__.*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Validate this MCP tool call. Check parameters are safe and within expected bounds."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__my-plugin-tools__.*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/log-mcp-usage.sh"
          }
        ]
      }
    ]
  }
}
```

### Key Considerations

- Use `mcp__<server>__.*` matchers to target all tools from a server
- Use `mcp__<server>__<tool>` for specific tool hooks
- PreToolUse hooks can validate parameters before MCP calls
- PostToolUse hooks can log, audit, or react to MCP results

## Pattern 5: Conditional Server Configuration

Server configuration with environment-based defaults.

### .mcp.json

```json
{
  "mcpServers": {
    "my-service": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/service.js"],
      "env": {
        "SERVICE_URL": "${SERVICE_URL:-https://api.default-service.com}",
        "LOG_LEVEL": "${LOG_LEVEL:-info}",
        "CACHE_DIR": "${CLAUDE_PLUGIN_ROOT}/.cache"
      }
    }
  }
}
```

Use `${VAR:-default}` syntax to provide sensible defaults while allowing customization.

## Security Best Practices

### Credentials

- **Never** hardcode API keys, tokens, or passwords
- Use `${ENV_VAR}` expansion for all secrets
- Document required variables in README with setup instructions
- Consider using credential helpers or secret managers

### Network

- Always use HTTPS/WSS for remote servers
- Validate server certificates
- Set appropriate timeouts
- Handle connection failures gracefully

### Permissions

- Limit server capabilities to what the plugin needs
- Document what data the MCP server accesses
- Be transparent about external service connections
- Follow principle of least privilege

## Naming Conventions

### Server Names

- Use kebab-case: `my-plugin-tools`, not `myPluginTools`
- Prefix with plugin name to avoid conflicts: `plugin-db`, not just `db`
- Be descriptive: `github-issues`, not `gh`

### Tool Registration

MCP tools appear as `mcp__<server>__<tool>`:

- Keep tool names descriptive and consistent
- Use snake_case for tool names (MCP convention)
- Document available tools in plugin README or skill
