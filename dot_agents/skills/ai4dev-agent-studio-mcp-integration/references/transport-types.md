# MCP Transport Types Reference

Detailed configuration reference for each MCP transport type.

## stdio (Standard I/O)

The most common transport for plugin-bundled servers. Launches a local process and communicates via stdin/stdout.

### Configuration

```json
{
  "mcpServers": {
    "server-name": {
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "KEY": "value"
      },
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Executable to run (e.g., `node`, `python`, `npx`) |
| `args` | No | Array of command arguments |
| `env` | No | Environment variables for the process |
| `cwd` | No | Working directory for the process |

### Common Patterns

**Node.js server:**

```json
{
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/index.js"]
}
```

**Python server:**

```json
{
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "PYTHONPATH": "${CLAUDE_PLUGIN_ROOT}/lib"
  }
}
```

**npx-based server (community packages):**

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
}
```

**uvx-based server (Python packages):**

```json
{
  "command": "uvx",
  "args": ["mcp-server-git", "--repository", "."]
}
```

### Best Practices

- Always use `${CLAUDE_PLUGIN_ROOT}` for paths to plugin files
- Set `cwd` if server expects a specific working directory
- Pass secrets via `env` variables, never hardcode
- Ensure the `command` executable is available on target systems
- Bundle dependencies or document installation requirements

## SSE (Server-Sent Events)

Connect to remote MCP servers using Server-Sent Events transport. Use for hosted services or shared servers.

### Configuration

```json
{
  "mcpServers": {
    "remote-service": {
      "type": "sse",
      "url": "https://mcp.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Must be `"sse"` |
| `url` | Yes | SSE endpoint URL (HTTPS recommended) |
| `headers` | No | HTTP headers for authentication |

### Best Practices

- Always use HTTPS for remote connections
- Pass auth tokens via environment variables in headers
- Handle connection timeouts gracefully
- Document the remote server URL and authentication requirements

## HTTP (Streamable HTTP)

Connect using HTTP streaming transport. Newer alternative to SSE with better bidirectional support.

### Configuration

```json
{
  "mcpServers": {
    "http-service": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}"
      }
    }
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Must be `"http"` |
| `url` | Yes | HTTP endpoint URL (HTTPS recommended) |
| `headers` | No | HTTP headers for authentication |

### Best Practices

- Prefer HTTP transport over SSE for new integrations when supported
- Same security practices as SSE (HTTPS, env var tokens)

## Choosing a Transport

| Criterion | stdio | SSE/HTTP |
|-----------|-------|----------|
| Server location | Local, bundled with plugin | Remote, hosted service |
| Setup complexity | Simple (command + args) | Requires running server |
| Authentication | N/A (local process) | Headers with tokens |
| Performance | Fast (local IPC) | Network dependent |
| Use case | Plugin tools, local utilities | Cloud APIs, shared services |

**Recommendation:** Use stdio for plugin-bundled tools. Use SSE/HTTP for connecting to external hosted services.
