#!/usr/bin/env python3
"""
Search for firmware versions compatible with specific software versions.
"""

import argparse
import importlib.util
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

# Import functions from other scripts
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import using importlib to handle filename with hyphens
    import importlib.util

    # Load nvidia-list-firmware.py
    list_spec = importlib.util.spec_from_file_location(
        "nvidia_list_firmware",
        os.path.join(os.path.dirname(__file__), "nvidia-list-firmware.py")
    )
    list_module = importlib.util.module_from_spec(list_spec)
    list_spec.loader.exec_module(list_module)
    fetch_firmware_versions = list_module.fetch_firmware_versions

    # Load nvidia-firmware-compat.py
    compat_spec = importlib.util.spec_from_file_location(
        "nvidia_firmware_compat",
        os.path.join(os.path.dirname(__file__), "nvidia-firmware-compat.py")
    )
    compat_module = importlib.util.module_from_spec(compat_spec)
    compat_spec.loader.exec_module(compat_module)
    fetch_firmware_compatibility = compat_module.fetch_firmware_compatibility
except ImportError as e:
    # If imports fail, we need the functions inline
    print(f"Warning: Could not import helper functions: {e}", file=sys.stderr)
    sys.exit(1)


SOFTWARE_MAPPING = {
    'doca': ['DOCA-HOST', 'DOCA-HOST (MLNX_OFED based code)'],
    'mlnx_ofed': ['MLNX_OFED', 'MLNX_OFED (DOCA-HOST based code)'],
    'mlnx_en': ['MLNX_EN', 'MLNX_EN (MLNX_OFED based code)'],
    'winof2': ['WinOF-2', 'WinOF2'],
    'mft': ['MFT', 'Mellanox Firmware Tools'],
    'mstflint': ['mstflint'],
    'flexboot': ['FlexBoot'],
    'uefi': ['UEFI'],
}


def version_matches(compatible_versions: str, target_version: str) -> bool:
    """
    Check if target version is in the compatible versions string.

    Args:
        compatible_versions: String like "2.9.3 / 2.9.2" or "24.10-3.2.5.0 / 24.10-1.1.4.0"
        target_version: Version to search for

    Returns:
        True if target version is found
    """
    # Split by / and clean each version
    versions = [v.strip() for v in compatible_versions.split('/')]
    return target_version in versions


def search_compatible_firmware(
    adapter: str,
    software_type: str,
    software_version: str
) -> List[Dict]:
    """
    Search for firmware versions compatible with given software version.

    Args:
        adapter: Adapter model
        software_type: Type of software (doca, mlnx_ofed, etc.)
        software_version: Software version to search for

    Returns:
        List of dicts with firmware information and compatibility
    """
    if software_type not in SOFTWARE_MAPPING:
        raise ValueError(f"Unknown software type: {software_type}")

    # Get all firmware versions
    print(f"Fetching firmware versions for {adapter}...", file=sys.stderr)
    all_versions = fetch_firmware_versions(adapter, lts_only=False)

    compatible_firmware = []

    # Check each firmware version
    for fw in all_versions:
        print(f"Checking firmware {fw['version']}...", file=sys.stderr)

        try:
            compat_info = fetch_firmware_compatibility(adapter, fw['version'], include_devices=False)

            # Check if the software version is compatible
            for software_name in SOFTWARE_MAPPING[software_type]:
                if software_name in compat_info['compatibility']:
                    compatible_versions = compat_info['compatibility'][software_name]

                    if version_matches(compatible_versions, software_version):
                        compatible_firmware.append({
                            'firmware_version': fw['version'],
                            'firmware_type': fw['type'],
                            'firmware_title': fw['title'],
                            'software_name': software_name,
                            'compatible_versions': compatible_versions,
                            'url': fw['url']
                        })
                        break  # Found match for this firmware
        except Exception as e:
            print(f"Error checking firmware {fw['version']}: {e}", file=sys.stderr)
            continue

    return compatible_firmware


def main():
    parser = argparse.ArgumentParser(
        description='Search for firmware versions compatible with specific software'
    )
    parser.add_argument(
        '--software',
        required=True,
        choices=list(SOFTWARE_MAPPING.keys()),
        help='Software type'
    )
    parser.add_argument(
        '--version',
        required=True,
        help='Software version to search for (e.g., 2.9.3 or 24.10-3.2.5.0)'
    )
    parser.add_argument(
        '--adapter',
        default='connectx-6-lx',
        help='Adapter model (default: connectx-6-lx)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    try:
        results = search_compatible_firmware(
            args.adapter,
            args.software,
            args.version
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print(f"\nNo firmware versions found compatible with {args.software.upper()} {args.version}", file=sys.stderr)
        sys.exit(0)

    if args.format == 'json':
        result = {
            'adapter': args.adapter,
            'adapter_display': args.adapter.upper().replace('-', ' '),
            'software': args.software,
            'software_version': args.version,
            'compatible_firmware': results
        }
        print(json.dumps(result, indent=2))
    else:
        adapter_display = args.adapter.upper().replace('-', ' ')
        software_display = args.software.upper().replace('_', ' ')
        print(f"\nAdapter Model: {adapter_display}")
        print(f"Firmware versions compatible with {software_display} {args.version}")
        print("=" * 60)
        print(f"Adapter: {args.adapter}\n")

        for result in results:
            print(f"\n  Firmware: {result['firmware_version']} ({result['firmware_type']})")
            print(f"  Title: {result['firmware_title']}")
            print(f"  {result['software_name']}: {result['compatible_versions']}")
            print(f"  URL: {result['url']}")

        print(f"\nTotal: {len(results)} compatible firmware version(s)\n")


if __name__ == '__main__':
    main()
