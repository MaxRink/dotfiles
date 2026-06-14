# TypeScript MCP SDK Reference

Comprehensive reference for building MCP servers with the TypeScript SDK (`@modelcontextprotocol/server` package).

## Installation

```bash
npm install @modelcontextprotocol/server zod
```

For TypeScript compilation:

```bash
npm install -D typescript @types/node
```

## Server Initialization

```typescript
import { McpServer } from "@modelcontextprotocol/server";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
    prompts: {},
  },
});
```

**Parameters:**

- `name` (string) — Server display name. Required.
- `version` (string) — Server version (semver). Required.
- `capabilities` (object) — Declare supported features. Automatically inferred from registered components if omitted.

## Tools

### Basic Tool

```typescript
import * as z from "zod/v4";

server.registerTool("greet", {
  description: "Greet someone by name",
  inputSchema: z.object({
    name: z.string().describe("Name of the person to greet"),
  }),
}, async ({ name }) => {
  return { content: [{ type: "text", text: `Hello, ${name}!` }] };
});
```

**Important:** `inputSchema` must be a `z.object()` — raw shapes are not accepted. Use `z.object({})` for tools with no parameters.

### Tool with Output Schema

Define structured output with Zod for validated, typed responses:

```typescript
import type { CallToolResult } from "@modelcontextprotocol/server";

server.registerTool("calculate-bmi", {
  title: "BMI Calculator",
  description: "Calculate Body Mass Index",
  inputSchema: z.object({
    weightKg: z.number().describe("Weight in kilograms"),
    heightM: z.number().describe("Height in meters"),
  }),
  outputSchema: z.object({
    bmi: z.number(),
    category: z.string(),
  }),
}, async ({ weightKg, heightM }): Promise<CallToolResult> => {
  const bmi = weightKg / (heightM * heightM);
  const category = bmi < 18.5 ? "underweight" : bmi < 25 ? "normal" : bmi < 30 ? "overweight" : "obese";
  return {
    content: [{ type: "text", text: `BMI: ${bmi.toFixed(1)} (${category})` }],
    structuredContent: { bmi: parseFloat(bmi.toFixed(1)), category },
  };
});
```

When `outputSchema` is provided, include `structuredContent` alongside `content` in the return value. `structuredContent` is validated against the output schema.

### Tool Annotations

Add metadata hints about tool behavior:

```typescript
server.registerTool("delete-file", {
  description: "Delete a file from the filesystem",
  inputSchema: z.object({ path: z.string() }),
  annotations: {
    title: "Delete File",
    destructiveHint: true,
    idempotentHint: true,
    readOnlyHint: false,
  },
}, async ({ path }) => {
  // implementation...
});
```

Available annotation fields:

- `title` — Human-readable display name
- `readOnlyHint` — Tool does not modify state
- `destructiveHint` — Tool may perform destructive operations
- `idempotentHint` — Repeated calls produce same result
- `openWorldHint` — Tool interacts with external systems

### Error Handling in Tools

Return `isError: true` to signal an error to the client:

```typescript
server.registerTool("read-file", {
  description: "Read a file's contents",
  inputSchema: z.object({ path: z.string() }),
}, async ({ path }) => {
  try {
    const content = await fs.readFile(path, "utf-8");
    return { content: [{ type: "text", text: content }] };
  } catch (err: any) {
    return {
      content: [{ type: "text", text: `Error reading file: ${err.message}` }],
      isError: true,
    };
  }
});
```

## Resources

### Static Resource

Expose data at a fixed URI:

```typescript
server.registerResource("app-config", "config://settings", {
  description: "Application configuration settings",
}, async (uri) => ({
  contents: [{
    uri: uri.href,
    text: JSON.stringify({ theme: "dark", language: "en" }, null, 2),
    mimeType: "application/json",
  }],
}));
```

### Resource Template

Expose parameterized resources with URI templates:

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/server";

