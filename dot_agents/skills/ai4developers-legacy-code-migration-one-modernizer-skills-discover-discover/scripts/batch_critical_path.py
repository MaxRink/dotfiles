#!/usr/bin/env python3
"""Analyze batch topology to identify critical path chains and parallelization opportunities.

Usage: python3 batch_critical_path.py [project-root]

Input: .migration/batch/topology.json
Output: .migration/batch/critical-paths.md
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def build_job_dag(topology: dict) -> dict[str, list[str]]:
    """Build a directed graph of job dependencies from dataset producer/consumer relationships."""
    datasets = topology.get("datasets", {})
    dag = defaultdict(set)

    for dsn, info in datasets.items():
        producers = info.get("producers", [])
        consumers = info.get("consumers", [])
        for prod in producers:
            prod_job = prod.split(".")[0]
            for cons in consumers:
                cons_job = cons.split(".")[0]
                if prod_job != cons_job:
                    dag[prod_job].add(cons_job)

    return {k: sorted(v) for k, v in dag.items()}


def find_all_paths(
    dag: dict, start: str, end: str, max_depth: int = 20
) -> list[list[str]]:
    """Find all paths between two nodes (BFS with depth limit)."""
    paths = []
    queue = [(start, [start])]
    while queue:
        node, path = queue.pop(0)
        if len(path) > max_depth:
            continue
        if node == end and len(path) > 1:
            paths.append(path)
            continue
        for neighbor in dag.get(node, []):
            if neighbor not in path:
                queue.append((neighbor, path + [neighbor]))
    return paths


def find_longest_chains(dag: dict) -> list[list[str]]:
    """Find the longest chains in the DAG using DFS."""
    all_nodes = set(dag.keys())
    for successors in dag.values():
        all_nodes.update(successors)

    # Find nodes with no predecessors (start nodes)
    has_predecessor = set()
    for successors in dag.values():
        has_predecessor.update(successors)
    start_nodes = all_nodes - has_predecessor

    if not start_nodes:
        start_nodes = all_nodes

    longest_paths = []

    def dfs(node: str, path: list[str], visited: set):
        successors = dag.get(node, [])
        extended = False
        for s in successors:
            if s not in visited:
                extended = True
                dfs(s, path + [s], visited | {s})
        if not extended:
            longest_paths.append(path)

    for start in sorted(start_nodes):
        dfs(start, [start], {start})

    longest_paths.sort(key=len, reverse=True)
    return longest_paths[:10]


def find_parallel_opportunities(dag: dict) -> list[set[str]]:
    """Find groups of jobs that have no dependency between each other (can run in parallel)."""
    all_nodes = set(dag.keys())
    for successors in dag.values():
        all_nodes.update(successors)

    # Build full reachability
    reachable = defaultdict(set)
    for node in all_nodes:
        queue = list(dag.get(node, []))
        visited = set()
        while queue:
            n = queue.pop(0)
            if n in visited:
                continue
            visited.add(n)
            reachable[node].add(n)
            queue.extend(dag.get(n, []))

    # Find independent sets
    parallel_groups = []
    remaining = set(all_nodes)

    while remaining:
        node = remaining.pop()
        group = {node}
        for other in list(remaining):
            if other not in reachable[node] and node not in reachable[other]:
                independent_of_group = all(
                    other not in reachable[g] and g not in reachable[other]
                    for g in group
                )
                if independent_of_group:
                    group.add(other)
                    remaining.discard(other)
        if len(group) > 1:
            parallel_groups.append(group)

    parallel_groups.sort(key=len, reverse=True)
    return parallel_groups[:10]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    topology_path = root / ".migration" / "discovery" / "batch" / "topology.json"

    if not topology_path.exists():
        print(
            "ERROR: .migration/batch/topology.json not found. Run extract_batch.py first."
        )
        sys.exit(1)

    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    dag = build_job_dag(topology)

    if not dag:
        print("No inter-job dependencies found (no shared datasets between jobs).")
        print("This may indicate jobs communicate via other mechanisms (DB, MQ, etc.)")
        sys.exit(0)

    longest = find_longest_chains(dag)
    parallel = find_parallel_opportunities(dag)

    # Generate report
    lines = ["# Batch Critical Path Analysis\n"]

    lines.append("## Job Dependency Graph Stats\n")
    all_nodes = set(dag.keys())
    for v in dag.values():
        all_nodes.update(v)
    total_edges = sum(len(v) for v in dag.values())
    lines.append(f"- **Jobs in dependency graph**: {len(all_nodes)}")
    lines.append(f"- **Dependencies (edges)**: {total_edges}")
    lines.append(f"- **Longest chain depth**: {len(longest[0]) if longest else 0}")
    lines.append("")

    lines.append("## Critical Path Chains (longest dependency sequences)\n")
    for i, chain in enumerate(longest[:5], 1):
        lines.append(f"### Chain {i} ({len(chain)} jobs)")
        lines.append("```")
        lines.append(" → ".join(chain))
        lines.append("```")
        lines.append("")

    if parallel:
        lines.append("## Parallelization Opportunities\n")
        lines.append(
            "These job groups have no dependencies between them and could run concurrently:\n"
        )
        for i, group in enumerate(parallel[:5], 1):
            lines.append(f"### Group {i} ({len(group)} independent jobs)")
            for job in sorted(group):
                lines.append(f"- {job}")
            lines.append("")

    # Dataset bottlenecks (datasets with many consumers)
    datasets = topology.get("datasets", {})
    bottlenecks = [
        (dsn, info)
        for dsn, info in datasets.items()
        if len(info.get("consumers", [])) > 2
    ]
    bottlenecks.sort(key=lambda x: -len(x[1]["consumers"]))

    if bottlenecks:
        lines.append("## Dataset Bottlenecks\n")
        lines.append("Datasets consumed by many jobs (potential contention points):\n")
        lines.append("| Dataset | Producers | Consumers |")
        lines.append("| ------- | --------- | --------- |")
        for dsn, info in bottlenecks[:10]:
            prods = ", ".join(info["producers"][:3])
            cons_count = len(info["consumers"])
            lines.append(f"| `{dsn}` | {prods} | {cons_count} jobs |")
        lines.append("")

    report = "\n".join(lines)
    out_path = root / ".migration" / "discovery" / "batch" / "critical-paths.md"
    out_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
