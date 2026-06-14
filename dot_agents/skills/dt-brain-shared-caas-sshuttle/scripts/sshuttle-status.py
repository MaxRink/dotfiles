#!/usr/bin/env python3
"""
Check sshuttle tunnel status.
Usage: sshuttle-status.py
"""

import os
import re
import subprocess
import sys


def main():
    current_pid = os.getpid()
    try:
        result = subprocess.run(
            ["pgrep", "-f", "sshuttle"],
            capture_output=True, text=True
        )
    except Exception as e:
        print(f"Error checking processes: {e}", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 or not result.stdout.strip():
        print("No sshuttle process running")
        sys.exit(0)

    pids = [p.strip() for p in result.stdout.strip().split("\n")
            if p.strip() and int(p.strip()) != current_pid]

    if not pids:
        print("No sshuttle process running")
        sys.exit(0)

    print("Active sshuttle process(es):\n")
    for pid in pids:
        try:
            ps = subprocess.run(
                ["ps", "-p", pid, "-o", "command="],
                capture_output=True, text=True
            )
            cmd = ps.stdout.strip() if ps.returncode == 0 else "unknown"
        except Exception:
            cmd = "unknown"

        # Extract cluster name from command
        match = re.search(r"kube\.([^.]+(?:\.[^.]+)*?)\.caas\.in\.pan-net\.eu", cmd)
        cluster = match.group(1) if match else "unknown"

        print(f"  PID: {pid}")
        print(f"  Cluster: {cluster}")
        print(f"  Command: {cmd}")
        print()


if __name__ == "__main__":
    main()
