---
name: psa-portal-soc-capture
description: Use when capturing, downloading, refreshing, answering, or filling Statement of Compliance (SoC) requirements from the Telekom PSA Portal for T-CaaS systems. Includes the proxy-backed Chromium workflow, DevTools automation, system snapshots, SoC ZIP export, XLSX/HTML/PDF extraction, answer templates, validation, and browser filling.
---

# PSA Portal SoC Capture

Use this skill to pull SoC requirement artifacts from `https://psa-portal.telekom.de/intranet-ui/` into a local workspace.

## Core Workflow

1. Start Chromium with Telekom proxy settings and DevTools enabled:

```bash
chromium-browser \
  --remote-debugging-port=9223 \
  --user-data-dir=/tmp/psa-portal-codex-chrome-proxy \
  --no-first-run \
  --proxy-server=http://sia-lb.telekom.de:8080 \
  --proxy-bypass-list="localhost;127.0.0.1" \
  --new-window "https://psa-portal.telekom.de/intranet-ui/"
```

2. If the portal is not already authenticated, let the user log in manually in that browser.

3. Use the bundled script from the repository or copied skill directory:

```bash
python -m venv tcaas-psa/.venv
tcaas-psa/.venv/bin/python -m pip install -r tcaas-psa/skill/psa-portal-soc-capture/requirements.txt
```

The `pip` script can have stale shebangs after a folder move; prefer `tcaas-psa/.venv/bin/python -m pip`.

4. Capture or export with `scripts/psa_capture.py`.

## Known Systems

- T-CaaS Core: `system=375203894`
- T-CaaS DT-Technik / DTT: `system=375203895`

## Commands

Snapshot a system page and SoC manifest:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  --port 9223 snapshot \
  --system-id 375203895 \
  --slug dtt \
  --out-dir tcaas-psa/artifacts/dtt/snapshots
```

Download all available SoCs for a system:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  --port 9223 download-socs \
  --system-id 375203894 \
  --slug tcaas-core \
  --snapshot-dir tcaas-psa/artifacts/tcaas-core/snapshots \
  --download-dir tcaas-psa/artifacts/tcaas-core/downloads
```

Extract the downloaded workbook:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  extract-xlsx \
  --xlsx tcaas-psa/artifacts/tcaas-core/extracted/Statement_of_Compliance_T-CaaS_Core.xlsx \
  --slug tcaas-core \
  --out-dir tcaas-psa/artifacts/tcaas-core/extracted
```

Render workbook requirements and current explanations into Markdown:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  render-markdown \
  --xlsx tcaas-psa/artifacts/tcaas-core/extracted/Statement_of_Compliance_T-CaaS_Core.xlsx \
  --slug tcaas-core \
  --out-dir tcaas-psa/artifacts/tcaas-core/markdown
```

Render the downloaded HTML export into Markdown. Prefer this for static requirement text, Motivation, references, ID, and Requirement-ID:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  render-html-markdown \
  --html tcaas-psa/artifacts/tcaas-core/extracted/Anforderungen_T-CaaS_Core.html \
  --slug tcaas-core \
  --out-dir tcaas-psa/artifacts/tcaas-core/html-markdown
```

Create the common answer file. This stores portal answers in `psa_answers_v1` JSON and preloads any current statements/explanations from the workbook and browser capture:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_answers.py \
  make-template \
  --html tcaas-psa/artifacts/tcaas-core/extracted/Anforderungen_T-CaaS_Core.html \
  --manifest tcaas-psa/artifacts/tcaas-core/snapshots/tcaas-core_soc_manifest.tsv \
  --xlsx tcaas-psa/artifacts/tcaas-core/extracted/Statement_of_Compliance_T-CaaS_Core.xlsx \
  --browser-fields tcaas-psa/artifacts/tcaas-core/browser-fields/tcaas-core_field_inspection.json \
  --slug tcaas-core \
  --system-id 375203894 \
  --system-name "T-CaaS Core Rel. 1" \
  --out tcaas-psa/answers/tcaas-core_answers.template.json
```

Validate an edited answer file before using the browser:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_answers.py \
  validate \
  --answers tcaas-psa/answers/tcaas-core_answers.template.json
