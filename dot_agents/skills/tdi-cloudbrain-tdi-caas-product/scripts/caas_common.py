#!/usr/bin/env python3
"""
CaaS Bundles Common Module - Shared utilities for tdi-caas-product skill scripts

Provides GitLab API access to the caas-bundles repository.
"""

import os
import sys
import json
import base64
from typing import Dict, List, Optional, Any
from functools import lru_cache

try:
    import gitlab
except ImportError:
    print("Error: python-gitlab library not installed", file=sys.stderr)
    print("Install with: pip install python-gitlab", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: pyyaml library not installed", file=sys.stderr)
    print("Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# GitLab configuration
GITLAB_URL = "https://gitlab.devops.telekom.de"
CAAS_BUNDLES_PROJECT = "tdi-caas/caas-bundles"

# Artifactory configuration
ARTIFACTORY_HELM_URL = "https://artifactory.devops.telekom.de/artifactory/tdi-caas-helm-virtual"
ARTIFACTORY_INDEX_URL = f"{ARTIFACTORY_HELM_URL}/index.yaml"


def get_gitlab_client():
    """Initialize GitLab API client"""
    token = os.environ.get("GITLAB_API_TOKEN")
    if not token:
        print("Error: GITLAB_API_TOKEN environment variable is not set", file=sys.stderr)
        print("Set it with: export GITLAB_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)

    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        gl = gitlab.Gitlab(GITLAB_URL, private_token=token, ssl_verify=False)
        gl.auth()
        return gl
    except Exception as e:
        print(f"Error: Failed to initialize GitLab client: {e}", file=sys.stderr)
        print("Make sure you are connected to Telekom VPN", file=sys.stderr)
        sys.exit(1)


class CaaSBundlesClient:
    """Client for accessing caas-bundles repository via GitLab API"""

    def __init__(self, ref: str = "master"):
        self.gl = get_gitlab_client()
        try:
            self.project = self.gl.projects.get(CAAS_BUNDLES_PROJECT)
        except Exception as e:
            print(f"Error: Failed to access project '{CAAS_BUNDLES_PROJECT}': {e}", file=sys.stderr)
            sys.exit(1)
        self.ref = ref
        self._tree_cache: Dict[str, List[Dict]] = {}
        self._file_cache: Dict[str, str] = {}

    def _get_tree(self, path: str = "", recursive: bool = False) -> List[Dict]:
        """Get repository tree (cached)"""
        cache_key = f"{path}:{recursive}"
        if cache_key in self._tree_cache:
            return self._tree_cache[cache_key]

        try:
            items = self.project.repository_tree(
                path=path,
                ref=self.ref,
                recursive=recursive,
                per_page=100,
                get_all=True
            )
            self._tree_cache[cache_key] = items
            return items
        except Exception as e:
            print(f"Error: Failed to get repository tree at '{path}': {e}", file=sys.stderr)
            return []

    def _get_file_content(self, file_path: str, silent: bool = False) -> Optional[str]:
        """Get file content (cached)"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        try:
            f = self.project.files.get(file_path=file_path, ref=self.ref)
            content = base64.b64decode(f.content).decode('utf-8')
            self._file_cache[file_path] = content
            return content
        except Exception as e:
            # Cache the failure to avoid repeated API calls
            self._file_cache[file_path] = None
            if not silent:
                print(f"Error: Failed to get file '{file_path}': {e}", file=sys.stderr)
            return None

    def _parse_yaml(self, content: str) -> Optional[Dict]:
        """Parse YAML content"""
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"Error: Failed to parse YAML: {e}", file=sys.stderr)
            return None

    def list_product_types(self) -> List[str]:
        """List available product types (directories under products/)"""
        items = self._get_tree("products")
        return sorted([item['name'] for item in items if item['type'] == 'tree'])

    def list_products(self, product_type: Optional[str] = None) -> List[Dict[str, str]]:
        """List all products, optionally filtered by type"""
        results = []

        if product_type:
            types = [product_type]
        else:
            types = self.list_product_types()

        for ptype in types:
            path = f"products/{ptype}"
            items = self._get_tree(path)
            for item in items:
                if item['type'] == 'blob' and item['name'].endswith('.yaml'):
                    product_name = item['name'].rsplit('.yaml', 1)[0]
                    version = self._extract_version(product_name)
                    results.append({
                        'type': ptype,
                        'name': product_name,
                        'version': version,
                        'path': item['path']
                    })

        return sorted(results, key=lambda x: (x['type'], x['name']))

    def find_product_file(self, product_name: str) -> Optional[str]:
        """Find product file path in repository"""
        for ptype in self.list_product_types():
            path = f"products/{ptype}/{product_name}.yaml"
            content = self._get_file_content(path)
            if content is not None:
                return path
        return None

    def get_product(self, product_name: str) -> Optional[Dict]:
        """Get parsed product YAML"""
        file_path = self.find_product_file(product_name)
        if not file_path:
            print(f"Error: Product not found: {product_name}", file=sys.stderr)
            return None

        content = self._get_file_content(file_path)
        if not content:
            return None

        return self._parse_yaml(content)

    def find_function_file(self, func_name: str, version: str) -> Optional[str]:
        """Find function file path in repository"""
        # Try different naming patterns
        patterns = [
            f"functions/{func_name}/{func_name}-{version}.yaml",
            f"functions/caas-{func_name}/caas-{func_name}-{version}.yaml",
        ]

        # If name starts with caas-, also try folder without prefix but file with prefix
        if func_name.startswith("caas-"):
            stripped = func_name[5:]
            patterns.append(f"functions/{stripped}/{stripped}-{version}.yaml")
            # Key pattern: folder uses stripped name, file uses full name
            patterns.append(f"functions/{stripped}/{func_name}-{version}.yaml")

        for path in patterns:
            content = self._get_file_content(path, silent=True)
            if content is not None:
                return path

        return None

    def get_function(self, func_name: str, version: str) -> Optional[Dict]:
        """Get parsed function YAML"""
        file_path = self.find_function_file(func_name, version)
        if not file_path:
            return None

        content = self._get_file_content(file_path)
        if not content:
            return None

        return self._parse_yaml(content)

    def get_product_functions(self, product_name: str) -> List[Dict[str, str]]:
        """Get list of functions for a product"""
        product = self.get_product(product_name)
        if not product:
            return []

        spec = product.get('spec', {})
        functions = spec.get('functions', [])

        return [
            {'name': f.get('name', ''), 'version': f.get('version', '')}
            for f in functions
        ]

    @staticmethod
    def _extract_version(product_name: str) -> str:
        """Extract version from product name (e.g., baremetal-cluster-34.6.10 -> 34.6.10)"""
        import re
        match = re.search(r'-(\d+\.\d+\.\d+)$', product_name)
        return match.group(1) if match else ''

    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """Compare two version strings. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2"""
        def parse_version(v: str) -> List[int]:
            try:
                return [int(x) for x in v.split('.')]
            except ValueError:
                return [0]

        p1, p2 = parse_version(v1), parse_version(v2)

        for a, b in zip(p1, p2):
            if a < b:
                return -1
            if a > b:
                return 1

        if len(p1) < len(p2):
            return -1
        if len(p1) > len(p2):
            return 1
        return 0


class HelmIndexClient:
    """Client for Artifactory Helm index lookups"""

    def __init__(self):
        self._index: Optional[Dict] = None
        self._index_loaded = False

    def _load_index(self) -> bool:
        """Load Helm index from Artifactory (cached)"""
        if self._index_loaded:
            return self._index is not None

        self._index_loaded = True
        token = os.environ.get("ARTIFACTORY_TOKEN")
        if not token:
            print("Warning: ARTIFACTORY_TOKEN not set. Helm index lookup will be skipped.", file=sys.stderr)
            return False

        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            import requests
            response = requests.get(
                ARTIFACTORY_INDEX_URL,
                headers={"Authorization": f"Bearer {token}"},
                verify=False,
                timeout=60
            )
            response.raise_for_status()

            # Clean content: remove non-UTF8 characters before YAML parsing
            content = response.content.decode('utf-8', errors='ignore')
            self._index = yaml.safe_load(content)
            return True
        except Exception as e:
            print(f"Warning: Failed to load Helm index: {e}", file=sys.stderr)
            return False

    def get_appversion(self, chart_name: str, chart_version: str) -> Optional[str]:
        """Lookup appVersion from Helm index"""
        if not self._load_index():
            return None

        entries = self._index.get('entries', {})
        chart_entries = entries.get(chart_name, [])

        # Handle version patterns with .x suffix (e.g., "27.3.x")
        use_prefix_match = chart_version.endswith('.x')
        version_prefix = chart_version[:-1] if use_prefix_match else None

        # Also try with/without v prefix
        alt_version = chart_version[1:] if chart_version.startswith('v') else f'v{chart_version}'

        matching_entries = []
        for entry in chart_entries:
            entry_version = entry.get('version', '')
            if use_prefix_match:
                if entry_version.startswith(version_prefix):
                    matching_entries.append(entry)
            elif entry_version == chart_version or entry_version == alt_version:
                matching_entries.append(entry)

        if not matching_entries:
            return None

        # Sort by version and return highest match's appVersion
        matching_entries.sort(key=lambda x: x.get('version', ''), reverse=True)
        return matching_entries[0].get('appVersion')


# Output formatting utilities

def format_table(headers: List[str], rows: List[List[str]], separator: str = '|') -> str:
    """Format data as ASCII table"""
    if not rows:
        return f"{separator.join(headers)}\n{separator.join(['-' * len(h) for h in headers])}"

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    # Format header
    header_line = separator.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator_line = separator.join('-' * w for w in widths)

    # Format rows
    row_lines = []
    for row in rows:
        row_line = separator.join(
            str(cell).ljust(widths[i]) if i < len(widths) else str(cell)
            for i, cell in enumerate(row)
        )
        row_lines.append(row_line)

    return '\n'.join([header_line, separator_line] + row_lines)


def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as Markdown table"""
    if not rows:
        header_line = '| ' + ' | '.join(headers) + ' |'
        separator_line = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'
        return f"{header_line}\n{separator_line}"

    header_line = '| ' + ' | '.join(headers) + ' |'
    separator_line = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'

    row_lines = []
    for row in rows:
        row_line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
        row_lines.append(row_line)

    return '\n'.join([header_line, separator_line] + row_lines)


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=indent)


def output_results(data: List[Dict], headers: List[str], keys: List[str], fmt: str = 'table'):
    """Output results in specified format"""
    if fmt == 'json':
        print(format_json(data))
    elif fmt == 'markdown':
        rows = [[str(item.get(k, '')) for k in keys] for item in data]
        print(format_markdown_table(headers, rows))
    else:  # table
        rows = [[str(item.get(k, '')) for k in keys] for item in data]
        print(format_table(headers, rows))
