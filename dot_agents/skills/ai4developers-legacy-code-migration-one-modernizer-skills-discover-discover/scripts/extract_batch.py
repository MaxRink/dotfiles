#!/usr/bin/env python3
"""Parse JCL + Control-M XML + Autosys JIL into a batch topology graph.

Usage: python3 extract_batch.py [project-root]

Outputs: .migration/batch/topology.json
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _constants import IGNORE_DIRS

_RE_JOB = re.compile(r"^//(\w+)\s+JOB\s", re.MULTILINE)
_RE_EXEC = re.compile(r"^//(\w+)\s+EXEC\s+(.*)", re.MULTILINE)
_RE_DD = re.compile(r"^//(\w+)\s+DD\s+(.*)", re.MULTILINE)
_RE_PGM = re.compile(r"PGM=(\w+)", re.IGNORECASE)
_RE_PROC_REF = re.compile(r"PROC=(\w+)", re.IGNORECASE)
_RE_DSN = re.compile(r"DSN=([^\s,]+)", re.IGNORECASE)
_RE_DISP = re.compile(r"DISP=\((\w+)", re.IGNORECASE)
_RE_COND = re.compile(r"COND=\(([^)]+)\)", re.IGNORECASE)

# Autosys JIL patterns
_RE_JIL_JOB = re.compile(r"insert_job:\s*(\S+)", re.IGNORECASE)
_RE_JIL_TYPE = re.compile(r"job_type:\s*(\S+)", re.IGNORECASE)
_RE_JIL_CMD = re.compile(r"command:\s*(.+)", re.IGNORECASE)
_RE_JIL_COND = re.compile(r"condition:\s*(.+)", re.IGNORECASE)
_RE_JIL_START = re.compile(r"start_times:\s*\"(.+)\"", re.IGNORECASE)
_RE_JIL_BOX = re.compile(r"box_name:\s*(\S+)", re.IGNORECASE)
_RE_JIL_MACHINE = re.compile(r"machine:\s*(\S+)", re.IGNORECASE)


def parse_jcl_file(path: Path, root: Path) -> dict:
    """Parse a single JCL file into topology entries."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    rel = str(path.relative_to(root))
    jobs = []
    current_job = None
    current_step = None

    for m in _RE_JOB.finditer(content):
        current_job = {
            "name": m.group(1),
            "source": rel,
            "line": content[: m.start()].count("\n") + 1,
            "steps": [],
        }
        jobs.append(current_job)

    # If no JOB card (might be a PROC), create synthetic container
    if not jobs:
        current_job = {
            "name": path.stem.upper(),
            "source": rel,
            "line": 1,
            "steps": [],
            "is_proc": True,
        }
        jobs.append(current_job)

    # Parse steps
    for m in _RE_EXEC.finditer(content):
        step_name = m.group(1)
        exec_params = m.group(2)
        line = content[: m.start()].count("\n") + 1

        step = {
            "name": step_name,
            "line": line,
            "program": None,
            "proc": None,
            "datasets": [],
            "condition": None,
        }

        pgm = _RE_PGM.search(exec_params)
        if pgm:
            step["program"] = pgm.group(1)

        proc = _RE_PROC_REF.search(exec_params)
        if proc:
            step["proc"] = proc.group(1)

        cond = _RE_COND.search(exec_params)
        if cond:
            step["condition"] = cond.group(1)

        current_step = step
        if current_job:
            current_job["steps"].append(step)

    # Parse DD statements
    for m in _RE_DD.finditer(content):
        dd_name = m.group(1)
        dd_params = m.group(2)

        dsn_match = _RE_DSN.search(dd_params)
        if dsn_match and current_step:
            dsn = dsn_match.group(1).rstrip(",")
            disp_match = _RE_DISP.search(dd_params)
            disp = disp_match.group(1).upper() if disp_match else "SHR"
            direction = "output" if disp in ("NEW", "MOD") else "input"
            current_step["datasets"].append(
                {
                    "dd_name": dd_name,
                    "dsn": dsn,
                    "direction": direction,
                }
            )

    return {"jobs": jobs, "source": rel}


