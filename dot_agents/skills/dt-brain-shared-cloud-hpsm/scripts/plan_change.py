#!/usr/bin/env python3
"""
HPSM Plan & Schedule Change
Navigate to an existing change request and fill the Plan & Schedule phase.

Usage:
    source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/plan_change.py \
        --change-id C22382 \
        --start "05/05/26 18:00:00" \
        --end "05/05/26 19:00:00" \
        --implementation-plan "Step 1: ..." \
        --remediation-plan "Step 1: ..."

Requires: HPSM_USERNAME, HPSM_PASSWORD env vars, VPN, playwright-cli
"""

import os
import re
import sys
import time
import argparse
import subprocess
from typing import Optional


HPSM_URL = "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
MAX_LOGIN_ATTEMPTS = 3
LDAP_RETRY_DELAY = 10

DEFAULT_GROUP = "INFRA-CAAS-L2S"
DEFAULT_RISK = "1 - Low Risk"


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def run_cli(*args: str, check: bool = True) -> str:
    cmd = ["playwright-cli", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"playwright-cli {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def take_snapshot() -> str:
    """Take a snapshot and return the full YAML content."""
    output = run_cli("snapshot")
    match = re.search(r'\((.playwright-cli/[^\)]+\.yml)\)', output)
    if match:
        with open(match.group(1), "r") as f:
            return f.read()
    return output


def find_ref(snapshot: str, pattern: str) -> Optional[str]:
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
    try:
        run_cli("close", check=False)
    except Exception:
        pass


def dismiss_popup(snapshot: str) -> str:
    ok_ref = find_ref(snapshot, 'button "OK"')
    if not ok_ref:
        ok_ref = find_ref(snapshot, 'button "Yes"')
    if ok_ref:
        run_cli("click", ok_ref)
        time.sleep(1)
        return take_snapshot()
    return snapshot


def login(username: str, password: str) -> str:
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
        for _ in range(5):
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


def navigate_to_change(sidebar_snapshot: str, change_id: str) -> str:
    """Navigate to Change Management → Search Changes → find change by ID."""
    cm_ref = find_ref(sidebar_snapshot, 'Change Management')
    if not cm_ref:
        raise RuntimeError("Could not find 'Change Management' in sidebar")
    run_cli("click", cm_ref)
    time.sleep(2)

    snapshot = take_snapshot()
    sc_ref = find_ref(snapshot, 'treeitem "Search Changes"')
    if not sc_ref:
        raise RuntimeError("Could not find 'Search Changes' in sub-menu")
    run_cli("click", sc_ref)
    time.sleep(5)

    snapshot = take_snapshot()
    cid_ref = find_ref(snapshot, 'textbox "Change ID"')
    if not cid_ref:
        raise RuntimeError("Could not find 'Change ID' search field")
    run_cli("fill", cid_ref, change_id)
    time.sleep(0.5)

    # Click the Search button explicitly (pressing Return doesn't always work)
    search_ref = find_ref(snapshot, 'button "Start this Search')
    if search_ref:
        run_cli("click", search_ref)
    else:
        run_cli("press", "Return")
    time.sleep(8)

    snapshot = take_snapshot()
    snapshot = dismiss_popup(snapshot)  # dismiss "No Changes found" if any

    if change_id not in snapshot:
        raise RuntimeError(f"Change {change_id} not found after search")
    log(f"  Change {change_id} loaded")
    return snapshot


def click_plan_and_schedule(snapshot: str) -> str:
    """Click 'Request Plan and Schedule' button to advance the phase."""
    btn_ref = find_ref(snapshot, 'button "Request Plan and Schedule"')
    if not btn_ref:
        # Maybe already in Plan and Schedule phase
        if "Plan and Schedule" in snapshot:
            log("  Already in Plan and Schedule phase")
            return snapshot
        raise RuntimeError("'Request Plan and Schedule' button not found")
    run_cli("click", btn_ref)
    time.sleep(5)
    snapshot = take_snapshot()
    snapshot = dismiss_popup(snapshot)
    log("  Advanced to Plan and Schedule phase")
    return snapshot


def fill_field(ref: str, value: str, press_tab: bool = True) -> None:
    run_cli("fill", ref, value)
    if press_tab:
        time.sleep(0.5)
        run_cli("press", "Tab")
        time.sleep(1)


def fill_plan_form(
    form_snapshot: str,
    coordinator: str,
    owner: str,
    group: str,
    risk: str,
    start: str,
    end: str,
    downtime_start: Optional[str],
    downtime_end: Optional[str],
    implementation_plan: str,
    remediation_plan: str,
) -> str:
    # Main form fields
    main_fields = [
        ('textbox "Change Coordinator"', coordinator),
        ('textbox "Change Owner"', owner),
        ('textbox "Change Owner Group"', group),
        ('textbox "Assignment Group"', group),
        ('textbox "Assignee"', coordinator),
    ]
    for field_pattern, value in main_fields:
        ref = find_ref(form_snapshot, field_pattern)
        if not ref:
            log(f"  WARNING: '{field_pattern}' not found, skipping")
            continue
        fill_field(ref, value)
        log(f"  Filled: {field_pattern.split(chr(34))[1]} = {value}")

    # Risk Assessment (combobox)
    risk_ref = find_ref(form_snapshot, 'combobox "Risk Assessment"')
    if risk_ref:
        fill_field(risk_ref, risk)
        log(f"  Filled: Risk Assessment = {risk}")

    form_snapshot = take_snapshot()
    form_snapshot = dismiss_popup(form_snapshot)

    # Click "Change Details" tab
    tab_ref = find_ref(form_snapshot, 'tab "Change Details"')
    if not tab_ref:
        # Try alternative label
        tab_ref = find_ref(form_snapshot, '"Change Details"')
    if tab_ref:
        run_cli("click", tab_ref)
        time.sleep(2)
        form_snapshot = take_snapshot()
        log("  Switched to Change Details tab")
    else:
        log("  WARNING: 'Change Details' tab not found, continuing without switching")

    # Date fields
    date_fields = [
        ('textbox "Scheduled Implementation Start"', start),
        ('textbox "Scheduled Implementation End"', end),
    ]
    if downtime_start:
        date_fields.append(('textbox "Scheduled Downtime Start"', downtime_start))
    if downtime_end:
        date_fields.append(('textbox "Scheduled Downtime End"', downtime_end))

    for field_pattern, value in date_fields:
        ref = find_ref(form_snapshot, field_pattern)
        if not ref:
            log(f"  WARNING: '{field_pattern}' not found, skipping")
            continue
        fill_field(ref, value)
        log(f"  Filled: {field_pattern.split(chr(34))[1]} = {value}")
        form_snapshot = take_snapshot()
        form_snapshot = dismiss_popup(form_snapshot)

    # Implementation Plan (click-to-activate)
    log("  Filling Implementation Plan...")
    form_snapshot = fill_click_to_activate_plan(form_snapshot, "Implementation Plan", implementation_plan)

    # Remediation Plan (click-to-activate or already active)
    log("  Filling Remediation Plan...")
    form_snapshot = fill_click_to_activate_plan(form_snapshot, "Remediation Plan", remediation_plan)

    return take_snapshot()


def fill_click_to_activate_plan(snapshot: str, label: str, value: str) -> str:
    """Fill a click-to-activate plan field."""
    # First check if already a textbox
    tb_ref = find_ref(snapshot, f'textbox "{label}"')
    if not tb_ref:
        # Find paragraph to click
        para_ref = None
        lines = snapshot.splitlines()
        for i, line in enumerate(lines):
            if label in line:
                for j in range(i + 1, min(i + 8, len(lines))):
                    m = re.search(r'paragraph \[ref=([a-z0-9]+)\]', lines[j])
                    if m:
                        para_ref = m.group(1)
                        break
                if para_ref:
                    break

        if not para_ref:
            log(f"  WARNING: Could not find paragraph for '{label}', trying run-code fallback")
            _fill_plan_via_dom(label, value)
            return take_snapshot()

        run_cli("click", para_ref)
        time.sleep(2)
        snapshot = take_snapshot()
        tb_ref = find_ref(snapshot, f'textbox "{label}"')

    if tb_ref:
        run_cli("fill", tb_ref, value)
        run_cli("press", "Tab")
        time.sleep(1)
    else:
        log(f"  WARNING: Textbox for '{label}' not activated, trying DOM fallback")
        _fill_plan_via_dom(label, value)

    return take_snapshot()


def _fill_plan_via_dom(label: str, value: str) -> None:
    """Fallback: fill plan textarea via DOM manipulation."""
    # Map label to known textarea name attributes
    name_map = {
        "Implementation Plan": "instance/description.structure/plan/plan",
        "Remediation Plan": "instance/backout.plan/backout.plan",
    }
    ta_name = name_map.get(label)
    if not ta_name:
        log(f"  WARNING: No DOM name mapping for '{label}'")
        return

    escaped_value = value.replace("'", "\\'").replace("\n", "\\n")
    escaped_name = ta_name.replace("/", "\\/")
    run_cli("run-code", f"""async page => {{
  for (const frame of page.frames()) {{
    const result = await frame.evaluate((args) => {{
      const ta = document.querySelector('textarea[name="' + args.name + '"]');
      if (!ta) return null;
      ta.value = args.value;
      ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
      ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
      const parent = ta.closest('td') || ta.parentElement;
      if (parent) {{
        const editable = parent.querySelector('[contenteditable="true"]');
        if (editable) editable.innerHTML = args.value.replace(/\\n/g, '<br>');
      }}
      return 'filled';
    }}, {{ name: '{ta_name}', value: '{escaped_value}' }});
    if (result) return result;
  }}
  return 'not found';
}}""")


def save_plan(snapshot: str) -> None:
    """Click Save button."""
    save_ref = find_ref(snapshot, 'button "Save Record (Ctrl+Shift+F4)"')
    if not save_ref:
        save_ref = find_ref(snapshot, ': Save')
    if not save_ref:
        raise RuntimeError("Save button not found")

    run_cli("click", save_ref)
    log("  Clicked Save, waiting...")
    time.sleep(5)

    snapshot = take_snapshot()
    snapshot = dismiss_popup(snapshot)
    log("  Plan saved successfully")


def main():
    parser = argparse.ArgumentParser(description="Plan & Schedule an HPSM change request")
    parser.add_argument("--change-id", required=True, help="Change ID (e.g. C22382)")
    parser.add_argument("--start", required=True, help="Scheduled start (DD/MM/YY HH:MM:SS)")
    parser.add_argument("--end", required=True, help="Scheduled end (DD/MM/YY HH:MM:SS)")
    parser.add_argument("--coordinator", help="Change coordinator username (default: HPSM_USERNAME)")
    parser.add_argument("--owner", help="Change owner username (default: HPSM_USERNAME)")
    parser.add_argument("--group", default=DEFAULT_GROUP, help=f"Owner/assignment group (default: {DEFAULT_GROUP})")
    parser.add_argument("--risk", default=DEFAULT_RISK, help=f"Risk assessment (default: {DEFAULT_RISK})")
    parser.add_argument("--downtime-start", help="Downtime start (optional, DD/MM/YY HH:MM:SS)")
    parser.add_argument("--downtime-end", help="Downtime end (optional, DD/MM/YY HH:MM:SS)")
    parser.add_argument("--implementation-plan", required=True, help="Implementation plan text")
    parser.add_argument("--remediation-plan", required=True, help="Remediation/rollback plan text")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--dry-run", action="store_true", help="Fill form but do NOT save")
    args = parser.parse_args()

    username = os.environ.get("HPSM_USERNAME")
    password = os.environ.get("HPSM_PASSWORD")
    if not username or not password:
        print("ERROR: HPSM_USERNAME and HPSM_PASSWORD must be set", file=sys.stderr)
        print("Hint: run 'source .env' before this script", file=sys.stderr)
        sys.exit(1)

    coordinator = args.coordinator or username
    owner = args.owner or username

    log(f"=== HPSM Plan & Schedule ===")
    log(f"Change ID: {args.change_id}")
    log(f"Start: {args.start} → End: {args.end}")
    log("")

    try:
        log("[1/6] Opening browser...")
        open_args = ["open"]
        if args.headed:
            open_args.append("--headed")
        open_args.append(HPSM_URL)
        run_cli(*open_args)
        time.sleep(3)

        log("[2/6] Logging in...")
        sidebar_snapshot = login(username, password)

        log(f"[3/6] Navigating to change {args.change_id}...")
        change_snapshot = navigate_to_change(sidebar_snapshot, args.change_id)

        log("[4/6] Advancing to Plan and Schedule phase...")
        plan_snapshot = click_plan_and_schedule(change_snapshot)

        log("[5/6] Filling plan form...")
        fill_plan_form(
            form_snapshot=plan_snapshot,
            coordinator=coordinator,
            owner=owner,
            group=args.group,
            risk=args.risk,
            start=args.start,
            end=args.end,
            downtime_start=args.downtime_start,
            downtime_end=args.downtime_end,
            implementation_plan=args.implementation_plan,
            remediation_plan=args.remediation_plan,
        )

        if args.dry_run:
            log("[6/6] Dry run — skipping save")
        else:
            log("[6/6] Saving plan...")
            snapshot = take_snapshot()
            save_plan(snapshot)

    finally:
        log("[Done] Closing browser...")
        close_browser()


if __name__ == "__main__":
    main()
