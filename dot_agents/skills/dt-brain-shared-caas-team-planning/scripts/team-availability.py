#!/usr/bin/env python3
"""
CaaS Team Availability Checker

Combines Google Sheets vacation planner with PagerDuty on-call data
to show team availability for a given date or date range.

Usage:
    team-availability.py --date 2026-04-09
    team-availability.py --today
    team-availability.py --from 2026-04-07 --to 2026-04-11
"""

import argparse
import csv
import io
import json
import sys
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

SPREADSHEET_ID = "163-0QlHpRuQmixYJ8uZOjdpNaFEyvNHhck-SkAGOTZc"
GVIZ_URL = (
    "https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={sheet}&headers=0"
)

LEGEND = {
    "V": "Vacation",
    "v": "Vacation",
    "V (0,5)": "Half Day Off",
    "BT": "Business Trip",
}

BANK_HOLIDAY_ROWS = {
    "SK Bank Holiday",
    "HR Bank Holiday",
    "ES Bank Holiday",
    "GR Bank Holiday",
    "PL Bank Holiday",
    "CZ Bank Holiday",
}

SKIP_ROWS = {"CaaS", "Onduty", ""} | BANK_HOLIDAY_ROWS


def fetch_sheet(year: int) -> List[List[str]]:
    """Download the planning sheet for a given year as CSV."""
    url = GVIZ_URL.format(sid=SPREADSHEET_ID, sheet=str(year))
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"Error: Cannot fetch planning sheet for {year}: {e}", file=sys.stderr)
        sys.exit(1)

    reader = csv.reader(io.StringIO(data))
    return list(reader)


def find_column(rows: List[List[str]], target_date: date) -> Optional[int]:
    """Find the column index for a specific date (DD/MM format).
    With headers=0, row 0=months, row 1=days, row 2=dates."""
    if len(rows) < 3:
        return None
    dates_row = rows[2]
    target_str = target_date.strftime("%d/%m")

    for i, d in enumerate(dates_row):
        if d == target_str:
            return i
    return None


def parse_sheet_for_date(
    rows: List[List[str]], col: int
) -> Dict[str, Any]:
    """Extract team status for a specific column (date).
    With headers=0, data rows start at index 3."""
    result: Dict[str, Any] = {
        "on_holiday": [],
        "available": [],
        "bank_holidays": [],
    }

    for row in rows[3:]:
        name = row[0].strip() if row and row[0] else ""
        if not name:
            continue
        # Stop at legend rows
        if name.startswith("V =") or name.startswith("V (0,5)") or name.startswith("BT ="):
            break

        val = row[col].strip() if col < len(row) else ""

        if name in BANK_HOLIDAY_ROWS:
            if val:
                result["bank_holidays"].append(name)
            continue

        if name == "CaaS" or name == "Onduty" or not name:
            continue

        if val:
            label = LEGEND.get(val, val)
            result["on_holiday"].append({"name": name, "status": label})
        else:
            result["available"].append(name)

    return result


def fetch_oncall(target_date: date) -> Optional[List[Dict[str, Any]]]:
    """Fetch PagerDuty on-call schedule for the given date."""
    import os

    token = os.environ.get("PAGERDUTY_TOKEN") or os.environ.get("PAGERDUTY_API_KEY")
    if not token:
        return None

    since = f"{target_date.isoformat()}T00:00:00Z"
    until_date = target_date + timedelta(days=1)
    until = f"{until_date.isoformat()}T00:00:00Z"

    # PagerDuty team ID for T-CaaS
    team_id = "P5TDGFM"
    api_url = (
        f"https://api.pagerduty.com/oncalls"
        f"?since={since}&until={until}&team_ids[]={team_id}"
    )

    headers = {
        "Authorization": f"Token token={token}",
        "Content-Type": "application/json",
    }

    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("oncalls", [])
    except Exception as e:
        print(f"Warning: Could not fetch PagerDuty on-call: {e}", file=sys.stderr)
        return None


