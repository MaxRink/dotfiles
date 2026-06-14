#!/usr/bin/env python3
"""
HPSM Change Request Creator
Create a Standard/Normal/Emergency change request in HPSM (TDI Trouble Ticket)
using playwright-cli.

Usage:
    source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/create_change.py \\
        --title "Upgrade cluster firmware" \\
        --description "Upgrade firmware on worker nodes" \\
        --effect "Nodes remain vulnerable to CVEs"

Requires: HPSM_USERNAME, HPSM_PASSWORD env vars, VPN, playwright-cli
Output: Change ID to stdout (e.g. C22016)
"""

import os
import re
import sys
import json
import time
import argparse
import subprocess
from typing import Optional


# Constants
HPSM_URL = "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
MAX_LOGIN_ATTEMPTS = 3
LDAP_RETRY_DELAY = 10

# Defaults for CaaS team
DEFAULT_MODEL = "Standard Change"
DEFAULT_GROUP = "INFRA-CAAS-L2S"
DEFAULT_SERVICE = "CAAS_BM"
DEFAULT_IMPACT = "4 - User"
DEFAULT_URGENCY = "4 - Low"
DEFAULT_REASON = "Maintenance"


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
    """Take a snapshot and return the full YAML content."""
    output = run_cli("snapshot")
    # playwright-cli may write snapshot to a file and return the path,
    # or it may return the YAML content directly.
    match = re.search(r'\((.playwright-cli/[^\)]+\.yml)\)', output)
    if match:
        with open(match.group(1), "r") as f:
            return f.read()
    # Output is the snapshot content directly
    return output


def find_ref(snapshot: str, pattern: str) -> Optional[str]:
    """
    Find an element ref in snapshot output matching a pattern.
    Normalizes Unicode icon characters (e.g. \\uea1d) for matching.
    """
    def normalize(s: str) -> str:
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


def dismiss_popup(snapshot: str) -> str:
    """Dismiss any HPSM validation popup. Returns updated snapshot."""
    ok_ref = find_ref(snapshot, 'button "OK"')
    if not ok_ref:
        ok_ref = find_ref(snapshot, 'button "Yes"')
    if ok_ref:
        run_cli("click", ok_ref)
        time.sleep(1)
        return take_snapshot()
    return snapshot


