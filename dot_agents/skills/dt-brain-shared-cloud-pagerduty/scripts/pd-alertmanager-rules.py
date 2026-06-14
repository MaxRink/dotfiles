#!/usr/bin/env python3
"""
CaaS AlertManager Rules Script
Shows alertmanager routing rules, inhibit rules, and receivers.
Usage: pd-alertmanager-rules.py [--inhibit] [--routes] [--receivers] [--all]
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


def find_alertmanager_file(base_dir: str) -> Optional[Path]:
    """Find the latest caas-alertmanager YAML file."""
    alertmanager_dir = Path(base_dir) / "functions" / "caas-alertmanager"

    if not alertmanager_dir.exists():
        return None

    yaml_files = list(alertmanager_dir.glob("caas-alertmanager-*.yaml"))
    if not yaml_files:
        return None

    # Sort by version and get latest
    return sorted(yaml_files, key=lambda p: p.name)[-1]


def extract_version(filepath: Path) -> str:
    """Extract version from filename."""
    match = re.search(r'caas-alertmanager-(.*)\.yaml', filepath.name)
    return match.group(1) if match else "unknown"


def show_inhibit_rules(config_text: str) -> None:
    """Display inhibit rules."""
    print("INHIBIT RULES")
    print("=" * 60)
    print("(When source alert fires, target alerts are suppressed)")
    print("")

    # Extract inhibit rules section
    inhibit_match = re.search(
        r'inhibit_rules:\s*\n(.*?)(?=\n          templates:|\n          receivers:)',
        config_text, re.DOTALL
    )

    if not inhibit_match:
        print("  No inhibit rules found")
        print("")
        return

    rules_text = inhibit_match.group(1)
    rules = re.split(r'\n            - ', rules_text)

    rule_num = 0
    for rule in rules:
        if not rule.strip():
            continue

        rule_num += 1

        # Try new format (source_matchers)
        if 'source_matchers' in rule:
            source = re.search(r'source_matchers:\s*\[\s*"([^"]+)"', rule)
            target = re.search(r'target_matchers:\s*\[\s*"([^"]+)"', rule)
            equal = re.findall(r'equal:\s*\n\s*-\s*(\w+)', rule)

            if source and target:
                print(f"  Rule {rule_num}:")
                print(f"    Source: {source.group(1)}")
                print(f"    Target: {target.group(1)}")
                if equal:
                    print(f"    Equal:  {', '.join(equal)}")
                print("")

        # Try old format (source_match)
        elif 'source_match' in rule:
            source = re.search(r"source_match:\s*\n\s*(\w+):\s*'([^']+)'", rule)
            target = re.search(r"target_match:\s*\n\s*(\w+):\s*'([^']+)'", rule)
            equal = re.search(r"equal:\s*\[([^\]]+)\]", rule)

            if source and target:
                print(f"  Rule {rule_num}:")
                print(f"    Source: {source.group(1)}={source.group(2)}")
                print(f"    Target: {target.group(1)}={target.group(2)}")
                if equal:
                    print(f"    Equal:  {equal.group(1)}")
                print("")

    if rule_num == 0:
        print("  No inhibit rules parsed")
    print("")


def show_receivers() -> None:
    """Display receiver information."""
    print("RECEIVERS")
    print("=" * 60)
    print("")
    print("  - OpenNMS2:           Development/internal clusters -> OpenNMS (disabled)")
    print("  - OpenNMS2_PROD:      Production clusters -> OpenNMS")
    print("  - PagerDuty_EU_T_CaaS: T-CaaS team PagerDuty (EU region)")
    print("  - null:               Alert sink (ignored)")
    print("")


def show_routes() -> None:
    """Display routing rules information."""
    print("ROUTING RULES")
    print("=" * 60)
    print("")
    print("Default grouping: alertname, cluster, tenant")
    print("Group wait: 30s | Group interval: 5m | Repeat: 12h")
    print("")
    print("Routes (in order of evaluation):")
    print("")
    print("  1. OpenNMS2_PROD (continue=true, repeat=4h)")
    print("     Alerts: goldpinger_nodes_unhealthy, KubeMasterNodeNotReady30m,")
    print("             KubeWorkerNodeNotReady30m, KubeMultipleMasterNodesNotReady5m,")
    print("             BlackboxCephConnectionLost, All_Masters_Workers_down_az*,")
    print("             HostNetworkBondDegraded, KubeApiCert*Error,")
    print("             Kubelet*CertificateExpiration, KubeClientCertificateExpirationCritical,")
    print("             KubeMasterNodeNotReady5m, KubeWorkerNodeNotReady5m,")
    print("             NodeFilesystemAlmostOutOfSpace20")
    print("     Severity: error|critical")
    print("     Environment: NOT development or t-caas-dev")
    print("")
    print("  2. OpenNMS2_PROD HeartBeat (continue=false, repeat=5m)")
    print("     Alerts: HeartBeat_Prometheus")
    print("     Environment: NOT development or t-caas-dev")
    print("")
    print("  3. PagerDuty_EU_T_CaaS")
    print("     Severity: error|critical")
    print("     Environment: NOT development or t-caas-dev")
    print("")
    print("  4. null (sink)")
    print("     Alerts: Watchdog")
    print("")
    print("Note: Development/t-caas-dev environments are excluded from paging")
    print("")


def main():
    parser = argparse.ArgumentParser(
        description='Show CaaS AlertManager configuration from caas-bundles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Show all configuration
  %(prog)s --inhibit    # Show only inhibit rules
  %(prog)s --routes     # Show only routing rules
  %(prog)s --receivers  # Show only receivers
        """
    )

    parser.add_argument('--inhibit', action='store_true',
                        help='Show inhibit rules (which alerts suppress others)')
    parser.add_argument('--routes', action='store_true',
                        help='Show routing rules (how alerts are routed)')
    parser.add_argument('--receivers', action='store_true',
                        help='Show receivers (where alerts are sent)')
    parser.add_argument('--all', action='store_true',
                        help='Show all configuration (default)')

    args = parser.parse_args()

    # Default to show all if no specific option
    show_all = not (args.inhibit or args.routes or args.receivers) or args.all

    # Find caas-bundles directory
    base_dir = os.environ.get('CAAS_BUNDLES_DIR',
                              os.path.expanduser('~/git/caas/caas-bundles'))

    alertmanager_file = find_alertmanager_file(base_dir)

    if not alertmanager_file:
        print(f"Error: CaaS bundles directory not found at {base_dir}", file=sys.stderr)
        print("Set CAAS_BUNDLES_DIR environment variable to the correct path", file=sys.stderr)
        sys.exit(1)

    version = extract_version(alertmanager_file)

    print("CaaS AlertManager Configuration")
    print("================================")
    print(f"Version: {version}")
    print(f"Source:  {alertmanager_file}")
    print("")

    # Read file content
    try:
        content = alertmanager_file.read_text()
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract config section
    match = re.search(
        r'name: alertmanager\s+.*?valuesData: \|-\s*\n(.*?)(?=\n    - name:|\n  source:|\Z)',
        content, re.DOTALL
    )

    if not match:
        print("Could not find alertmanager valuesData section", file=sys.stderr)
        sys.exit(1)

    values_content = match.group(1)

    # Remove template markers for display
    values_content = re.sub(r'\{\{.*?\}\}', '<template>', values_content)
    values_content = re.sub(r'\{\{-.*?-\}\}', '', values_content)
    values_content = re.sub(r'\{\{\`.*?\`\}\}', '<template>', values_content)

    # Find config section
    config_match = re.search(
        r'^        config:\s*\n(.*?)(?=\n        [a-zA-Z]|\n    - name:|\Z)',
        values_content, re.MULTILINE | re.DOTALL
    )

    if not config_match:
        print("Could not find config section", file=sys.stderr)
        sys.exit(1)

    config_text = config_match.group(1)

    # Display requested sections
    if show_all or args.inhibit:
        show_inhibit_rules(config_text)

    if show_all or args.receivers:
        show_receivers()

    if show_all or args.routes:
        show_routes()


if __name__ == '__main__':
    main()