```

Preflight portal filling before opening live sheets. This checks validation, answer statuses, manifest matching, and how many rows the selected status gate would process:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_answers.py \
  preflight-fill \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json \
  --manifest tcaas-psa/artifacts/tcaas-core/snapshots/tcaas-core_soc_manifest.tsv \
  --out tcaas-psa/analysis/soc-answers/portal_fill_preflight_default.json
```

By default, `fill-browser` and `preflight-fill` process only `answer.status == approved_for_portal`. If a reviewed answer set intentionally remains `ready_for_review`, pass `--required-status ready_for_review` and store the preflight report before running a browser dry-run. `fill-browser` refuses to open live sheets when any selected answer cannot be matched to the supplied SoC manifest.

Dry-run portal filling against an authenticated browser. This matches answer rows to rendered portal fields but does not modify anything:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_answers.py \
  --port 9223 fill-browser \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json \
  --manifest tcaas-psa/artifacts/tcaas-core/snapshots/tcaas-core_soc_manifest.tsv \
  --required-status ready_for_review \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_fill.dry-run.json
```

Fill fields without saving by adding `--apply`. Fill fields and click the portal `Speichern` button per changed sheet by using `--save`. Do not use either flag until the dry-run report has been reviewed.

Inspect live browser fields for every SoC sheet in a manifest:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  --port 9223 inspect-fields \
  --manifest tcaas-psa/artifacts/tcaas-core/snapshots/tcaas-core_soc_manifest.tsv \
  --slug tcaas-core \
  --out-dir tcaas-psa/artifacts/tcaas-core/browser-fields
```

List visible systems from `Meine Systeme`:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/psa-portal-soc-capture/scripts/psa_capture.py \
  --port 9223 list-systems
```

## Capture Notes

- Direct portal access timed out; explicit proxy access via `http://sia-lb.telekom.de:8080` worked.
- The portal is a PrimeFaces/JSF app. The script uses Chrome DevTools Protocol to interact with the already-authenticated browser instead of replaying credentials.
- Bulk export uses the page's "select all" checkbox and "bulk export" button. It writes the portal ZIP to the configured download directory.
- If a page says `Keine SoCs`, do not modify system properties unless the user explicitly asks. Store the snapshot and zero-count manifest as the current portal truth.
- For T-CaaS DT-Technik / DTT on 2026-06-11, the portal showed no SoCs; the page also indicated incomplete system properties. Treat the zero-row manifest as the portal truth unless PSA later exposes rows.
- The live SoC browser fields observed on 2026-06-11 were: one `Statement` radio group per requirement (`SOC`, `SOPC`, `SONC`, `NA`), a `Begruendung` textarea (`idExplanationText`), a note textarea (`idNoteInputField`), a note visibility checkbox (`idExternallyVisible_input`), and read-only visible notes from other users (`idExternText`).
- For `SOPC`, `SONC`, and `NA`, the process text says a justification must be provided. Treat that justification as the authoritative answer narrative; notes are not a substitute.
- Store answer data in `psa_answers_v1` JSON. See `references/answers-format.md` and `references/psa_answers_v1.schema.json`.
- Requirement-IDs are reused across some sheets. Use the generated `answerKey`, which includes system and sheet context, instead of Requirement-ID alone.
- `scripts/psa_answers.py fill-browser` defaults to dry-run. It only changes browser fields with `--apply`, and only clicks `Speichern` with `--save`.
- The ZIP export contains three useful static artifacts:
  - `Statement_of_Compliance_*.xlsx`: structured rows, existing statement choices, current `Begruendung`, test/review columns.
  - `Anforderungen_*.html`: best static source for full requirement text, Motivation, SDM/DSGVO/BCRP references, export ID, and Requirement-ID.
  - `Anforderungen_*.pdf`: human-readable archival copy; extract with `pdftotext` for search.
- Use browser inspection only for live UI state and field IDs, or when checking notes/current unsaved portal rendering. Static requirement content should be verified against the downloaded HTML/PDF/XLSX.

## Outputs

Expected artifact layout:

```text
tcaas-psa/
  artifacts/
    tcaas-core/
      downloads/
      extracted/
      markdown/
      browser-fields/
      snapshots/
    dtt/
      downloads/
      snapshots/
  skill/psa-portal-soc-capture/
```

Keep raw portal files (`.zip`, `.xlsx`, `.html`, `.pdf`) plus extracted JSON/CSV outputs. The raw files are the source of truth; CSV/JSON files are convenience artifacts for search, diffing, and downstream automation.
