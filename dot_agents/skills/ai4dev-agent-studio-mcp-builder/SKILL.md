---
name: ai4dev-agent-studio-mcp-builder
description: This skill should be used when the user asks to "build an MCP server", "create an MCP server", "write MCP tools", "use FastMCP", "use MCP SDK", "MCP server in Python", "MCP server in TypeScript", "create MCP tools", "build MCP resources", "scaffold MCP project", or needs guidance on writing MCP server code using the Python or TypeScript SDKs. Provides comprehensive guidance for building Model Context Protocol servers that expose tools, resources, and prompts to Claude Code.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/agent-studio/skills/mcp-builder by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Building MCP Servers

## Overview

An MCP (Model Context Protocol) server is a process that exposes tools, resources, and prompts to LLM-powered applications like Claude Code through
a standardized protocol. Build an MCP server when:

- External API integration is needed (databases, web services, internal tools)
- Computational work should run outside the LLM context (file processing, data analysis)
- A plugin needs to provide custom tools beyond what hooks and skills offer
- Reusable tool packages should be shareable across projects

MCP servers communicate over **stdio** (stdin/stdout) for local processes or **streamable HTTP** for remote deployments. For Claude Code plugins, stdio is the standard transport.

## Choosing a Language

| Factor | Python (FastMCP) | TypeScript (McpServer) |
|--------|-------------------|------------------------|
| Setup complexity | Minimal — decorator-based | Moderate — config objects + Zod |
| Type safety | Runtime via docstrings | Compile-time via Zod schemas |
| Async support | Native `async/await` | Native `async/await` |
| Output schemas | `json_response=True` | `outputSchema` with Zod |
| Best for | Rapid prototyping, data/ML tools | Node.js ecosystems, strict typing |
| Package | `mcp[cli]` | `@modelcontextprotocol/server` |

Both SDKs support the full MCP specification. Choose based on ecosystem fit and team familiarity.

## Core Concepts

MCP servers expose three primitives:

1. **Tools** — Functions the LLM can invoke (side effects allowed). Examples: query a database, call an API, process a file.
2. **Resources** — Read-only data the LLM can access. Examples: configuration, documentation, live metrics. Identified by URI (`config://settings`, `file:///path`).
3. **Prompts** — Reusable prompt templates with parameters. Examples: code review prompt, summarization prompt.

Tools are the most commonly used primitive. Resources and prompts are optional but useful for exposing data and standardizing interactions.

**Design guidelines for tools:**

- Each tool should do one thing well. Prefer multiple focused tools over one large multi-purpose tool.
- Write clear, descriptive docstrings — these become the tool descriptions the LLM reads to decide when to call the tool.
- Use specific parameter names and types. `query: str` is better than `input: str`.
- Return structured data (JSON strings) when the output has multiple fields.
- Handle errors gracefully and return informative error messages as content rather than raising exceptions.

## Python Quick Start

Install the SDK:

```bash
pip install "mcp[cli]"
```

Create a server with tools, resources, and prompts using decorators:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def search_files(pattern: str, directory: str = ".") -> str:
    """Search for files matching a glob pattern."""
    import glob
    matches = glob.glob(f"{directory}/{pattern}", recursive=True)
    return "\n".join(matches) if matches else "No files found."

@mcp.resource("config://settings")
def get_settings() -> str:
    """Expose application settings."""
    return '{"log_level": "info", "max_retries": 3}'

@mcp.prompt()
def analyze_code(code: str, language: str = "python") -> str:
    """Generate a code analysis prompt."""
    return f"Analyze this {language} code for bugs and improvements:\n\n```{language}\n{code}\n```"

if __name__ == "__main__":
    mcp.run()  # Defaults to stdio transport
```

Key patterns:

- `@mcp.tool()` — Register a callable tool. The docstring becomes the tool description. Parameter types are inferred from annotations.
- `@mcp.resource("uri://path")` — Register a static resource at a fixed URI.
- `@mcp.resource("template://{param}")` — Register a resource template with dynamic URI segments.
- `@mcp.prompt()` — Register a prompt template. Parameters become prompt arguments.
- `mcp.run()` — Start the server with stdio transport (default). Pass `transport="streamable-http"` for HTTP.

See `references/python-fastmcp-reference.md` for advanced patterns including Context injection, lifespan management, Image handling, and structured output.

## TypeScript Quick Start

Initialize a project and install dependencies:

```bash
npm init -y
npm install @modelcontextprotocol/server zod
```

Create a server with tools and resources:

```typescript
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.registerTool(
  "search-files",
  {
    description: "Search for files matching a glob pattern",
    inputSchema: z.object({
      pattern: z.string().describe("Glob pattern to match"),
      directory: z.string().default(".").describe("Directory to search"),
    }),
  },
  async ({ pattern, directory }) => {
    const { globSync } = await import("glob");
    const matches = globSync(`${directory}/${pattern}`);
    return {
      content: [{ type: "text", text: matches.join("\n") || "No files found." }],
    };
  }
);

