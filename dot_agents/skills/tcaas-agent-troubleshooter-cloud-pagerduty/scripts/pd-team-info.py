#!/usr/bin/env python3
"""
PagerDuty Team Info Script
Usage: pd-team-info.py [TEAM_NAME] [--json]
"""

import argparse
import sys
from typing import List, Dict, Any

from pd_common import (
    PagerDutyClient, PagerDutyError, error_exit, output_json
)


def format_teams(teams: List[Dict[str, Any]], search_name: str) -> None:
    """Format and print team information."""
    if not teams:
        print(f'No teams found matching "{search_name}"')
        return

    print(f'Teams matching "{search_name}":')
    print()

    for team in teams:
        team_id = team.get('id', 'N/A')
        name = team.get('name', 'Unknown')
        description = team.get('description', '-') or '-'
        html_url = team.get('html_url', '')

        print(f'ID:          {team_id}')
        print(f'Name:        {name}')
        print(f'Description: {description}')
        print(f'URL:         {html_url}')
        print()
        print(f'# To use this team ID in scripts, set:')
        print(f'# TCAAS_TEAM_ID="{team_id}"')
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Search for PagerDuty teams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                 # Search for T-CaaS team (default)
  %(prog)s "Platform"      # Search for teams with "Platform" in name
  %(prog)s --json          # JSON output
        """
    )

    parser.add_argument('team_name', nargs='?', default='T-CaaS',
                        help='Team name to search for (default: T-CaaS)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        client = PagerDutyClient()
    except PagerDutyError as e:
        error_exit(str(e))

    try:
        teams = client.search_teams(args.team_name)
    except PagerDutyError as e:
        error_exit(str(e))

    # Output
    if args.json:
        output_json(teams)
    else:
        format_teams(teams, args.team_name)


if __name__ == '__main__':
    main()
