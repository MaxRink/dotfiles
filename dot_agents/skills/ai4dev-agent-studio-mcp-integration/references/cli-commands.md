# MCP CLI Commands Reference

Complete reference for `claude mcp` commands used to manage MCP servers.

## claude mcp add

Add an MCP server configuration.

### stdio Server

```bash
claude mcp add <name> -- <command> [args...]
```

**Examples:**

```bash
# Add a Node.js MCP server
claude mcp add my-server -- node /path/to/server.js

# Add with npx (community package)
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /home/user/docs

# Add a Python MCP server
claude mcp add py-tools -- python -m my_mcp_server

# Add with environment variables
claude mcp add github -- npx -y @modelcontextprotocol/server-github
# Then set GITHUB_TOKEN in environment
```

### SSE Server

```bash
claude mcp add --transport sse <name> <url>
```

**Examples:**

```bash
# Add an SSE server
claude mcp add --transport sse remote-api https://mcp.example.com/sse

# Add with authentication header
claude mcp add --transport sse --header "Authorization: Bearer $TOKEN" remote-api https://mcp.example.com/sse
```

### HTTP Server

```bash
claude mcp add --transport http <name> <url>
```

### Scope Options

```bash
# Add to project scope (default, saved to .mcp.json)
claude mcp add my-server -- node server.js

# Add to user scope (saved to ~/.claude/settings.json)
claude mcp add -s user my-server -- node server.js

# Add to project scope explicitly
claude mcp add -s project my-server -- node server.js
```

## claude mcp list

List all configured MCP servers.

```bash
claude mcp list
```

**Output shows:**

- Server name
- Transport type
- Command/URL
- Scope (project, user, managed)
- Status (if applicable)

## claude mcp get

Show detailed configuration for a specific server.

```bash
claude mcp get <name>
```

**Example:**

```bash
claude mcp get github
# Shows: command, args, env, scope, transport type
```

## claude mcp remove

Remove an MCP server configuration.

```bash
claude mcp remove <name>
```

**Example:**

```bash
claude mcp remove my-server
```

## In-Session Commands

### /mcp

In an active Claude Code session, use `/mcp` to:

- List all registered MCP servers
- View available tools per server
- Check server connection status
- Verify tool registration

## Common Workflows

### Add and Test a New Server

```bash
# 1. Add the server
claude mcp add my-tools -- node ./servers/my-tools.js

# 2. Start Claude Code with debug
claude --debug

# 3. In session, verify with /mcp
# 4. Test a tool call
```

### Migrate from Project to User Scope

```bash
# Remove from project scope
claude mcp remove my-server

# Add to user scope
claude mcp add -s user my-server -- node ./servers/my-tools.js
```

### Environment Variable Setup

For servers requiring API keys:

```bash
# Set environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Add server (it will use the env var)
claude mcp add github -- npx -y @modelcontextprotocol/server-github

# Or use .env file in project
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxx" >> .env
```