server.registerResourceTemplate(
  "user-profile",
  new ResourceTemplate("users://{userId}/profile", {
    list: async () => ({
      resources: [
        { uri: "users://1/profile", name: "User 1" },
        { uri: "users://2/profile", name: "User 2" },
      ],
    }),
  }),
  { description: "User profile by ID" },
  async (uri, { userId }) => ({
    contents: [{
      uri: uri.href,
      text: JSON.stringify({ id: userId, name: `User ${userId}` }),
    }],
  })
);
```

The `list` callback is optional but recommended — it enables clients to discover available resource instances.

## Prompts

### Basic Prompt

```typescript
server.registerPrompt("code-review", {
  description: "Review code for best practices and bugs",
  argsSchema: z.object({
    code: z.string().describe("The code to review"),
    language: z.string().optional().describe("Programming language"),
  }),
}, async ({ code, language }) => {
  const langHint = language ? ` (${language})` : "";
  return {
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Review this code${langHint} for bugs, security issues, and improvements:\n\n\`\`\`\n${code}\n\`\`\``,
      },
    }],
  };
});
```

### Multi-Message Prompt

```typescript
server.registerPrompt("debug-error", {
  description: "Debug an error with code context",
  argsSchema: z.object({
    error: z.string(),
    code: z.string(),
  }),
}, async ({ error, code }) => ({
  messages: [
    { role: "user", content: { type: "text", text: `Error:\n\`\`\`\n${error}\n\`\`\`` } },
    { role: "user", content: { type: "text", text: `Code:\n\`\`\`\n${code}\n\`\`\`` } },
    { role: "assistant", content: { type: "text", text: "I'll analyze the error and suggest fixes." } },
  ],
}));
```

## Transport

### stdio Transport

Standard transport for Claude Code plugins. Communicates via stdin/stdout:

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Streamable HTTP Transport

For remote deployments behind an HTTP server:

```typescript
import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/server/streamableHttp";

const app = express();
app.use(express.json());

const transports = new Map<string, StreamableHTTPServerTransport>();

app.post("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"] as string;
  let transport = transports.get(sessionId);

  if (!transport) {
    transport = new StreamableHTTPServerTransport({ sessionIdGenerator: () => crypto.randomUUID() });
    transports.set(transport.sessionId!, transport);
    const serverInstance = new McpServer({ name: "http-server", version: "1.0.0" });
    // Register tools...
    await serverInstance.connect(transport);
  }

  await transport.handleRequest(req, res);
});

app.listen(3000);
```

**Session management:** Each HTTP client gets its own transport instance, identified by the `mcp-session-id` header.

## TypeScript Configuration

Recommended `tsconfig.json` for MCP servers:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

Set `"type": "module"` in `package.json` for ESM support.

## Complete Minimal Server

```typescript
#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.registerTool("hello", {
  description: "Say hello",
  inputSchema: z.object({ name: z.string() }),
}, async ({ name }) => ({
  content: [{ type: "text", text: `Hello, ${name}!` }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

Run: `npx tsc && node dist/server.js` (stdio) or configure in `.mcp.json` for Claude Code.

## Common Patterns

### Wrapping an HTTP API

```typescript
server.registerTool("api-request", {
  description: "Make a request to the internal API",
  inputSchema: z.object({
    endpoint: z.string().describe("API endpoint path"),
    method: z.enum(["GET", "POST", "PUT", "DELETE"]).default("GET"),
    body: z.string().optional().describe("Request body as JSON string"),
  }),
}, async ({ endpoint, method, body }) => {
  try {
    const response = await fetch(`https://api.internal.com${endpoint}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ?? undefined,
    });
    const data = await response.text();
    return { content: [{ type: "text", text: data }] };
  } catch (err: any) {
    return { content: [{ type: "text", text: `API error: ${err.message}` }], isError: true };
  }
});
```

### Input Validation with Zod

Zod schemas provide automatic validation. Use `.describe()` for parameter documentation:

```typescript
const inputSchema = z.object({
  query: z.string().min(1).describe("Search query"),
  limit: z.number().int().min(1).max(100).default(10).describe("Max results"),
  sort: z.enum(["relevance", "date", "name"]).default("relevance"),
  filters: z.object({
    type: z.string().optional(),
    dateAfter: z.string().optional(),
  }).optional(),
});
```

Zod validates inputs before the handler runs. Invalid inputs return an error automatically.
