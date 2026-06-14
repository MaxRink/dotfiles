#!/usr/bin/env python3
"""
GitLab MR Pipelines - List pipelines for an MR and inspect jobs/logs of failed pipelines.
"""

import argparse
import sys
import json
import os

sys.path.insert(0, os.path.dirname(__file__))
from gitlab_common import (
    get_gitlab_client,
    validate_project,
    print_error,
    print_json,
    print_table,
    truncate,
    format_date,
)

# Status icons for pipeline/job status
STATUS_ICONS = {
    "success": "✅",
    "failed": "❌",
    "running": "🔄",
    "pending": "⏳",
    "canceled": "⛔",
    "skipped": "⏭️",
    "manual": "🔧",
    "created": "🆕",
    "waiting_for_resource": "⏳",
    "preparing": "🔄",
    "scheduled": "📅",
}


def get_status_icon(status: str) -> str:
    return STATUS_ICONS.get(status, "❓")


def get_pipelines(project, mr_iid: int) -> list:
    """Get all pipelines for an MR, newest first."""
    try:
        mr = project.mergerequests.get(mr_iid)
        pipelines = mr.pipelines.list(per_page=20)
        return pipelines
    except Exception as e:
        print_error(f"Failed to get pipelines for MR !{mr_iid}: {e}")
        sys.exit(1)


def get_pipeline_jobs(project, pipeline_id: int) -> list:
    """Get all jobs for a pipeline."""
    try:
        pipeline = project.pipelines.get(pipeline_id)
        jobs = pipeline.jobs.list(per_page=100, all=True)
        # Sort by id (chronological order)
        return sorted(jobs, key=lambda j: j.id)
    except Exception as e:
        print_error(f"Failed to get jobs for pipeline {pipeline_id}: {e}")
        return []


def get_job_log(project, job_id: int, tail_lines: int = 80) -> str:
    """Get the trace/log of a job, returning the last N lines."""
    try:
        job = project.jobs.get(job_id)
        trace = job.trace()
        if isinstance(trace, bytes):
            trace = trace.decode("utf-8", errors="replace")
        lines = trace.splitlines()
        if len(lines) > tail_lines:
            lines = lines[-tail_lines:]
            return f"[... showing last {tail_lines} lines ...]\n" + "\n".join(lines)
        return "\n".join(lines)
    except Exception as e:
        return f"(Could not retrieve log: {e})"


def print_pipelines_table(pipelines):
    headers = ["#", "ID", "Status", "Ref", "SHA", "Created", "URL"]
    rows = []
    for i, p in enumerate(pipelines, 1):
        icon = get_status_icon(p.status)
        sha = p.sha[:10] if p.sha else ""
        rows.append([
            i,
            p.id,
            f"{icon} {p.status}",
            truncate(p.ref, 40),
            sha,
            format_date(p.created_at),
            p.web_url,
        ])
    print_table(headers, rows, max_widths={3: 40})


def print_jobs_table(jobs):
    headers = ["ID", "Stage", "Name", "Status", "Duration", "URL"]
    rows = []
    for j in jobs:
        icon = get_status_icon(j.status)
        duration = ""
        if hasattr(j, "duration") and j.duration:
            duration = f"{int(j.duration)}s"
        rows.append([
            j.id,
            j.stage,
            truncate(j.name, 45),
            f"{icon} {j.status}",
            duration,
            j.web_url,
        ])
    print_table(headers, rows, max_widths={2: 45})


def select_target_pipeline(pipelines, pipeline_id=None):
    """
    Select which pipeline to inspect:
    - If pipeline_id given, use that one
    - Otherwise: most recent failed pipeline, or latest if none failed
    """
    if pipeline_id:
        for p in pipelines:
            if p.id == pipeline_id:
                return p
        print_error(f"Pipeline {pipeline_id} not found in this MR's pipelines")
        sys.exit(1)

    # Find the most recent failed pipeline
    for p in pipelines:
        if p.status == "failed":
            return p

    # Fall back to latest
    return pipelines[0] if pipelines else None


