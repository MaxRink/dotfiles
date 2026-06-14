#!/usr/bin/env python3
"""
Get NVIDIA ConnectX firmware compatibility information.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed", file=sys.stderr)
    print("Run: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


BASE_URL = "https://docs.nvidia.com/networking/"
ADAPTER_MAPPING = {
    "connectx-6-lx": "connectx6lxfirmwarev",
}


def find_firmware_url(adapter: str, version: str) -> Optional[str]:
    """
    Find the URL for a specific firmware version.

    Args:
        adapter: Adapter model
        version: Firmware version (e.g., '26.43.3608')

    Returns:
        URL to the firmware release notes or None if not found
    """
    if adapter not in ADAPTER_MAPPING:
        raise ValueError(f"Unsupported adapter: {adapter}")

    # Format version for URL (remove dots, lowercase)
    version_formatted = version.replace('.', '')

    # Try different URL patterns
    patterns = [
        f"display/{ADAPTER_MAPPING[adapter]}{version_formatted}lts/firmware+compatible+products",
        f"display/{ADAPTER_MAPPING[adapter]}{version_formatted}/firmware+compatible+products",
    ]

    for pattern in patterns:
        url = urljoin(BASE_URL, pattern)
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return url
        except requests.RequestException:
            continue

    return None


def parse_compatibility_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Parse the compatibility table from firmware release notes.

    Returns:
        Dict mapping software name to compatible versions
    """
    compatibility = {}

    # Find the "Driver Software, Tools and Switch Firmware" section
    section = soup.find('h2', string=re.compile(r'Driver Software.*Firmware', re.IGNORECASE))
    if not section:
        return compatibility

    # Find the table after this section
    table = section.find_next('table')
    if not table:
        return compatibility

    # Parse table rows
    rows = table.find_all('tr')
    for row in rows[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) >= 2:
            software_name = cols[0].get_text(strip=True)
            versions = cols[1].get_text(strip=True)

            # Clean up version text (remove notes and extra whitespace)
            versions = re.split(r'Note:', versions, flags=re.IGNORECASE)[0].strip()
            versions = re.sub(r'\s+', ' ', versions)  # Normalize whitespace

            compatibility[software_name] = versions

    return compatibility


def parse_supported_devices(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Parse the supported devices table.

    Returns:
        List of dicts with device information
    """
    devices = []

    # Find the "Supported Devices" section
    section = soup.find('h2', string=re.compile(r'Supported Devices', re.IGNORECASE))
    if not section:
        return devices

    # Find the table
    table = section.find_next('table')
    if not table:
        return devices

    # Parse table rows
    rows = table.find_all('tr')
    for row in rows[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) >= 4:
            devices.append({
                'part_number': cols[0].get_text(strip=True),
                'model': cols[1].get_text(strip=True),
                'device_id': cols[2].get_text(strip=True),
                'description': cols[3].get_text(strip=True),
            })

    return devices


def fetch_firmware_compatibility(
    adapter: str,
    version: str,
    include_devices: bool = False
) -> Dict:
    """
    Fetch firmware compatibility information.

    Args:
        adapter: Adapter model
        version: Firmware version
        include_devices: Whether to include supported devices list

    Returns:
        Dict with compatibility information
    """
    url = find_firmware_url(adapter, version)
    if not url:
        print(f"Error: Could not find firmware version {version} for {adapter}", file=sys.stderr)
        sys.exit(1)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    result = {
        'adapter': adapter,
        'version': version,
        'url': url,
        'compatibility': parse_compatibility_table(soup),
    }

    if include_devices:
        result['supported_devices'] = parse_supported_devices(soup)

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Get NVIDIA ConnectX firmware compatibility information'
    )
    parser.add_argument(
        '--version',
        required=True,
        help='Firmware version (e.g., 26.43.3608)'
    )
    parser.add_argument(
        '--adapter',
        default='connectx-6-lx',
        choices=list(ADAPTER_MAPPING.keys()),
        help='Adapter model (default: connectx-6-lx)'
    )
    parser.add_argument(
        '--include-devices',
        action='store_true',
        help='Include supported devices list'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    result = fetch_firmware_compatibility(
        args.adapter,
        args.version,
        args.include_devices
    )

    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        adapter_display = args.adapter.upper().replace('-', ' ')
        print(f"\nAdapter Model: {adapter_display}")
        print(f"Firmware Version: {result['version']}")
        print("=" * 60)
        print(f"Adapter: {args.adapter}")
        print(f"Documentation: {result['url']}\n")

        if result['compatibility']:
            print("Compatible Software:")
            print("-" * 60)
            for software, versions in result['compatibility'].items():
                print(f"  {software}:")
                print(f"    {versions}\n")
        else:
            print("No compatibility information found.\n")

        if args.include_devices and result.get('supported_devices'):
            print("\nSupported Devices:")
            print("-" * 60)
            for device in result['supported_devices'][:5]:  # Show first 5
                print(f"  {device['model']} ({device['part_number']})")
                print(f"    {device['description']}\n")

            if len(result['supported_devices']) > 5:
                print(f"  ... and {len(result['supported_devices']) - 5} more devices\n")


if __name__ == '__main__':
    main()
