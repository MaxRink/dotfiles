
# Code Review Concern Reference

Your concern templates are available at [review-templates.md](review-templates.md) —
consult the template for your specific concern.

## Process

1. Consult the template for your assigned concern
2. Run the grep patterns listed in the template BEFORE reading any files (grep-first)
3. Read source files only where grep found matches or where a full read is warranted by tier
4. Write the findings file to the output path in your prompt

## Output Conventions

- Write to `.migration/<feature>/validation/code-review/findings/<concern>-findings.md`
- Evidence-based: every finding references `file/path:line`
- Severity per finding: `critical` | `warning` | `minor`
- Structured headers (`##` / `###`) — one section per severity level
- Skip any template section with no findings — do not produce empty sections
