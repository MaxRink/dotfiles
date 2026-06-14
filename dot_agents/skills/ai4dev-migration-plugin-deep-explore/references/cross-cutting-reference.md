
# Cross-Cutting Analysis Reference

Your concern templates are available at [cross-cutting-templates.md](cross-cutting-templates.md) —
consult the template for your specific concern.

## Process

1. Read the stack doc files listed in your prompt to understand what each stack contains
2. Consult the cross-cutting template for your assigned concern
3. Read source files only where the stack docs lack precision on your concern
4. Write the cross-cutting documentation file to the output path in your prompt

## Output Conventions

- Write to `.migration/docs/cross-cutting/<concern-name>.md`
- Evidence-based: every claim references `file/path:line`
- Concise bullets, structured headers (`##` / `###`)
- Skip any template section that has no content — do not produce empty sections
