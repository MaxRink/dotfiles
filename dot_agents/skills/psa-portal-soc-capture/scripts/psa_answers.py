#!/usr/bin/env python3
import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from psa_capture import (
    CdpClient,
    DEFAULT_BASE_URL,
    md_escape,
    navigate,
    one_line,
    parse_requirements_html,
    prepare_soc_sheet_for_capture,
    read_manifest,
    safe_filename,
    wait_ready,
    workbook_requirement_sheets,
    requirement_rows,
)


SCHEMA_NAME = "psa_answers_v1"
ALLOWED_STATEMENTS = {"", "SOC", "SOPC", "SONC", "NA"}
STATEMENT_LABEL_TO_CODE = {
    "Fulfilled (SoC)": "SOC",
    "Partially fulfilled (SoPC)": "SOPC",
    "Not fulfilled (SoNC)": "SONC",
    "Not applicable": "NA",
    "Erfuellt (SoC)": "SOC",
    "Teilweise erfuellt (SoPC)": "SOPC",
    "Nicht erfuellt (SoNC)": "SONC",
    "Nicht zutreffend": "NA",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def normalize_space(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def strip_sheet_prefix(value):
    text = normalize_space(value)
    text = re.sub(r"^\d+\)\s*", "", text)
    text = re.sub(r"^\d+(?:\.\d+)*(?:-\d+)?\s+", "", text)
    text = re.sub(r"^\d{5,}\s+", "", text)
    return text.strip()


def normalize_title(value):
    text = strip_sheet_prefix(value).casefold()
    text = text.replace("...", "")
    text = re.sub(r"[^0-9a-zäöüß]+", " ", text, flags=re.IGNORECASE)
    return normalize_space(text)


def compatible_titles(left, right):
    left_norm = normalize_title(left)
    right_norm = normalize_title(right)
    if not left_norm or not right_norm:
        return False
    return (
        left_norm == right_norm
        or (len(left_norm) >= 8 and right_norm.startswith(left_norm))
        or (len(right_norm) >= 8 and left_norm.startswith(right_norm))
    )


def text_key(value):
    text = normalize_space(value).casefold()
    return re.sub(r"[^0-9a-zäöüß]+", " ", text, flags=re.IGNORECASE).strip()


def statement_code(value):
    raw = normalize_space(value)
    if not raw:
        return ""
    upper = raw.upper()
    if upper in ALLOWED_STATEMENTS:
        return upper
    return STATEMENT_LABEL_TO_CODE.get(raw, "")


def requirement_number_from_key(value):
    match = re.search(r"\bReq\s+(\d+)\b", str(value or ""))
    return match.group(1) if match else ""


def manifest_by_normalized_title(manifest_rows):
    result = {}
    for row in manifest_rows:
        result[normalize_title(row.get("name", ""))] = row
    return result


def best_manifest_match(sheet_title, manifest_rows):
    normalized = normalize_title(sheet_title)
    by_title = manifest_by_normalized_title(manifest_rows)
    if normalized in by_title:
        return by_title[normalized]
    candidates = []
    for row in manifest_rows:
        row_title = normalize_title(row.get("name", ""))
        if normalized and (row_title.endswith(normalized) or normalized.endswith(row_title)):
            candidates.append(row)
    if len(candidates) == 1:
        return candidates[0]
    return None


def load_workbook_current_values(xlsx_path):
    if not xlsx_path:
        return {"by_text": {}, "by_sheet_number": {}}
    by_text = {}
    by_sheet_number = {}
    for sheet_title, rows in workbook_requirement_sheets(Path(xlsx_path)):
        for req in requirement_rows(rows):
            requirement_number = requirement_number_from_key(req.get("key", ""))
            current = {
                "sheetTitle": sheet_title,
                "sheetTitleNormalized": normalize_title(sheet_title),
                "key": req.get("key", ""),
                "requirementNumber": requirement_number,
                "requirementId": req.get("requirementId", ""),
                "statement": statement_code(req.get("statement", "")),
                "statementLabel": req.get("statement", ""),
                "explanation": req.get("explanation", ""),
                "securityTest": req.get("securityTest", ""),
                "reviewResult": req.get("reviewResult", ""),
                "reviewExplanation": req.get("reviewExplanation", ""),
                "excelRow": req.get("excelRow", ""),
            }
            by_text.setdefault(text_key(req.get("requirement", "")), []).append(current)
            by_sheet_number.setdefault((normalize_title(sheet_title), requirement_number), []).append(current)
    return {"by_text": by_text, "by_sheet_number": by_sheet_number}


def pick_workbook_candidate(candidates, requirement_id, number):
    if not candidates:
        return {}
    exact = [
        item
        for item in candidates
        if (not requirement_id or item.get("requirementId") == requirement_id)
        and (not number or item.get("requirementNumber") == str(number))
    ]
    if len(exact) == 1:
        return exact[0]
    id_only = [item for item in candidates if not requirement_id or item.get("requirementId") == requirement_id]
    if len(id_only) == 1:
        return id_only[0]
    return candidates[0]


def workbook_current_for_requirement(workbook_values, sheet_title, requirement_text, requirement_id, number):
    number = str(number or "")
    sheet_number_candidates = []
    for (workbook_sheet_title, workbook_number), candidates in workbook_values.get("by_sheet_number", {}).items():
        if workbook_number == number and compatible_titles(sheet_title, workbook_sheet_title):
            sheet_number_candidates.extend(candidates)
    picked = pick_workbook_candidate(sheet_number_candidates, requirement_id, number)
    if picked:
        return picked

    text_candidates = workbook_values.get("by_text", {}).get(text_key(requirement_text), [])
    return pick_workbook_candidate(text_candidates, requirement_id, number)


def load_browser_fields(browser_fields_path):
    if not browser_fields_path:
        return {}
    inspections = json.loads(Path(browser_fields_path).read_text(encoding="utf-8"))
    by_sheet = {}
    for inspection in inspections:
        sheet_title = normalize_title(inspection.get("manifestName") or inspection.get("title", ""))
        by_req = {}
        for req in inspection.get("requirements", []):
            number_match = re.search(r"(\d+)", req.get("heading", ""))
            number = number_match.group(1) if number_match else ""
            rid = req.get("requirementId", "")
            if rid:
                by_req[("id", rid)] = req
            if number:
                by_req[("number", number)] = req
        by_sheet[sheet_title] = {"inspection": inspection, "requirements": by_req}
    return by_sheet


def browser_fields_for_requirement(browser_fields, sheet_title, requirement_id, number):
    sheet = browser_fields.get(normalize_title(sheet_title))
    if not sheet:
        return {}
    by_req = sheet["requirements"]
    return by_req.get(("id", requirement_id)) or by_req.get(("number", str(number))) or {}


def answer_key(system_id, sheet_id, sheet_title, number, requirement_id):
    parts = [
        normalize_space(system_id) or "system",
        normalize_space(sheet_id) or safe_filename(sheet_title),
        f"req-{number}",
        requirement_id or "no-requirement-id",
    ]
    return "|".join(parts)


def build_answer_template(
    html_path,
    manifest_path=None,
    xlsx_path=None,
    browser_fields_path=None,
    slug="system",
    system_id="",
    system_name="",
):
    requirements = parse_requirements_html(Path(html_path))
    manifest_rows = read_manifest(manifest_path) if manifest_path else []
    workbook_values = load_workbook_current_values(xlsx_path)
    browser_fields = load_browser_fields(browser_fields_path)
    answers = []

    for req in requirements:
        manifest_row = best_manifest_match(req["sheet"], manifest_rows) if manifest_rows else None
        sheet_id = manifest_row.get("sheet", "") if manifest_row else ""
        href = manifest_row.get("href", "") if manifest_row else ""
        manifest_name = manifest_row.get("name", "") if manifest_row else ""
        current_workbook = workbook_current_for_requirement(
            workbook_values,
            req["sheet"],
            req.get("requirement", ""),
            req.get("requirementId", ""),
            req.get("requirementNumber", ""),
        )
        current_browser = browser_fields_for_requirement(
            browser_fields,
            manifest_name or req["sheet"],
            req.get("requirementId", ""),
            req.get("requirementNumber", ""),
        )
        current_statement = current_workbook.get("statement", "") or statement_code(
            current_browser.get("currentStatementValue", "")
        )
        current_explanation = current_workbook.get("explanation", "") or current_browser.get("explanationText", "")
        current_note = current_browser.get("noteText", "")
        answers.append(
            {
                "answerKey": answer_key(
                    system_id,
                    sheet_id,
                    manifest_name or req["sheet"],
                    req.get("requirementNumber", ""),
                    req.get("requirementId", ""),
                ),
                "sheet": {
                    "title": req["sheet"],
                    "manifestName": manifest_name,
                    "sheetId": sheet_id,
                    "href": href,
                },
                "requirement": {
                    "number": req.get("requirementNumber", ""),
                    "requirementId": req.get("requirementId", ""),
                    "exportId": req.get("id", ""),
                    "section": req.get("section", ""),
                    "text": req.get("requirement", ""),
                    "details": req.get("details", ""),
                    "motivation": req.get("motivation", ""),
                },
                "current": {
                    "statement": current_statement,
                    "explanation": current_explanation,
                    "note": current_note,
                    "noteVisibleForOthers": current_browser.get("noteVisibleForOthers"),
                    "visibleExternalNotes": current_browser.get("visibleExternalNotesText", ""),
                    "workbook": current_workbook,
                },
                "portalFields": {
                    "statementGroupName": current_browser.get("statementGroupName", ""),
                    "explanationTextareaId": current_browser.get("explanationTextareaId", ""),
                    "noteTextareaId": current_browser.get("noteTextareaId", ""),
                    "noteVisibleCheckboxId": current_browser.get("noteVisibleCheckboxId", ""),
                    "visibleExternalNotesTextareaId": current_browser.get("visibleExternalNotesTextareaId", ""),
                },
                "answer": {
                    "statement": current_statement,
                    "explanation": current_explanation,
                    "note": current_note,
                    "noteVisibleForOthers": current_browser.get("noteVisibleForOthers"),
                    "evidence": [],
                    "owner": "",
                    "status": "draft",
                },
            }
        )

    return {
        "schema": SCHEMA_NAME,
        "generatedAt": now_iso(),
        "system": {
            "slug": slug,
            "systemId": system_id,
            "name": system_name,
            "baseUrl": DEFAULT_BASE_URL,
        },
        "sources": {
            "html": str(html_path),
            "manifest": str(manifest_path or ""),
            "xlsx": str(xlsx_path or ""),
            "browserFields": str(browser_fields_path or ""),
        },
        "allowedStatements": ["SOC", "SOPC", "SONC", "NA"],
        "fillBehavior": {
            "blankStatementIsSkipped": True,
            "explanationRequiredFor": ["SOPC", "SONC", "NA"],
            "saveRequiresExplicitFlag": True,
        },
        "answers": answers,
    }


def validate_answers(payload, require_explanations=True):
    errors = []
    warnings = []
    seen_keys = set()
    candidate_count = 0
    for index, item in enumerate(payload.get("answers", []), start=1):
        key = item.get("answerKey", "")
        where = key or f"answers[{index}]"
        if not key:
            errors.append(f"{where}: missing answerKey")
        elif key in seen_keys:
            errors.append(f"{where}: duplicate answerKey")
        seen_keys.add(key)

        req = item.get("requirement", {})
        answer = item.get("answer", {})
        statement = statement_code(answer.get("statement", ""))
        if answer.get("statement", "") and not statement:
            errors.append(f"{where}: invalid statement {answer.get('statement')!r}")
        if statement:
            candidate_count += 1
        if statement in {"SOPC", "SONC", "NA"} and require_explanations and not normalize_space(
            answer.get("explanation", "")
        ):
            errors.append(f"{where}: {statement} requires answer.explanation")
        if statement and not req.get("number"):
            errors.append(f"{where}: cannot fill because requirement.number is missing")
        if statement and not (item.get("sheet", {}).get("href") or item.get("sheet", {}).get("sheetId")):
            warnings.append(f"{where}: no sheet href/sheetId in answer; manifest matching will be required")
    if payload.get("schema") != SCHEMA_NAME:
        errors.append(f"payload schema must be {SCHEMA_NAME!r}")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "answerCount": len(payload.get("answers", [])),
        "fillableAnswerCount": candidate_count,
        "emptyAnswerCount": len(payload.get("answers", [])) - candidate_count,
    }


def write_answer_markdown(payload, markdown_path):
    def block(value):
        text = normalize_space(value)
        return text if text else "n/a"

    lines = [
        f"# {payload.get('system', {}).get('slug', 'system')} PSA Answers",
        "",
        f"- Schema: `{payload.get('schema')}`",
        f"- Generated: `{payload.get('generatedAt')}`",
        f"- System ID: `{payload.get('system', {}).get('systemId') or 'n/a'}`",
        f"- Answers: {len(payload.get('answers', []))}",
        "",
        "## Format",
        "",
        "Edit `answer.statement` to one of `SOC`, `SOPC`, `SONC`, or `NA`.",
        "For `SOPC`, `SONC`, and `NA`, fill `answer.explanation`; this is the portal `Begruendung` value.",
        "`answer.note` maps to `Meine Notiz`; notes are working notes and are not the authoritative answer.",
        "",
        "## Sheets",
        "",
    ]
    by_sheet = defaultdict(list)
    for item in payload.get("answers", []):
        by_sheet[item.get("sheet", {}).get("manifestName") or item.get("sheet", {}).get("title", "")].append(item)
    for sheet, items in by_sheet.items():
        answered = sum(1 for item in items if statement_code(item.get("answer", {}).get("statement", "")))
        lines.extend([f"### {sheet}", "", f"- Requirements: {len(items)}", f"- Fillable answers now: {answered}", ""])
        for item in items:
            req = item.get("requirement", {})
            answer = item.get("answer", {})
            statement = statement_code(answer.get("statement", "")) or "blank"
            status = answer.get("status") or "draft"
            evidence = [str(ref).strip() for ref in answer.get("evidence", []) if str(ref).strip()]
            lines.extend(
                [
                    f"#### Requirement {req.get('number') or 'n/a'}",
                    "",
                    f"- Answer key: `{item.get('answerKey')}`",
                    f"- Requirement ID: `{req.get('requirementId') or 'n/a'}`",
                    f"- Statement: `{statement}`",
                    f"- Status: `{status}`",
                    "",
                    "**Requirement**",
                    "",
                    block(req.get("text")),
                    "",
                ]
            )
            if normalize_space(req.get("details", "")):
                lines.extend(["**Details**", "", block(req.get("details")), ""])
            if normalize_space(req.get("motivation", "")):
                lines.extend(["**Motivation**", "", block(req.get("motivation")), ""])
            lines.extend(["**Answer Explanation**", "", block(answer.get("explanation", "")), ""])
            if evidence:
                lines.extend(["**Evidence**", ""])
                lines.extend(f"- {ref}" for ref in evidence)
                lines.append("")
            if normalize_space(answer.get("note", "")):
                lines.extend(["**Portal Note**", "", block(answer.get("note")), ""])
        lines.append("")
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


FILL_SHEET_SCRIPT = r"""async (answers, options) => {
  const clean = (node) => (node?.textContent || "").replace(/\s+/g, " ").trim();
  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const dryRun = !options.apply;
  const result = {
    href: location.href,
    dryRun,
    saveRequested: Boolean(options.save),
    matched: 0,
    skipped: 0,
    changed: 0,
    saved: false,
    entries: []
  };
  const fieldsets = Array.from(document.querySelectorAll('fieldset[class*="soc-statement"]')).map((fieldset) => {
    const text = fieldset.innerText || "";
    const number = (text.match(/Anforderung\s+(\d+)/) || [])[1] || "";
    const requirementIdText = Array.from(fieldset.querySelectorAll('[id*="compactMigrationId"], [id*="j_idt1123"]'))
      .map((node) => clean(node))
      .find((value) => value.includes("Requirement-ID")) || "";
    const requirementId = (requirementIdText.match(/Requirement-ID:\s*([A-Za-z0-9_-]+)/) || [])[1] || "";
    return {fieldset, number, requirementId};
  });
  const setValue = (element, value) => {
    if (!element) {
      return false;
    }
    element.value = value || "";
    element.dispatchEvent(new Event("input", {bubbles: true}));
    element.dispatchEvent(new Event("change", {bubbles: true}));
    return true;
  };
  const findFieldset = (answer) => {
    const req = answer.requirement || {};
    const number = String(req.number || "");
    const rid = String(req.requirementId || "");
    return fieldsets.find((item) => number && item.number === number && (!rid || !item.requirementId || item.requirementId === rid))
      || fieldsets.find((item) => number && item.number === number)
      || fieldsets.find((item) => !number && rid && item.requirementId === rid)
      || null;
  };
  for (const answer of answers) {
    const desired = answer.answer || {};
    const statement = String(desired.statement || "").trim().toUpperCase();
    if (!statement && !options.includeEmpty) {
      result.skipped += 1;
      result.entries.push({answerKey: answer.answerKey, status: "skipped-empty"});
      continue;
    }
    const match = findFieldset(answer);
    if (!match) {
      result.entries.push({answerKey: answer.answerKey, status: "not-found"});
      continue;
    }
    result.matched += 1;
    if (dryRun) {
      result.entries.push({
        answerKey: answer.answerKey,
        status: "dry-run",
        requirementNumber: match.number,
        renderedRequirementId: match.requirementId
      });
      continue;
    }
    const fieldset = match.fieldset;
    let touched = false;
    if (statement) {
      const radio = fieldset.querySelector(`input[type="radio"][name*="idComplianceRadioBtns"][value="${CSS.escape(statement)}"]`);
      if (radio && !radio.disabled && !radio.checked) {
        radio.click();
        touched = true;
      }
    }
    const explanation = fieldset.querySelector('textarea[id*="idExplanationText"]');
    if (desired.explanation !== undefined && setValue(explanation, desired.explanation)) {
      touched = true;
    }
    const note = fieldset.querySelector('textarea[id*="idNoteInputField"]');
    if (desired.note !== undefined && setValue(note, desired.note)) {
      touched = true;
    }
    const noteVisible = fieldset.querySelector('input[id*="idExternallyVisible_input"]');
    if (typeof desired.noteVisibleForOthers === "boolean" && noteVisible && noteVisible.checked !== desired.noteVisibleForOthers) {
      noteVisible.click();
      touched = true;
    }
    if (touched) {
      result.changed += 1;
    }
    result.entries.push({
      answerKey: answer.answerKey,
      status: touched ? "changed" : "already-matching",
      requirementNumber: match.number,
      renderedRequirementId: match.requirementId,
      explanationFieldPresent: Boolean(explanation),
      noteFieldPresent: Boolean(note)
    });
  }
  if (options.save && !dryRun && result.changed > 0) {
    const saveButton = Array.from(document.querySelectorAll("button"))
      .find((button) => /Speichern/.test(button.innerText || "")
        && (button.id || "").includes("idSocForm")
        && !(button.id || "").includes("Commit")
        && !button.disabled);
    if (saveButton) {
      saveButton.click();
      await wait(options.saveWaitMs || 3000);
      result.saved = true;
      result.saveButtonId = saveButton.id || "";
    } else {
      result.saveError = "No enabled SoC save button found";
    }
  }
  return result;
}"""


def load_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def group_answers_for_manifest(payload, manifest_rows, include_empty=False, allowed_statuses=None):
    by_sheet_id = {row.get("sheet", ""): row for row in manifest_rows}
    by_title = manifest_by_normalized_title(manifest_rows)
    grouped = defaultdict(list)
    unresolved = []
    for item in payload.get("answers", []):
        status = normalize_space(item.get("answer", {}).get("status", ""))
        if allowed_statuses is not None and status not in allowed_statuses:
            continue
        statement = statement_code(item.get("answer", {}).get("statement", ""))
        if not statement and not include_empty:
            continue
        sheet = item.get("sheet", {})
        row = None
        if sheet.get("sheetId"):
            row = by_sheet_id.get(sheet["sheetId"])
        if not row and sheet.get("manifestName"):
            row = by_title.get(normalize_title(sheet["manifestName"]))
        if not row and sheet.get("title"):
            row = best_manifest_match(sheet["title"], manifest_rows)
        if not row:
            unresolved.append(item.get("answerKey", ""))
            continue
        grouped[row["sheet"]].append((row, item))
    return grouped, unresolved


def command_make_template(args):
    payload = build_answer_template(
        Path(args.html),
        manifest_path=args.manifest,
        xlsx_path=args.xlsx,
        browser_fields_path=args.browser_fields,
        slug=args.slug,
        system_id=args.system_id or "",
        system_name=args.system_name or "",
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = Path(args.markdown) if args.markdown else out.with_suffix(".md")
    write_answer_markdown(payload, markdown)
    print(
        json.dumps(
            {
                "answers": str(out),
                "markdown": str(markdown),
                "answerCount": len(payload["answers"]),
                "fillableAnswerCount": validate_answers(payload)["fillableAnswerCount"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def command_validate(args):
    payload = load_payload(args.answers)
    report = validate_answers(payload, require_explanations=not args.allow_missing_explanations)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


def command_render_markdown(args):
    payload = load_payload(args.answers)
    markdown = Path(args.markdown)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    write_answer_markdown(payload, markdown)
    print(
        json.dumps(
            {
                "answers": str(args.answers),
                "markdown": str(markdown),
                "answerCount": len(payload.get("answers", [])),
                "fillableAnswerCount": validate_answers(payload)["fillableAnswerCount"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def count_answer_values(payload):
    status_counts = defaultdict(int)
    statement_counts = defaultdict(int)
    for item in payload.get("answers", []):
        answer = item.get("answer", {}) or {}
        status_counts[normalize_space(answer.get("status", "")) or "<empty>"] += 1
        statement_counts[statement_code(answer.get("statement", "")) or "<empty>"] += 1
    return dict(sorted(status_counts.items())), dict(sorted(statement_counts.items()))


def command_preflight_fill(args):
    payload = load_payload(args.answers)
    validation = validate_answers(payload, require_explanations=not args.allow_missing_explanations)
    manifest_rows = read_manifest(args.manifest)
    allowed_statuses = None if args.allow_any_status else set(args.required_status or ["approved_for_portal"])
    grouped, unresolved = group_answers_for_manifest(
        payload,
        manifest_rows,
        include_empty=args.include_empty,
        allowed_statuses=allowed_statuses,
    )
    grouped_any, unresolved_any = group_answers_for_manifest(
        payload,
        manifest_rows,
        include_empty=args.include_empty,
        allowed_statuses=None,
    )
    status_counts, statement_counts = count_answer_values(payload)
    selected_answer_count = sum(len(pairs) for pairs in grouped.values())
    selected_sheet_count = len(grouped)
    all_matchable_count = sum(len(pairs) for pairs in grouped_any.values())
    report = {
        "answers": str(args.answers),
        "manifest": str(args.manifest),
        "validation": validation,
        "answerCount": len(payload.get("answers", [])),
        "statusCounts": status_counts,
        "statementCounts": statement_counts,
        "allowedStatuses": sorted(allowed_statuses) if allowed_statuses is not None else "any",
        "selectedAnswerCount": selected_answer_count,
        "selectedSheetCount": selected_sheet_count,
        "unresolvedSelected": unresolved,
        "allStatusMatchableAnswerCount": all_matchable_count,
        "allStatusSheetCount": len(grouped_any),
        "unresolvedAllStatuses": unresolved_any,
        "manifestSheetCount": len(manifest_rows),
        "warnings": [],
    }
    if allowed_statuses == {"approved_for_portal"} and selected_answer_count == 0 and status_counts.get("ready_for_review", 0):
        report["warnings"].append(
            "Default fill-browser status gate would process zero rows because all current answers are ready_for_review, not approved_for_portal. After manual review, either promote approved rows to approved_for_portal or run fill-browser with --required-status ready_for_review intentionally."
        )
    if unresolved:
        report["warnings"].append("Some selected answers could not be matched to a manifest sheet.")
    if not validation["ok"]:
        report["warnings"].append("Answer validation failed; do not fill the portal.")
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if validation["ok"] and not unresolved else 1


def command_fill_browser(args):
    payload = load_payload(args.answers)
    validation = validate_answers(payload, require_explanations=not args.allow_missing_explanations)
    if not validation["ok"]:
        print(json.dumps(validation, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
    manifest_rows = read_manifest(args.manifest)
    allowed_statuses = None if args.allow_any_status else set(args.required_status or ["approved_for_portal"])
    grouped, unresolved = group_answers_for_manifest(
        payload,
        manifest_rows,
        include_empty=args.include_empty,
        allowed_statuses=allowed_statuses,
    )
    results = {
        "dryRun": not (args.apply or args.save),
        "apply": bool(args.apply or args.save),
        "save": bool(args.save),
        "allowedStatuses": sorted(allowed_statuses) if allowed_statuses is not None else "any",
        "validation": validation,
        "unresolved": unresolved,
        "sheets": [],
    }
    if unresolved:
        message = {
            "ok": False,
            "error": "selected answers could not be matched to the supplied SoC manifest; refusing browser fill",
            "unresolvedCount": len(unresolved),
            "unresolved": unresolved,
        }
        results["error"] = message["error"]
        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(message, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
    cdp = CdpClient(args.port)
    try:
        sheet_items = list(grouped.items())
        if args.limit_sheets:
            sheet_items = sheet_items[: args.limit_sheets]
        for sheet_id, pairs in sheet_items:
            row = pairs[0][0]
            answers = [item for _, item in pairs]
            if args.only_answer_key:
                answers = [item for item in answers if item.get("answerKey") == args.only_answer_key]
            if not answers:
                continue
            href = row.get("href")
            navigate(cdp, href)
            wait_ready(cdp, expected_url=href)
            prepare_soc_sheet_for_capture(cdp)
            script = f"({FILL_SHEET_SCRIPT})({json.dumps(answers, ensure_ascii=False)}, {json.dumps({'apply': bool(args.apply or args.save), 'save': bool(args.save), 'includeEmpty': bool(args.include_empty), 'saveWaitMs': args.save_wait_ms})})"
            sheet_result = cdp.evaluate_json(script, await_promise=True)
            sheet_result["sheet"] = row.get("name", "")
            sheet_result["sheetId"] = sheet_id
            results["sheets"].append(sheet_result)
            time.sleep(args.pause)
    finally:
        cdp.close()
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Create, validate, and fill PSA SoC answer files.")
    parser.add_argument("--port", type=int, default=9223, help="Chrome DevTools port for browser fill.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    template = subparsers.add_parser("make-template", help="Create a psa_answers_v1 JSON template.")
    template.add_argument("--html", required=True, help="Downloaded Anforderungen HTML export.")
    template.add_argument("--manifest", help="SoC manifest TSV with portal sheet URLs.")
    template.add_argument("--xlsx", help="Statement_of_Compliance workbook with current statements/explanations.")
    template.add_argument("--browser-fields", help="Browser field inspection JSON.")
    template.add_argument("--slug", required=True, help="System slug.")
    template.add_argument("--system-id", help="PSA system ID.")
    template.add_argument("--system-name", help="Human-readable system name.")
    template.add_argument("--out", required=True, help="Output answer JSON path.")
    template.add_argument("--markdown", help="Output Markdown index path. Defaults to answer JSON path with .md suffix.")
    template.set_defaults(func=command_make_template)

    validate = subparsers.add_parser("validate", help="Validate a psa_answers_v1 JSON file.")
    validate.add_argument("--answers", required=True, help="Answer JSON path.")
    validate.add_argument("--allow-missing-explanations", action="store_true", help="Do not require explanations for SOPC/SONC/NA.")
    validate.set_defaults(func=command_validate)

    markdown = subparsers.add_parser("render-markdown", help="Render an existing psa_answers_v1 JSON file into Markdown docs.")
    markdown.add_argument("--answers", required=True, help="Answer JSON path.")
    markdown.add_argument("--markdown", required=True, help="Output Markdown path.")
    markdown.set_defaults(func=command_render_markdown)

    preflight = subparsers.add_parser("preflight-fill", help="Check answer status gates and manifest matching before browser fill.")
    preflight.add_argument("--answers", required=True, help="Answer JSON path.")
    preflight.add_argument("--manifest", required=True, help="SoC manifest TSV with portal sheet URLs.")
    preflight.add_argument("--include-empty", action="store_true", help="Also process blank statement entries.")
    preflight.add_argument("--allow-missing-explanations", action="store_true", help="Do not require explanations for SOPC/SONC/NA.")
    preflight.add_argument(
        "--required-status",
        action="append",
        help="Only process answers with this answer.status. Defaults to approved_for_portal unless --allow-any-status is set.",
    )
    preflight.add_argument("--allow-any-status", action="store_true", help="Process all answer statuses for the preflight report.")
    preflight.add_argument("--out", help="Optional preflight report JSON path.")
    preflight.set_defaults(func=command_preflight_fill)

    fill = subparsers.add_parser("fill-browser", help="Fill live PSA portal fields from an answer JSON file.")
    fill.add_argument("--answers", required=True, help="Answer JSON path.")
    fill.add_argument("--manifest", required=True, help="SoC manifest TSV with portal sheet URLs.")
    fill.add_argument("--include-empty", action="store_true", help="Also process blank statement entries.")
    fill.add_argument("--apply", action="store_true", help="Modify fields in the browser without clicking Save.")
    fill.add_argument("--save", action="store_true", help="Modify fields and click the SoC Save button on each changed sheet.")
    fill.add_argument("--allow-missing-explanations", action="store_true", help="Do not require explanations for SOPC/SONC/NA.")
    fill.add_argument(
        "--required-status",
        action="append",
        help="Only process answers with this answer.status. Defaults to approved_for_portal unless --allow-any-status is set.",
    )
    fill.add_argument("--allow-any-status", action="store_true", help="Process all answer statuses. Use only for deliberate draft dry-runs.")
    fill.add_argument("--limit-sheets", type=int, help="Only process the first N matched sheets.")
    fill.add_argument("--only-answer-key", help="Only process one answerKey.")
    fill.add_argument("--pause", type=float, default=0.5, help="Pause between sheets.")
    fill.add_argument("--save-wait-ms", type=int, default=3000, help="Wait after Save clicks.")
    fill.add_argument("--out", help="Optional fill report JSON path.")
    fill.set_defaults(func=command_fill_browser)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        result = args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0 if result is None else result


if __name__ == "__main__":
    raise SystemExit(main())
