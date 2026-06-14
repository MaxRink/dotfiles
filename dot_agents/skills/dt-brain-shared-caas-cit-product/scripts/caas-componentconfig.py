#!/usr/bin/env python3
"""
CaaS ComponentConfig - Show componentConfig details for a CaaS product

Shows the componentConfig referenced by a product, including kube-apiserver extraArgs,
kubelet configuration, kubeadm settings, and other cluster-level parameters.

Usage:
  caas-componentconfig.py <product-name> [--format FORMAT]
  caas-componentconfig.py <product-name> --section apiserver
  caas-componentconfig.py <product-name> --section kubelet
  caas-componentconfig.py <product-name> --section etcd
  caas-componentconfig.py <product-name> --section scheduler
  caas-componentconfig.py <product-name> --section controller-manager
  caas-componentconfig.py <product-name> --section features
  caas-componentconfig.py <product-name> --raw
  caas-componentconfig.py --list
"""

import argparse
import sys
import re
from typing import Dict, Any, Optional, List

from caas_common import (
    CaaSBundlesClient,
    format_json,
    format_table,
    format_markdown_table,
)


def find_componentconfig_file(client: CaaSBundlesClient, config_name: str) -> Optional[str]:
    """Find componentConfig file path in repository"""
    path = f"componentconfig/{config_name}.yaml"
    content = client._get_file_content(path, silent=True)
    if content is not None:
        return path
    return None


def get_componentconfig(client: CaaSBundlesClient, product_name: str) -> tuple:
    """Get componentConfig for a product. Returns (config_name, parsed_yaml)"""
    product = client.get_product(product_name)
    if not product:
        return None, None

    config_name = product.get('spec', {}).get('componentConfig', '')
    if not config_name:
        print(f"Error: Product '{product_name}' has no componentConfig defined", file=sys.stderr)
        return None, None

    file_path = find_componentconfig_file(client, config_name)
    if not file_path:
        print(f"Error: ComponentConfig file not found: {config_name}", file=sys.stderr)
        return config_name, None

    content = client._get_file_content(file_path)
    if not content:
        return config_name, None

    parsed = client._parse_yaml(content)
    return config_name, parsed


def list_componentconfigs(client: CaaSBundlesClient) -> List[Dict[str, str]]:
    """List all componentConfig files in the repository"""
    items = client._get_tree("componentconfig")
    results = []
    for item in items:
        if item['type'] == 'blob' and item['name'].endswith('.yaml'):
            name = item['name'].rsplit('.yaml', 1)[0]
            results.append({'name': name, 'path': item['path']})
    return sorted(results, key=lambda x: x['name'])


def extract_kubeadm_config(spec: Dict) -> Optional[Dict]:
    """Extract kubeadm config containing clusterConfiguration.

    Known paths in componentConfig:
    - spec.kubeadmControlPlane.kubeadmConfigSpec.clusterConfiguration (control plane)
    - spec.kubeadmConfigTemplate.clusterConfiguration (worker template)
    - spec.controlPlane.kubeadmConfigSpec.clusterConfiguration (alternative)
    """
    # Try kubeadmControlPlane path (most common for baremetal)
    kcp = spec.get('kubeadmControlPlane', {})
    kubeadm = kcp.get('kubeadmConfigSpec', {})
    if kubeadm and 'clusterConfiguration' in kubeadm:
        return kubeadm

    # Try controlPlane path
    cp = spec.get('controlPlane', {})
    kubeadm = cp.get('kubeadmConfigSpec', {})
    if kubeadm and 'clusterConfiguration' in kubeadm:
        return kubeadm

    # Try top-level kubeadmConfigTemplate
    kubeadm_template = spec.get('kubeadmConfigTemplate', {})
    if kubeadm_template and 'clusterConfiguration' in kubeadm_template:
        return kubeadm_template

    # Try bareMetal.kubeadmConfigTemplate
    bm = spec.get('bareMetal', {})
    kubeadm_template = bm.get('kubeadmConfigTemplate', {})
    if kubeadm_template and 'clusterConfiguration' in kubeadm_template:
        return kubeadm_template

    # Fallback: walk entire spec
    def find_cluster_config(d, depth=0):
        if depth > 10:
            return None
        if isinstance(d, dict):
            if 'clusterConfiguration' in d:
                return d
            for v in d.values():
                result = find_cluster_config(v, depth + 1)
                if result:
                    return result
        elif isinstance(d, list):
            for item in d:
                result = find_cluster_config(item, depth + 1)
                if result:
                    return result
        return None

    return find_cluster_config(spec)


