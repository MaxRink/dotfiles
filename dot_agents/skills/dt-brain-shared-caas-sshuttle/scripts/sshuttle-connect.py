#!/usr/bin/env python3
"""
sshuttle tunnel connector for CaaS clusters.
Usage: sshuttle-connect.py <cluster-name> [--kill]
"""

import subprocess
import sys
import os
import time
import argparse

SSHUTTLE_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "../../../.venv/bin/sshuttle")


def get_existing_sshuttle():
    """Find existing sshuttle processes (excludes the current process)."""
    current_pid = os.getpid()
    try:
        result = subprocess.run(
            ["pgrep", "-f", "sshuttle"],
            capture_output=True, text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []

        pids = result.stdout.strip().split("\n")
        processes = []
        for pid in pids:
            pid = pid.strip()
            if not pid or int(pid) == current_pid:
                continue
            try:
                ps = subprocess.run(
                    ["ps", "-p", pid, "-o", "pid=,command="],
                    capture_output=True, text=True
                )
                if ps.returncode == 0 and ps.stdout.strip():
                    processes.append({"pid": int(pid), "command": ps.stdout.strip()})
            except Exception:
                pass
        return processes
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser(description="Start sshuttle tunnel to a CaaS cluster")
    parser.add_argument("cluster_name", help="CaaS cluster name")
    parser.add_argument("--kill", action="store_true",
                        help="Kill existing sshuttle processes before connecting")
    parser.add_argument("--extra-subnets", nargs="*", default=[],
                        help="Additional CIDR subnets to route (e.g., 10.242.140.0/24)")
    args = parser.parse_args()

    cluster_name = args.cluster_name
    remote_host = f"kube.{cluster_name}.caas.in.pan-net.eu"
    subnet = "100.64.0.0/10"
    subnets = [subnet] + list(args.extra_subnets)

    # Check for existing processes
    existing = get_existing_sshuttle()
    if existing:
        print("WARNING: Existing sshuttle process(es) found:", file=sys.stderr)
        for proc in existing:
            print(f"  PID {proc['pid']}: {proc['command']}", file=sys.stderr)

        if args.kill:
            for proc in existing:
                print(f"Killing PID {proc['pid']}...", file=sys.stderr)
                try:
                    subprocess.run(["kill", str(proc['pid'])], check=True)
                except subprocess.CalledProcessError:
                    print(f"  Failed to kill PID {proc['pid']}", file=sys.stderr)
            time.sleep(1)
        else:
            print("\nKill existing process(es) first, or use --kill flag.", file=sys.stderr)
            sys.exit(2)

    print(f"Starting sshuttle tunnel to {cluster_name}...")
    print(f"  Remote: {remote_host}")
    print(f"  Subnets: {', '.join(subnets)}")

    proc = subprocess.Popen(
        [SSHUTTLE_BIN, "--no-latency-control", "-r", remote_host] + subnets,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    time.sleep(3)

    if proc.poll() is not None:
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        print(f"Error: sshuttle exited unexpectedly (code {proc.returncode})", file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(3)

    print(f"sshuttle started successfully")
    print(f"PID: {proc.pid}")
    print(f"Cluster: {cluster_name}")


if __name__ == "__main__":
    main()
