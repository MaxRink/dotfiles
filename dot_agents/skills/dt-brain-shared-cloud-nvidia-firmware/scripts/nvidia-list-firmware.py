#!/usr/bin/env python3
"""
List available NVIDIA ConnectX firmware versions.
"""

import argparse
import json
import re
import sys
from typing import List, Dict
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed", file=sys.stderr)
    print("Run: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


BASE_URL = "https://docs.nvidia.com/networking/software/adapter-firmware/"
ADAPTER_MAPPING = {
    "connectx-6-lx": "index.html#connectx-6-lx",
    "connectx-6": "index.html#connectx-6",
    "connectx-7": "index.html#connectx-7",
    "connectx-8": "index.html#connectx-8",
}


def fetch_firmware_versions(adapter: str, lts_only: bool = False) -> List[Dict[str, str]]:
    """
    Fetch firmware versions from NVIDIA documentation.

    Args:
        adapter: Adapter model (e.g., 'connectx-6-lx')
        lts_only: If True, only return LTS versions

    Returns:
        List of dicts with 'version', 'type' (LTS/GA), 'title', and 'url'
    """
    if adapter not in ADAPTER_MAPPING:
        raise ValueError(f"Unsupported adapter: {adapter}. Supported: {list(ADAPTER_MAPPING.keys())}")

    url = urljoin(BASE_URL, ADAPTER_MAPPING[adapter])

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    versions = []

    # Find the adapter section by ID (e.g., 'connectx-6-lx')
    adapter_section = soup.find(id=adapter)
    if not adapter_section:
        return versions

    # Find all links within this adapter section that contain version numbers
    links = adapter_section.find_all('a', href=True)

    for link in links:
        title = link.get_text(strip=True)
        href = link['href']

        # Extract version number from title
        version_match = re.search(r'v(\d+\.\d+\.\d+)', title, re.IGNORECASE)
        if version_match:
            version = version_match.group(1)

            # Determine if LTS or GA
            is_lts = bool(re.search(r'LTS', title, re.IGNORECASE))

            # Skip if LTS-only mode and this is not LTS
            if lts_only and not is_lts:
                continue

            release_type = 'LTS' if is_lts else 'GA'

            # Skip if already in list
            if not any(v['version'] == version for v in versions):
                versions.append({
                    'version': version,
                    'type': release_type,
                    'title': title,
                    'url': href if href.startswith('http') else urljoin(BASE_URL, href)
                })

    return versions


def main():
    parser = argparse.ArgumentParser(
        description='List available NVIDIA ConnectX firmware versions'
    )
    parser.add_argument(
        '--adapter',
        default='connectx-6-lx',
        choices=list(ADAPTER_MAPPING.keys()),
        help='Adapter model (default: connectx-6-lx)'
    )
    parser.add_argument(
        '--lts-only',
        action='store_true',
        help='Show only LTS releases'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    versions = fetch_firmware_versions(args.adapter, args.lts_only)

    if not versions:
        print(f"No firmware versions found for {args.adapter}", file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        result = {
            'adapter': args.adapter,
            'adapter_display': args.adapter.upper().replace('-', ' '),
            'versions': versions
        }
        print(json.dumps(result, indent=2))
    else:
        adapter_display = args.adapter.upper().replace('-', ' ')
        print(f"\nAdapter Model: {adapter_display}")
        print(f"Firmware Versions for {args.adapter}")
        print("=" * 60)

        # Group by type
        lts_versions = [v for v in versions if v['type'] == 'LTS']
        ga_versions = [v for v in versions if v['type'] == 'GA']

        if lts_versions:
            print("\nLTS Releases:")
            print("-" * 60)
            for v in lts_versions:
                print(f"  {v['version']:<15} {v['title']}")

        if ga_versions and not args.lts_only:
            print("\nGA Releases:")
            print("-" * 60)
            for v in ga_versions:
                print(f"  {v['version']:<15} {v['title']}")

        print(f"\nTotal: {len(versions)} version(s)\n")


if __name__ == '__main__':
    main()