server.registerResource("settings", "config://settings", {}, async (uri) => ({
  contents: [{ uri: uri.href, text: '{"log_level": "info", "max_retries": 3}' }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

Key patterns:

- `server.registerTool(name, config, handler)` — Register a tool. `inputSchema` uses Zod objects. Must be wrapped in `z.object()`.
- `server.registerResource(name, uri, metadata, handler)` — Register a resource at a fixed URI.
- `server.registerResourceTemplate(name, template, metadata, handler)` — Register a URI template resource.
- `server.registerPrompt(name, config, handler)` — Register a prompt. `argsSchema` uses Zod objects.
- Return `{ content: [{ type: "text", text: "..." }] }` from tool handlers.

See `references/typescript-sdk-reference.md` for advanced patterns including output schemas, resource templates, and HTTP transport.

## Context and Lifecycle

### Python Context

Inject a `Context` object to access server capabilities within tools:

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def long_task(items: list[str], ctx: Context) -> str:
    """Process items with progress reporting."""
    for i, item in enumerate(items):
        await ctx.report_progress(i, len(items))
        # process item...
    return f"Processed {len(items)} items"
```

### Python Lifespan

Manage shared resources (database connections, HTTP clients) across the server lifecycle:

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class AppContext:
    db: DatabaseConnection

@asynccontextmanager
async def app_lifespan(server):
    db = await DatabaseConnection.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

mcp = FastMCP("my-server", lifespan=app_lifespan)

@mcp.tool()
def query(sql: str, ctx: Context) -> str:
    """Run a database query."""
    db = ctx.request_context.lifespan_context.db
    return db.execute(sql)
```

## Error Handling

Return errors as text content rather than raising exceptions. This gives the LLM useful error context.

**Python:**

```python
@mcp.tool()
def read_file(path: str) -> str:
    """Read a file's contents."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
```

**TypeScript:**

```typescript
server.registerTool("read-file", {
  description: "Read a file's contents",
  inputSchema: z.object({ path: z.string() }),
}, async ({ path }) => {
  try {
    const content = await fs.readFile(path, "utf-8");
    return { content: [{ type: "text", text: content }] };
  } catch (err) {
    return { content: [{ type: "text", text: `Error: ${err.message}` }], isError: true };
  }
});
```

Set `isError: true` in TypeScript to signal error state to the client.

## Plugin Bundling

To bundle an MCP server with a Claude Code plugin, configure it in `.mcp.json` at the plugin root:

**Python server:**

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/tool_server.py"]
    }
  }
}
```

**TypeScript server:**

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/tool_server.js"]
    }
  }
}
```

Always use `${CLAUDE_PLUGIN_ROOT}` for paths to plugin-bundled files. Pass secrets via environment variables, never hardcode them:

```json
{
  "env": {
    "API_KEY": "${API_KEY}",
    "DB_URL": "${DB_URL:-postgresql://localhost:5432/default}"
  }
}
```

See the `mcp-integration` skill for detailed `.mcp.json` configuration, transport types, and CLI commands.

## Testing

### Run Standalone

Test a server directly before integrating with Claude Code:

```bash
# Python — run with stdio (reads from stdin, writes to stdout)
python server.py

# TypeScript — compile and run
npx tsc && node server.js
```

### Debug in Claude Code

```bash
# Start Claude with debug logging to see MCP registration
claude --debug

# Inside a session, list MCP servers and tools
/mcp
```

### Validate Syntax

Before deploying, verify the server code parses correctly:

```bash
# Python
python -c "import ast; ast.parse(open('server.py').read())"

# TypeScript
npx tsc --noEmit server.ts
```

### Common Issues

- **Server not appearing in `/mcp`**: Check that `.mcp.json` is at the plugin root and uses valid JSON. Verify `${CLAUDE_PLUGIN_ROOT}` paths resolve correctly.
- **Tools not registering**: Ensure the server starts without errors by running it standalone. Check for import errors or missing dependencies.
- **Timeout on startup**: The server must respond to the MCP initialization handshake promptly. Avoid heavy computation at import time; use lifespan management for slow initialization.

## Quick Reference

| Task | Python (FastMCP) | TypeScript (McpServer) |
|------|-------------------|------------------------|
| Install | `pip install "mcp[cli]"` | `npm install @modelcontextprotocol/server zod` |
| Init server | `mcp = FastMCP("name")` | `new McpServer({ name, version })` |
| Add tool | `@mcp.tool()` | `server.registerTool(name, config, handler)` |
| Add resource | `@mcp.resource("uri")` | `server.registerResource(name, uri, meta, handler)` |
| Add prompt | `@mcp.prompt()` | `server.registerPrompt(name, config, handler)` |
| Run stdio | `mcp.run()` | `server.connect(new StdioServerTransport())` |
| Run HTTP | `mcp.run(transport="streamable-http")` | Use `StreamableHTTPServerTransport` |
| Error return | Return error string | `{ content: [...], isError: true }` |
| Progress | `await ctx.report_progress(i, n)` | Not built-in; use logging |
| Lifespan | `FastMCP("n", lifespan=fn)` | Manual setup/teardown |

## Additional Resources

### Reference Files

For deep SDK-specific guidance, consult:

- **`references/python-fastmcp-reference.md`** — FastMCP initialization, decorators, Context, Image, lifespan, OAuth, structured output
- **`references/typescript-sdk-reference.md`** — McpServer registration, Zod schemas, transports, session management, output schemas

### Example Files

Complete working servers in `examples/`:

- **`examples/python-tool-server.py`** — Python MCP server with tools, resource, and prompt
- **`examples/typescript-tool-server.ts`** — TypeScript MCP server with tools and resource

### Utility Scripts

- **`scripts/scaffold-mcp-server.sh`** — Interactive scaffolding script that creates a new MCP server project with boilerplate code and configuration
