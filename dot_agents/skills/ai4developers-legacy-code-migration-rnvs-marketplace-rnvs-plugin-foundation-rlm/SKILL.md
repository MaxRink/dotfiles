---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-rlm
description: >
  Run a Recursive Language Model-style loop for long-context tasks.
  Uses a persistent Python REPL and rlm-subcall-agent subagent.
  Invoke when analyzing documents, logs, or codebases exceeding
  context limits. Supports chunking, iterative sub-LLM calls, and
  evidence aggregation. Supports single-file and multi-file modes.
model: claude-opus-4-5@20251101
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Task
user-invocable: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm-stop-hook.sh"
          timeout: 30
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/rlm by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# rlm (Recursive Language Model workflow)

Use this Skill when:
- The user provides a very large context file (docs, logs, transcripts, code)
- The context won't fit comfortably in the chat context window
- You need to iteratively inspect, search, chunk, and extract information
- You can delegate chunk-level analysis to a subagent

## CRITICAL: rlm-subcall-agent is an AGENT, NOT a skill

> **DO NOT use `Skill(rlm-subcall-agent)`** - this will fail with "Unknown skill" error.
>
> **ALWAYS use `Task(subagent_type="rlm-subcall-agent")`** to invoke chunk analysis.
>
> The `rlm-subcall-agent` is a **subagent** defined in the plugin's `agents/` directory.
> It must be invoked via the Task tool, not the Skill tool.

## Mental model

```
┌─────────────────────────────────────────────────┐
│ Root LLM (this conversation, Opus)              │
│   ↓                                             │
│ Persistent REPL (rlm_repl.py)                   │
│   ↓                                             │
│ Sub-LLM (rlm-subcall-agent, via Task tool)      │
│   - Called with: Task(subagent_type="rlm-subcall-agent")
│   - NOT: Skill(rlm-subcall-agent) ← WRONG!     │
└─────────────────────────────────────────────────┘
```

## Inputs

This Skill reads `$ARGUMENTS`. Accept these patterns:

### Single-file mode (original)
- `context=<path>` (required): path to the large context file
- `query=<question>` (required): what the user wants to know

### Multi-file mode (new)
- `context_dir=<path>` (required): path to directory containing files
- `pattern=<glob>` (optional, default "*"): glob pattern for file matching
- `query=<question>` (required): what the user wants to know

### Common options
- `chunk_chars=<int>` (optional, default 200000): characters per chunk
- `overlap_pct=<float>` (optional, default 0.1): overlap percentage between chunks
- `mode=<dependencies|business_rules>` (optional, default "dependencies"): analysis mode
- `quality_mode=<default|high>` (optional, default "default"): model quality
  - `default`: Use Haiku for fast scanning
  - `high`: Use Sonnet for complex analysis
- `exclude=<pattern>` (optional): exclusion pattern (can repeat)
- `exclude_from=<path>` (optional): JSON file with excluded_scope array

### Analysis Modes

| Mode | Use Case | Output Fields |
|------|----------|---------------|
| `dependencies` | Phase 1 code analysis | `dependencies[]`, `keyword_matches[]` with file:line |
| `business_rules` | Phase 3 rule extraction | `business_rules[]` with pattern, evidence, error_code |

**mode=dependencies (Phase 1 Integration)**

Used by Phase 1 workflow for large codebase analysis (>50K LOC):
- Extracts package/procedure calls with source file and line
- Counts keyword occurrences with sample line numbers
- Identifies #include and source statements
- Results transform to file-inventory.json via transformer layer

**mode=business_rules (Phase 3 Integration)**

Used by Phase 3 workflow for business rule extraction:
- Identifies validation patterns, error codes, state transitions
- Two-stage workflow: quick scan (Haiku) → user selection → deep dive (Sonnet)
- Enables specialist skill integration for error code enrichment
- Results transform to ruletable.json via transformer layer

If arguments are missing, ask for:
1. The context file/directory path
2. The query/question

## Step-by-step procedure

### Mode Selection

Choose mode based on arguments:

**Single-file mode:** When `context=<path>` is provided
**Multi-file mode:** When `context_dir=<path>` is provided

---

## Single-File Mode Procedure

### Step 1: Initialize the REPL

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init <context_path>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py status
```

### Step 2: Scout the context

```bash
# View beginning
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py exec -c "print(peek(0, 3000))"

# View end
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py exec -c "print(peek(len(content)-3000, len(content)))"

# Search for patterns
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py exec -c "print(grep('keyword', max_matches=5))"
```

### Step 3: Choose a chunking strategy

- **Semantic chunking**: If format is clear (markdown headings, JSON, timestamps)
- **Character chunking**: Otherwise, use `chunk_chars` with optional `overlap_pct`
- **Filter-first**: Use `grep()` to find relevant sections, then chunk those

### Step 4: Materialize chunks as files

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py exec <<'PY'
paths = write_chunks('.claude/rlm_state/chunks', size=200000, overlap=0)
print(f"Created {len(paths)} chunks")
for p in paths[:5]:
    print(p)
PY
```

### Step 5: Subcall loop (delegate to rlm-subcall-agent)

For each chunk file, invoke the rlm-subcall-agent subagent:

```
Task(subagent_type="rlm-subcall-agent"):
  Query: {user_query}
  Chunk file: {chunk_path}
```

Collect results:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py exec -c "add_buffer('''<paste subagent JSON>''')"
```

If a subagent returns `answer_if_complete`, consider early termination.

### Step 6: Synthesis

Once evidence is collected:

1. Export buffers if needed:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py export-buffers .claude/rlm_state/all_findings.txt
   ```

