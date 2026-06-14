# Python FastMCP Reference

Comprehensive reference for building MCP servers with the Python FastMCP SDK (`mcp[cli]` package).

## Installation

```bash
pip install "mcp[cli]"
```

For development with the MCP Inspector:

```bash
pip install "mcp[cli,dev]"
```

## Server Initialization

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Server Name",
    json_response=True,              # Enable structured JSON output
    website_url="https://example.com",
    icons=[Icon(src="https://example.com/icon.png", mimeType="image/png")]
)
```

**Parameters:**

- `name` (str) — Server display name. Required.
- `json_response` (bool) — When `True`, tool return values are serialized as JSON. Default `False`.
- `website_url` (str) — Optional URL for server metadata.
- `icons` (list[Icon]) — Optional icons for server branding.
- `lifespan` (callable) — Async context manager for lifecycle resources. See Lifespan section.

## Tools

### Basic Tool

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

The docstring becomes the tool's description. Parameter types are inferred from annotations. Return type determines serialization.

### Async Tool

```python
import httpx

@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch the content of a URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

### Tool Annotations

Add metadata hints for clients about tool behavior:

```python
from mcp.server.fastmcp import FastMCP

@mcp.tool(annotations={
    "title": "File Reader",
    "readOnlyHint": True,
    "openWorldHint": False
})
def read_file(path: str) -> str:
    """Read a file from the local filesystem."""
    with open(path) as f:
        return f.read()
```

Available annotation fields:

- `title` — Human-readable display name
- `readOnlyHint` — Tool does not modify state
- `destructiveHint` — Tool may perform destructive operations
- `idempotentHint` — Repeated calls with same args produce same result
- `openWorldHint` — Tool interacts with external systems

### Context Injection

Add a `Context` parameter to access server capabilities:

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def process_batch(items: list[str], ctx: Context) -> str:
    """Process a batch of items with progress reporting."""
    results = []
    for i, item in enumerate(items):
        await ctx.report_progress(i, len(items))
        results.append(item.upper())
    return "\n".join(results)
```

**Context capabilities:**

- `ctx.report_progress(current, total)` — Report progress to the client
- `ctx.info(message)` / `ctx.debug(message)` / `ctx.warning(message)` / `ctx.error(message)` — Log messages
- `ctx.read_resource(uri)` — Read another resource from within a tool
- `ctx.request_context.lifespan_context` — Access lifespan-managed resources

### Structured Output

When `json_response=True` is set on the server, tool return values are serialized as JSON:

```python
mcp = FastMCP("my-server", json_response=True)

@mcp.tool()
def analyze_text(text: str) -> dict:
    """Analyze text and return statistics."""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "unique_words": len(set(words))
    }
```

## Resources

### Static Resource

Expose data at a fixed URI:

```python
@mcp.resource("config://app-settings")
def get_settings() -> str:
    """Return application settings."""
    import json
    return json.dumps({"theme": "dark", "language": "en"})
```

### Resource Template

Expose parameterized resources with URI templates:

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get a user's profile by ID."""
    # Fetch from database or API
    return f'{{"id": "{user_id}", "name": "User {user_id}"}}'
```

The `{user_id}` segment in the URI becomes a function parameter.

### Resource MIME Types

Specify content types for resources:

```python
@mcp.resource("data://report.csv", mime_type="text/csv")
def get_report() -> str:
    """Return a CSV report."""
    return "name,value\nfoo,42\nbar,17"
```

## Prompts

### Basic Prompt

```python
@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code for bugs and improvements:\n\n```{language}\n{code}\n```"
```

### Multi-Message Prompt

Return a list of messages for multi-turn prompts:

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt()
def debug_error(error: str, code: str) -> list[base.Message]:
    """Generate a debugging prompt with context."""
    return [
        base.UserMessage(f"I'm getting this error:\n\n```\n{error}\n```"),
        base.UserMessage(f"Here's my code:\n\n```python\n{code}\n```"),
        base.AssistantMessage("I'll analyze the error and suggest fixes."),
    ]
```

## Image Handling

Return images from tools using the `Image` class:

```python
from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("image-server")

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image file."""
    from PIL import Image as PILImage
    img = PILImage.open(image_path)
    img.thumbnail((200, 200))
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Image(data=buf.getvalue(), format="png")
```

The `Image` class accepts:

- `data` (bytes) — Raw image data
- `format` (str) — Image format: `"png"`, `"jpeg"`, `"gif"`, `"webp"`
- `path` (str) — Alternative: path to an image file

## Lifespan Management

Manage shared resources across the server's lifetime using an async context manager:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

@dataclass
class AppContext:
    db: DatabaseConnection
    http_client: httpx.AsyncClient

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize and clean up shared resources."""
    db = await DatabaseConnection.connect("postgresql://localhost/mydb")
    client = httpx.AsyncClient()
    try:
        yield AppContext(db=db, http_client=client)
    finally:
        await client.aclose()
        await db.disconnect()

mcp = FastMCP("my-server", lifespan=app_lifespan)

@mcp.tool()
async def query_database(sql: str, ctx: Context) -> str:
    """Execute a SQL query."""
    app = ctx.request_context.lifespan_context
    result = await app.db.execute(sql)
    return str(result)

@mcp.tool()
async def fetch_api(url: str, ctx: Context) -> str:
    """Fetch data from an external API."""
    app = ctx.request_context.lifespan_context
    response = await app.http_client.get(url)
    return response.text
```

**Pattern:** Define a `@dataclass` for typed access. Initialize resources in the `try` block, clean up in `finally`. Tools access via `ctx.request_context.lifespan_context`.

## Transport Options

### stdio (Default)

Standard transport for Claude Code plugins. Server communicates via stdin/stdout:

```python
if __name__ == "__main__":
    mcp.run()  # Defaults to stdio
```

### Streamable HTTP

For remote/hosted deployments. Starts an HTTP server:

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # Listens on http://localhost:8000/mcp
```

## Error Handling Patterns

### Return Errors as Content

Prefer returning error messages over raising exceptions:

```python
@mcp.tool()
def read_json(path: str) -> str:
    """Read and parse a JSON file."""
    try:
        with open(path) as f:
            import json
            data = json.load(f)
        return json.dumps(data, indent=2)
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in {path}: {e}"
```

### Validate Inputs Early

```python
@mcp.tool()
def query_table(table: str, limit: int = 100) -> str:
    """Query a database table."""
    allowed_tables = {"users", "orders", "products"}
    if table not in allowed_tables:
        return f"Error: Unknown table '{table}'. Allowed: {', '.join(allowed_tables)}"
    if limit < 1 or limit > 1000:
        return "Error: Limit must be between 1 and 1000"
    # Execute query...
    return f"Results from {table} (limit {limit})"
```

## Complete Minimal Server

```python
#!/usr/bin/env python3
"""Minimal MCP server template."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

Run: `python server.py` (stdio) or configure in `.mcp.json` for Claude Code.
