#!/usr/bin/env python3
"""
SSH to a TOR switch and run diagnostic commands.
Supports Cisco NX-OS and Juniper (JunOS/QFX/EX) switches.

Usage: switch-diag.py <switch_ip> --vendor cisco|juniper --ports port1,port2 [options]
"""

import subprocess
import sys
import os
import argparse

# Cisco NX-OS commands for port diagnostics
CISCO_COMMANDS = {
    "port_status": "show interface {port}",
    "port_brief": "show interface {port} status",
    "port_counters": "show interface {port} counters",
    "mac_table": "show mac address-table interface {port}",
    "vlan_port": "show interface {port} switchport",
    "cdp_neighbor": "show cdp neighbors interface {port}",
    "spanning_tree": "show spanning-tree interface {port}",
}

# Cisco NX-OS global/log commands (not per-port)
CISCO_GLOBAL_COMMANDS = {
    "log_recent": "show logging last 100",
    "log_interface": "show logging | include {port}",
    "alarms": "show environment | include -i alarm|fail|error",
    "uptime": "show system uptime",
}

# Juniper commands for port diagnostics
JUNIPER_COMMANDS = {
    "port_status": "show interfaces {port}",
    "port_extensive": "show interfaces {port} extensive",
    "mac_table": "show ethernet-switching table interface {port}",
    "vlan_port": "show vlans interface {port}",
    "lldp_neighbor": "show lldp neighbors interface {port}",
    "spanning_tree": "show spanning-tree interface {port}",
}

# Juniper global/log commands (not per-port)
JUNIPER_GLOBAL_COMMANDS = {
    "log_recent": "show log messages | last 100",
    "log_interface": "show log messages | match {port} | last 50",
    "alarms": "show system alarms",
    "chassis_alarms": "show chassis alarms",
    "uptime": "show system uptime",
}


def build_command_string(vendor: str, ports: list, commands: list = None,
                         include_logs: bool = False) -> str:
    """Build the full command string to send over SSH."""
    if vendor == "cisco":
        cmd_templates = CISCO_COMMANDS
        global_templates = CISCO_GLOBAL_COMMANDS
        separator = " ; "
        preamble = "terminal length 0\n"
    elif vendor == "juniper":
        cmd_templates = JUNIPER_COMMANDS
        global_templates = JUNIPER_GLOBAL_COMMANDS
        separator = " | no-more\n"
        preamble = "set cli screen-length 0\n"
    else:
        print(f"Error: Unknown vendor '{vendor}'", file=sys.stderr)
        sys.exit(1)

    # Select which per-port commands to run
    if commands:
        # Split user commands into per-port and global
        per_port_keys = set(cmd_templates.keys())
        global_keys = set(global_templates.keys())
        selected = {k: v for k, v in cmd_templates.items() if k in commands and k in per_port_keys}
        selected_global = {k: v for k, v in global_templates.items() if k in commands and k in global_keys}
    else:
        # Default: run most useful subset
        default_keys = ["port_status", "port_brief" if vendor == "cisco" else "port_extensive",
                        "mac_table", "vlan_port"]
        selected = {k: v for k, v in cmd_templates.items() if k in default_keys}
        selected_global = {}

    # Always include logs if flag set
    if include_logs and not selected_global:
        selected_global = global_templates.copy()

    all_cmds = [preamble.strip()]

    # Per-port commands
    for port in ports:
        for name, template in selected.items():
            cmd = template.format(port=port)
            if vendor == "juniper":
                cmd += " | no-more"
            all_cmds.append(cmd)

    # Global/log commands (run once, not per-port)
    for name, template in selected_global.items():
        if "{port}" in template:
            # Log commands that reference ports — run for each port
            for port in ports:
                cmd = template.format(port=port)
                if vendor == "juniper":
                    cmd += " | no-more"
                all_cmds.append(cmd)
        else:
            cmd = template
            if vendor == "juniper":
                cmd += " | no-more"
            all_cmds.append(cmd)

    return "\n".join(all_cmds) + "\n"


