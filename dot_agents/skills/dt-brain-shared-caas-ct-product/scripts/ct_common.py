#!/usr/bin/env python3
"""
CT-CaaS Bundles Common Module - Shared utilities for ct-caas-product skill scripts

Provides GitLab API access to the CT-CaaS bundles repository and OCI registry
for image version lookups.
"""

import io
import os
import re
import sys
import json
import tarfile
import base64
import tempfile
from typing import Dict, List, Optional, Any

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

try:
    import requests
except ImportError:
    print("Error: requests library not installed", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

# GitLab configuration
GITLAB_URL = "https://gitlab.devops.telekom.de"
CT_BUNDLES_PROJECT = "cit/t-caas/software/bundles"

# OCI Registry configuration
OCI_REGISTRY_URL = "https://artifactory.devops.telekom.de/v2/cit-t-caas-oci/charts"

# Bundle types to list by default
DEFAULT_BUNDLE_TYPES = ["netbox", "openstack"]


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


class CTBundlesClient:
    """Client for accessing CT-CaaS bundles repository via GitLab API"""

    def __init__(self, ref: str = "main"):
        self.gl = get_gitlab_client()
        try:
            self.project = self.gl.projects.get(CT_BUNDLES_PROJECT)
        except Exception as e:
            print(f"Error: Failed to access project '{CT_BUNDLES_PROJECT}': {e}", file=sys.stderr)
            sys.exit(1)
        self.ref = ref
        self._tree_cache: Dict[str, List[Dict]] = {}
        self._file_cache: Dict[str, Optional[str]] = {}

    def _get_tree(self, path: str = "", recursive: bool = False, silent: bool = False) -> List[Dict]:
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
            if not silent:
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

    def list_bundle_types(self) -> List[str]:
        """List available bundle types (directories under bundles/)"""
        items = self._get_tree("bundles")
        return sorted([item['name'] for item in items if item['type'] == 'tree'])

    def list_bundles(self, bundle_type: Optional[str] = None) -> List[Dict[str, str]]:
        """List all bundles, optionally filtered by type"""
        results = []

        if bundle_type:
            types = [bundle_type]
        else:
            types = [t for t in self.list_bundle_types() if t in DEFAULT_BUNDLE_TYPES]

        for btype in types:
            path = f"bundles/{btype}"
            items = self._get_tree(path)
            for item in items:
                if item['type'] == 'blob' and item['name'].endswith('.yaml'):
                    bundle_name = item['name'].rsplit('.yaml', 1)[0]
                    version = self._extract_version(bundle_name)
                    results.append({
                        'type': btype,
                        'name': bundle_name,
                        'version': version,
                        'path': item['path']
                    })

        return sorted(results, key=lambda x: (x['type'], x['name']))

    def find_bundle_file(self, bundle_name: str) -> Optional[str]:
        """Find bundle file path in repository"""
        for btype in self.list_bundle_types():
            path = f"bundles/{btype}/{bundle_name}.yaml"
            content = self._get_file_content(path, silent=True)
            if content is not None:
                return path
        return None

    def get_bundle(self, bundle_name: str) -> Optional[Dict]:
        """Get parsed bundle YAML"""
        file_path = self.find_bundle_file(bundle_name)
        if not file_path:
            print(f"Error: Bundle not found: {bundle_name}", file=sys.stderr)
            return None

        content = self._get_file_content(file_path)
        if not content:
            return None

        return self._parse_yaml(content)

    def get_bundle_type(self, bundle_name: str) -> Optional[str]:
        """Detect bundle type from name or by finding the file"""
        if bundle_name.startswith("netbox-"):
            return "netbox"
        elif bundle_name.startswith("openstack-"):
            return "openstack"
        # Fallback: find the file
        file_path = self.find_bundle_file(bundle_name)
        if file_path:
            # path is bundles/TYPE/name.yaml
            parts = file_path.split('/')
            if len(parts) >= 2:
                return parts[1]
        return None

    def get_bundle_functions(self, bundle_name: str) -> List[Dict[str, str]]:
        """Get list of functions for a bundle, splitting combined name-version refs"""
        bundle = self.get_bundle(bundle_name)
        if not bundle:
            return []

        spec = bundle.get('spec', {})
        functions = spec.get('functions', [])

        results = []
        for f in functions:
            ref = f.get('ref', {})
            full_name = ref.get('name', '')
            if not full_name:
                continue

            name, version = self._split_name_version(full_name)
            results.append({
                'name': name,
                'version': version,
                'full_name': full_name
            })

        return results

    def find_functiondef_file(self, full_name: str) -> Optional[str]:
        """Find function definition file path in repository"""
        name, version = self._split_name_version(full_name)

        # Try different naming patterns
        patterns = [
            f"functiondefinitions/{name}/{full_name}.yaml",
            f"functiondefinitions/{name}/{name}-{version}.yaml",
        ]

        for path in patterns:
            content = self._get_file_content(path, silent=True)
            if content is not None:
                return path

        # Try listing the directory to find the file
        try:
            items = self._get_tree(f"functiondefinitions/{name}", silent=True)
            for item in items:
                if item['type'] == 'blob' and item['name'].endswith('.yaml'):
                    # Check if version matches
                    if version in item['name']:
                        content = self._get_file_content(item['path'], silent=True)
                        if content is not None:
                            return item['path']
        except Exception:
            pass

        # Fallback: search all functiondefinitions/ subdirectories for the file
        # Handles cases where directory name differs from function name
        # (e.g., flux-workload-0.1.2.yaml lives in functiondefinitions/flux/)
        try:
            all_dirs = self._get_tree("functiondefinitions")
            for d in all_dirs:
                if d['type'] != 'tree' or d['name'] == name:
                    continue
                # Only search directories whose name is a prefix of the function name
                if not name.startswith(d['name']):
                    continue
                try:
                    items = self._get_tree(d['path'])
                    for item in items:
                        if item['type'] == 'blob' and item['name'] == f"{full_name}.yaml":
                            return item['path']
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def get_functiondef(self, full_name: str) -> Optional[Dict]:
        """Get parsed function definition YAML"""
        file_path = self.find_functiondef_file(full_name)
        if not file_path:
            return None

        content = self._get_file_content(file_path)
        if not content:
            return None

        return self._parse_yaml(content)

    @staticmethod
    def _split_name_version(full_name: str) -> tuple:
        """Split combined name-version (e.g., 'coredns-0.3.1' -> ('coredns', '0.3.1'))"""
        match = re.search(r'-(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?)$', full_name)
        if match:
            version = match.group(1)
            name = full_name[:match.start()]
            return name, version
        return full_name, 'unknown'

    @staticmethod
    def _extract_version(bundle_name: str) -> str:
        """Extract version from bundle name (e.g., netbox-workload-34.0.19 -> 34.0.19)"""
        match = re.search(r'-(\d+\.\d+\.\d+)$', bundle_name)
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


def extract_helm_releases(funcdef_data: Dict) -> List[Dict[str, str]]:
    """Extract Helm chart releases from function definition spec.releases[]"""
    results = []
    spec = funcdef_data.get('spec', {})
    releases = spec.get('releases', [])

    for release in releases:
        helm = release.get('helm')
        if not helm:
            continue

        chart_name = helm.get('name', '')
        chart_version = helm.get('version', '')

        # Extract chart path from provider config
        chart_path = ''
        provider = helm.get('provider', {})
        flux = provider.get('flux', {})
        manual = provider.get('manual', {})
        if flux:
            chart_path = flux.get('repo', {}).get('path', '')
        elif manual:
            chart_path = manual.get('repo', {}).get('path', '')

        if chart_name and chart_version:
            results.append({
                'chart': chart_name,
                'version': chart_version,
                'path': chart_path
            })

    return results


def extract_kustomize_releases(funcdef_data: Dict) -> List[Dict[str, str]]:
    """Extract Kustomize releases from function definition spec.releases[]"""
    results = []
    spec = funcdef_data.get('spec', {})
    releases = spec.get('releases', [])

    for release in releases:
        kustomize = release.get('kustomize')
        if not kustomize:
            continue

        release_name = release.get('name', '')
        provider = kustomize.get('provider', {})

        # Get OCI reference from flux provider
        flux = provider.get('flux', {})
        manual = provider.get('manual', {})

        reference = ''
        if flux:
            reference = flux.get('repo', {}).get('oci', {}).get('reference', '')
        if not reference and manual:
            reference = manual.get('repo', {}).get('git', {}).get('reference', '')

        if release_name and reference:
            results.append({
                'name': release_name,
                'reference': reference
            })

    return results


def extract_kustomize_images(funcdef_data: Dict) -> List[str]:
    """Extract container image names from kustomize images block"""
    images = []
    spec = funcdef_data.get('spec', {})
    releases = spec.get('releases', [])

    for release in releases:
        kustomize = release.get('kustomize')
        if not kustomize:
            continue

        for img in kustomize.get('images', []):
            name = img.get('name', '')
            # Skip template variables
            if name and '{{' not in name:
                images.append(name)

    return images


class OCIRegistryClient:
    """Client for OCI registry chart lookups to extract appVersion"""

    def __init__(self):
        self._session = None

    def _get_session(self) -> Optional[requests.Session]:
        """Get authenticated requests session"""
        if self._session is not None:
            return self._session

        token = os.environ.get("ARTIFACTORY_TOKEN")
        if not token:
            print("Warning: ARTIFACTORY_TOKEN not set. Image version lookup will be skipped.", file=sys.stderr)
            return None

        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        self._session.verify = False
        return self._session

    def _clean_chart_path(self, raw_path: str) -> str:
        """Clean template variables from chart path"""
        # Remove Go template variable prefix like '{{ .config.sources.registry.mirrors.charts.path }}/'
        return re.sub(r'^\{\{[^}]+\}\}/', '', raw_path)

    def get_appversion(self, chart_name: str, chart_version: str, chart_path_raw: str = '') -> Optional[str]:
        """Lookup appVersion by downloading chart from OCI registry"""
        session = self._get_session()
        if not session:
            return None

        # Use the path from function definition
        chart_path = self._clean_chart_path(chart_path_raw) if chart_path_raw else ''
        if not chart_path:
            return None

        # Try different version formats (with and without v prefix)
        versions_to_try = [chart_version]
        if chart_version.startswith('v'):
            versions_to_try.append(chart_version[1:])
        else:
            versions_to_try.append(f'v{chart_version}')

        for ver in versions_to_try:
            app_version = self._fetch_chart_appversion(session, chart_path, ver, chart_name)
            if app_version:
                return app_version

        return None

    def _fetch_chart_appversion(self, session: requests.Session, chart_path: str,
                                 version: str, chart_name: str) -> Optional[str]:
        """Fetch a chart from OCI registry and extract appVersion"""
        try:
            # Get OCI manifest
            manifest_url = f"{OCI_REGISTRY_URL}/{chart_path}/manifests/{version}"
            resp = session.get(
                manifest_url,
                headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
                timeout=30
            )
            if resp.status_code != 200:
                return None

            manifest = resp.json()
            layers = manifest.get('layers', [])
            if not layers:
                return None

            layer_digest = layers[0].get('digest')
            if not layer_digest:
                return None

            # Download the chart layer
            blob_url = f"{OCI_REGISTRY_URL}/{chart_path}/blobs/{layer_digest}"
            blob_resp = session.get(blob_url, timeout=60)
            if blob_resp.status_code != 200:
                return None

            # Extract appVersion from the chart tarball
            return self._extract_appversion_from_tgz(blob_resp.content, chart_name)

        except Exception:
            return None

    def _extract_appversion_from_tgz(self, tgz_content: bytes, chart_name: str) -> Optional[str]:
        """Extract appVersion from a chart .tgz content"""
        try:
            with tarfile.open(fileobj=io.BytesIO(tgz_content), mode='r:gz') as tar:
                # First try: extract image tag from values.yaml patterns
                app_version = self._try_values_yaml(tar, chart_name)
                if app_version:
                    return app_version

                # Try top-level Chart.yaml appVersion (most reliable for wrapper charts)
                app_version = self._try_chart_yaml_appversion(tar)
                if app_version:
                    return app_version

                # Fallback: try bundled sub-charts
                app_version = self._try_subchart_appversion(tar, chart_name)
                if app_version:
                    return app_version

        except Exception:
            pass
        return None

    def _try_values_yaml(self, tar: tarfile.TarFile, chart_name: str) -> Optional[str]:
        """Try to extract image tag from values.yaml"""
        for member in tar.getmembers():
            if member.name.endswith('/values.yaml') and member.name.count('/') == 1:
                f = tar.extractfile(member)
                if not f:
                    continue
                try:
                    values = yaml.safe_load(f.read().decode('utf-8', errors='ignore'))
                except Exception:
                    continue
                if not isinstance(values, dict):
                    continue

                tag = self._find_image_tag(values, chart_name)
                if tag and not self._is_placeholder(tag):
                    return str(tag)
        return None

    def _try_subchart_appversion(self, tar: tarfile.TarFile, chart_name: str) -> Optional[str]:
        """Try to extract appVersion from bundled sub-chart Chart.yaml"""
        for member in tar.getmembers():
            # Look for charts/*/Chart.yaml (depth 3) or sub-chart tgz
            if '/charts/' in member.name and member.name.endswith('/Chart.yaml'):
                f = tar.extractfile(member)
                if not f:
                    continue
                try:
                    chart_data = yaml.safe_load(f.read().decode('utf-8', errors='ignore'))
                except Exception:
                    continue
                if isinstance(chart_data, dict):
                    av = chart_data.get('appVersion')
                    if av:
                        return str(av)
        return None

    def _try_chart_yaml_appversion(self, tar: tarfile.TarFile) -> Optional[str]:
        """Extract appVersion from top-level Chart.yaml"""
        for member in tar.getmembers():
            if member.name.endswith('/Chart.yaml') and member.name.count('/') == 1:
                f = tar.extractfile(member)
                if not f:
                    continue
                try:
                    chart_data = yaml.safe_load(f.read().decode('utf-8', errors='ignore'))
                except Exception:
                    continue
                if isinstance(chart_data, dict):
                    av = chart_data.get('appVersion')
                    if av:
                        return str(av)
        return None

    def _find_image_tag(self, values: Dict, chart_name: str) -> Optional[str]:
        """Find image tag from values.yaml using multiple patterns"""
        # Pattern 1: image.tag at root
        tag = self._get_nested(values, 'image', 'tag')
        if tag and not self._is_placeholder(str(tag)):
            return str(tag)

        # Pattern 2: global.image.tag
        tag = self._get_nested(values, 'global', 'image', 'tag')
        if tag and not self._is_placeholder(str(tag)):
            return str(tag)

        # Pattern 3: controller.image.tag (ingress-nginx)
        tag = self._get_nested(values, 'controller', 'image', 'tag')
        if tag and not self._is_placeholder(str(tag)):
            return str(tag)

        # Pattern 4: collector.image.tag or forwarder.image.tag (fluent-bit)
        for section in ('collector', 'forwarder'):
            tag = self._get_nested(values, section, 'image', 'tag')
            if tag and not self._is_placeholder(str(tag)):
                return str(tag)

        # Pattern 5: chart_name.image.tag
        if chart_name:
            tag = self._get_nested(values, chart_name, 'image', 'tag')
            if tag and not self._is_placeholder(str(tag)):
                return str(tag)

        return None

    @staticmethod
    def _get_nested(d: Dict, *keys) -> Any:
        """Safely get nested dict value"""
        for key in keys:
            if not isinstance(d, dict):
                return None
            d = d.get(key)
            if d is None:
                return None
        return d

    @staticmethod
    def _is_placeholder(tag: str) -> bool:
        """Check if a tag value is a placeholder"""
        if not tag:
            return True
        tag = str(tag)
        if tag in ('latest', ''):
            return True
        if re.match(r'^v?X\.Y\.Z$', tag):
            return True
        if '{{' in tag:
            return True
        return False

    def get_dependency_appversion(self, chart_path: str, dep_name: str, dep_version: str) -> Optional[str]:
        """Fetch appVersion from a dependency chart"""
        session = self._get_session()
        if not session:
            return None
        return self._fetch_chart_appversion(session, f"{chart_path}/{dep_name}" if chart_path else dep_name,
                                             dep_version, dep_name)


# Output formatting utilities (same pattern as tdi-caas-product)

def format_table(headers: List[str], rows: List[List[str]], separator: str = '|') -> str:
    """Format data as ASCII table"""
    if not rows:
        return f"{separator.join(headers)}\n{separator.join(['-' * len(h) for h in headers])}"

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    header_line = separator.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator_line = separator.join('-' * w for w in widths)

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
    header_line = '| ' + ' | '.join(headers) + ' |'
    separator_line = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'

    row_lines = []
    for row in rows:
        row_line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
        row_lines.append(row_line)

    return '\n'.join([header_line, separator_line] + row_lines)


def format_confluence_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as Confluence wiki markup table"""
    header_line = '|| ' + ' || '.join(headers) + ' ||'

    row_lines = []
    for row in rows:
        row_line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
        row_lines.append(row_line)

    return '\n'.join([header_line] + row_lines)


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
    elif fmt == 'confluence':
        rows = [[str(item.get(k, '')) for k in keys] for item in data]
        print(format_confluence_table(headers, rows))
    else:  # table
        rows = [[str(item.get(k, '')) for k in keys] for item in data]
        print(format_table(headers, rows))
