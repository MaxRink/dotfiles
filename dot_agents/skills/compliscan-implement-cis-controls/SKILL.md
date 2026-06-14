---
name: compliscan-implement-cis-controls
description: "Implement CIS benchmark controls into compliscan YAML files from a CSV input. Use when: adding a new OS version to benchmarks, importing CIS controls from CSV, adding id_map entries to existing checks, creating new audit checks for version-specific differences. Triggers: 'implement controls', 'add CIS', 'new OS version benchmark', 'import CSV controls'."
argument-hint: "Provide the CSV file path and target OS version (e.g., 'RHEL 8', 'Ubuntu 24.04', 'SUSE 15')"
---

<!-- Imported from devsecops-tools/public/compliscan/.github/skills/implement-cis-controls by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Implement CIS Controls into Compliscan Benchmarks

Add CIS benchmark controls for a new OS version into the compliscan embedded YAML benchmark files. Works with any OS under `benchmarks/linux/` (rhel, ubuntu, suse, amazon).

## Input Requirements

- **CSV file** with columns: `Section #`, `Recommendation #`, `Profile`, `Title`, `Audit Procedure`
- **Target OS** and **major version** (e.g., RHEL 8 → key `'8'`, Ubuntu 24.04 → key `'24.04'`, Amazon 2023 → key `'2023'`)

## Architecture Context

- Benchmarks live in `compliscan/internal/benchmark/benchmarks/linux/<os>/level{1,2}/section*.yaml`
- `embed.go` uses `//go:embed benchmarks` — new YAML files are auto-included at compile time
- Each check has an `id_map` where keys are OS major versions and values are CIS control IDs
- `filterByVersion()` in `benchmark.go` does exact/prefix matching on these keys
- Audit types: `command`, `file_content`, `file_permission`, `sysctl`, `service_status`

## Procedure

### Phase 1: Analysis

1. **Read the CSV** to understand all controls, their sections, levels, and audit procedures
1. **Determine the version key** — ask the user which `id_map` key to use (e.g., `'8'` for RHEL 8)
1. **List existing YAML files** for the target OS:

   ```bash
   find compliscan/internal/benchmark/benchmarks/linux/<os> -name '*.yaml' | sort
   ```

1. **Read existing YAML files** section by section to understand current checks

### Phase 2: Mapping

For each control in the CSV, classify it into one of three categories:

| Category | Condition | Action |
|----------|-----------|--------|
| **Reuse** | Existing check has identical audit command/type | Add version key to existing `id_map` |
| **New entry** | Same concept but different audit command (e.g., different package name) | Create a new check entry with only the new version key |
| **New file** | No existing file covers this section | Create a new YAML file following naming convention `section{N}_{M}.yaml` |
| **Skip** | Control is manual/not automatable (e.g., "review and verify") | Document as skipped |

**Decision criteria for Reuse vs New entry:**

- Compare the audit command from the CSV with existing checks
- If the command, expected output, and match type are identical → **Reuse**
- If the package name, service name, or path differs → **New entry**
- Pay attention to: package names (e.g., `cockpit` vs `cockpit-ws`), binary paths (e.g., `xorg-x11-server-Xorg` vs `xorg-x11-server-common`), command syntax differences

### Phase 3: Implementation

Work section by section. For each section file:

1. **Read the full file content** before editing (need exact strings for replacements)
1. **Add `id_map` entries** to existing checks — always insert the new key in numerical order:

   ```yaml
   # Before:
   - id_map:
       '9': 2.1.1
       '10': 2.1.1

   # After (adding '8'):
   - id_map:
       '8': 2.1.1
       '9': 2.1.1
       '10': 2.1.1
   ```

1. **Create new check entries** for version-specific differences — place them after related existing checks:

   ```yaml
   - id_map:
       '8': 2.1.3
     title: Ensure cockpit web services are not in use
     level: 2
     section: 2.1 Configure Server Services
     audit:
       type: command
       command: systemctl is-enabled cockpit.socket 2>/dev/null; rpm -q cockpit-ws 2>/dev/null
       expected: masked|disabled|not installed|not-found
       match: regex
     tags:
       - services
       - cockpit
   ```

1. **Use `multi_replace_string_in_file`** for batching multiple id_map additions in one file (up to ~10 per call)
1. **Create new YAML files** when needed — follow the existing structure exactly

### Phase 4: Validation

After each section (or batch of sections):

```bash
cd compliscan && go build ./... && go test ./...
```

Both must pass before proceeding to the next section.

## YAML Check Structure Reference

```yaml
- id_map:
    '<version_key>': <cis_control_id>
  title: <control title from CSV>
  level: <1 or 2>
  section: <section number> <section name>
  audit:
    type: <command|file_content|file_permission|sysctl|service_status>
    command: <shell command>          # for type: command
    path: <file path>                 # for file_content, file_permission
    key: <sysctl key>                 # for type: sysctl
    service: <service name>           # for type: service_status
    expected: <expected value/pattern>
    match: <exact|regex|contains>
  tags:
    - <category>
    - <subcategory>
```

## Version Key Reference

| OS | Example Versions | Key Format |
|----|-----------------|------------|
| RHEL | 8, 9, 10 | `'8'`, `'9'`, `'10'` |
| Ubuntu | 20.04, 22.04, 24.04 | `'20.04'`, `'22.04'`, `'24.04'` |
| SUSE | 15 | `'15'` |
| Amazon | 2, 2023 | `'2'`, `'2023'` |

## Common Pitfalls

- **Don't guess audit commands** — always compare CSV audit procedure with existing checks
- **Profile mapping**: "Level 1 - Server" → `level: 1` in `level1/` dir, "Level 2 - Server" → `level: 2` in `level2/` dir
- **Manual controls** (e.g., "Ensure only approved services are listening") cannot be automated — skip and document
- **Ordering**: Insert version keys in ascending numerical order within `id_map`
- **YAML indentation**: 2 spaces, consistent with existing files. Check entries are indented 2 spaces under `checks:`
- **Tags**: Reuse existing tags from similar checks; don't invent new tag categories
