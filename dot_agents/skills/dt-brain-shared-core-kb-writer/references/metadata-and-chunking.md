# Metadata & AI Optimization

## YAML Front Matter for RAG Systems

Include metadata in YAML front matter for AI indexing and filtering.

### Required Fields (all articles)

```yaml
---
title: "Fix VPN Authentication Failure (Error 691)"
type: troubleshooting  # or: how-to, configuration, comparison
category: network      # primary category
tags: [vpn, authentication, cisco-anyconnect, windows]  # 3-8 relevant tags
audience: internal     # or: external, public
created: 2024-02-09    # YYYY-MM-DD
updated: 2024-02-09    # YYYY-MM-DD
---
```

### Optional Fields (when relevant)

```yaml
product: "Cisco AnyConnect"
version: "4.10.06079"
os: ["windows-11", "windows-10"]
severity: high         # critical, high, medium, low
skill_level: beginner  # beginner, intermediate, advanced
time_required: "10 minutes"
related_errors: ["691", "800", "619"]
deprecated: false      # true if article superseded
replaces: "KB-2023-045"  # if updating old article
author: "jane.smith@company.com"
reviewed_by: "john.doe@company.com"
```

## Semantic Chunking for RAG

### Why Chunking Matters

RAG systems break documents into chunks (200-500 tokens) for semantic search. Poor chunking splits related content, degrading AI retrieval accuracy.

### Chunking Strategy by Article Type

| Article Type | Optimal Chunk Boundaries | Chunk Size Target | Overlap |
|--------------|--------------------------|-------------------|---------|
| **Troubleshooting** | Section boundaries (Environment, Problem, Cause, Resolution) | 300-400 tokens | 50 tokens |
| **How-To (short)** | Step boundaries (Step 1, Step 2, etc.) | 250-350 tokens | 30 tokens |
| **How-To (long)** | Major sections + critical steps | 400-500 tokens | 50 tokens |
| **Configuration** | Configuration blocks, option groups | 300-450 tokens | 40 tokens |

### Section Separation Rules

**ALWAYS separate** these sections (never chunk together):

1. **Problem ≠ Resolution**: Symptoms must be separate from solutions for AI to match user queries to problems, not solutions
2. **Cause ≠ Resolution**: Root cause analysis separate from fix steps
3. **Environment ≠ Problem**: Context separate from symptoms
4. **Prerequisites ≠ Steps**: Requirements separate from procedures

**✅ GOOD - Separated Sections**:
```markdown
<!-- Chunk 1: PROBLEM only -->
## Problem
When connecting to company VPN, employees receive error:
"VPN Error 691: The remote connection was denied..."
[full problem description]

<!-- AI retrieves THIS when user asks "why vpn failing?" -->

<!-- Chunk 2: CAUSE only -->
## Cause
VPN authentication fails because affected employees' accounts were added to "VPN-RequiresMFA" security group...

<!-- Chunk 3: RESOLUTION only -->
## Resolution
Step 1: Enroll in Duo MFA
[full resolution steps]
```

### AI-Friendly Writing Rules

- Avoid implicit references ("it", "this", "that") — use specific nouns
- Define all acronyms on first use
- Use absolute URLs (not relative links)
- Specify language on all code blocks (```bash, ```yaml, etc.)