def parse_jil_file(path: Path, root: Path) -> list[dict]:
    """Parse an Autosys JIL file into job definitions."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    rel = str(path.relative_to(root))
    jobs = []
    current = None

    for line in content.split("\n"):
        jm = _RE_JIL_JOB.search(line)
        if jm:
            if current:
                jobs.append(current)
            current = {
                "name": jm.group(1),
                "source": rel,
                "type": None,
                "command": None,
                "condition": None,
                "start_times": None,
                "box": None,
                "machine": None,
            }
            continue

        if current is None:
            continue

        for pattern, key in [
            (_RE_JIL_TYPE, "type"),
            (_RE_JIL_CMD, "command"),
            (_RE_JIL_COND, "condition"),
            (_RE_JIL_START, "start_times"),
            (_RE_JIL_BOX, "box"),
            (_RE_JIL_MACHINE, "machine"),
        ]:
            m = pattern.search(line)
            if m:
                current[key] = m.group(1)

    if current:
        jobs.append(current)

    return jobs


def parse_controlm_xml(path: Path, root: Path) -> list[dict]:
    """Parse Control-M export XML into job definitions."""
    try:
        tree = ET.parse(path)
        xml_root = tree.getroot()
    except (ET.ParseError, OSError):
        return []

    rel = str(path.relative_to(root))
    jobs = []

    for job_el in xml_root.iter():
        if "JOB" in job_el.tag.upper() or job_el.tag in ("SMART_FOLDER", "JOB"):
            name = job_el.get("JOBNAME") or job_el.get("MEMNAME") or job_el.get("NAME")
            if not name:
                continue
            job = {
                "name": name,
                "source": rel,
                "application": job_el.get("APPLICATION"),
                "sub_application": job_el.get("SUB_APPLICATION"),
                "node_id": job_el.get("NODEID"),
                "command": job_el.get("CMDLINE"),
                "conditions_in": [],
                "conditions_out": [],
            }
            for cond in job_el.findall(".//INCOND") + job_el.findall(".//IN_CONDITION"):
                cond_name = cond.get("NAME") or cond.text
                if cond_name:
                    job["conditions_in"].append(cond_name)
            for cond in job_el.findall(".//OUTCOND") + job_el.findall(
                ".//OUT_CONDITION"
            ):
                cond_name = cond.get("NAME") or cond.text
                if cond_name:
                    job["conditions_out"].append(cond_name)
            jobs.append(job)

    return jobs


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    print(f"Scanning {root.name} for batch definitions...", file=sys.stderr)

    jcl_results = []
    jil_results = []
    ctm_results = []

    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file():
            continue

        suffix = f.suffix.lower()
        if suffix in (".jcl", ".proc"):
            result = parse_jcl_file(f, root)
            if result.get("jobs"):
                jcl_results.append(result)
        elif suffix == ".jil":
            jobs = parse_jil_file(f, root)
            jil_results.extend(jobs)
        elif suffix == ".xml":
            # Try parsing as Control-M (won't error on non-CTM XML)
            jobs = parse_controlm_xml(f, root)
            if jobs:
                ctm_results.extend(jobs)

    # Build topology
    all_programs = set()
    all_datasets = defaultdict(lambda: {"producers": [], "consumers": []})
    job_count = sum(len(r["jobs"]) for r in jcl_results)

    for result in jcl_results:
        for job in result["jobs"]:
            for step in job["steps"]:
                if step["program"]:
                    all_programs.add(step["program"])
                for ds in step["datasets"]:
                    key = ds["dsn"]
                    ref = f"{job['name']}.{step['name']}"
                    if ds["direction"] == "output":
                        all_datasets[key]["producers"].append(ref)
                    else:
                        all_datasets[key]["consumers"].append(ref)

    # Output
    out_dir = root / ".migration" / "discovery" / "batch"
    out_dir.mkdir(parents=True, exist_ok=True)

    topology = {
        "jcl_jobs": [r["jobs"] for r in jcl_results],
        "autosys_jobs": jil_results,
        "controlm_jobs": ctm_results,
        "programs_referenced": sorted(all_programs),
        "datasets": {k: v for k, v in all_datasets.items()},
        "summary": {
            "jcl_job_count": job_count,
            "autosys_job_count": len(jil_results),
            "controlm_job_count": len(ctm_results),
            "unique_programs": len(all_programs),
            "unique_datasets": len(all_datasets),
        },
    }

    (out_dir / "topology.json").write_text(
        json.dumps(topology, indent=2, default=str), encoding="utf-8"
    )

    print("\n# Batch Topology Summary")
    print("")
    print(f"**JCL Jobs**: {job_count}")
    print(f"**Autosys Jobs**: {len(jil_results)}")
    print(f"**Control-M Jobs**: {len(ctm_results)}")
    print(f"**Unique Programs**: {len(all_programs)}")
    print(f"**Unique Datasets**: {len(all_datasets)}")
    print("")
    print(f"Output: {out_dir / 'topology.json'}")


if __name__ == "__main__":
    main()