def main():
    parser = argparse.ArgumentParser(
        description="Inspect pipelines for a GitLab MR. Automatically focuses on the latest failed pipeline."
    )
    parser.add_argument("project", help="Full project path (e.g., cit/t-caas/my-repo)")
    parser.add_argument("mr_iid", type=int, help="Merge request IID number")
    parser.add_argument(
        "--pipeline-id",
        type=int,
        default=None,
        help="Inspect a specific pipeline by ID (default: auto-select latest failed)",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list pipelines, do not inspect jobs or logs",
    )
    parser.add_argument(
        "--no-logs",
        action="store_true",
        help="Show jobs but skip logs for failed jobs",
    )
    parser.add_argument(
        "--log-lines",
        type=int,
        default=80,
        help="Number of log lines to show for each failed job (default: 80)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    args = parser.parse_args()

    if not validate_project(args.project):
        print_error(
            f"Project '{args.project}' is not in an allowed group. "
            "Allowed groups: cit/t-caas, tdi-caas, cit-iaas/cid"
        )
        sys.exit(1)

    gl = get_gitlab_client()

    try:
        project = gl.projects.get(args.project)
    except Exception as e:
        print_error(f"Failed to get project '{args.project}': {e}")
        sys.exit(1)

    # --- Get pipelines ---
    pipelines = get_pipelines(project, args.mr_iid)

    if not pipelines:
        print(f"No pipelines found for MR !{args.mr_iid}")
        sys.exit(0)

    if args.format == "json" and args.list_only:
        print_json([{
            "id": p.id,
            "status": p.status,
            "ref": p.ref,
            "sha": p.sha,
            "created_at": p.created_at,
            "web_url": p.web_url,
        } for p in pipelines])
        return

    # --- Table: pipelines summary ---
    print(f"\n{'=' * 80}")
    print(f"  PIPELINES FOR MR !{args.mr_iid} — {project.name_with_namespace}")
    print(f"{'=' * 80}\n")
    print_pipelines_table(pipelines)

    if args.list_only:
        return

    # --- Select pipeline to inspect ---
    target = select_target_pipeline(pipelines, args.pipeline_id)
    if not target:
        return

    auto_selected = args.pipeline_id is None
    label = "(auto-selected: latest failed)" if auto_selected and target.status == "failed" else \
            "(auto-selected: latest)" if auto_selected else "(specified)"
    icon = get_status_icon(target.status)

    print(f"\n{'=' * 80}")
    print(f"  PIPELINE {target.id} — {icon} {target.status.upper()} {label}")
    print(f"  Ref: {target.ref} | SHA: {target.sha[:12] if target.sha else 'N/A'}")
    print(f"  URL: {target.web_url}")
    print(f"{'=' * 80}\n")

    # --- Jobs ---
    jobs = get_pipeline_jobs(project, target.id)

    if args.format == "json":
        output = {
            "pipeline": {
                "id": target.id,
                "status": target.status,
                "ref": target.ref,
                "sha": target.sha,
                "web_url": target.web_url,
            },
            "jobs": [],
        }
        for j in jobs:
            job_data = {
                "id": j.id,
                "stage": j.stage,
                "name": j.name,
                "status": j.status,
                "duration": getattr(j, "duration", None),
                "web_url": j.web_url,
            }
            if j.status == "failed" and not args.no_logs:
                job_data["log"] = get_job_log(project, j.id, args.log_lines)
            output["jobs"].append(job_data)
        print_json(output)
        return

    print("JOBS\n" + "-" * 80)
    print_jobs_table(jobs)

    # --- Logs for failed jobs ---
    if not args.no_logs:
        failed_jobs = [j for j in jobs if j.status == "failed"]
        if failed_jobs:
            for job in failed_jobs:
                print(f"\n{'=' * 80}")
                print(f"  LOG — Job #{job.id}: {job.name} (stage: {job.stage})")
                print(f"  URL: {job.web_url}")
                print(f"{'=' * 80}\n")
                log = get_job_log(project, job.id, args.log_lines)
                print(log)
        else:
            print(f"\n✅ No failed jobs in this pipeline.")


if __name__ == "__main__":
    main()