def format_oncall(oncalls: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format PagerDuty on-call entries into readable dicts."""
    results = []
    # Group by schedule
    by_schedule: Dict[str, List[Dict[str, Any]]] = {}
    for oc in oncalls:
        sched = oc.get("schedule", {}).get("summary", "Direct")
        by_schedule.setdefault(sched, []).append(oc)

    for sched_name, entries in sorted(by_schedule.items()):
        # Merge consecutive entries by same user
        sorted_entries = sorted(entries, key=lambda x: x.get("start", ""))
        merged = []
        for oc in sorted_entries:
            user = oc.get("user", {}).get("summary", "Unknown")
            level = oc.get("escalation_level", "?")
            start = oc.get("start", "")
            end = oc.get("end", "")

            if merged and merged[-1]["user"] == user:
                merged[-1]["end"] = end
            else:
                merged.append(
                    {
                        "schedule": sched_name,
                        "user": user,
                        "level": str(level),
                        "start": _fmt_dt(start),
                        "end": _fmt_dt(end),
                    }
                )
        results.extend(merged)
    return results


def _fmt_dt(iso_str: str) -> str:
    """Format ISO datetime to readable HH:MM on YYYY-MM-DD."""
    if not iso_str:
        return "?"
    try:
        cleaned = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        local_dt = dt.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str[:16]


def print_report(
    target_date: date,
    sheet_data: Dict[str, Any],
    oncall_entries: Optional[List[Dict[str, str]]],
) -> None:
    """Print a formatted availability report."""
    day_name = target_date.strftime("%A")
    print(f"\n{'=' * 60}")
    print(f"CaaS Team Availability — {day_name}, {target_date.isoformat()}")
    print(f"{'=' * 60}")

    # Bank holidays
    if sheet_data["bank_holidays"]:
        print("\n🏛️  Bank Holidays:")
        for bh in sheet_data["bank_holidays"]:
            print(f"  • {bh}")

    # On holiday
    if sheet_data["on_holiday"]:
        print(f"\n🏖️  On Holiday / Away ({len(sheet_data['on_holiday'])}):")
        for entry in sheet_data["on_holiday"]:
            print(f"  • {entry['name']} — {entry['status']}")
    else:
        print("\n✅ No one is on holiday!")

    # On-call
    if oncall_entries:
        print("\n📞 On-Call (PagerDuty):")
        for oc in oncall_entries:
            print(f"  • {oc['schedule']}: {oc['user']} (L{oc['level']})")
            print(f"    {oc['start']} → {oc['end']}")
    elif oncall_entries is None:
        print("\n📞 On-Call: (skipped — no PagerDuty token)")

    # Available
    if sheet_data["available"]:
        print(f"\n👨‍💻 Available ({len(sheet_data['available'])}):")
        for name in sheet_data["available"]:
            print(f"  • {name}")

    print()


def output_json_report(
    target_date: date,
    sheet_data: Dict[str, Any],
    oncall_entries: Optional[List[Dict[str, str]]],
) -> Dict[str, Any]:
    """Build a JSON-serialisable report."""
    return {
        "date": target_date.isoformat(),
        "day": target_date.strftime("%A"),
        "bank_holidays": sheet_data["bank_holidays"],
        "on_holiday": sheet_data["on_holiday"],
        "on_call": oncall_entries,
        "available": sheet_data["available"],
    }


def process_date(
    target_date: date,
    rows: List[List[str]],
    no_oncall: bool,
    as_json: bool,
) -> Optional[Dict[str, Any]]:
    """Process a single date and either print or return JSON."""
    col = find_column(rows, target_date)
    if col is None:
        print(
            f"Warning: Date {target_date.isoformat()} not found in the {target_date.year} sheet.",
            file=sys.stderr,
        )
        return None

    sheet_data = parse_sheet_for_date(rows, col)

    oncall_entries = None
    if not no_oncall:
        raw_oncall = fetch_oncall(target_date)
        if raw_oncall is not None:
            oncall_entries = format_oncall(raw_oncall)

    if as_json:
        return output_json_report(target_date, sheet_data, oncall_entries)
    else:
        print_report(target_date, sheet_data, oncall_entries)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check CaaS team availability (vacations + on-call)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --date 2026-04-09          # Specific date
  %(prog)s --today                     # Today
  %(prog)s --from 2026-04-07 --to 2026-04-11  # Date range
  %(prog)s --date 2026-04-09 --no-oncall       # Skip PagerDuty
  %(prog)s --date 2026-04-09 --json            # JSON output
        """,
    )

    parser.add_argument("--date", help="Date to check (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Check today")
    parser.add_argument("--from", dest="from_date", help="Start of date range (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="End of date range (YYYY-MM-DD)")
    parser.add_argument(
        "--no-oncall", action="store_true", help="Skip PagerDuty on-call lookup"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Determine target dates
    dates: List[date] = []
    if args.today:
        dates = [date.today()]
    elif args.date:
        dates = [date.fromisoformat(args.date)]
    elif args.from_date and args.to_date:
        start = date.fromisoformat(args.from_date)
        end = date.fromisoformat(args.to_date)
        current = start
        while current <= end:
            dates.append(current)
            current += timedelta(days=1)
    else:
        parser.error("Provide --date, --today, or --from/--to range")

    # Group dates by year (in case range spans years)
    by_year: Dict[int, List[date]] = {}
    for d in dates:
        by_year.setdefault(d.year, []).append(d)

    # Fetch sheets and process
    json_results = []
    for year, year_dates in sorted(by_year.items()):
        rows = fetch_sheet(year)
        for d in year_dates:
            result = process_date(d, rows, args.no_oncall, args.json)
            if result is not None:
                json_results.append(result)

    if args.json:
        output = json_results if len(json_results) > 1 else json_results[0] if json_results else {}
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
