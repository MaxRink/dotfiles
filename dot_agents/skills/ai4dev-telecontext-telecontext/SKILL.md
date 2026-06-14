---
name: ai4dev-telecontext-telecontext
description: >-
  Query Deutsche Telekom IT's internal knowledge base. Use when the user asks about
  DT-IT internal topics, processes, documentation, guidelines, best practices,
  organizational structure, technical standards, or compliance requirements.
  Also use when the user says "ask telecontext", "search internal docs", "check DT policies",
  or references internal Telekom systems. Do NOT use for external/public documentation.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/telecontext by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Telecontext - DT-IT Internal Knowledge Base

Query Deutsche Telekom IT's internal knowledge using the `query_company_knowledge` tool.

The user's query is: "$ARGUMENTS"

## Tool

Use the `query_company_knowledge` Telecontext MCP tool with a specific, DT-IT-contextualized query string.

## Query Guidelines

1. **Be specific** - "how to deploy on TARDIS" not "how to deploy"
2. **Use internal names** - TARDIS, T-RAP, PSA, ChatbotFactory, Raccoon, LeanIX, etc.
3. **Scope it** - Narrow to: security, architecture, API specs, compliance, etc.

| Bad Query | Good Query |
|-----------|-----------|
| "API docs" | "TARDIS API catalog for service X" |
| "security" | "PSA requirements for new microservices" |
| "deployment" | "T-RAP deployment pipeline configuration" |
| "chatbot" | "ChatbotFactory chatbot integration guide" |

## Other Telecontext Skills

For specialized tasks, use the dedicated skills instead:
- `/telecontext:tardis` - TARDIS API catalog search and OpenAPI specs
- `/telecontext:psa` - Privacy and Security Assessment requirements
- `/telecontext:gitlab` - GitLab operations (issues, MRs, epics, pipelines)
- `/telecontext:jira` - Jira project management (issues, sprints, boards)
- `/telecontext:confluence` - Confluence wiki (search, read, create pages)
- `/telecontext:raccoon` - Raccoon/VictoriaMetrics monitoring and PromQL queries
- `/telecontext:chatbot-factory` - ChatbotFactory chatbot interactions
- `/telecontext:leanix` - LeanIX factsheet lookups (applications, governance, orgs)
- `/telecontext:feedback` - Submit feedback or view agent performance analytics

## Troubleshooting

- **No results**: Make query more specific to DT-IT context. This tool only has internal knowledge.
- **Auth errors**: Complete login when prompted. If token expired: Teleconsole > Authorization Services > revoke > reconnect > restart.
- **Connection issues**: Check `/mcp`. Internet URL: `https://telecontext.trap.ng.telekom.net/mcp` / Internal: `https://telecontext-internal.trap.prod.tap.telekom.de/mcp`
