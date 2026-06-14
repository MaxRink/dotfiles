#!/usr/bin/env python3
"""
AlertManager Delete Silence Script
Usage: am-silence-delete.py <silence-id>
"""

import argparse
import sys

from am_common import (
    AlertManagerClient, AlertManagerError, error_exit
)


def main():
    parser = argparse.ArgumentParser(
        description='Delete (expire) an AlertManager silence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s abc123def456    # Delete silence by ID

Note: This expires the silence immediately. The silence ID can be
found using am-silence-list.py
        """
    )

    parser.add_argument('silence_id',
                        help='Silence ID to delete')

    args = parser.parse_args()

    try:
        client = AlertManagerClient()
    except AlertManagerError as e:
        error_exit(str(e))

    try:
        client.delete_silence(args.silence_id)
        print(f"Silence {args.silence_id} deleted successfully.")
    except AlertManagerError as e:
        error_exit(str(e))


if __name__ == '__main__':
    main()