def login(username: str, password: str) -> str:
    """
    Login to HPSM with LDAP retry.
    Returns the post-login snapshot on success.
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

        post_login = take_snapshot()
        for wait in range(5):
            if "Change Management" in post_login:
                break
            time.sleep(3)
            post_login = take_snapshot()

        if "Change Management" in post_login:
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


def navigate_to_create_change(sidebar_snapshot: str) -> str:
    """Navigate to Change Management → Create New Change."""
    # Click Change Management treeitem
    cm_ref = find_ref(sidebar_snapshot, 'Change Management')
    if not cm_ref:
        raise RuntimeError("Could not find 'Change Management' in sidebar")

    run_cli("click", cm_ref)
    time.sleep(2)

    # Click Create New Change
    snapshot = take_snapshot()
    cnc_ref = find_ref(snapshot, 'treeitem "Create New Change"')
    if not cnc_ref:
        raise RuntimeError("Could not find 'Create New Change' in sub-menu")

    run_cli("click", cnc_ref)
    time.sleep(5)

    return take_snapshot()


def select_change_model(dialog_snapshot: str, model: str) -> str:
    """
    Select a change model from the 'Select Change Model' grid.
    Models appear as links in gridcells: link "Standard Change", etc.
    """
    link_ref = find_ref(dialog_snapshot, f'link "{model}"')
    if not link_ref:
        available = []
        for line in dialog_snapshot.splitlines():
            m = re.search(r'link "(.*?Change)"', line)
            if m and m.group(1) not in available:
                available.append(m.group(1))
        raise RuntimeError(
            f"Change model '{model}' not found. "
            f"Available: {', '.join(available) if available else 'none detected'}"
        )

    run_cli("click", link_ref)
    log(f"  Selected model: {model}")
    time.sleep(5)

    return take_snapshot()


def fill_field(ref: str, value: str, press_tab: bool = True) -> None:
    """Fill a field by ref and optionally press Tab to trigger validation."""
    run_cli("fill", ref, value)
    if press_tab:
        time.sleep(0.5)
        run_cli("press", "Tab")
        time.sleep(1)


def fill_click_to_activate_field(snapshot: str, label: str, value: str) -> str:
    """
    Fill a click-to-activate field (Description, Effect of not Implementing).
    These appear as paragraph elements that become textboxes when clicked.
    Returns updated snapshot.
    """
    # Find the paragraph inside the field container
    para_ref = None
    lines = snapshot.splitlines()
    for i, line in enumerate(lines):
        if f'generic [ref=' in line and label in line:
            # Look for paragraph in the next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                m = re.search(r'paragraph \[ref=([a-z0-9]+)\]', lines[j])
                if m:
                    para_ref = m.group(1)
                    break
            break

    if not para_ref:
        raise RuntimeError(f"Could not find paragraph for '{label}'")

    # Click to activate
    run_cli("click", para_ref)
    time.sleep(1)

    # Re-snapshot to get the activated textbox ref
    snapshot = take_snapshot()
    tb_ref = find_ref(snapshot, f'textbox "{label}"')
    if not tb_ref:
        raise RuntimeError(f"Textbox for '{label}' did not activate after click")

    run_cli("fill", tb_ref, value)
    return snapshot


def extract_change_id(snapshot: str) -> Optional[str]:
    """Extract the Change ID from the form snapshot."""
    for line in snapshot.splitlines():
        m = re.search(r'textbox "Change ID".*?:\s*(C\d+)', line)
        if m:
            return m.group(1)
    # Also try page heading
    for line in snapshot.splitlines():
        m = re.search(r'Change\s*-\s*(C\d+)', line)
        if m:
            return m.group(1)
    return None


def fill_change_form(
    form_snapshot: str,
    title: str,
    description: str,
    effect: str,
    requester_group: str,
    coordinator_group: str,
    impact: str,
    urgency: str,
    requested_end_date: str,
    reason: str,
    service: str,
) -> str:
    """
    Fill all fields in the change request form.
    Returns the snapshot after all fields are filled.
    """
    # Regular text/combobox fields (fill + Tab)
    fields = [
        ('textbox "Title"', title),
        ('textbox "Change Requester - Group"', requester_group),
        ('combobox "Impact"', impact),
        ('combobox "Urgency"', urgency),
        ('textbox "Requested End Date"', requested_end_date),
        ('combobox "Reason for Change"', reason),
        ('textbox "Service"', service),
        ('textbox "Change Coordinator Group"', coordinator_group),
    ]

    for field_pattern, value in fields:
        ref = find_ref(form_snapshot, field_pattern)
        if not ref:
            log(f"  WARNING: Field '{field_pattern}' not found, skipping")
            continue
        fill_field(ref, value)
        log(f"  Filled: {field_pattern.split('\"')[1]} = {value}")

    # Re-snapshot after all regular fields
    snapshot = take_snapshot()
    snapshot = dismiss_popup(snapshot)

    # Click-to-activate fields (Description, Effect)
    log("  Filling Description...")
    snapshot = fill_click_to_activate_field(snapshot, "Description", description)

    log("  Filling Effect of not Implementing...")
    snapshot = fill_click_to_activate_field(snapshot, "Effect of not Implementing", effect)

    return take_snapshot()


def save_change(snapshot: str) -> str:
    """
    Click the Save button and return the Change ID.
    The Save button is in the top toolbar (outside iframe).
    """
    save_ref = find_ref(snapshot, 'button "Save Record (Ctrl+Shift+F4)"')
    if not save_ref:
        # Fallback: look for button with text "Save" that isn't "Save & Exit"
        save_ref = find_ref(snapshot, ': Save')
        if not save_ref:
            raise RuntimeError("Save button not found")

    run_cli("click", save_ref)
    log("  Clicked Save, waiting for confirmation...")
    time.sleep(5)

    snapshot = take_snapshot()
    snapshot = dismiss_popup(snapshot)

    change_id = extract_change_id(snapshot)
    return change_id or "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Create an HPSM change request"
    )
    parser.add_argument(
        "--title", required=True,
        help="Change request title"
    )
    parser.add_argument(
        "--description", required=True,
        help="Change description text"
    )
    parser.add_argument(
        "--effect", required=True,
        help="Effect of not implementing the change"
    )
    parser.add_argument(
        "--model",
        choices=["Standard Change", "Normal Change", "Emergency Change"],
        default=DEFAULT_MODEL,
        help=f"Change model type (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--group", default=DEFAULT_GROUP,
        help=f"Requester and Coordinator group (default: {DEFAULT_GROUP})"
    )
    parser.add_argument(
        "--service", default=DEFAULT_SERVICE,
        help=f"Service (default: {DEFAULT_SERVICE})"
    )
    parser.add_argument(
        "--impact", default=DEFAULT_IMPACT,
        help=f"Impact level (default: {DEFAULT_IMPACT})"
    )
    parser.add_argument(
        "--urgency", default=DEFAULT_URGENCY,
        help=f"Urgency level (default: {DEFAULT_URGENCY})"
    )
    parser.add_argument(
        "--end-date", required=True,
        help="Requested end date in DD/MM/YY HH:MM:SS format"
    )
    parser.add_argument(
        "--reason", default=DEFAULT_REASON,
        help=f"Reason for change (default: {DEFAULT_REASON})"
    )
    parser.add_argument(
        "--headed", action="store_true",
        help="Show the browser window during execution"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fill the form but do NOT save (for validation)"
    )
    args = parser.parse_args()

    # Validate date format
    if not re.match(r'\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', args.end_date):
        log("ERROR: --end-date must be in DD/MM/YY HH:MM:SS format")
        log("Example: 31/03/26 00:00:00")
        sys.exit(1)

    # Validate environment
    username = os.environ.get("HPSM_USERNAME")
    password = os.environ.get("HPSM_PASSWORD")
    if not username or not password:
        log("ERROR: HPSM_USERNAME and HPSM_PASSWORD must be set")
        log("Hint: run 'source .env' before this script")
        sys.exit(1)

    log("=== HPSM Change Request Creator ===")
    log(f"Model: {args.model}")
    log(f"Title: {args.title}")
    log(f"Group: {args.group}")
    log(f"End Date: {args.end_date}")
    if args.dry_run:
        log("Mode: DRY RUN (will NOT save)")
    log("")

    try:
        # Step 1: Open browser
        log("[1/7] Opening browser...")
        open_args = ["open"]
        if args.headed:
            open_args.append("--headed")
        open_args.append(HPSM_URL)
        run_cli(*open_args)
        time.sleep(3)

        # Step 2: Login
        log("[2/7] Logging in...")
        post_login = login(username, password)

        # Step 3: Navigate to Create New Change
        log("[3/7] Navigating to Create New Change...")
        dialog_snapshot = navigate_to_create_change(post_login)

        # Step 4: Select change model
        log(f"[4/7] Selecting {args.model}...")
        form_snapshot = select_change_model(dialog_snapshot, args.model)

        # Extract auto-assigned Change ID
        change_id = extract_change_id(form_snapshot)
        if change_id:
            log(f"  Change ID assigned: {change_id}")

        # Step 5: Fill the form
        log("[5/7] Filling change form...")
        filled_snapshot = fill_change_form(
            form_snapshot,
            title=args.title,
            description=args.description,
            effect=args.effect,
            requester_group=args.group,
            coordinator_group=args.group,
            impact=args.impact,
            urgency=args.urgency,
            requested_end_date=args.end_date,
            reason=args.reason,
            service=args.service,
        )

        if args.dry_run:
            # Take screenshot for verification
            log("[6/7] Taking screenshot (dry run)...")
            run_cli("screenshot")
            log("[7/7] Dry run complete — form filled but NOT saved")
            log(f"\nChange ID: {change_id or 'unknown'} (NOT saved)")
            log("Browser left open for manual inspection.")
            if change_id:
                print(change_id)
        else:
            # Step 6: Save
            log("[6/7] Saving change...")
            saved_id = save_change(filled_snapshot)

            # Step 7: Close browser
            log("[7/7] Closing browser...")
            close_browser()

            log(f"\nChange request saved: {saved_id}")
            print(saved_id)

    except Exception as e:
        log(f"\nERROR: {e}")
        if not args.dry_run:
            close_browser()
        sys.exit(1)


if __name__ == "__main__":
    main()