def run_ssh_commands(switch_ip: str, ldap_id: str, vendor: str, ports: list,
                     commands: list = None, include_logs: bool = False,
                     timeout: int = 30) -> str:
    """SSH to switch and run diagnostic commands, return output."""
    cmd_input = build_command_string(vendor, ports, commands, include_logs)

    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", f"ConnectTimeout={timeout}",
        "-o", "BatchMode=no",
        f"{ldap_id}@{switch_ip}"
    ]

    print(f"Connecting to {switch_ip} as {ldap_id} ({vendor})...", file=sys.stderr)
    print(f"Running diagnostics for ports: {', '.join(ports)}", file=sys.stderr)

    try:
        result = subprocess.run(
            ssh_cmd,
            input=cmd_input,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )
        output = result.stdout
        if result.stderr:
            print(f"SSH stderr: {result.stderr}", file=sys.stderr)
        return output
    except subprocess.TimeoutExpired:
        print(f"Error: SSH connection timed out after {timeout}s", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Error: SSH failed: {e}", file=sys.stderr)
        return ""


def open_interactive_ssh(switch_ip: str, ldap_id: str):
    """Open an interactive SSH session to the switch."""
    print(f"Opening interactive SSH session to {switch_ip} as {ldap_id}...", file=sys.stderr)
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"{ldap_id}@{switch_ip}"
    ]
    os.execvp("ssh", ssh_cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Run diagnostic commands on a TOR switch via SSH",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run default diagnostics on Cisco switch
  %(prog)s 100.64.1.10 --vendor cisco --ports Ethernet1/1,Ethernet1/2

  # Run specific commands on Juniper switch
  %(prog)s 100.64.1.20 --vendor juniper --ports xe-0/0/1 --commands port_status,mac_table

  # Include switch logs and alarms
  %(prog)s 100.64.1.10 --vendor cisco --ports Ethernet1/1 --logs

  # Run only log/alarm commands
  %(prog)s 100.64.1.10 --vendor juniper --ports et-0/0/16 --commands log_recent,alarms,chassis_alarms

  # Open interactive session
  %(prog)s 100.64.1.10 --vendor cisco --interactive

  # List available commands
  %(prog)s --list-commands

Per-port command keys:
  Cisco:   port_status, port_brief, port_counters, mac_table, vlan_port, cdp_neighbor, spanning_tree
  Juniper: port_status, port_extensive, mac_table, vlan_port, lldp_neighbor, spanning_tree

Global/log command keys:
  Cisco:   log_recent, log_interface, alarms, uptime
  Juniper: log_recent, log_interface, alarms, chassis_alarms, uptime
        """,
    )
    parser.add_argument("switch_ip", nargs="?", help="Switch management IP address")
    parser.add_argument("--vendor", choices=["cisco", "juniper"], help="Switch vendor")
    parser.add_argument("--ports", help="Comma-separated list of port interfaces")
    parser.add_argument("--commands", help="Comma-separated list of command keys to run (default: common subset)")
    parser.add_argument("--ldap-id", help="LDAP ID for SSH (default: $LDAP_ID env var)")
    parser.add_argument("--interactive", action="store_true", help="Open interactive SSH session")
    parser.add_argument("--logs", action="store_true",
                        help="Include switch logs, alarms, and uptime in output")
    parser.add_argument("--timeout", type=int, default=30, help="SSH timeout in seconds (default: 30)")
    parser.add_argument("--list-commands", action="store_true", help="List available commands and exit")

    args = parser.parse_args()

    if args.list_commands:
        print("Cisco NX-OS per-port commands:")
        for k, v in CISCO_COMMANDS.items():
            print(f"  {k:<20} {v}")
        print("\nCisco NX-OS global/log commands:")
        for k, v in CISCO_GLOBAL_COMMANDS.items():
            print(f"  {k:<20} {v}")
        print("\nJuniper per-port commands:")
        for k, v in JUNIPER_COMMANDS.items():
            print(f"  {k:<20} {v}")
        print("\nJuniper global/log commands:")
        for k, v in JUNIPER_GLOBAL_COMMANDS.items():
            print(f"  {k:<20} {v}")
        sys.exit(0)

    if not args.switch_ip:
        parser.error("switch_ip is required")

    ldap_id = args.ldap_id or os.environ.get("LDAP_ID")
    if not ldap_id:
        print("Error: LDAP_ID not set. Use --ldap-id or set LDAP_ID env var.", file=sys.stderr)
        sys.exit(1)

    if args.interactive:
        open_interactive_ssh(args.switch_ip, ldap_id)
        return

    if not args.vendor:
        parser.error("--vendor is required for command mode")
    if not args.ports:
        parser.error("--ports is required for command mode")

    ports = [p.strip() for p in args.ports.split(",")]
    commands = [c.strip() for c in args.commands.split(",")] if args.commands else None

    output = run_ssh_commands(args.switch_ip, ldap_id, args.vendor, ports, commands,
                              args.logs, args.timeout)
    if output:
        print(output)
    else:
        print("No output received from switch", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
