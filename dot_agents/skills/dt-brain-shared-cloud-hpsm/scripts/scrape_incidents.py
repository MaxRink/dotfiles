#!/usr/bin/env python3
"""
HPSM Incident Scraper
Scrape open incidents from the HPSM (TDI Trouble Ticket) incident queue
for a given assignment group using playwright-cli.

Usage:
    source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py [ASSIGNMENT_GROUP]

Default assignment group: INFRA-CAAS-L2S
Requires: HPSM_USERNAME, HPSM_PASSWORD env vars, VPN, playwright-cli
Output: JSON array of incidents to stdout
"""

import os
import re
import sys
import json
import time
import argparse
import subprocess
from typing import Dict, List, Optional, Tuple


# Constants
HPSM_URL = "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
DEFAULT_GROUP = "INFRA-CAAS-L2S"
MAX_LOGIN_ATTEMPTS = 3
LDAP_RETRY_DELAY = 10

# JavaScript for extracting incident data from the ExtJS treegrid.
# The grid uses .x-grid3-row elements with aria-level="2" for data rows
# and .x-grid3-cell-inner for cell values (ordered by column position).
EXTRACT_JS = """el => {
  const body = el.querySelector(".x-grid3-body");
  if (!body) return JSON.stringify({ error: "No grid body found" });
  const rows = body.querySelectorAll('.x-grid3-row[aria-level="2"]');
  const results = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll(".x-grid3-cell-inner");
    if (cells.length > 14) {
      results.push({
        incidentId: cells[1]?.textContent?.trim() || "",
        category: cells[2]?.textContent?.trim() || "",
        alertStatus: cells[3]?.textContent?.trim() || "",
        status: cells[4]?.textContent?.trim() || "",
        assignmentGroup: cells[5]?.textContent?.trim() || "",
        assignee: cells[6]?.textContent?.trim() || "",
        title: cells[7]?.textContent?.trim() || "",
        description: cells[8]?.textContent?.trim() || "",
        priority: cells[9]?.textContent?.trim() || "",
        impact: cells[10]?.textContent?.trim() || "",
        urgency: cells[11]?.textContent?.trim() || "",
        parent: cells[12]?.textContent?.trim() || "",
        parentIncident: cells[13]?.textContent?.trim() || "",
        openTime: cells[14]?.textContent?.trim() || ""
      });
    }
  });
  return JSON.stringify(results, null, 2);
}"""


def log(msg: str) -> None:
    """Print to stderr for progress messages."""
    print(msg, file=sys.stderr)