def extract_section(spec: Dict, section: str) -> Dict:
    """Extract a specific section from the componentConfig"""
    kubeadm = extract_kubeadm_config(spec)

    if section == 'apiserver':
        if kubeadm:
            cc = kubeadm.get('clusterConfiguration', {})
            return cc.get('apiServer', {})
        return {}

    elif section == 'kubelet':
        result = {}
        # Get kubelet config from initConfiguration and joinConfiguration
        if kubeadm:
            init_conf = kubeadm.get('initConfiguration', {})
            init_kubelet = init_conf.get('nodeRegistration', {}).get('kubeletExtraArgs', {})
            if init_kubelet:
                result['initConfiguration_kubeletExtraArgs'] = init_kubelet

            join_conf = kubeadm.get('joinConfiguration', {})
            join_kubelet = join_conf.get('nodeRegistration', {}).get('kubeletExtraArgs', {})
            if join_kubelet:
                result['joinConfiguration_kubeletExtraArgs'] = join_kubelet

        # Also check worker kubeadmConfigTemplate
        worker_template = spec.get('kubeadmConfigTemplate', {})
        if worker_template:
            wt_join = worker_template.get('joinConfiguration', {})
            wt_kubelet = wt_join.get('nodeRegistration', {}).get('kubeletExtraArgs', {})
            if wt_kubelet:
                result['workerTemplate_kubeletExtraArgs'] = wt_kubelet

        # Look for kubelet drop-in files
        for template_key in ['kubeadmConfigTemplate', 'kubeadmControlPlane']:
            template = spec.get(template_key, {})
            if template_key == 'kubeadmControlPlane':
                template = template.get('kubeadmConfigSpec', {})
            files = template.get('files', [])
            for f in files:
                path = f.get('path', '')
                if 'kubelet' in path:
                    result.setdefault('kubelet_files', []).append({
                        'path': path,
                        'content_preview': (f.get('content', '') or '')[:500]
                    })

        return result

    elif section == 'etcd':
        if kubeadm:
            cc = kubeadm.get('clusterConfiguration', {})
            return cc.get('etcd', {})
        return {}

    elif section == 'controller-manager':
        if kubeadm:
            cc = kubeadm.get('clusterConfiguration', {})
            return cc.get('controllerManager', {})
        return {}

    elif section == 'scheduler':
        if kubeadm:
            cc = kubeadm.get('clusterConfiguration', {})
            return cc.get('scheduler', {})
        return {}

    elif section == 'features':
        return {
            'enabledFeatures': spec.get('enabledFeatures', []),
        }

    return {}


