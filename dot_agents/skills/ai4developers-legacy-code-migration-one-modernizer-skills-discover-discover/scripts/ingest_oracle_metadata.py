#!/usr/bin/env python3
"""Ingest Oracle DBA view exports (CSV/JSON) and inject into the knowledge graph.

Usage: python3 ingest_oracle_metadata.py [project-root] --file <path-to-csv-or-json> --type <dba_objects|dba_dependencies|dba_tab_columns>

Accepts exports from Oracle DBA views:
- DBA_OBJECTS — object inventory
- DBA_DEPENDENCIES — object dependency chains
- DBA_TAB_COLUMNS — table column metadata
- DBA_TRIGGERS — trigger definitions
- DBA_PROCEDURES — procedure/function list

Outputs: .migration/discovery/oracle/schema-metadata.json (normalized)
         Updates .migration/discovery/graphify-out/graph.json with new nodes/edges if present
"""

import csv
import json
import re
import sys
from pathlib import Path


def _make_id(*parts: str) -> str:
    combined = "_".join(p.strip("_.") for p in parts if p)
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", combined)
    return cleaned.strip("_").lower()


def load_input(file_path: Path) -> list[dict]:
    """Load CSV or JSON input file."""
    suffix = file_path.suffix.lower()
    content = file_path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".json":
        data = json.loads(content)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "rows" in data:
            return data["rows"]
        return [data]
    elif suffix == ".csv":
        reader = csv.DictReader(content.splitlines())
        return [row for row in reader]
    else:
        print(
            f"ERROR: Unsupported file format: {suffix}. Use .csv or .json",
            file=sys.stderr,
        )
        sys.exit(1)


def process_dba_objects(rows: list[dict]) -> dict:
    """Process DBA_OBJECTS export."""
    objects = []
    for row in rows:
        name = row.get("OBJECT_NAME") or row.get("object_name") or ""
        obj_type = row.get("OBJECT_TYPE") or row.get("object_type") or ""
        owner = row.get("OWNER") or row.get("owner") or ""
        status = row.get("STATUS") or row.get("status") or "VALID"
        if name and obj_type:
            objects.append(
                {
                    "name": name,
                    "type": obj_type,
                    "owner": owner,
                    "status": status,
                }
            )
    return {"dba_objects": objects}


def process_dba_dependencies(rows: list[dict]) -> dict:
    """Process DBA_DEPENDENCIES export."""
    deps = []
    for row in rows:
        name = row.get("NAME") or row.get("name") or ""
        dep_type = row.get("TYPE") or row.get("type") or ""
        ref_name = row.get("REFERENCED_NAME") or row.get("referenced_name") or ""
        ref_type = row.get("REFERENCED_TYPE") or row.get("referenced_type") or ""
        if name and ref_name:
            deps.append(
                {
                    "source": name,
                    "source_type": dep_type,
                    "target": ref_name,
                    "target_type": ref_type,
                }
            )
    return {"dba_dependencies": deps}


def process_dba_tab_columns(rows: list[dict]) -> dict:
    """Process DBA_TAB_COLUMNS export."""
    tables = {}
    for row in rows:
        table = row.get("TABLE_NAME") or row.get("table_name") or ""
        col = row.get("COLUMN_NAME") or row.get("column_name") or ""
        dtype = row.get("DATA_TYPE") or row.get("data_type") or ""
        nullable = row.get("NULLABLE") or row.get("nullable") or "Y"
        data_length = row.get("DATA_LENGTH") or row.get("data_length") or ""
        if table and col:
            tables.setdefault(table, []).append(
                {
                    "column": col,
                    "data_type": dtype,
                    "nullable": nullable == "Y",
                    "data_length": data_length,
                }
            )
    return {"table_columns": tables}


