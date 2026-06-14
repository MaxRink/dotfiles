#!/usr/bin/env node
/**
 * Example MCP server demonstrating tools and resources in TypeScript.
 *
 * This server provides file analysis utilities:
 * - file-stats: Get statistics about a file (lines, words, characters)
 * - search-text: Search for a regex pattern in files
 * - list-directory: List contents of a directory
 *
 * Plus a resource for server configuration.
 *
 * Usage:
 *     npx tsc && node dist/typescript-tool-server.js
 *
 * Configure in .mcp.json:
 *     {
 *       "mcpServers": {
 *         "file-tools": {
 *           "command": "node",
 *           "args": ["${CLAUDE_PLUGIN_ROOT}/servers/typescript-tool-server.js"]
 *         }
 *       }
 *     }
 */

import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";
import * as fs from "node:fs/promises";
import * as path from "node:path";

const server = new McpServer({ name: "file-tools", version: "1.0.0" });

// --- Tools ---

server.registerTool(
  "file-stats",
  {
    description:
      "Get statistics about a file: line count, word count, character count, and file size",
    inputSchema: z.object({
      path: z.string().describe("Path to the file to analyze"),
    }),
  },
  async ({ path: filePath }) => {
    try {
      const content = await fs.readFile(filePath, "utf-8");
      const stat = await fs.stat(filePath);
      const lines = content.split("\n");
      const words = content.split(/\s+/).filter(Boolean);

      const result = {
        path: path.resolve(filePath),
        lines: lines.length,
        words: words.length,
        characters: content.length,
        size_bytes: stat.size,
        empty_lines: lines.filter((line) => line.trim() === "").length,
      };

      return {
        content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
      };
    } catch (err: any) {
      const message =
        err.code === "ENOENT"
          ? `File not found: ${filePath}`
          : err.code === "EACCES"
            ? `Permission denied: ${filePath}`
            : `Error reading file: ${err.message}`;
      return {
        content: [{ type: "text" as const, text: `Error: ${message}` }],
        isError: true,
      };
    }
  }
);

server.registerTool(
  "search-text",
  {
    description: "Search for a regex pattern in files within a directory",
    inputSchema: z.object({
      pattern: z.string().describe("Regular expression to search for"),
      directory: z
        .string()
        .default(".")
        .describe("Directory to search in"),
      fileExtension: z
        .string()
        .optional()
        .describe("File extension filter, e.g. '.ts' or '.py'"),
    }),
  },
  async ({ pattern, directory, fileExtension }) => {
    let regex: RegExp;
    try {
      regex = new RegExp(pattern);
    } catch {
      return {
        content: [
          { type: "text" as const, text: `Error: Invalid regex pattern: ${pattern}` },
        ],
        isError: true,
      };
    }

    const matches: Array<{ file: string; line: number; text: string }> = [];
    const maxResults = 50;
    let filesSearched = 0;

    async function searchDir(dir: string): Promise<void> {
      let entries: Awaited<ReturnType<typeof fs.readdir>>;
      try {
        entries = await fs.readdir(dir, { withFileTypes: true });
      } catch {
        return;
      }

      for (const entry of entries) {
        if (matches.length >= maxResults) return;
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory() && !entry.name.startsWith(".")) {
          await searchDir(fullPath);
        } else if (entry.isFile()) {
          if (fileExtension && !entry.name.endsWith(fileExtension)) continue;
          try {
            const content = await fs.readFile(fullPath, "utf-8");
            filesSearched++;
            const lines = content.split("\n");
            for (let i = 0; i < lines.length; i++) {
              if (regex.test(lines[i])) {
                matches.push({
                  file: fullPath,
                  line: i + 1,
                  text: lines[i].trim().slice(0, 200),
                });
                if (matches.length >= maxResults) return;
              }
            }
          } catch {
            // Skip files that cannot be read
          }
        }
      }
    }

    await searchDir(directory);

    const result = {
      matches,
      files_searched: filesSearched,
      truncated: matches.length >= maxResults,
    };

    return {
      content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
    };
  }
);

server.registerTool(
  "list-directory",
  {
    description: "List contents of a directory with file types and sizes",
    inputSchema: z.object({
      path: z.string().default(".").describe("Directory path to list"),
      includeHidden: z
        .boolean()
        .default(false)
        .describe("Whether to include hidden files"),
    }),
  },
  async ({ path: dirPath, includeHidden }) => {
    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });
      const results: Array<{
        name: string;
        type: string;
        size_bytes?: number;
      }> = [];

      for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        if (!includeHidden && entry.name.startsWith(".")) continue;

        const entryInfo: { name: string; type: string; size_bytes?: number } = {
          name: entry.name,
          type: entry.isDirectory() ? "directory" : "file",
        };

        if (entry.isFile()) {
          const stat = await fs.stat(path.join(dirPath, entry.name));
          entryInfo.size_bytes = stat.size;
        }

        results.push(entryInfo);
      }

      const result = {
        path: path.resolve(dirPath),
        entries: results,
        count: results.length,
      };

      return {
        content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
      };
    } catch (err: any) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Error: ${err.code === "ENOENT" ? "Directory not found" : err.message}: ${dirPath}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Resources ---

server.registerResource(
  "server-info",
  "config://server-info",
  { description: "Server configuration and capabilities" },
  async (uri) => ({
    contents: [
      {
        uri: uri.href,
        text: JSON.stringify(
          {
            server: "file-tools",
            version: "1.0.0",
            tools: ["file-stats", "search-text", "list-directory"],
            cwd: process.cwd(),
          },
          null,
          2
        ),
        mimeType: "application/json",
      },
    ],
  })
);

// --- Start server ---

const transport = new StdioServerTransport();
await server.connect(transport);