2. Synthesize the final answer in the main conversation

3. Mark completion with:
   ```
   FINAL: [Your complete answer here]
   ```

---

## Multi-File Mode Procedure

### Step 1: Initialize from directory

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init-dir <context_dir> \
  --pattern "<glob_pattern>" \
  --recursive \
  --exclude "test/**" \
  --exclude-from <feature_definition.json>
```

This creates:
- Session-based state in `.claude/rlm_state/session_<id>/`
- `chunks_manifest.json` with file boundary metadata
- Chunk files with FILE_START/FILE_END markers

### Step 2: Review session info

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py sessions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state .claude/rlm_state/session_<id>/state.pkl status
```

### Step 3: Explore the content

```bash
# Using session state
STATE=".claude/rlm_state/session_<id>/state.pkl"

# View files
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state $STATE exec -c "
print('Session:', get_session_id())
print('Files:', len(get_files()))
for f in get_files()[:10]:
    print(f'  {f[\"path\"]}: {f[\"lines\"]} lines')
"

# Search with file context
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state $STATE exec -c "
hits = grep('RAISE_APPLICATION_ERROR', max_matches=10)
for h in hits:
    info = file_at_offset(h['span'][0])
    if info:
        print(f'{info[\"path\"]}:{info[\"line\"]}: {h[\"match\"][:50]}')
"
```

### Step 4: Review chunks manifest

```bash
cat .claude/rlm_state/session_<id>/chunks_manifest.json | head -50
```

The manifest contains:
- `session_id`: Unique session identifier
- `total_files`: Number of source files
- `total_chunks`: Number of chunks created
- `chunks[]`: Each chunk with `files_contained` metadata

### Step 5: Subcall loop with file context

For each chunk, invoke rlm-subcall-agent with mode:

```
Task(subagent_type="rlm-subcall-agent"):
  Mode: {mode}  # "dependencies" or "business_rules"
  Query: {user_query}
  Chunk file: .claude/rlm_state/session_<id>/chunks/{chunk_id}.txt
  Manifest: .claude/rlm_state/session_<id>/chunks_manifest.json
```

Run in batches of 10 for efficiency.

### Step 6: Aggregate results

Collect all subagent outputs. Each response includes:
- `files_in_chunk`: Files covered by this chunk
- `dependencies[]` or `business_rules[]`: Findings with file:line citations

### Step 7: Transform to target format

Apply phase-specific transformer:

**For Phase 1 (dependencies mode):**
- Map to file-inventory.json format
- Compute scoring_breakdown from keyword counts
- Set read_method: "rlm_delegated"

**For Phase 3 (business_rules mode):**
- Auto-generate rule_id, rule_name
- Group by domain
- Set validation_status: "pending"

### Step 8: Synthesis

Mark completion with:
```
FINAL: [Your complete answer here]
```

---

## Quality Mode

| Mode | Model | Use Case |
|------|-------|----------|
| `default` | claude-haiku-4-5@20251001 | Fast scanning, simple patterns |
| `high` | claude-sonnet-4-5@20250929 | Complex business rules, subtle patterns |

When using `quality_mode=high`, update Task calls:
```
Task(subagent_type="rlm-subcall-agent", model="sonnet"):
  ...
```

---

## Guardrails

- Do NOT paste large raw chunks into the main chat context
- Use the REPL to locate exact excerpts; quote only what you need
- Subagents cannot spawn other subagents - orchestration stays here
- Keep state files under `.claude/rlm_state/`
- The Stop-Hook will block early termination until you write FINAL:
- In multi-file mode, always preserve file:line citations

## Interrupt Recovery

If processing is interrupted (Ctrl+C or timeout), partial results are automatically saved:

```bash
# Partial results saved to session directory:
.claude/rlm_state/session_<id>/partial_results.json
```

The Stop-Hook will detect and report partial results in the continuation prompt.

To use partial results during processing:
```python
# After processing each chunk, save the result:
add_partial_result({"chunk_id": "chunk_0005", "findings": [...]})

# When complete, clear the buffer:
clear_partial_results()
```

## REPL Helper Functions

| Function | Description |
|----------|-------------|
| `peek(start, end)` | View slice of content |
| `grep(pattern, max_matches, window)` | Regex search with context |
| `chunk_indices(size, overlap)` | Compute chunk boundaries |
| `write_chunks(out_dir, size, overlap)` | Materialize chunks as files |
| `add_buffer(text)` | Accumulate intermediate results |
| `file_at_offset(offset)` | Get file:line for offset (multi-file mode) |
| `get_files()` | List all files (multi-file mode) |
| `get_session_id()` | Current session ID (multi-file mode) |
| `add_partial_result(result)` | Save result for interrupt recovery |
| `clear_partial_results()` | Clear partial results on success |

## Available Variables

| Variable | Description |
|----------|-------------|
| `context` | Dict with `{path, loaded_at, content}` |
| `content` | String alias for `context['content']` |
| `buffers` | List of accumulated results |

## CLI Commands

```bash
# Single-file initialization
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init <file>

# Multi-file initialization
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py init-dir <directory> --pattern "*.sql" --recursive

# List sessions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py sessions

# Check status
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state <state_file> status

# Execute code
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state <state_file> exec -c "<code>"

# Export buffers
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state <state_file> export-buffers <output_file>

# Reset
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py --state <state_file> reset
```

## Debugging

```bash
# REPL status
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py status --show-vars

# List all sessions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py sessions

# Reset state
python3 ${CLAUDE_PLUGIN_ROOT}/skills/rlm/scripts/rlm_repl.py reset
rm -rf .claude/rlm_state/
```