def format_overview(config_name: str, spec: Dict, fmt: str = 'table') -> str:
    """Format componentConfig overview"""
    lines = []

    lines.append(f"ComponentConfig: {config_name}")
    lines.append("=" * 60)

    # Basic info
    lines.append(f"  Name: {spec.get('name', 'N/A')}")
    lines.append(f"  Version: {spec.get('version', 'N/A')}")
    lines.append("")

    # Enabled features
    features = spec.get('enabledFeatures', [])
    if features:
        lines.append("## Enabled Features")
        for f in features:
            lines.append(f"  - {f}")
        lines.append("")

    # Extract kubeadm config
    kubeadm = extract_kubeadm_config(spec)
    if kubeadm:
        cc = kubeadm.get('clusterConfiguration', {})

        # apiServer extraArgs
        apiserver = cc.get('apiServer', {})
        extra_args = apiserver.get('extraArgs', {})
        if extra_args:
            lines.append("## kube-apiserver extraArgs")
            if fmt == 'markdown':
                headers = ['Argument', 'Value']
                rows = [[k, str(v)[:80]] for k, v in sorted(extra_args.items())]
                lines.append(format_markdown_table(headers, rows))
            else:
                headers = ['ARGUMENT', 'VALUE']
                rows = [[k, str(v)[:80]] for k, v in sorted(extra_args.items())]
                lines.append(format_table(headers, rows))
            lines.append("")

        # apiServer extraVolumes
        extra_volumes = apiserver.get('extraVolumes', [])
        if extra_volumes:
            lines.append("## kube-apiserver extraVolumes")
            if fmt == 'markdown':
                headers = ['Name', 'HostPath', 'MountPath']
                rows = [[v.get('name', ''), v.get('hostPath', ''), v.get('mountPath', '')] for v in extra_volumes]
                lines.append(format_markdown_table(headers, rows))
            else:
                headers = ['NAME', 'HOST_PATH', 'MOUNT_PATH']
                rows = [[v.get('name', ''), v.get('hostPath', ''), v.get('mountPath', '')] for v in extra_volumes]
                lines.append(format_table(headers, rows))
            lines.append("")

        # controllerManager
        cm = cc.get('controllerManager', {})
        cm_args = cm.get('extraArgs', {})
        if cm_args:
            lines.append("## controller-manager extraArgs")
            if fmt == 'markdown':
                headers = ['Argument', 'Value']
                rows = [[k, str(v)[:80]] for k, v in sorted(cm_args.items())]
                lines.append(format_markdown_table(headers, rows))
            else:
                headers = ['ARGUMENT', 'VALUE']
                rows = [[k, str(v)[:80]] for k, v in sorted(cm_args.items())]
                lines.append(format_table(headers, rows))
            lines.append("")

        # scheduler
        sched = cc.get('scheduler', {})
        sched_args = sched.get('extraArgs', {})
        if sched_args:
            lines.append("## scheduler extraArgs")
            if fmt == 'markdown':
                headers = ['Argument', 'Value']
                rows = [[k, str(v)[:80]] for k, v in sorted(sched_args.items())]
                lines.append(format_markdown_table(headers, rows))
            else:
                headers = ['ARGUMENT', 'VALUE']
                rows = [[k, str(v)[:80]] for k, v in sorted(sched_args.items())]
                lines.append(format_table(headers, rows))
            lines.append("")

        # kubelet extraArgs (init)
        init_conf = kubeadm.get('initConfiguration', {})
        init_kubelet = init_conf.get('nodeRegistration', {}).get('kubeletExtraArgs', {})
        if init_kubelet:
            lines.append("## kubelet extraArgs (initConfiguration)")
            if fmt == 'markdown':
                headers = ['Argument', 'Value']
                rows = [[k, str(v)[:80]] for k, v in sorted(init_kubelet.items())]
                lines.append(format_markdown_table(headers, rows))
            else:
                headers = ['ARGUMENT', 'VALUE']
                rows = [[k, str(v)[:80]] for k, v in sorted(init_kubelet.items())]
                lines.append(format_table(headers, rows))
            lines.append("")

        # networking
        net = cc.get('networking', {})
        if net:
            lines.append("## Networking")
            for k, v in net.items():
                lines.append(f"  {k}: {v}")
            lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Show componentConfig details for a CaaS product'
    )
    parser.add_argument(
        'product',
        nargs='?',
        help='Product name (e.g., baremetal-cluster-ubuntu24-32.7.5)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available componentConfig files'
    )
    parser.add_argument(
        '--section',
        choices=['apiserver', 'kubelet', 'etcd', 'controller-manager', 'scheduler', 'features'],
        help='Show only a specific section'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Show raw YAML content of the componentConfig'
    )
    parser.add_argument(
        '--ref',
        default='master',
        help='Git branch/tag/commit (default: master)'
    )
    parser.add_argument(
        '--format',
        choices=['table', 'json', 'markdown'],
        default='table',
        help='Output format (default: table)'
    )

    args = parser.parse_args()

    client = CaaSBundlesClient(ref=args.ref)

    if args.list:
        configs = list_componentconfigs(client)
        if not configs:
            print("No componentConfig files found", file=sys.stderr)
            sys.exit(1)
        if args.format == 'json':
            print(format_json(configs))
        else:
            headers = ['NAME', 'PATH'] if args.format != 'markdown' else ['Name', 'Path']
            rows = [[c['name'], c['path']] for c in configs]
            if args.format == 'markdown':
                print(format_markdown_table(headers, rows))
            else:
                print(format_table(headers, rows))
        return

    if not args.product:
        parser.error("product name is required (or use --list)")

    config_name, config = get_componentconfig(client, args.product)
    if not config:
        sys.exit(1)

    spec = config.get('spec', {})

    if args.raw:
        import yaml
        content = client._get_file_content(f"componentconfig/{config_name}.yaml")
        if content:
            print(content)
        return

    if args.format == 'json':
        if args.section:
            print(format_json(extract_section(spec, args.section)))
        else:
            print(format_json(config))
        return

    if args.section:
        section_data = extract_section(spec, args.section)
        if not section_data:
            print(f"No data found for section '{args.section}'", file=sys.stderr)
            sys.exit(1)
        print(format_json(section_data))
        return

    print(format_overview(config_name, spec, args.format))


if __name__ == '__main__':
    main()
