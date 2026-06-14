#!/usr/bin/env python3
"""Run the repeatable T-CaaS PSA SoC readiness gates.

This wrapper intentionally writes a compact summary instead of another large
workbook. The individual gate commands still update their normal JSON/Markdown
reports, and this script records the current pass/blocker state in one place.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


KNOWN_SEPARATE_FILING_TYPES = {
    "dtt_operations_sheet_all_na_for_core_scope",
    "dtt_system_has_no_soc_manifest_rows",
    "dtt_system_manifest_missing",
    "natco_system_has_no_soc_manifest_rows",
    "natco_system_manifest_missing",
    "natco_system_manifest_not_provided",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def run_json(command, cwd):
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    record = {
        "command": command,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
    }
    try:
        record["json"] = json.loads(completed.stdout)
    except json.JSONDecodeError:
        record["stdout"] = completed.stdout.strip()
        record["json"] = {}
    return record


def command_ok(record):
    return record.get("returncode") == 0


def load_generated_json(repo, command_record):
    output = command_record.get("json", {}) or {}
    path = output.get("json")
    if not path:
        return output
    report = Path(path)
    if not report.is_absolute():
        report = repo / report
    try:
        return json.loads(report.read_text(encoding="utf-8"))
    except Exception:
        return output


def list_len(value):
    return len(value or [])


def completeness_report_valid(report):
    return (
        isinstance(report, dict)
        and report.get("schema") == "tcaas_answer_completeness_audit_v1"
        and isinstance(report.get("findingCount"), int)
        and isinstance(report.get("severityCounts"), dict)
        and isinstance(report.get("issueCounts"), dict)
    )


def build_summary(args):
    repo = Path(args.repo_root).resolve()
    py = sys.executable
    tcaas_script = repo / "skill/tcaas-soc-analysis/scripts/tcaas_analysis.py"
    psa_answers_script = repo / "skill/psa-portal-soc-capture/scripts/psa_answers.py"

    commands = {}
    commands["answer_quality"] = run_json(
        [
            py,
            str(tcaas_script),
            "answer-quality",
            "--answers",
            args.answers,
            "--out-dir",
            args.out_dir,
            "--vetted-links",
            args.vetted_links,
            "--workspace-root",
            args.workspace_root,
        ],
        repo,
    )
    commands["answer_completeness"] = run_json(
        [
            py,
            str(tcaas_script),
            "answer-completeness-audit",
            "--answers",
            args.answers,
            "--out-dir",
            args.out_dir,
        ],
        repo,
    )
    commands["confluence_evidence"] = run_json(
        [
            py,
            str(tcaas_script),
            "confluence-evidence-audit",
            "--answers",
            args.answers,
            "--vetted-links",
            args.vetted_links,
            "--out-dir",
            args.out_dir,
        ],
        repo,
    )
    platform_command = [
        py,
        str(tcaas_script),
        "platform-coverage-audit",
        "--answers",
        args.answers,
        "--out-dir",
        args.out_dir,
    ]
    if args.dtt_manifest:
        platform_command.extend(["--dtt-manifest", args.dtt_manifest])
    if args.natco_manifest:
        platform_command.extend(["--natco-manifest", args.natco_manifest])
    if args.require_natco_manifest:
        platform_command.append("--require-natco-manifest")
    commands["platform_coverage"] = run_json(platform_command, repo)
    commands["preflight_fill"] = run_json(
        [
            py,
            str(psa_answers_script),
            "preflight-fill",
            "--answers",
            args.answers,
            "--manifest",
            args.manifest,
            "--required-status",
            args.required_status,
            "--out",
            args.preflight_out,
        ],
        repo,
    )

    answer_quality = commands["answer_quality"].get("json", {})
    answer_completeness = load_generated_json(repo, commands["answer_completeness"])
    answer_completeness_valid = completeness_report_valid(answer_completeness)
    answer_completeness_severity_counts = answer_completeness.get("severityCounts", {}) or {}
    answer_completeness_error_count = answer_completeness_severity_counts.get("error", 0)
    answer_completeness_review_count = answer_completeness_severity_counts.get("review", 0)
    confluence = commands["confluence_evidence"].get("json", {})
    platform = load_generated_json(repo, commands["platform_coverage"])
    preflight = commands["preflight_fill"].get("json", {})
    validation = preflight.get("validation", {})
    platform_issue_counts = platform.get("issueCounts", {}) or {}
    non_separate_filing_issues = {
        issue_type: count
        for issue_type, count in platform_issue_counts.items()
        if issue_type not in KNOWN_SEPARATE_FILING_TYPES
    }
    component_issue_count = sum(
        count for issue_type, count in platform_issue_counts.items() if issue_type.startswith("component_")
    )
    commands_ok = all(command_ok(record) for record in commands.values())
    core_gates_ok = (
        commands_ok
        and answer_quality.get("issueCount") == 0
        and answer_completeness_valid
        and answer_completeness_error_count == 0
        and confluence.get("unvettedConfluenceReferenceCount") == 0
        and validation.get("ok") is True
        and list_len(preflight.get("unresolvedSelected")) == 0
        and list_len(preflight.get("warnings")) == 0
        and component_issue_count == 0
        and not non_separate_filing_issues
    )
    blockers = []
    deferred_separate_filing_issues = []
    if not answer_completeness_valid:
        blockers.append(
            {
                "severity": "blocker",
                "type": "answer_completeness_audit_invalid",
                "detail": "The answer completeness audit did not produce the expected report schema/counts.",
            }
        )
    for issue in platform.get("issues", []) or []:
        if issue.get("type") in KNOWN_SEPARATE_FILING_TYPES:
            if issue.get("severity") == "blocker":
                blockers.append(issue)
            else:
                deferred_separate_filing_issues.append(issue)
    if args.required_status != "approved_for_portal":
        blockers.append(
            {
                "severity": "blocker",
                "type": "portal_not_approved_for_save",
                "detail": "Answers are gated for review status; portal save still requires manual review/approval.",
            }
        )

    summary = {
        "schema": "tcaas_soc_gate_summary_v1",
        "generatedAt": now(),
        "answers": args.answers,
        "manifest": args.manifest,
        "requiredStatus": args.required_status,
        "commandsOk": commands_ok,
        "coreGatesOk": core_gates_ok,
        "overallStatus": "core_ready_for_review_not_filed" if core_gates_ok else "gate_issues_found",
        "answerRows": preflight.get("answerCount"),
        "selectedAnswerCount": preflight.get("selectedAnswerCount"),
        "statementCounts": preflight.get("statementCounts", {}),
        "answerQualityIssueCount": answer_quality.get("issueCount"),
        "answerCompletenessReportValid": answer_completeness_valid,
        "answerCompletenessFindingCount": answer_completeness.get("findingCount"),
        "answerCompletenessReviewedSingleSourceCount": answer_completeness.get("reviewedSingleSourceCount", 0),
        "answerCompletenessSeverityCounts": answer_completeness_severity_counts,
        "answerCompletenessIssueCounts": answer_completeness.get("issueCounts", {}),
        "answerCompletenessErrorCount": answer_completeness_error_count,
        "answerCompletenessReviewCount": answer_completeness_review_count,
        "unvettedConfluenceReferenceCount": confluence.get("unvettedConfluenceReferenceCount"),
        "platformComponentCount": platform.get("componentCount") or len(platform.get("componentSummaries", []) or []),
        "platformComponentIssueCount": component_issue_count,
        "platformHygiene": platform.get("hygiene", {}),
        "platformIssueCounts": platform_issue_counts,
        "nonSeparateFilingIssues": non_separate_filing_issues,
        "deferredSeparateFilingIssues": deferred_separate_filing_issues,
        "unresolvedSelectedCount": list_len(preflight.get("unresolvedSelected")),
        "preflightWarningCount": list_len(preflight.get("warnings")),
        "blockers": blockers,
        "outputs": {name: record.get("json", {}) for name, record in commands.items()},
        "commandResults": {
            name: {
                "returncode": record.get("returncode"),
                "stderr": record.get("stderr"),
            }
            for name, record in commands.items()
        },
    }
    return summary


def write_markdown(summary, markdown_path):
    lines = [
        "# T-CaaS SoC Gate Summary",
        "",
        f"Generated: `{summary['generatedAt']}`",
        "",
        "## Status",
        "",
        f"- Overall status: `{summary['overallStatus']}`",
        f"- Commands OK: `{summary['commandsOk']}`",
        f"- Core gates OK: `{summary['coreGatesOk']}`",
        f"- Answer rows: `{summary.get('answerRows')}`",
        f"- Selected rows: `{summary.get('selectedAnswerCount')}`",
        f"- Required status: `{summary.get('requiredStatus')}`",
        "",
        "## Gate Counts",
        "",
        f"- Answer quality issues: `{summary.get('answerQualityIssueCount')}`",
        f"- Answer completeness report valid: `{summary.get('answerCompletenessReportValid')}`",
        f"- Answer completeness findings: `{summary.get('answerCompletenessFindingCount')}`",
        f"- Answer completeness reviewed single-source rows: `{summary.get('answerCompletenessReviewedSingleSourceCount')}`",
        f"- Answer completeness errors: `{summary.get('answerCompletenessErrorCount')}`",
        f"- Answer completeness reviews: `{summary.get('answerCompletenessReviewCount')}`",
        f"- Unvetted Confluence references: `{summary.get('unvettedConfluenceReferenceCount')}`",
        f"- Platform components checked: `{summary.get('platformComponentCount')}`",
        f"- Platform component issues: `{summary.get('platformComponentIssueCount')}`",
        f"- Unresolved preflight rows: `{summary.get('unresolvedSelectedCount')}`",
        f"- Preflight warnings: `{summary.get('preflightWarningCount')}`",
        f"- Platform hygiene: `{json.dumps(summary.get('platformHygiene', {}), sort_keys=True)}`",
        f"- Statement counts: `{json.dumps(summary.get('statementCounts', {}), sort_keys=True)}`",
        "",
        "## Remaining Blockers",
        "",
    ]
    blockers = summary.get("blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker.get('type')}`: {blocker.get('detail', '')}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Deferred Separate Filings",
            "",
        ]
    )
    deferred = summary.get("deferredSeparateFilingIssues", [])
    if deferred:
        for issue in deferred:
            lines.append(f"- `{issue.get('type')}`: {issue.get('detail', '')}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Answer Completeness Issue Counts",
            "",
            f"`{json.dumps(summary.get('answerCompletenessIssueCounts', {}), sort_keys=True)}`",
            "",
            "## Platform Issue Counts",
            "",
            f"`{json.dumps(summary.get('platformIssueCounts', {}), sort_keys=True)}`",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run the repeatable T-CaaS PSA SoC readiness gates.")
    parser.add_argument("--repo-root", default=".", help="Path to the tcaas-psa repository root.")
    parser.add_argument("--answers", default="analysis/soc-answers/tcaas-core_scope_fillable_answers.json")
    parser.add_argument("--manifest", default="artifacts/tcaas-core/snapshots/tcaas-core_soc_manifest.tsv")
    parser.add_argument("--dtt-manifest", default="artifacts/dtt/snapshots/dtt_soc_manifest.json")
    parser.add_argument("--natco-manifest", default="")
    parser.add_argument("--require-natco-manifest", action="store_true", default=False)
    parser.add_argument("--required-status", default="ready_for_review")
    parser.add_argument("--vetted-links", default="analysis/evidence/vetted_links.json")
    parser.add_argument("--workspace-root", default="/home/a92615428/git/devops.telekom.de")
    parser.add_argument("--out-dir", default="analysis/soc-answers")
    parser.add_argument(
        "--preflight-out",
        default="analysis/soc-answers/portal_fill_preflight_ready_for_review_2026-06-13.json",
    )
    parser.add_argument("--out", default="analysis/soc-answers/latest_gate_summary.json")
    parser.add_argument("--markdown", default="analysis/soc-answers/latest_gate_summary.md")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    summary = build_summary(args)
    out = repo / args.out
    markdown = repo / args.markdown
    out.parent.mkdir(parents=True, exist_ok=True)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(summary, markdown)
    print(json.dumps({"json": str(out), "markdown": str(markdown), "coreGatesOk": summary["coreGatesOk"]}, indent=2))


if __name__ == "__main__":
    main()
