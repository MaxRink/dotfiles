---
name: dt-brain-shared-core-kb-writer
description: This skill should be used when the user mentions "KB article", "knowledge base", "troubleshooting article", "how-to guide", "KCS", "KCS template", or needs to create, structure, or improve a knowledge base article optimized for both human readers and AI retrieval systems (RAG, semantic search).
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/core-kb-writer by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# KB Article Writer

Generate knowledge base articles using the Hybrid KCS (Knowledge-Centered Service) Template — optimized for human readability and AI retrieval accuracy.

## Workflow

Creating a KB article involves these steps:

1. **Determine article type** (troubleshooting, how-to, configuration, comparison)
2. **Write the title** using action verb + object + error code pattern
3. **Fill the template sections** (Environment → Problem → Cause → Resolution)
4. **Add YAML front matter** for RAG metadata
5. **Validate the article** (run `scripts/validate_kb.py`)

## Article Type Selection

| Article Type | Use When | Title Pattern | Primary Sections |
|--------------|----------|---------------|------------------|
| **Troubleshooting** | Error, failure, or unexpected behavior | [Verb] + [Object] + [Error Code] | Environment, Problem, Cause, Resolution |
| **How-To Guide** | Accomplish a task or configure something | How to [Action] + [Context] | Prerequisites, Steps, Verification, Troubleshooting |
| **Configuration** | Set up or customize a feature | Configure [Feature] for [Use Case] | Prerequisites, Configuration, Validation, Common Options |
| **Comparison** | Choose between options | [Feature A] vs [Feature B]: [Context] | Overview, Comparison Table, Recommendations, Migration |
| **Out of scope** | Postmortems, ADRs, API docs, runbooks | — | — |

## Title Rules

Use **[Action Verb] + [Specific Object] + [Error Code/Context]** for every title.

### Action Verb Selection

| Problem Type | Recommended Verbs |
|--------------|-------------------|
| System errors | Fix, Resolve, Clear, Troubleshoot |
| User account issues | Reset, Unlock, Restore, Recover |
| Configuration | Configure, Set Up, Enable, Disable |
| Performance | Optimize, Improve, Tune, Accelerate |
| Installation | Install, Deploy, Upgrade, Migrate |

### Title Examples

```
Fix VPN Authentication Failure (Error 691)
Resolve Database Connection Timeout (Error 2003)
How to Set Up Two-Factor Authentication for GitHub
Configure Email Notifications for Production Alerts
```

## Template Sections

### Environment (Context Layer)

Filter irrelevant results so AI does not suggest a Mac fix for Windows, and humans skip non-matching articles.

**Required fields**:
```yaml
Product/Service: [specific name and version]
Version: [exact version number]
Operating System: [OS name and version]
Environment: [Production, Staging, Development, Local]
User Role/Permissions: [Admin, Standard User, Guest, etc.]
```

**Optional fields** (include when relevant):
```yaml
Hardware: [CPU, RAM, disk space requirements]
Network: [VPN, proxy, firewall settings]
Browser: [for web applications]
Configuration: [specific settings that affect the issue]
```

### Problem / Symptom

The MOST CRITICAL section for AI semantic search. AI maps natural language queries to this text block.

Include ALL of these:
- Exact error code or message (copy-paste, in quotes or blockquote)
- Visual description (what the user sees on screen)
- User action that triggered the problem
- Expected vs actual behavior
- Frequency (always, sometimes, intermittent)

**Rules**:
1. Quote exact error text
2. Describe visuals explicitly ("red banner at top", "grayed-out button")
3. Use user perspective ("When I try to...", "After clicking...")
4. List symptoms only — NEVER mix in solutions

### Cause (Assessment)

Explain "The Why" — builds user trust and helps AI distinguish similar symptoms with different root causes.

Include:
- Root cause (technical explanation)
- Trigger condition (why the error occurred)
- Why the symptom manifests this way
- Connection to environment factors

Balance technical depth for engineers with clarity for end users.

### Resolution (Plan)

Provide clear, step-by-step instructions. Follow these rules:

1. Start with the most common solution
2. Number steps sequentially — one action per step
3. Include expected outcome after each critical step
4. Use exact command syntax in code blocks
5. Include verification step at end
6. Provide rollback/alternative if a step fails
7. Use imperative voice ("Click the...", "Run the...")

## YAML Front Matter

Add front matter at the top of every article for RAG indexing. See `references/metadata-and-chunking.md` for full field reference.

**Required fields**:
```yaml
---
title: "Fix VPN Authentication Failure (Error 691)"
type: troubleshooting
category: network
tags: [vpn, authentication, cisco-anyconnect, windows]
audience: internal
created: 2024-02-09
updated: 2024-02-09
---
```

## Key Rules for AI Optimization

1. **NEVER chunk Problem + Resolution together** — keep sections separate for accurate retrieval
2. **Avoid implicit references** ("it", "this", "that") — use specific nouns
3. **Define all acronyms** on first use
4. **Use absolute URLs** (not relative links)
5. **Specify language on all code blocks** (```bash, ```yaml, etc.)

See `references/metadata-and-chunking.md` for chunking strategies and `references/examples.md` for detailed ❌ BAD / ✅ GOOD pairs.

## Validation

Run the validation script to check article structure, front matter, and content quality:

```bash
python3 scripts/validate_kb.py <path-to-article.md>
```

The script checks:
- YAML front matter completeness
- Required sections present
- Title follows action verb pattern
- Error messages are properly quoted
- Resolution uses numbered steps with expected outcomes
- Code blocks have language specified

## Pre-Publish Checklist

**Structure**:
- [ ] Title uses [Action Verb] + [Object] + [Error Code] pattern
- [ ] All required sections present (Environment, Problem, Cause, Resolution)
- [ ] Problem section SEPARATE from Resolution (not mixed)
- [ ] Resolution uses numbered steps with expected outcomes

**Content Quality**:
- [ ] Environment specifies: product, version, OS, role
- [ ] Problem includes exact error code/message in quotes
- [ ] Cause explains root cause and why error manifested
- [ ] Resolution verified by testing
- [ ] Related articles linked at end

**AI Optimization**:
- [ ] YAML front matter complete (title, type, category, tags, audience, dates)
- [ ] No implicit references — use specific nouns
- [ ] All acronyms defined on first use
- [ ] Absolute URLs, code blocks have language specified
