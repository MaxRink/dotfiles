# PSA Answer Format

Use `psa_answers_v1` JSON for storing PSA SoC answers before filling the portal.

## Required Workflow

1. Generate a template from the downloaded HTML export, manifest, workbook, and browser field inspection.
2. Edit only the `answer` object for each requirement.
3. Validate the answer file.
4. Run `preflight-fill` to verify the answer status gate and manifest matching before opening the browser.
5. Run `fill-browser` first without `--apply` or `--save` to dry-run live field matching.
6. Use `--apply` to fill the authenticated browser without saving, or `--save` to fill and click `Speichern`.

For large systems, keep the full template as the audit/research source and generate a compact fill file for portal operations:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  export-fillable-answers \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json
```

The compact file keeps `schema`, system metadata, sheet ID/href, requirement number/ID, and `answer` values. It omits static requirement text, motivation, current portal values, and browser field IDs, so it remains usable by `fill-browser` while producing much smaller diffs.

## Answer Object

Each item in `answers[]` has a stable `answerKey` and these important fields:

- `sheet`: portal sheet context. `sheetId` and `href` come from the manifest.
- `requirement`: canonical requirement text, additional details, motivation, export ID, and Requirement-ID from the HTML export.
- `current`: values captured from XLSX/browser at template generation time.
- `portalFields`: live browser field IDs observed during capture. These are useful for audit/debugging but are not required for filling.
- `answer`: editable values used by `fill-browser`.

Set `answer.statement` to one of:

- `SOC`: fulfilled.
- `SOPC`: partially fulfilled.
- `SONC`: not fulfilled.
- `NA`: not applicable.
- Empty string: skip during fill.

For `SOPC`, `SONC`, and `NA`, fill `answer.explanation`. This maps to the portal `Begruendung` textarea. `answer.note` maps to `Meine Notiz`; it is not a substitute for `Begruendung`.

`fill-browser` defaults to `answer.status == approved_for_portal`. If the answer set is still in `ready_for_review`, the default fill command intentionally processes zero rows. Use `preflight-fill` to confirm that state. After manual review, either promote approved rows to `approved_for_portal` or intentionally pass `--required-status ready_for_review` for a reviewed fill run.

## Why Requirement-ID Alone Is Not Enough

Requirement-IDs are reused across some sheets. A fill key must include sheet context plus requirement number/ID. The generated `answerKey` follows:

```text
<system-id>|<sheet-id>|req-<number>|<requirement-id>
```

The fill script navigates one sheet at a time and matches by requirement number first. Requirement-ID is kept as an audit/check field because some rendered portal rows have no Requirement-ID and some IDs are reused across sheets.
