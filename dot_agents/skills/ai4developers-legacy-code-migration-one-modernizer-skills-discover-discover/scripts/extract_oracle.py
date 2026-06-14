#!/usr/bin/env python3
"""Parse Oracle DDL dumps and PL/SQL files to build procedure→table dependency maps.

Usage: python3 extract_oracle.py [project-root]

Scans for .sql, .pls, .pkb, .pks, .trg, .fnc, .prc files and produces:
- .migration/oracle/objects.json — inventory of all DB objects
- .migration/oracle/dependencies.json — procedure→table dependency map
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _constants import ORACLE_EXTENSIONS, IGNORE_DIRS

_RE_CREATE_TABLE = re.compile(
    r"CREATE\s+(?:GLOBAL\s+TEMPORARY\s+)?TABLE\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_VIEW = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:FORCE\s+)?(?:MATERIALIZED\s+)?VIEW\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_PACKAGE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+(BODY\s+)?(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_PROC = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_FUNC = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_TRIGGER = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_SEQUENCE = re.compile(
    r"CREATE\s+SEQUENCE\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_SYNONYM = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:PUBLIC\s+)?SYNONYM\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?\s+FOR\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_CREATE_DBLINK = re.compile(
    r"CREATE\s+(?:PUBLIC\s+)?DATABASE\s+LINK\s+\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_TRIGGER_ON = re.compile(
    r"(?:BEFORE|AFTER|INSTEAD\s+OF)\s+(?:INSERT|UPDATE|DELETE)(?:\s+OR\s+(?:INSERT|UPDATE|DELETE))*\s+ON\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_TABLE_DML = re.compile(
    r"(?:FROM|INTO|UPDATE|DELETE\s+FROM|INSERT\s+INTO|MERGE\s+INTO|JOIN)\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?",
    re.IGNORECASE,
)
_RE_PARTITION = re.compile(
    r"PARTITION\s+BY\s+(RANGE|LIST|HASH)\s*\(\s*(\w+)",
    re.IGNORECASE,
)

_SQL_NOISE = frozenset(
    {
        "SET",
        "VALUES",
        "WHERE",
        "SELECT",
        "NULL",
        "DUAL",
        "FROM",
        "INTO",
        "BEGIN",
        "END",
        "IF",
        "THEN",
        "ELSE",
        "LOOP",
        "EXIT",
        "WHEN",
        "EXCEPTION",
        "RETURN",
        "IS",
        "AS",
        "DECLARE",
        "CURSOR",
        "TABLE",
        "NOT",
        "AND",
        "OR",
        "EXISTS",
        "IN",
        "ANY",
        "ALL",
        "BETWEEN",
    }
)


def scan_file(path: Path, root: Path) -> dict:
    """Extract Oracle objects and dependencies from a single file."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    rel = str(path.relative_to(root))
    objects = []
    dependencies = []

    def _line(pos):
        return content[:pos].count("\n") + 1

    # Tables
    for m in _RE_CREATE_TABLE.finditer(content):
        name = m.group(1)
        obj = {"type": "TABLE", "name": name, "file": rel, "line": _line(m.start())}
        # Check for partitioning
        region = content[m.start() : m.start() + 2000]
        pm = _RE_PARTITION.search(region)
        if pm:
            obj["partition_type"] = pm.group(1).upper()
            obj["partition_key"] = pm.group(2)
        objects.append(obj)

    # Views
    for m in _RE_CREATE_VIEW.finditer(content):
        name = m.group(1)
        is_mview = "MATERIALIZED" in content[m.start() : m.end()].upper()
        obj_type = "MATERIALIZED_VIEW" if is_mview else "VIEW"
        objects.append(
            {"type": obj_type, "name": name, "file": rel, "line": _line(m.start())}
        )

    # Packages
    for m in _RE_CREATE_PACKAGE.finditer(content):
        is_body = m.group(1) is not None
        name = m.group(2)
        obj_type = "PACKAGE_BODY" if is_body else "PACKAGE_SPEC"
        objects.append(
            {"type": obj_type, "name": name, "file": rel, "line": _line(m.start())}
        )

    # Procedures
    for m in _RE_CREATE_PROC.finditer(content):
        name = m.group(1)
        objects.append(
            {"type": "PROCEDURE", "name": name, "file": rel, "line": _line(m.start())}
        )
        # Find table references in procedure body
        body_start = m.end()
        body_end = min(body_start + 50000, len(content))
        body = content[body_start:body_end]
        tables = _extract_table_refs(body)
        for t in tables:
            dependencies.append(
                {
                    "source": name,
                    "source_type": "PROCEDURE",
                    "target": t,
                    "target_type": "TABLE",
                    "file": rel,
                }
            )

    # Functions
    for m in _RE_CREATE_FUNC.finditer(content):
        name = m.group(1)
        objects.append(
            {"type": "FUNCTION", "name": name, "file": rel, "line": _line(m.start())}
        )
        body_start = m.end()
        body_end = min(body_start + 50000, len(content))
        body = content[body_start:body_end]
        tables = _extract_table_refs(body)
        for t in tables:
            dependencies.append(
                {
                    "source": name,
                    "source_type": "FUNCTION",
                    "target": t,
                    "target_type": "TABLE",
                    "file": rel,
                }
            )

    # Triggers
    for m in _RE_CREATE_TRIGGER.finditer(content):
        name = m.group(1)
        obj = {"type": "TRIGGER", "name": name, "file": rel, "line": _line(m.start())}
        # Find target table
        region = content[m.start() : m.start() + 500]
        on_match = _RE_TRIGGER_ON.search(region)
        if on_match:
            obj["fires_on"] = on_match.group(1)
            dependencies.append(
                {
                    "source": name,
                    "source_type": "TRIGGER",
                    "target": on_match.group(1),
                    "target_type": "TABLE",
                    "file": rel,
                }
            )
        objects.append(obj)

    # Sequences
    for m in _RE_CREATE_SEQUENCE.finditer(content):
        objects.append(
            {
                "type": "SEQUENCE",
                "name": m.group(1),
                "file": rel,
                "line": _line(m.start()),
            }
        )

    # Synonyms
    for m in _RE_CREATE_SYNONYM.finditer(content):
        syn_name = m.group(1)
        target = m.group(2)
        objects.append(
            {
                "type": "SYNONYM",
                "name": syn_name,
                "target": target,
                "file": rel,
                "line": _line(m.start()),
            }
        )
        dependencies.append(
            {
                "source": syn_name,
                "source_type": "SYNONYM",
                "target": target,
                "target_type": "TABLE",
                "file": rel,
            }
        )

    # DB Links
    for m in _RE_CREATE_DBLINK.finditer(content):
        objects.append(
            {
                "type": "DB_LINK",
                "name": m.group(1),
                "file": rel,
                "line": _line(m.start()),
            }
        )

    return {"objects": objects, "dependencies": dependencies}


