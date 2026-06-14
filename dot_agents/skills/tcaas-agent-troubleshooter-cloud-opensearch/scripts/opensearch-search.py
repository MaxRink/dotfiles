#!/usr/bin/env python3
"""
OpenSearch Log Search Script
Search and query logs from CaaS infrastructure.

Usage: opensearch-search.py [options]
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta, timezone
import urllib3

# Disable SSL warnings for internal certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Configuration
OPENSEARCH_DASHBOARDS_URL = "https://infra-os-prod-dashboards.infra-mon.in.pan-net.eu"
OPENSEARCH_TENANT = "caas-tenant"
INDEX_PATTERN = "caas-*,*-caas-*,tcaas-*"


def get_auth_config():
    """Get authentication configuration from environment variables."""
    config = {
        "user": os.environ.get("OPENSEARCH_USER"),
        "password": os.environ.get("OPENSEARCH_PASSWORD"),
        "api_token": os.environ.get("OPENSEARCH_API_TOKEN"),
        "session_cookie": os.environ.get("OPENSEARCH_SESSION_COOKIE"),
    }
    return config


def create_session(auth_config):
    """Create a requests session with appropriate authentication."""
    session = requests.Session()
    session.verify = False  # Disable SSL verification for internal CA

    # Set tenant header
    session.headers["securitytenant"] = OPENSEARCH_TENANT
    session.headers["osd-xsrf"] = "true"

    # Try different auth methods
    if auth_config["session_cookie"]:
        cookie_str = auth_config["session_cookie"]
        if "=" in cookie_str:
            for cookie in cookie_str.split(";"):
                cookie = cookie.strip()
                if "=" in cookie:
                    name, value = cookie.split("=", 1)
                    session.cookies.set(name.strip(), value.strip())
    elif auth_config["api_token"]:
        session.headers["Authorization"] = f"Bearer {auth_config['api_token']}"
    elif auth_config["user"] and auth_config["password"]:
        session.auth = (auth_config["user"], auth_config["password"])
    else:
        print("Warning: No authentication configured", file=sys.stderr)
        print("Set OPENSEARCH_SESSION_COOKIE, OPENSEARCH_API_TOKEN, or OPENSEARCH_USER/PASSWORD", file=sys.stderr)

    return session


def parse_time(time_str):
    """Parse time string to datetime object.

    Supports:
    - ISO 8601: "2026-02-05T10:00:00Z"
    - Relative: "1h", "30m", "2d", "1w"
    """
    if not time_str:
        return None

    # Check for relative time format
    relative_pattern = r'^(\d+)([mhdwM])$'
    match = re.match(relative_pattern, time_str)

    if match:
        value = int(match.group(1))
        unit = match.group(2)

        now = datetime.now(timezone.utc)

        if unit == 'm':
            return now - timedelta(minutes=value)
        elif unit == 'h':
            return now - timedelta(hours=value)
        elif unit == 'd':
            return now - timedelta(days=value)
        elif unit == 'w':
            return now - timedelta(weeks=value)
        elif unit == 'M':
            return now - timedelta(days=value * 30)  # Approximate

    # Try parsing as ISO 8601
    try:
        # Handle various ISO formats
        if time_str.endswith('Z'):
            time_str = time_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(time_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass

    # Try simple date format
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    raise ValueError(f"Cannot parse time: {time_str}")


def build_query(args):
    """Build OpenSearch query from arguments."""
    must_clauses = []

    # Time range filter
    time_range = {}
    if args.time_from:
        from_dt = parse_time(args.time_from)
        time_range["gte"] = from_dt.isoformat()
    if args.time_to:
        to_dt = parse_time(args.time_to)
        time_range["lte"] = to_dt.isoformat()
    else:
        time_range["lte"] = "now"

    if time_range:
        must_clauses.append({
            "range": {
                "@timestamp": time_range
            }
        })

    # Cluster filter - use cluster_name.keyword for exact/wildcard matching
    if args.cluster:
        must_clauses.append({
            "bool": {
                "should": [
                    {"term": {"cluster_name.keyword": args.cluster}},
                    {"wildcard": {"cluster_name.keyword": f"*{args.cluster}*"}}
                ],
                "minimum_should_match": 1
            }
        })

    # Log level filter - search in message since level is often embedded
    if args.level:
        level_upper = args.level.upper()
        level_lower = args.level.lower()
        # Handle common variations
        level_variants = [level_upper, level_lower, level_lower.capitalize()]
        if args.level.lower() == "warn":
            level_variants.extend(["WARNING", "warning", "Warning"])
        elif args.level.lower() == "warning":
            level_variants.extend(["WARN", "warn", "Warn"])
        elif args.level.lower() == "error":
            level_variants.extend(["ERR", "err", "Err", "E0"])

        must_clauses.append({
            "bool": {
                "should": [
                    {"term": {"level": level_lower}},
                    {"term": {"level": level_upper}},
                    {"term": {"log.level": level_lower}},
                    {"term": {"log.level": level_upper}},
                    {"term": {"severity": level_lower}},
                    {"term": {"severity": level_upper}},
                    # Also search in log/message for level patterns
                    {"query_string": {"query": f"log:({' OR '.join(level_variants)})", "default_field": "log"}},
                ],
                "minimum_should_match": 1
            }
        })

    # Free text query
    if args.query:
        must_clauses.append({
            "query_string": {
                "query": args.query,
                "default_field": "message"
            }
        })

    # Build final query
    if must_clauses:
        query = {
            "bool": {
                "must": must_clauses
            }
        }
    else:
        query = {"match_all": {}}

    return {
        "size": args.limit,
        "query": query,
        "sort": [{"@timestamp": {"order": "desc"}}],
        "_source": True
    }


def execute_search(session, query):
    """Execute search query against OpenSearch."""
    url = f"{OPENSEARCH_DASHBOARDS_URL}/api/console/proxy"

    # URL encode the index pattern
    index = INDEX_PATTERN.replace("*", "%2A")
    params = {"path": f"{index}/_search", "method": "POST"}

    response = session.post(
        url,
        params=params,
        json=query,
        headers={"Content-Type": "application/json"},
        timeout=60
    )

    if response.status_code == 401:
        print("Error: Authentication failed (401)", file=sys.stderr)
        print("Check your OPENSEARCH_* credentials", file=sys.stderr)
        sys.exit(1)
    elif response.status_code == 403:
        print("Error: Access denied (403)", file=sys.stderr)
        print("Check access to caas-tenant", file=sys.stderr)
        sys.exit(1)
    elif response.status_code != 200:
        print(f"Error: Search failed with status {response.status_code}", file=sys.stderr)
        print(response.text[:500], file=sys.stderr)
        sys.exit(1)

    return response.json()


def format_timestamp(ts):
    """Format timestamp for display."""
    if not ts:
        return "N/A"
    try:
        if isinstance(ts, str):
            # Parse ISO format
            if ts.endswith('Z'):
                ts = ts[:-1] + '+00:00'
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    return str(ts)[:19]


def extract_field(source, field_paths):
    """Extract a field from source, trying multiple paths."""
    for path in field_paths:
        parts = path.split('.')
        value = source
        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None
                    break
            if value is not None:
                return value
        except:
            continue
    return None


def format_table(hits):
    """Format search results as a table."""
    if not hits:
        print("No results found.")
        return

    # Define column widths
    ts_width = 19
    level_width = 6
    cluster_width = 30
    msg_width = 80

    # Print header
    print("-" * (ts_width + level_width + cluster_width + msg_width + 9))
    print(f"{'Timestamp':<{ts_width}} | {'Level':<{level_width}} | {'Cluster':<{cluster_width}} | Message")
    print("-" * (ts_width + level_width + cluster_width + msg_width + 9))

    for hit in hits:
        source = hit.get("_source", {})

        # Extract fields
        timestamp = format_timestamp(
            extract_field(source, ["@timestamp", "timestamp", "time"])
        )

        level = extract_field(source, ["level", "log.level", "severity", "loglevel"]) or "INFO"
        if isinstance(level, str):
            level = level.upper()[:level_width]

        cluster = extract_field(source, [
            "cluster_name",
            "kubernetes.cluster_name",
            "cluster",
            "kubernetes.labels.cluster"
        ]) or "-"
        if len(str(cluster)) > cluster_width:
            cluster = str(cluster)[:cluster_width-3] + "..."

        message = extract_field(source, ["log", "message", "msg", "log.message"]) or ""
        if isinstance(message, str):
            message = message.replace("\n", " ").replace("\r", "")
            if len(message) > msg_width:
                message = message[:msg_width-3] + "..."

        print(f"{timestamp:<{ts_width}} | {level:<{level_width}} | {cluster:<{cluster_width}} | {message}")

    print("-" * (ts_width + level_width + cluster_width + msg_width + 9))
    print(f"Showing {len(hits)} results")


def format_json(hits):
    """Format search results as JSON."""
    results = []
    for hit in hits:
        results.append({
            "_index": hit.get("_index"),
            "_id": hit.get("_id"),
            "_source": hit.get("_source")
        })
    print(json.dumps(results, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="Search OpenSearch logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search last hour for a cluster
  %(prog)s --cluster atgraf1-ndl-prod --from 1h

  # Search specific time range
  %(prog)s --cluster prod --from "2026-02-05T10:00:00Z" --to "2026-02-05T11:00:00Z"

  # Search for errors
  %(prog)s --cluster prod --from 24h --level error

  # Free text search
  %(prog)s --cluster prod --from 1h --query "connection refused"
        """
    )

    parser.add_argument("--cluster", "-c", help="Filter by cluster name (partial match)")
    parser.add_argument("--from", "-f", dest="time_from", help="Start time (ISO 8601 or relative: 1h, 30m, 2d)")
    parser.add_argument("--to", "-t", dest="time_to", help="End time (ISO 8601, default: now)")
    parser.add_argument("--query", "-q", help="Free text search query")
    parser.add_argument("--level", "-l", choices=["error", "warn", "warning", "info", "debug"],
                       help="Filter by log level")
    parser.add_argument("--limit", "-n", type=int, default=100, help="Maximum results (default: 100)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                       help="Output format (default: table)")

    args = parser.parse_args()

    # Require at least --from
    if not args.time_from:
        parser.error("--from is required. Example: --from 1h or --from 2026-02-05T10:00:00Z")

    # Get auth config
    auth_config = get_auth_config()

    # Create session
    session = create_session(auth_config)

    # Build and execute query
    query = build_query(args)

    try:
        result = execute_search(session, query)
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed. Are you connected to VPN?", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out", file=sys.stderr)
        sys.exit(1)

    # Extract hits
    hits = result.get("hits", {}).get("hits", [])
    total = result.get("hits", {}).get("total", {})
    if isinstance(total, dict):
        total_count = total.get("value", 0)
    else:
        total_count = total

    # Format output
    if args.format == "json":
        format_json(hits)
    else:
        if hits:
            print(f"Found {total_count:,} total matches (showing {len(hits)})\n")
        format_table(hits)


if __name__ == "__main__":
    main()
