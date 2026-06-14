#!/usr/bin/env python3
"""
Add a note to a PagerDuty incident.
"""

import sys
import json
import argparse
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from pd_common import PagerDutyClient, PagerDutyError
except ImportError:
    print("Error: pd_common module not found", file=sys.stderr)
    sys.exit(1)


def add_note(client: PagerDutyClient, incident_id: str, note: str, from_email: str = "caas-automation@telekom.de") -> dict:
    """Add a note to an incident."""
    url = f"{client.base_url}/incidents/{incident_id}/notes"

    headers = client.headers.copy()
    headers["From"] = from_email
    headers["Accept"] = "application/vnd.pagerduty+json;version=2"

    data = {
        "note": {
            "content": note
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        try:
            error_data = e.response.json()
            message = error_data.get('error', {}).get('message', str(e))
        except (json.JSONDecodeError, AttributeError):
            message = str(e)
        raise PagerDutyError(f"Failed to add note ({status_code}): {message}")
    except requests.exceptions.RequestException as e:
        raise PagerDutyError(f"Request failed: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Add a note to a PagerDuty incident",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add note to incident
  pd-incident-note.py 107041 "Alert silenced in AlertManager"

  # Add note with JSON output
  pd-incident-note.py Q1UFIV4RJQRWCS "Investigating the issue" --json

  # Specify custom from email
  pd-incident-note.py 107041 "Fixed by team" --from "user@example.com"
        """
    )

    parser.add_argument(
        "incident_id",
        help="Incident ID or number (e.g., 107041 or Q1UFIV4RJQRWCS)"
    )
    parser.add_argument(
        "note",
        help="Note content to add"
    )
    parser.add_argument(
        "--from",
        dest="from_email",
        default="caas-automation@telekom.de",
        help="From email address (default: caas-automation@telekom.de)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    try:
        client = PagerDutyClient()

        result = add_note(client, args.incident_id, args.note, args.from_email)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            note_data = result.get("note", {})
            print(f"Note added successfully!")
            print(f"  ID: {note_data.get('id')}")
            print(f"  Content: {note_data.get('content')}")
            print(f"  Created: {note_data.get('created_at')}")
            print(f"  By: {note_data.get('user', {}).get('summary', 'Unknown')}")

    except PagerDutyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
