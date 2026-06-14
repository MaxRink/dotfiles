#!/usr/bin/env python3
"""
Resolve (close) a PagerDuty incident.
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


def resolve_incident(
    client: PagerDutyClient,
    incident_id: str,
    note: Optional[str] = None,
    from_email: str = "caas-automation@telekom.de"
) -> dict:
    """Resolve an incident, optionally adding a note first."""

    # Add note if provided
    if note:
        note_url = f"{client.base_url}/incidents/{incident_id}/notes"
        headers = client.headers.copy()
        headers["From"] = from_email
        headers["Accept"] = "application/vnd.pagerduty+json;version=2"

        note_data = {"note": {"content": note}}

        try:
            response = requests.post(note_url, headers=headers, json=note_data, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Warning: Failed to add note: {e}", file=sys.stderr)

    # Resolve the incident
    url = f"{client.base_url}/incidents/{incident_id}"

    headers = client.headers.copy()
    headers["From"] = from_email
    headers["Accept"] = "application/vnd.pagerduty+json;version=2"

    data = {
        "incident": {
            "type": "incident_reference",
            "status": "resolved"
        }
    }

    try:
        response = requests.put(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        try:
            error_data = e.response.json()
            message = error_data.get('error', {}).get('message', str(e))
        except (json.JSONDecodeError, AttributeError):
            message = str(e)
        raise PagerDutyError(f"Failed to resolve incident ({status_code}): {message}")
    except requests.exceptions.RequestException as e:
        raise PagerDutyError(f"Request failed: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Resolve (close) a PagerDuty incident",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve incident
  pd-incident-resolve.py 107041

  # Resolve with a note explaining why
  pd-incident-resolve.py Q1UFIV4RJQRWCS --note "Alert silenced for 2 years"

  # Resolve with JSON output
  pd-incident-resolve.py 107041 --note "Fixed" --json

  # Specify custom from email
  pd-incident-resolve.py 107041 --from "user@example.com"
        """
    )

    parser.add_argument(
        "incident_id",
        help="Incident ID or number (e.g., 107041 or Q1UFIV4RJQRWCS)"
    )
    parser.add_argument(
        "--note", "-n",
        help="Optional note to add before resolving"
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

        result = resolve_incident(client, args.incident_id, args.note, args.from_email)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            incident_data = result.get("incident", {})
            print(f"Incident #{incident_data.get('incident_number')} resolved successfully!")
            print(f"  ID: {incident_data.get('id')}")
            print(f"  Status: {incident_data.get('status')}")
            print(f"  Resolved at: {incident_data.get('resolved_at')}")
            print(f"  Title: {incident_data.get('title')}")

    except PagerDutyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