def inject_into_graph(metadata: dict, graph_path: Path) -> int:
    """Inject metadata as nodes/edges into existing graph.json."""
    if not graph_path.exists():
        return 0

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = graph.get("nodes", [])
    edges = graph.get("links", graph.get("edges", []))
    existing_ids = {n["id"] for n in nodes}
    added = 0

    # Inject DBA_OBJECTS as nodes
    for obj in metadata.get("dba_objects", []):
        nid = _make_id("oracle", obj["type"], obj["name"])
        if nid not in existing_ids:
            nodes.append(
                {
                    "id": nid,
                    "label": f"{obj['type']}:{obj['name']}",
                    "file_type": "code",
                    "source_file": "",
                    "source_location": None,
                }
            )
            existing_ids.add(nid)
            added += 1

    # Inject DBA_DEPENDENCIES as edges
    for dep in metadata.get("dba_dependencies", []):
        src_nid = _make_id("oracle", dep["source_type"], dep["source"])
        tgt_nid = _make_id("oracle", dep["target_type"], dep["target"])
        if src_nid not in existing_ids:
            nodes.append(
                {
                    "id": src_nid,
                    "label": f"{dep['source_type']}:{dep['source']}",
                    "file_type": "code",
                    "source_file": "",
                    "source_location": None,
                }
            )
            existing_ids.add(src_nid)
        if tgt_nid not in existing_ids:
            nodes.append(
                {
                    "id": tgt_nid,
                    "label": f"{dep['target_type']}:{dep['target']}",
                    "file_type": "code",
                    "source_file": "",
                    "source_location": None,
                }
            )
            existing_ids.add(tgt_nid)
        edges.append(
            {
                "source": src_nid,
                "target": tgt_nid,
                "relation": "depends_on",
                "confidence": "EXTRACTED",
                "source_file": "DBA_DEPENDENCIES",
                "weight": 1.0,
            }
        )
        added += 1

    # Write back
    if "links" in graph:
        graph["links"] = edges
    else:
        graph["edges"] = edges
    graph["nodes"] = nodes
    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return added


PROCESSORS = {
    "dba_objects": process_dba_objects,
    "dba_dependencies": process_dba_dependencies,
    "dba_tab_columns": process_dba_tab_columns,
}


def main():
    if len(sys.argv) < 5 or "--file" not in sys.argv or "--type" not in sys.argv:
        print(
            "Usage: python3 ingest_oracle_metadata.py [root] --file <path> --type <dba_objects|dba_dependencies|dba_tab_columns>"
        )
        sys.exit(1)

    root = (
        Path(sys.argv[1]).resolve() if sys.argv[1] != "--file" else Path(".").resolve()
    )

    file_idx = sys.argv.index("--file")
    input_path = Path(sys.argv[file_idx + 1]).resolve()

    type_idx = sys.argv.index("--type")
    data_type = sys.argv[type_idx + 1].lower()

    if data_type not in PROCESSORS:
        print(
            f"ERROR: Unknown type '{data_type}'. Supported: {list(PROCESSORS.keys())}"
        )
        sys.exit(1)

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    print(f"Loading {data_type} from {input_path.name}...", file=sys.stderr)
    rows = load_input(input_path)
    print(f"  Loaded {len(rows)} rows", file=sys.stderr)

    metadata = PROCESSORS[data_type](rows)

    # Save to .migration/oracle/
    out_dir = root / ".migration" / "discovery" / "oracle"
    out_dir.mkdir(parents=True, exist_ok=True)

    existing_meta = {}
    meta_path = out_dir / "schema-metadata.json"
    if meta_path.exists():
        existing_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    existing_meta.update(metadata)
    meta_path.write_text(json.dumps(existing_meta, indent=2), encoding="utf-8")

    # Try to inject into graph
    graph_path = root / ".migration" / "discovery" / "graphify-out" / "graph.json"
    injected = inject_into_graph(metadata, graph_path)

    print("\n# Oracle Metadata Ingestion")
    print("")
    print(f"**Type**: {data_type}")
    print(f"**Rows processed**: {len(rows)}")
    if injected:
        print(f"**Nodes/edges injected into graph**: {injected}")
    print(f"**Output**: {meta_path}")


if __name__ == "__main__":
    main()
