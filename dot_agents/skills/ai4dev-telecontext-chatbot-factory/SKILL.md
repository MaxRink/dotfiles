---
name: ai4dev-telecontext-chatbot-factory
description: >-
  Interact with ChatbotFactory chatbots via Telecontext. Use when the user wants to
  list available chatbots, query a specific chatbot, or interact with AI chatbots
  hosted on the ChatbotFactory platform. Also use when the user references
  "chatbot factory", "my chatbots", or wants to ask a question to a specific chatbot.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telecontext/skills/chatbot-factory by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# ChatbotFactory - Chatbot Interactions

Interact with AI chatbots hosted on the ChatbotFactory platform.

The user's query is: "$ARGUMENTS"

## Tools

### `chatbot_factory_list_chatbots` (no params)
Lists all chatbots the user has access to, including IDs, names, descriptions, and types.
Use this first to discover available chatbots and get the chatbot ID needed for queries.

### `chatbot_factory_query_chatbot`
Send a question to a specific chatbot.

Parameters:
- `query` (required): The question to ask (max 16384 chars)
- `chatbotId` (required): The chatbot ID (format: `cf-12a3b4c56789`). Get this from `list_chatbots`.

## Workflow

```
chatbot_factory_list_chatbots → find the right chatbot + its ID
    ↓
chatbot_factory_query_chatbot(chatbotId, query) → ask your question
```

## Tips

- Always list chatbots first if you don't know the chatbot ID
- Each chatbot has its own knowledge base and capabilities - pick the right one for the question
- These chatbots have organization-specific knowledge beyond what `query_company_knowledge` provides