def run_cli(*args: str, check: bool = True) -> str:
    """Run a playwright-cli command and return its stdout."""
    cmd = ["playwright-cli", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"playwright-cli {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def take_snapshot() -> str:
    """Take a snapshot and return the full YAML content (not just the file path)."""
    output = run_cli("snapshot")
    # Extract the snapshot file path from output like:
    #   - [Snapshot](.playwright-cli/page-2026-03-10T12-28-32-832Z.yml)
    match = re.search(r'\((.playwright-cli/[^\)]+\.yml)\)', output)
    if not match:
        raise RuntimeError(f"Could not find snapshot file in output:\n{output}")
    snapshot_path = match.group(1)
    with open(snapshot_path, "r") as f:
        return f.read()


def find_ref(snapshot: str, pattern: str) -> Optional[str]:
    """
    Find an element ref in snapshot output matching a pattern.

    Note: HPSM uses Unicode icon characters (e.g. \\uea1d) that look like spaces
    in the snapshot. We normalize these for matching.
    """
    def normalize(s: str) -> str:
        # Replace non-ASCII chars with space, then collapse multiple spaces
        return re.sub(r'\s+', ' ', re.sub(r'[^\x20-\x7E]', ' ', s))

    normalized_pattern = normalize(pattern)
    for line in snapshot.splitlines():
        if normalized_pattern in normalize(line):
            match = re.search(r'\[ref=([a-z0-9]+)\]', line)
            if match:
                return match.group(1)
    return None


def close_browser() -> None:
    """Close the playwright-cli browser session."""
    try:
        run_cli("close", check=False)
    except Exception:
        pass


def login(username: str, password: str) -> str:
    """
    Login to HPSM with LDAP retry.

    LDAP transient errors manifest as "Invalid login name/password" — the same
    message as wrong credentials. We retry up to MAX_LOGIN_ATTEMPTS times with
    a delay between attempts.

    Returns the post-login snapshot output on success.
    Raises RuntimeError on failure.
    """
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        snapshot = take_snapshot()

        username_ref = find_ref(snapshot, 'textbox "Username"')
        password_ref = find_ref(snapshot, 'textbox "Password"')
        login_ref = find_ref(snapshot, 'button "LOGIN"')

        if not all([username_ref, password_ref, login_ref]):
            log(f"  Could not find login form elements (attempt {attempt})")
            time.sleep(5)
            continue

        run_cli("fill", username_ref, username)
        run_cli("fill", password_ref, password)
        run_cli("click", login_ref)
        time.sleep(5)

        # Dashboard can take time to load — poll for navigation tree
        post_login = take_snapshot()
        for wait in range(5):
            if "Incident Management" in post_login:
                break
            time.sleep(3)
            post_login = take_snapshot()

        if "Incident Management" in post_login:
            log(f"  Login successful (attempt {attempt})")
            return post_login

        if "Invalid login" in post_login:
            log(f"  Login failed (attempt {attempt}) — LDAP transient error, "
                f"retrying in {LDAP_RETRY_DELAY}s...")
            time.sleep(LDAP_RETRY_DELAY)
            continue

        log(f"  Unexpected state after login (attempt {attempt})")
        time.sleep(5)

    raise RuntimeError(f"Failed to login after {MAX_LOGIN_ATTEMPTS} attempts")


def navigate_to_incident_queue(sidebar_snapshot: str) -> str:
    """
    Navigate from the HPSM dashboard to the Incident Queue.

    The sidebar is an ARIA tree widget with treeitem elements.
    Click "Incident Management" to expand, then "Incident Queue".

    Returns the snapshot after the incident table has loaded.
    """
    # Click "Incident Management" treeitem
    im_ref = find_ref(sidebar_snapshot, 'treeitem " Incident Management"')
    if not im_ref:
        raise RuntimeError("Could not find 'Incident Management' in sidebar")

    run_cli("click", im_ref)
    time.sleep(2)

    # Click "Incident Queue" in expanded sub-menu
    nav_snapshot = take_snapshot()
    iq_ref = find_ref(nav_snapshot, 'treeitem "Incident Queue"')
    if not iq_ref:
        raise RuntimeError("Could not find 'Incident Queue' in sub-menu")

    run_cli("click", iq_ref)

    # Wait for the ExtJS treegrid to load
    time.sleep(8)
    table_snapshot = take_snapshot()

    for retry in range(5):
        if "Record List" in table_snapshot:
            return table_snapshot
        time.sleep(3)
        table_snapshot = take_snapshot()

    raise RuntimeError("Incident table did not load after waiting")


def expand_group(table_snapshot: str, group: str) -> Tuple[str, str]:
    """
    Expand an assignment group in the incident queue treegrid.

    The queue groups incidents by assignment group. Group headers are level-1
    rows with text like "Level 1 Group, Assignment Group, INFRA-CAAS-L2S, 17 Items".

    Returns (expanded_snapshot, item_count_text).
    """
    group_ref = find_ref(
        table_snapshot,
        f'gridcell "Level 1 Group, Assignment Group, {group}'
    )
    if not group_ref:
        # List available groups to help the user
        available = []
        seen = set()
        for line in table_snapshot.splitlines():
            m = re.search(r'Assignment Group,\s*([^,]+),\s*(\d+ Items?)', line)
            if m:
                name = m.group(1).strip()
                if name not in seen:
                    seen.add(name)
                    available.append(f"  - {name} ({m.group(2)})")
        hint = ""
        if available:
            hint = "\n\nAvailable groups:\n" + "\n".join(available)
        raise RuntimeError(
            f"Assignment group '{group}' not found in incident queue{hint}"
        )

    # Extract item count for reporting
    item_match = re.search(rf'{group}.*?(\d+ Items?)', table_snapshot)
    item_count = item_match.group(1) if item_match else "? Items"

    run_cli("click", group_ref)
    time.sleep(4)

    expanded_snapshot = take_snapshot()
    return expanded_snapshot, item_count


def extract_incidents(snapshot: str) -> List[Dict]:
    """
    Extract incident data from the expanded ExtJS treegrid.

    Uses `playwright-cli eval` on the treegrid ref with JavaScript that queries
    .x-grid3-row[aria-level="2"] elements. The eval command automatically
    resolves the correct iframe for the snapshot ref.
    """
    grid_ref = find_ref(snapshot, 'treegrid "Record List')
    if not grid_ref:
        raise RuntimeError("Could not find treegrid element")

    result = run_cli("eval", EXTRACT_JS, grid_ref)

    # Parse the JSON from playwright-cli output
    # Output format: ### Result\n"<escaped-json>"\n### Ran Playwright code...
    json_str = parse_eval_result(result)
    incidents = json.loads(json_str)

    if isinstance(incidents, dict) and "error" in incidents:
        raise RuntimeError(f"Extraction error: {incidents['error']}")

    return incidents


def parse_eval_result(output: str) -> str:
    """
    Parse JSON from playwright-cli eval output.

    The eval command returns output in this format:
        ### Result
        "<json-string-with-escaped-quotes>"
        ### Ran Playwright code
        ...

    The JSON is wrapped in quotes with internal quotes escaped.
    """
    lines = output.strip().splitlines()

    # Find the line after "### Result"
    for i, line in enumerate(lines):
        if line.strip() == "### Result":
            if i + 1 < len(lines):
                raw = lines[i + 1].strip()
                # If it starts and ends with quotes, it's a JSON string that needs unescaping
                if raw.startswith('"') and raw.endswith('"'):
                    # Remove outer quotes and unescape inner quotes
                    return json.loads(raw)
                # Otherwise it might be raw JSON
                return raw

    # Fallback: try to find JSON array in the output
    match = re.search(r'(\[[\s\S]*\])', output)
    if match:
        return match.group(1)

    raise RuntimeError(f"Could not parse eval result:\n{output[:500]}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape HPSM incidents for an assignment group"
    )
    parser.add_argument(
        "group",
        nargs="?",
        default=DEFAULT_GROUP,
        help=f"Assignment group to scrape (default: {DEFAULT_GROUP})"
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--list-groups",
        action="store_true",
        help="List available assignment groups and exit"
    )
    args = parser.parse_args()

    # Validate environment
    username = os.environ.get("HPSM_USERNAME")
    password = os.environ.get("HPSM_PASSWORD")
    if not username or not password:
        log("ERROR: HPSM_USERNAME and HPSM_PASSWORD must be set")
        log("Hint: run 'source .env' before this script")
        sys.exit(1)

    log(f"=== HPSM Incident Scraper ===")
    log(f"Assignment Group: {args.group}")
    log("")

    try:
        # Step 1: Open browser
        log("[1/6] Opening browser...")
        run_cli("open", HPSM_URL)
        time.sleep(3)

        # Step 2: Login
        log("[2/6] Logging in...")
        post_login = login(username, password)

        # Step 3: Navigate to Incident Queue
        log("[3/6] Navigating to Incident Queue...")
        table_snapshot = navigate_to_incident_queue(post_login)

        # If --list-groups, print available groups and exit
        if args.list_groups:
            log("\nAvailable assignment groups:")
            seen = set()
            for line in table_snapshot.splitlines():
                m = re.search(r'Assignment Group,\s*([^,]+),\s*(\d+ Items?)', line)
                if m:
                    name = m.group(1).strip()
                    if name not in seen:
                        seen.add(name)
                        log(f"  - {name} ({m.group(2)})")
            close_browser()
            sys.exit(0)

        # Step 4: Find and expand assignment group
        log(f"[4/6] Expanding {args.group} group...")
        expanded_snapshot, item_count = expand_group(table_snapshot, args.group)
        log(f"  Found: {args.group} ({item_count})")

        # Step 5: Extract incidents
        log("[5/6] Extracting incidents...")
        incidents = extract_incidents(expanded_snapshot)

        # Step 6: Close browser
        log("[6/6] Closing browser...")
        close_browser()

        log(f"\nSuccessfully extracted {len(incidents)} incidents from {args.group}")

        # Output
        if args.format == "table":
            print_table(incidents)
        else:
            print(json.dumps(incidents, indent=2))

    except Exception as e:
        log(f"\nERROR: {e}")
        close_browser()
        sys.exit(1)


def print_table(incidents: List[Dict]) -> None:
    """Print incidents as a formatted table."""
    if not incidents:
        print("No incidents found.")
        return

    # Column definitions: (header, key, max_width)
    columns = [
        ("Incident ID", "incidentId", 10),
        ("Status", "status", 20),
        ("Assignee", "assignee", 10),
        ("Title", "title", 80),
        ("Priority", "priority", 12),
        ("Open Time", "openTime", 18),
    ]

    # Print header
    header = " | ".join(h.ljust(w) for h, _, w in columns)
    print(header)
    print("-" * len(header))

    # Print rows
    for inc in incidents:
        row = " | ".join(
            str(inc.get(k, ""))[:w].ljust(w)
            for _, k, w in columns
        )
        print(row)


if __name__ == "__main__":
    main()