def _extract_table_refs(body: str) -> list[str]:
    """Extract table names from DML in a procedure/function body."""
    tables = set()
    for m in _RE_TABLE_DML.finditer(body):
        name = m.group(1)
        if name.upper() not in _SQL_NOISE and len(name) > 1:
            tables.add(name)
    return sorted(tables)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"Scanning {root.name} for Oracle DDL/PL-SQL...", file=sys.stderr)

    all_objects = []
    all_dependencies = []

    for f in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in f.parts):
            continue
        if not f.is_file() or f.suffix.lower() not in ORACLE_EXTENSIONS:
            continue

        result = scan_file(f, root)
        all_objects.extend(result.get("objects", []))
        all_dependencies.extend(result.get("dependencies", []))

    # Output
    out_dir = root / ".migration" / "discovery" / "oracle"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Object inventory
    by_type = defaultdict(list)
    for obj in all_objects:
        by_type[obj["type"]].append(obj)

    (out_dir / "objects.json").write_text(
        json.dumps({"objects": all_objects, "by_type": dict(by_type)}, indent=2),
        encoding="utf-8",
    )

    # Dependency map
    (out_dir / "dependencies.json").write_text(
        json.dumps({"dependencies": all_dependencies}, indent=2),
        encoding="utf-8",
    )

    # Summary
    print("\n# Oracle Object Inventory")
    print("")
    for obj_type, objs in sorted(by_type.items()):
        print(f"- **{obj_type}**: {len(objs)}")
    print("")
    print(f"**Total dependencies mapped**: {len(all_dependencies)}")
    print("")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
