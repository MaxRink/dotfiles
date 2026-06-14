# Environment Variable Patterns for MCP Configuration

## Basic Variable Expansion

Reference environment variables with `${VAR_NAME}`:

```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}",
    "DB_HOST": "${DATABASE_HOST}"
  }
}
```

The variable is expanded at server startup from the current environment.

## Default Values

Use `${VAR:-default}` to provide fallback values when a variable is unset:

```json
{
  "env": {
    "DB_URL": "${DB_URL:-postgresql://localhost:5432/mydb}",
    "LOG_LEVEL": "${LOG_LEVEL:-info}",
    "TIMEOUT": "${REQUEST_TIMEOUT:-30}",
    "CACHE_DIR": "${CACHE_DIR:-/tmp/mcp-cache}"
  }
}
```

## Plugin Root Paths

Use `${CLAUDE_PLUGIN_ROOT}` for paths relative to the plugin directory:

```json
{
  "command": "python",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/main.py"],
  "env": {
    "CONFIG": "${CLAUDE_PLUGIN_ROOT}/config/settings.json",
    "TEMPLATES": "${CLAUDE_PLUGIN_ROOT}/assets/templates",
    "DATA_DIR": "${CLAUDE_PLUGIN_ROOT}/data"
  }
}
```

## Combining Patterns

Combine plugin paths with user-configurable variables:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/index.js"],
      "env": {
        "PLUGIN_ROOT": "${CLAUDE_PLUGIN_ROOT}",
        "API_KEY": "${SERVICE_API_KEY}",
        "BASE_URL": "${SERVICE_URL:-https://api.default.com}",
        "LOG_DIR": "${LOG_DIR:-${CLAUDE_PLUGIN_ROOT}/logs}",
        "MAX_RETRIES": "${MAX_RETRIES:-3}"
      }
    }
  }
}
```

## Security Notes

- **Never hardcode secrets** in `.mcp.json` or `plugin.json`
- Use `${ENV_VAR}` for all API keys, tokens, and passwords
- Document required environment variables in plugin README
- Provide defaults only for non-sensitive configuration (log levels, timeouts, URLs)
- Add `.env` to `.gitignore` if using `.env` files for local development
