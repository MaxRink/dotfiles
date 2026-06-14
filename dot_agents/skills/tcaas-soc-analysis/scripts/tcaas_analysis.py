#!/usr/bin/env python3
import argparse
import csv
import base64
import ipaddress
import json
import os
import re
import shlex
import socket
import subprocess
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from urllib.parse import quote
from urllib.parse import unquote, urlparse

import requests
import websocket


SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "vendor",
    "bin",
    "out",
    ".terraform",
}

TEXT_SUFFIXES = {
    ".adoc",
    ".conf",
    ".csv",
    ".go",
    ".hcl",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".tmpl",
    ".tpl",
    ".txt",
    ".yaml",
    ".yml",
}

SENSITIVE_PATH_RE = re.compile(
    r"(secret|sops|kubeconfig|token|credential|password|private|agekey|ssh[-_]?key|\\.pem|\\.key)",
    re.IGNORECASE,
)

CATEGORIES = {
    "gitops": [
        "flux",
        "GitRepository",
        "Kustomization",
        "HelmRelease",
        "ImageRepository",
        "ImagePolicy",
        "FunctionDefinition",
        "FunctionInstance",
    ],
    "cluster_lifecycle": [
        "Cluster API",
        "cluster-api",
        "KubeadmControlPlane",
        "MachineDeployment",
        "TCaasCluster",
        "upgrade",
        "version",
    ],
    "baremetal_redfish": [
        "Redfish",
        "bm4x",
        "BareMetalHost",
        "ironic",
        "BMC",
        "preprovisioning",
    ],
    "identity_rbac": [
        "RBAC",
        "RoleBinding",
        "ClusterRole",
        "ServiceAccount",
        "IDPProvider",
        "IdentityProvider",
        "Keycloak",
        "breakglass",
        "OIDC",
    ],
    "secrets_certificates": [
        "SOPS",
        "age",
        "Secret",
        "cert-manager",
        "Certificate",
        "Issuer",
        "ClusterIssuer",
        "TLS",
        "Vault",
    ],
    "networking": [
        "Calico",
        "CNI",
        "Multus",
        "SR-IOV",
        "MetalLB",
        "kube-vip",
        "ingress",
        "NetworkPolicy",
        "CoreDNS",
        "DNS",
        "IPAM",
        "VLAN",
    ],
    "observability_logging": [
        "Prometheus",
        "Grafana",
        "Alertmanager",
        "Fluent Bit",
        "fluent-bit",
        "logging",
        "metrics",
        "ServiceMonitor",
        "Zabbix",
        "OpenNMS",
    ],
    "backup_restore": [
        "Velero",
        "backup",
        "restore",
        "snapshot",
        "VolumeSnapshot",
    ],
    "policy_compliance": [
        "Kyverno",
        "OPA",
        "Mondoo",
        "policy",
        "compliance",
        "PSA",
        "security",
    ],
    "tenant_isolation": [
        "TCaasTenant",
        "tenant",
        "Namespace",
        "ResourceQuota",
        "NetworkPolicy",
        "Mandant",
    ],
    "cicd_supply_chain": [
        "GitLab CI",
        ".gitlab-ci",
        "Renovate",
        "registry",
        "Artifactory",
        "image",
        "SBOM",
        "pipeline",
    ],
    "storage": [
        "CSI",
        "Cinder",
        "Ceph",
        "NetApp",
        "vSphere CSI",
        "StorageClass",
        "storage",
    ],
    "dtt_tdg": [
        "DTT",
        "DT Technik",
        "TDG",
        "tmdc",
        "t-caas-mgmt",
    ],
}

SOC_TOPIC_HINTS = {
    "GCP": ["gcp", "google cloud"],
    "GKE": ["gke", "kubernetes"],
    "IAM": ["iam", "rbac", "authent", "identity", "account"],
    "CICD": ["pipeline", "repository", "deployment", "artifact", "image"],
    "Container": ["container", "image", "kubernetes", "pod"],
    "Orchestrator": ["orchestrator", "kubernetes", "cluster"],
    "Netze": ["network", "netz", "firewall", "vlan", "dns", "ip-adresse"],
    "Logging": ["log", "monitor", "siem", "incident", "audit"],
    "Backup": ["backup", "restore", "snapshot"],
    "Datenschutz": ["personenbezogen", "datenschutz", "lösch", "privacy"],
    "Krypto": ["tls", "certificate", "zertifikat", "verschlüssel", "key"],
}

ALLOWED_EVIDENCE_URL_PREFIXES = (
    "https://gitlab.devops.telekom.de/",
    "https://github.com/",
    "https://wiki.telekom.de/",
)

VETTED_GIT_EVIDENCE_PREFIXES = (
    "https://gitlab.devops.telekom.de/",
    "https://github.com/",
)

SENSITIVE_VALUE_KEY_RE = re.compile(
    r"(token|password|secret|credential|authorization|certificate|private|client[-_]?key|"
    r"kubeconfig|cookie|tenanttoken|ssh|tls|ca\.crt|key$)",
    re.IGNORECASE,
)

ADDRESS_VALUE_KEY_RE = re.compile(
    r"(^|_)(ip|ips|address|addresses)(_|$)|podIP|hostIP|externalIP|loadBalancerIP",
    re.IGNORECASE,
)

NETWORK_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
NETWORK_IPV6_RE = re.compile(r"(?<![0-9A-Za-z])(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F]{0,4}(?:/\d{1,3})?(?![0-9A-Za-z])")
NETWORK_MAC_RE = re.compile(r"\b[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\b")

MONDOO_CATEGORY_RULES = {
    "kubernetes_namespace": ["default namespace"],
    "kubernetes_network_exposure": ["hostnetwork", "hostnetwork", "host port", "hostpid", "hostipc", "hostaliases"],
    "container_privilege": [
        "privileged",
        "privilege escalation",
        "run as root",
        "not run as root",
        "sys_admin",
        "net_raw",
        "capability",
    ],
    "container_filesystem": ["immutable root filesystem", "docker socket", "cri-o socket", "containerd socket", "host path"],
    "secret_handling": ["secret", "unencrypted secrets"],
    "resource_management": ["memory", "cpu", "readinessprobe", "livenessprobe"],
    "identity_rbac": ["service account", "duplicate user", "duplicate uid", "duplicate group", "duplicate gid", "system accounts"],
    "os_baseline": ["/etc/shadow", "/etc/passwd", "/etc/group", "x window"],
    "vulnerability_management": ["cve", "advisory", "package"],
}

SOC_CATEGORY_HINTS = {
    "kubernetes_namespace": ["namespace", "mandant", "tenant", "kubernetes", "orchestrator", "private cloud"],
    "kubernetes_network_exposure": ["network", "netz", "port", "firewall", "router", "switch", "kubernetes", "server"],
    "container_privilege": ["container", "pod", "privileg", "root", "capability", "server", "kubernetes", "orchestrator"],
    "container_filesystem": ["container", "filesystem", "dateisystem", "socket", "mount", "server"],
    "secret_handling": ["secret", "password", "credential", "key", "krypto", "verschluessel", "verschlüssel"],
    "resource_management": ["resource", "capacity", "cpu", "memory", "server"],
    "identity_rbac": ["iam", "identity", "authent", "authorization", "berechtig", "account", "user", "rolle"],
    "os_baseline": ["server", "hardening", "patch", "betriebssystem", "linux", "ubuntu"],
    "vulnerability_management": ["vulnerab", "cve", "patch", "schwachstelle", "update"],
}

KUBECTL_COLLECTIONS = [
    ("version", ["version", "--output=json"], False),
    ("nodes", ["get", "nodes", "-o", "json"], True),
    ("namespaces", ["get", "namespaces", "-o", "json"], True),
    ("pods_all", ["get", "pods", "-A", "-o", "json"], True),
    ("workloads_all", ["get", "deployments,daemonsets,statefulsets", "-A", "-o", "json"], False),
    ("services_all", ["get", "services", "-A", "-o", "json"], False),
    ("ingress_all", ["get", "ingress", "-A", "-o", "json"], False),
    ("networkpolicies_all", ["get", "networkpolicies", "-A", "-o", "json"], False),
    ("serviceaccounts_all", ["get", "serviceaccounts", "-A", "-o", "json"], False),
    ("roles_all", ["get", "roles,rolebindings", "-A", "-o", "json"], False),
    ("clusterroles", ["get", "clusterroles,clusterrolebindings", "-o", "json"], False),
    ("storageclasses", ["get", "storageclasses", "-o", "json"], False),
    ("persistentvolumes", ["get", "persistentvolumes", "-o", "json"], False),
    ("persistentvolumeclaims_all", ["get", "persistentvolumeclaims", "-A", "-o", "json"], False),
    ("crds", ["get", "crds", "-o", "json"], False),
    ("flux_sources", ["get", "gitrepositories,kustomizations,helmreleases", "-A", "-o", "json"], False),
    ("tcaas_clusters", ["get", "tcaasclusters", "-A", "-o", "json"], False),
]

RAW_COLLECTION_DIRNAME = "raw-collections"

NODE_SHELL_COMMANDS = [
    ("hostnamectl", "hostnamectl"),
    ("os_release", "cat /etc/os-release"),
    ("kernel", "uname -a"),
    ("uptime", "uptime -p"),
    ("service_active", "systemctl is-active kubelet containerd chrony ssh 2>/dev/null || true"),
    ("service_enabled", "systemctl is-enabled kubelet containerd chrony ssh 2>/dev/null || true"),
    ("sshd_effective", "sshd -T 2>/dev/null || /usr/sbin/sshd -T 2>/dev/null"),
    (
        "sshd_config",
        "grep -Rhv '^[[:space:]]*#' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null | sed '/^[[:space:]]*$/d'",
    ),
    ("kubelet_version", "kubelet --version"),
    ("kubelet_config", "sudo -n sed -n '1,240p' /var/lib/kubelet/config.yaml"),
    (
        "kubelet_dropins",
        "sudo -n find /etc/systemd/system/kubelet.service.d /etc/kubernetes/kubelet.conf.d -maxdepth 1 -type f -print -exec sed -n '1,220p' {} \\; 2>/dev/null",
    ),
    ("containerd_version", "containerd --version 2>/dev/null || ctr version 2>/dev/null"),
    ("containerd_config", "sudo -n sed -n '1,280p' /etc/containerd/config.toml"),
    ("time_sync", "chronyc tracking 2>/dev/null || timedatectl status"),
    (
        "sysctl_security",
        "sysctl kernel.randomize_va_space kernel.kptr_restrict kernel.dmesg_restrict net.ipv4.ip_forward net.ipv6.conf.all.forwarding net.ipv6.conf.default.forwarding 2>/dev/null",
    ),
    ("mount_security", "findmnt -no TARGET,FSTYPE,OPTIONS / /tmp /var/tmp /dev/shm /boot /boot/efi 2>/dev/null"),
    (
        "file_permissions",
        "sudo -n stat -c '%a %U:%G %n' /etc/passwd /etc/passwd- /etc/group /etc/group- /etc/shadow /etc/shadow- /var/lib/kubelet/config.yaml /etc/kubernetes/manifests/kube-apiserver.yaml /etc/kubernetes/manifests/etcd.yaml 2>/dev/null",
    ),
    (
        "kubernetes_security_flags",
        "sudo -n grep -HnE -- '--anonymous-auth|--authorization-mode|--encryption-provider-config|--client-ca-file|--tls-cert-file|--tls-private-key-file|--audit|--profiling|--insecure|--secure-port|--read-only-port|--protect-kernel-defaults|rotateCertificates|authentication:|authorization:|tlsCipherSuites' /etc/kubernetes/manifests/*.yaml /var/lib/kubelet/config.yaml 2>/dev/null",
    ),
    ("module_blacklist", "grep -Rhv '^[[:space:]]*#' /etc/modprobe.d 2>/dev/null | sed '/^[[:space:]]*$/d'"),
    ("uid0_accounts", "awk -F: '$3 == 0 {print $1\":\"$3\":\"$4\":\"$7}' /etc/passwd"),
    ("listening_sockets", "sudo -n ss -tulpen 2>/dev/null"),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def rel(path):
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def run_git(root, *args):
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def git_command_ok(root, *args):
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return completed.returncode == 0
    except Exception:
        return False


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        current = Path(dirpath)
        for filename in filenames:
            path = current / filename
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            yield path


def is_text_candidate(path):
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in {"Dockerfile", "Makefile", "Taskfile", "AGENTS.md", "README"}


def safe_excerpt(line):
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"(?i)(password|token|secret|credential|private[_-]?key)\s*[:=]\s*\\S+", r"\\1=<redacted>", line)
    return line[:300]


def inventory_roots(roots):
    result = {"generatedAt": now(), "roots": []}
    for root_arg in roots:
        root = Path(root_arg)
        files = list(iter_files(root)) if root.exists() else []
        suffixes = Counter(path.suffix.lower() or path.name for path in files)
        top_dirs = Counter(path.relative_to(root).parts[0] for path in files if len(path.relative_to(root).parts) > 1)
        git_root = run_git(root, "rev-parse", "--show-toplevel")
        result["roots"].append(
            {
                "root": str(root),
                "exists": root.exists(),
                "gitRoot": git_root,
                "gitBranch": run_git(root, "branch", "--show-current") if git_root else "",
                "gitHead": run_git(root, "rev-parse", "--short", "HEAD") if git_root else "",
                "fileCount": len(files),
                "textCandidateCount": sum(1 for path in files if is_text_candidate(path)),
                "topExtensions": suffixes.most_common(30),
                "topDirectories": top_dirs.most_common(40),
            }
        )
    return result


def write_inventory(result, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "repo_inventory.json"
    md_path = out / "repo_inventory.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Repository Inventory", "", f"Generated: `{result['generatedAt']}`", ""]
    for root in result["roots"]:
        lines.extend(
            [
                f"## {root['root']}",
                "",
                f"- Exists: {root['exists']}",
                f"- Git root: `{root['gitRoot'] or 'n/a'}`",
                f"- Git branch: `{root['gitBranch'] or 'n/a'}`",
                f"- Git head: `{root['gitHead'] or 'n/a'}`",
                f"- Files: {root['fileCount']}",
                f"- Text candidates: {root['textCandidateCount']}",
                "",
                "Top directories:",
            ]
        )
        lines.extend(f"- {name}: {count}" for name, count in root["topDirectories"][:20])
        lines.extend(["", "Top extensions:"])
        lines.extend(f"- `{name}`: {count}" for name, count in root["topExtensions"][:20])
        lines.append("")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def scan_file(path):
    sensitive = bool(SENSITIVE_PATH_RE.search(str(path)))
    if not is_text_candidate(path):
        return []
    try:
        if path.stat().st_size > 1_000_000:
            return []
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        haystack = line.casefold()
        for category, needles in CATEGORIES.items():
            if any(needle.casefold() in haystack for needle in needles):
                findings.append(
                    {
                        "category": category,
                        "path": str(path),
                        "line": line_no,
                        "sensitivePath": sensitive,
                        "excerpt": "<sensitive path; content not copied>" if sensitive else safe_excerpt(line),
                    }
                )
    return findings


def scan_evidence(roots):
    records = []
    for root in roots:
        for path in iter_files(root):
            records.extend(scan_file(path))
    by_category = defaultdict(list)
    for record in records:
        by_category[record["category"]].append(record)
    return {"generatedAt": now(), "records": records, "byCategory": by_category}


def write_evidence(scan, out_dir, write_full_records=False, sample_limit=2000):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    records_path = out / "evidence_records.jsonl"
    sample_records_path = out / "evidence_records.sample.jsonl"
    sample_records = scan["records"][:sample_limit]
    index = {
        "generatedAt": scan["generatedAt"],
        "categoryCounts": {category: len(items) for category, items in sorted(scan["byCategory"].items())},
        "recordCount": len(scan["records"]),
        "recordsPath": str(records_path) if write_full_records else "",
        "sampleRecordsPath": str(sample_records_path),
        "sampleRecordCount": len(sample_records),
        "fullRecordsOmitted": not write_full_records,
        "categories": {},
    }
    if write_full_records:
        with records_path.open("w", encoding="utf-8") as handle:
            for record in scan["records"]:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    with sample_records_path.open("w", encoding="utf-8") as handle:
        for record in sample_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    lines = ["# Evidence Index", "", f"Generated: `{scan['generatedAt']}`", ""]
    lines.extend(
        [
            f"- Records scanned: {len(scan['records'])}",
            f"- Sample records: `{sample_records_path}`",
            f"- Full records written: `{write_full_records}`",
            "",
        ]
    )
    for category, items in sorted(scan["byCategory"].items()):
        sample = items[:30]
        index["categories"][category] = sample
        lines.extend([f"## {category}", "", f"Matches: {len(items)}", ""])
        for item in sample:
            lines.append(f"- `{item['path']}:{item['line']}`: {item['excerpt']}")
        lines.append("")
    index_path = out / "evidence_index.json"
    md_path = out / "evidence_index.md"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    result = {"index": str(index_path), "sampleRecords": str(sample_records_path), "markdown": str(md_path)}
    if write_full_records:
        result["records"] = str(records_path)
    return result


def load_evidence_index(path):
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def infer_topics(answer):
    sheet = answer.get("sheet", {}).get("title", "")
    req = answer.get("requirement", {})
    text = " ".join([sheet, req.get("text", ""), req.get("details", ""), req.get("motivation", "")]).casefold()
    topics = []
    for topic, needles in SOC_TOPIC_HINTS.items():
        if topic.casefold() in sheet.casefold() or any(needle.casefold() in text for needle in needles):
            topics.append(topic)
    return topics or ["general"]


def evidence_for_topics(evidence_index, topics):
    if not evidence_index:
        return []
    categories = evidence_index.get("categories", {})
    mapping = {
        "GKE": ["cluster_lifecycle", "gitops", "policy_compliance"],
        "IAM": ["identity_rbac", "tenant_isolation"],
        "CICD": ["cicd_supply_chain", "gitops"],
        "Container": ["cicd_supply_chain", "policy_compliance", "cluster_lifecycle"],
        "Orchestrator": ["cluster_lifecycle", "gitops"],
        "Netze": ["networking", "tenant_isolation"],
        "Logging": ["observability_logging"],
        "Backup": ["backup_restore", "storage"],
        "Datenschutz": ["tenant_isolation", "policy_compliance"],
        "Krypto": ["secrets_certificates"],
        "GCP": ["dtt_tdg"],
    }
    picked = []
    for topic in topics:
        for category in mapping.get(topic, []):
            picked.extend(categories.get(category, [])[:5])
    dedup = []
    seen = set()
    for item in picked:
        key = (item.get("path"), item.get("line"), item.get("category"))
        if key not in seen:
            dedup.append(item)
            seen.add(key)
    return dedup[:20]


def build_soc_workbook(answers_path, evidence_path=None):
    answers = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    evidence_index = load_evidence_index(evidence_path)
    rows = []
    for item in answers.get("answers", []):
        topics = infer_topics(item)
        evidence = evidence_for_topics(evidence_index, topics)
        current = item.get("current", {})
        answer = item.get("answer", {})
        row = {
            "answerKey": item.get("answerKey"),
            "sheet": item.get("sheet", {}).get("title", ""),
            "manifestName": item.get("sheet", {}).get("manifestName", ""),
            "number": item.get("requirement", {}).get("number", ""),
            "requirementId": item.get("requirement", {}).get("requirementId", ""),
            "topics": topics,
            "currentStatement": current.get("statement", ""),
            "draftStatement": answer.get("statement", ""),
            "draftExplanation": answer.get("explanation", ""),
            "researchStatus": "has_current_answer" if answer.get("statement") else "research_needed",
            "suggestedEvidence": evidence,
            "requirementText": item.get("requirement", {}).get("text", ""),
            "requirementDetails": item.get("requirement", {}).get("details", ""),
            "motivation": item.get("requirement", {}).get("motivation", ""),
        }
        rows.append(row)
    return {"generatedAt": now(), "source": str(answers_path), "rows": rows}


def normalize_title(value):
    value = (value or "").casefold()
    value = (
        value.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().casefold()
    return value


def load_sheet_plan(path):
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    by_title = {}
    for sheet in plan.get("sheets", []):
        by_title[normalize_title(sheet.get("sheet", ""))] = sheet
    return plan, by_title


def scope_explanation(sheet, disposition):
    title = sheet.get("sheet", "")
    if disposition == "likely_na":
        if "Machine Learning" in title:
            return (
                "Not applicable for the documented T-CaaS Core runtime scope because the platform provides "
                "managed Kubernetes/CaaS capabilities and does not itself train, validate, test, or operate "
                "machine-learning models for tenant workloads."
            )
        return (
            "Not applicable for the documented T-CaaS Core runtime scope because the platform provides "
            "managed Kubernetes/CaaS capabilities and is not itself an AI system for tenant workloads."
        )
    if disposition == "dtt_specific":
        return (
            "Not applicable for T-CaaS Core. This requirement is specific to DT Technik operation; "
            "this Core answer only records a scope exclusion and does not attest that the control is "
            "fulfilled there. DTT currently has no separate SoC rows to answer. Row-specific production, "
            "reference, and DT-Technik deployment evidence must be maintained when PSA exposes DTT SoCs."
        )
    if disposition == "likely_na_mixed":
        return (
            "Likely not applicable for T-CaaS Core where the requirement concerns physical infrastructure "
            "or provider operation. T-CaaS Core documents the Kubernetes/CaaS platform; the responsible "
            "operator must be confirmed per requirement."
        )
    return ""


def seed_scope_drafts(answers_path, plan_path, out_path, include_mixed=False):
    answers = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    _, sheets = load_sheet_plan(plan_path)
    seeded = 0
    for item in answers.get("answers", []):
        title = item.get("sheet", {}).get("title", "")
        sheet = sheets.get(normalize_title(title))
        if not sheet:
            continue
        disposition = sheet.get("disposition", "")
        if disposition not in {"likely_na", "dtt_specific"} and not (include_mixed and disposition == "likely_na_mixed"):
            continue
        answer = item.setdefault("answer", {})
        if answer.get("statement"):
            continue
        explanation = scope_explanation(sheet, disposition)
        if not explanation:
            continue
        if disposition == "dtt_specific":
            requirement = item.get("requirement", {}) or {}
            req_number = str(requirement.get("number") or "").strip()
            if req_number:
                explanation = (
                    f"Not applicable for T-CaaS Core for DT Technik operational requirement {req_number}. "
                    "This requirement is specific to DT Technik operation. This Core answer only records "
                    "a scope exclusion and does not attest that the control is fulfilled there. DTT currently "
                    "has no separate SoC rows to answer. Row-specific production, reference, and DT-Technik "
                    "deployment evidence must be maintained when PSA exposes DTT SoCs."
                )
        answer["statement"] = "NA"
        answer["explanation"] = explanation
        answer["status"] = "ready_for_review" if disposition in {"likely_na", "dtt_specific"} else "draft"
        evidence = answer.setdefault("evidence", [])
        for source in sheet.get("primaryEvidence", []):
            if source not in evidence:
                evidence.append(source)
        answer["owner"] = answer.get("owner") or "manual-review"
        seeded += 1
    answers.setdefault("analysis", {})
    answers["analysis"]["scopeDraftSeed"] = {
        "generatedAt": now(),
        "sheetPlan": str(plan_path),
        "includeMixed": include_mixed,
        "seededAnswers": seeded,
        "note": "Scope-based draft only. Review before portal filling.",
    }
    Path(out_path).write_text(json.dumps(answers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"out": str(out_path), "seededAnswers": seeded}


def deep_merge(target, patch):
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def apply_answer_batch(answers_path, batch_path, out_path):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    batch = json.loads(Path(batch_path).read_text(encoding="utf-8"))
    by_key = {item.get("answerKey"): item for item in payload.get("answers", [])}
    applied = []
    missing = []
    for entry in batch.get("answers", []):
        key = entry.get("answerKey", "")
        item = by_key.get(key)
        if not item:
            missing.append(key)
            continue
        updates = entry.get("set", {})
        if "answer" in updates:
            deep_merge(item.setdefault("answer", {}), updates["answer"])
        for top_level in ("requirement", "analysis"):
            if top_level in updates:
                deep_merge(item.setdefault(top_level, {}), updates[top_level])
        applied.append(key)

    payload.setdefault("analysis", {}).setdefault("answerBatches", []).append(
        {
            "batchId": batch.get("batchId") or Path(batch_path).stem,
            "source": str(batch_path),
            "appliedAt": now(),
            "appliedAnswers": len(applied),
            "missingAnswers": missing,
        }
    )
    Path(out_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"out": str(out_path), "appliedAnswers": len(applied), "missingAnswers": missing}


def resolve_manifest_path(manifest_path, value):
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return Path(manifest_path).parent / path


def rebuild_answer_draft(manifest_path, out_path=None):
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    output = Path(out_path or manifest.get("out") or "analysis/soc-answers/tcaas-core_scope_draft_answers.json")
    if not output.is_absolute():
        output = Path.cwd() / output
    output.parent.mkdir(parents=True, exist_ok=True)

    template = resolve_manifest_path(manifest_file, manifest["template"])
    sheet_plan = resolve_manifest_path(manifest_file, manifest["sheetPlan"])
    seed_result = seed_scope_drafts(
        answers_path=template,
        plan_path=sheet_plan,
        out_path=output,
        include_mixed=bool(manifest.get("includeMixed", False)),
    )

    batch_results = []
    for batch_ref in manifest.get("batches", []):
        batch_path = resolve_manifest_path(manifest_file, batch_ref)
        result = apply_answer_batch(output, batch_path, output)
        batch_results.append({"batch": str(batch_path), **result})

    note_result = None
    if manifest.get("syncNotes", True):
        note_result = sync_answer_notes(output, output)

    total_missing = [missing for result in batch_results for missing in result.get("missingAnswers", [])]
    return {
        "out": str(output),
        "manifest": str(manifest_file),
        "seededAnswers": seed_result.get("seededAnswers", 0),
        "appliedBatches": len(batch_results),
        "appliedAnswers": sum(result.get("appliedAnswers", 0) for result in batch_results),
        "missingAnswers": total_missing,
        "notesSynced": None if note_result is None else note_result.get("updatedAnswers", 0),
    }


def append_markdown_field(lines, title, value, empty="[empty]"):
    lines.extend([f"**{title}**", ""])
    text = str(value or "").strip()
    if not text:
        lines.append(empty)
    else:
        lines.extend(line.rstrip() for line in text.splitlines())
    lines.append("")


def export_answer_markdown(answers_path, out_path):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    answers = payload.get("answers", [])
    by_sheet = defaultdict(list)
    sheet_order = []
    for item in answers:
        sheet = item.get("sheet", {}) or {}
        sheet_key = (
            sheet.get("sheetId", ""),
            sheet.get("manifestName", ""),
            sheet.get("title", ""),
        )
        if sheet_key not in by_sheet:
            sheet_order.append(sheet_key)
        by_sheet[sheet_key].append(item)

    statement_counts = Counter(str((item.get("answer", {}) or {}).get("statement") or "<blank>") for item in answers)
    fillable_count = sum(1 for item in answers if str((item.get("answer", {}) or {}).get("statement") or "").strip())
    lines = [
        "# tcaas-core PSA Answers",
        "",
        f"- Schema: `{payload.get('schema', '')}`",
        f"- Generated: `{now()}`",
        f"- Source: `{answers_path}`",
        f"- System ID: `{(payload.get('system', {}) or {}).get('id', '')}`",
        f"- Answers: {len(answers)}",
        f"- Fillable answers now: {fillable_count}",
        "",
        "## Statement Counts",
        "",
    ]
    lines.extend(f"- `{statement}`: {count}" for statement, count in sorted(statement_counts.items()))
    lines.extend(
        [
            "",
            "## Format",
            "",
            "Edit `answer.statement` to one of `SOC`, `SOPC`, `SONC`, or `NA`.",
            "For `SOPC`, `SONC`, and `NA`, fill `answer.explanation`; this is the portal `Begruendung` value.",
            "`answer.note` maps to `Meine Notiz`; notes are working notes and include the reviewed reference URLs.",
            "",
            "## Sheets",
            "",
        ]
    )

    for sheet_id, manifest_name, title in sheet_order:
        rows = by_sheet[(sheet_id, manifest_name, title)]
        sheet_counts = Counter(str((item.get("answer", {}) or {}).get("statement") or "<blank>") for item in rows)
        lines.extend(
            [
                f"### {manifest_name} {title}".strip(),
                "",
                f"- Sheet ID: `{sheet_id}`",
                f"- Requirements: {len(rows)}",
                f"- Fillable answers now: {sum(1 for item in rows if str((item.get('answer', {}) or {}).get('statement') or '').strip())}",
                f"- Statement counts: {', '.join(f'{key}={value}' for key, value in sorted(sheet_counts.items()))}",
                "",
            ]
        )
        for item in rows:
            requirement = item.get("requirement", {}) or {}
            answer = item.get("answer", {}) or {}
            current = item.get("current", {}) or {}
            lines.extend(
                [
                    f"#### Requirement {requirement.get('number', '')}",
                    "",
                    f"- Answer key: `{item.get('answerKey', '')}`",
                    f"- Requirement ID: `{requirement.get('requirementId', '')}`",
                    f"- Export ID: `{requirement.get('exportId', '')}`",
                    f"- Current portal statement: `{current.get('statement', '') or '[empty]'}`",
                    f"- Statement: `{answer.get('statement', '') or '[empty]'}`",
                    f"- Status: `{answer.get('status', '') or '[empty]'}`",
                    f"- Owner: `{answer.get('owner', '') or '[empty]'}`",
                    "",
                ]
            )
            append_markdown_field(lines, "Requirement", requirement.get("text", ""))
            append_markdown_field(lines, "Details", requirement.get("details", ""))
            append_markdown_field(lines, "Motivation", requirement.get("motivation", ""))
            append_markdown_field(lines, "Answer Explanation", answer.get("explanation", ""))
            append_markdown_field(lines, "Portal Note", answer.get("note", ""))
            evidence = [str(ref).strip() for ref in answer.get("evidence", []) if str(ref).strip()]
            lines.extend(["**Evidence**", ""])
            if evidence:
                lines.extend(f"- {ref}" for ref in evidence)
            else:
                lines.append("[empty]")
            lines.append("")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"out": str(out), "answerCount": len(answers), "fillableAnswers": fillable_count}


def build_reference_note(evidence):
    refs = [str(ref).strip() for ref in evidence or [] if str(ref).strip()]
    if not refs:
        return ""
    lines = ["References for review:"]
    lines.extend(f"- {ref}" for ref in refs)
    return "\n".join(lines)


def sync_answer_notes(answers_path, out_path, only_empty=False):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    updated = 0
    skipped = 0
    for item in payload.get("answers", []):
        answer = item.setdefault("answer", {})
        evidence = [str(ref).strip() for ref in answer.get("evidence", []) if str(ref).strip()]
        if not evidence:
            skipped += 1
            continue
        reference_note = build_reference_note(evidence)
        existing = str(answer.get("note") or "").strip()
        if only_empty and existing:
            skipped += 1
            continue
        missing = [ref for ref in evidence if ref not in existing]
        if existing and not missing:
            skipped += 1
            continue
        answer["note"] = f"{existing}\n\n{reference_note}".strip() if existing else reference_note
        answer["noteVisibleForOthers"] = bool(answer.get("noteVisibleForOthers", False))
        updated += 1
    payload.setdefault("analysis", {}).setdefault("noteSyncs", []).append(
        {
            "syncedAt": now(),
            "source": str(answers_path),
            "updatedAnswers": updated,
            "skippedAnswers": skipped,
            "onlyEmpty": only_empty,
            "note": "Copied answer.evidence references into answer.note for PSA portal review.",
        }
    )
    Path(out_path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"out": str(out_path), "updatedAnswers": updated, "skippedAnswers": skipped}


def compact_answer_item(item):
    sheet = item.get("sheet", {}) or {}
    requirement = item.get("requirement", {}) or {}
    compact = {
        "answerKey": item.get("answerKey", ""),
        "sheet": {
            key: sheet.get(key, "")
            for key in ("title", "manifestName", "sheetId", "href")
            if sheet.get(key, "") != ""
        },
        "requirement": {
            key: requirement.get(key, "")
            for key in ("number", "requirementId", "exportId")
            if requirement.get(key, "") != ""
        },
        "answer": item.get("answer", {}) or {},
    }
    return compact


def export_fillable_answers(answers_path, out_path, include_empty=False):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    compact_answers = []
    skipped = 0
    for item in payload.get("answers", []):
        statement = str((item.get("answer", {}) or {}).get("statement", "")).strip()
        if not include_empty and not statement:
            skipped += 1
            continue
        compact_answers.append(compact_answer_item(item))

    compact_payload = {
        "schema": payload.get("schema", "psa_answers_v1"),
        "generatedAt": now(),
        "system": payload.get("system", {}),
        "allowedStatements": payload.get("allowedStatements", []),
        "fillBehavior": payload.get("fillBehavior", {}),
        "analysis": {
            "sourceFile": Path(answers_path).name,
            "format": "fillable_compact_answers_v1",
            "includeEmpty": include_empty,
            "omittedFields": [
                "requirement.text",
                "requirement.details",
                "requirement.motivation",
                "current",
                "portalFields",
                "sources",
            ],
        },
        "answers": compact_answers,
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(compact_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "out": str(out),
        "answerCount": len(compact_answers),
        "skippedAnswers": skipped,
        "bytes": out.stat().st_size,
    }


def short_text(value, limit=220):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def coverage_review_state(item):
    answer = item.get("answer", {}) or {}
    statement = str(answer.get("statement") or "").strip()
    if not statement:
        return "unanswered"
    if statement == "NA":
        return "answered_not_applicable"
    return "answered_applicable"


def build_coverage_ledger(answers_path, sheet_plan_path=None, out_dir=None):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    plan_by_title = {}
    if sheet_plan_path:
        _, plan_by_title = load_sheet_plan(sheet_plan_path)

    rows = []
    sheet_summary = {}
    statement_counts = Counter()
    topic_counts = Counter()

    for item in payload.get("answers", []):
        sheet = item.get("sheet", {}) or {}
        req = item.get("requirement", {}) or {}
        answer = item.get("answer", {}) or {}
        title = sheet.get("title", "")
        statement = str(answer.get("statement") or "").strip()
        topics = infer_topics(item)
        plan = plan_by_title.get(normalize_title(title), {})
        review_state = coverage_review_state(item)
        evidence = [str(ref).strip() for ref in answer.get("evidence", []) if str(ref).strip()]
        row = {
            "answerKey": item.get("answerKey", ""),
            "sheet": title,
            "manifestName": sheet.get("manifestName", ""),
            "sheetId": sheet.get("sheetId", ""),
            "requirementNumber": req.get("number", ""),
            "requirementId": req.get("requirementId", ""),
            "statement": statement,
            "reviewState": review_state,
            "answerStatus": answer.get("status", ""),
            "owner": answer.get("owner", ""),
            "evidenceCount": len(evidence),
            "topics": topics,
            "sheetPlanPriority": plan.get("priority", ""),
            "sheetPlanDisposition": plan.get("disposition", ""),
            "requirementText": req.get("text", ""),
            "requirementDetails": req.get("details", ""),
            "motivation": req.get("motivation", ""),
            "shortRequirementText": short_text(req.get("text", "")),
            "shortExplanation": short_text(answer.get("explanation", "")),
            "needsAnalysis": not bool(statement),
        }
        rows.append(row)
        statement_counts[statement or "<blank>"] += 1
        for topic in topics:
            topic_counts[topic] += 1
        summary = sheet_summary.setdefault(
            title,
            {
                "sheet": title,
                "manifestName": sheet.get("manifestName", ""),
                "sheetId": sheet.get("sheetId", ""),
                "total": 0,
                "answered": 0,
                "applicableAnswered": 0,
                "notApplicable": 0,
                "unanswered": 0,
                "statementCounts": Counter(),
                "priority": plan.get("priority", ""),
                "disposition": plan.get("disposition", ""),
                "topics": Counter(),
            },
        )
        summary["total"] += 1
        summary["statementCounts"][statement or "<blank>"] += 1
        for topic in topics:
            summary["topics"][topic] += 1
        if review_state == "unanswered":
            summary["unanswered"] += 1
        else:
            summary["answered"] += 1
            if review_state == "answered_not_applicable":
                summary["notApplicable"] += 1
            else:
                summary["applicableAnswered"] += 1

    sheet_summaries = []
    for summary in sheet_summary.values():
        summary = dict(summary)
        summary["statementCounts"] = dict(summary["statementCounts"])
        summary["topics"] = dict(summary["topics"])
        summary["answeredPercent"] = round((summary["answered"] / summary["total"]) * 100, 1) if summary["total"] else 0.0
        sheet_summaries.append(summary)
    sheet_summaries.sort(key=lambda item: (-item["unanswered"], item["sheet"]))

    unanswered_rows = [row for row in rows if row["reviewState"] == "unanswered"]
    answered_rows = [row for row in rows if row["reviewState"] != "unanswered"]
    ledger = {
        "schema": "tcaas_soc_coverage_ledger_v1",
        "generatedAt": now(),
        "source": str(answers_path),
        "sheetPlan": str(sheet_plan_path or ""),
        "totals": {
            "rows": len(rows),
            "answered": len(answered_rows),
            "applicableAnswered": sum(1 for row in answered_rows if row["reviewState"] == "answered_applicable"),
            "notApplicable": sum(1 for row in answered_rows if row["reviewState"] == "answered_not_applicable"),
            "unanswered": len(unanswered_rows),
            "statementCounts": dict(statement_counts),
            "topicCounts": dict(topic_counts),
        },
        "sheetSummaries": sheet_summaries,
        "rows": rows,
        "unansweredRows": unanswered_rows,
    }

    out = Path(out_dir or ".")
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "soc_coverage_ledger.json"
    tsv_path = out / "soc_coverage_ledger.tsv"
    md_path = out / "soc_coverage_ledger.md"
    json_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fieldnames = [
        "answerKey",
        "sheet",
        "requirementNumber",
        "requirementId",
        "statement",
        "reviewState",
        "answerStatus",
        "owner",
        "evidenceCount",
        "topics",
        "sheetPlanPriority",
        "sheetPlanDisposition",
        "shortRequirementText",
        "shortExplanation",
        "needsAnalysis",
    ]
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            serializable = dict(row)
            serializable["topics"] = ",".join(row.get("topics", []))
            writer.writerow(serializable)

    lines = [
        "# SoC Coverage Ledger",
        "",
        f"Generated: `{ledger['generatedAt']}`",
        f"Source: `{answers_path}`",
        "",
        "## Totals",
        "",
        f"- Rows: {ledger['totals']['rows']}",
        f"- Answered: {ledger['totals']['answered']}",
        f"- Applicable answered: {ledger['totals']['applicableAnswered']}",
        f"- Not applicable: {ledger['totals']['notApplicable']}",
        f"- Unanswered: {ledger['totals']['unanswered']}",
        f"- Statement counts: `{json.dumps(ledger['totals']['statementCounts'], ensure_ascii=False)}`",
        "",
        "## Sheets By Remaining Work",
        "",
        "| Unanswered | Answered | Total | % Answered | Sheet | Disposition | Priority |",
        "|---:|---:|---:|---:|---|---|---|",
    ]
    for summary in sheet_summaries:
        lines.append(
            "| {unanswered} | {answered} | {total} | {answeredPercent} | {sheet} | {disposition} | {priority} |".format(
                **summary
            )
        )
    lines.extend(["", "## Unanswered Rows", ""])
    if unanswered_rows:
        for row in unanswered_rows:
            lines.append(
                "- `{answerKey}` {sheet} req {requirementNumber} / `{requirementId}`: {shortRequirementText}".format(
                    **row
                )
            )
    else:
        lines.append("- none")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "json": str(json_path),
        "tsv": str(tsv_path),
        "markdown": str(md_path),
        "rows": len(rows),
        "answered": len(answered_rows),
        "unanswered": len(unanswered_rows),
        "sheetCount": len(sheet_summaries),
    }


def git_toplevel_for(path):
    path = Path(path)
    probe = path if path.is_dir() else path.parent
    git_root = run_git(probe, "rev-parse", "--show-toplevel")
    return Path(git_root) if git_root else None


def git_remote_https(remote):
    if not remote:
        return ""
    remote = remote.strip()
    if remote.endswith(".git"):
        remote = remote[:-4]
    match = re.match(r"git@([^:]+):(.+)$", remote)
    if match:
        return f"https://{match.group(1)}/{match.group(2)}"
    if remote.startswith("ssh://git@"):
        parsed = urlparse(remote)
        return f"https://{parsed.hostname}{parsed.path}".removesuffix(".git")
    if remote.startswith("http://") or remote.startswith("https://"):
        return remote
    return remote


def git_blob_link(base_url, commit, rel_path, line_start=None, line_end=None, is_dir=False):
    if not base_url or not commit or not rel_path:
        return ""
    rel_path = str(rel_path).replace("\\", "/").lstrip("/")
    encoded = "/".join(quote(part) for part in rel_path.split("/"))
    sep = "/-/tree/" if "gitlab" in base_url else "/tree/"
    if not is_dir:
        sep = "/-/blob/" if "gitlab" in base_url else "/blob/"
    url = f"{base_url}{sep}{commit}/{encoded}"
    if not is_dir and line_start:
        url += f"#L{line_start}"
        if line_end and line_end != line_start:
            url += f"-{line_end}"
    return url


def git_path_exists_at_ref(git_root, rel_path, is_dir, ref="HEAD"):
    rel_path = str(rel_path).replace("\\", "/")
    if is_dir:
        output = run_git(git_root, "ls-tree", "-d", ref, rel_path)
        return bool(output)
    return git_command_ok(git_root, "cat-file", "-e", f"{ref}:{rel_path}")


def git_path_exists_at_head(git_root, rel_path, is_dir):
    return git_path_exists_at_ref(git_root, rel_path, is_dir, "HEAD")


def line_count(path):
    try:
        with Path(path).open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except Exception:
        return None


def git_blob_line_count(git_root, ref, rel_path):
    try:
        content = run_git(git_root, "show", f"{ref}:{str(rel_path).replace(chr(92), '/')}")
    except RuntimeError:
        return None
    if not content:
        return 0
    return content.count("\n") + (0 if content.endswith("\n") else 1)


def vet_source(source, workspace_root):
    result = dict(source)
    target = source.get("path") or source.get("url") or ""
    result["target"] = target
    result["checkedAt"] = now()
    result["checks"] = []
    if source.get("type") == "confluence_url":
        result["type"] = "confluence_url"
        result["deepLink"] = target
        parsed = urlparse(target)
        wiki_url = parsed.scheme in {"http", "https"} and parsed.netloc == "wiki.telekom.de"
        result["checks"].append("target is wiki.telekom.de URL" if wiki_url else "target is not wiki.telekom.de URL")

        capture_paths = source.get("capturePaths") or []
        if source.get("capturePath"):
            capture_paths = [source["capturePath"], *capture_paths]
        captures = []
        target_seen = False
        for capture_ref in capture_paths:
            capture_path = Path(capture_ref)
            if not capture_path.is_absolute():
                capture_path = Path(workspace_root) / capture_path
            capture_path = capture_path.resolve()
            capture_exists = capture_path.exists()
            capture_info = {"path": str(capture_path), "exists": capture_exists, "containsTarget": False}
            if capture_exists and capture_path.is_file():
                text = capture_path.read_text(encoding="utf-8", errors="ignore")
                capture_info["containsTarget"] = target in text
                target_seen = target_seen or capture_info["containsTarget"]
            captures.append(capture_info)

        result["captures"] = captures
        if captures:
            result["checks"].append("capture file exists" if any(item["exists"] for item in captures) else "capture file missing")
            result["checks"].append("capture contains target URL" if target_seen else "capture does not contain target URL")
        else:
            result["checks"].append("no capture path supplied")
        result["status"] = "vetted" if wiki_url and target_seen else "needs_review"
        return result
    if re.match(r"^https?://", target):
        result["type"] = "url"
        result["status"] = "external_url_unverified"
        result["checks"].append("external URL retained; verify manually or with browser capture")
        return result

    path = Path(target)
    if not path.is_absolute():
        path = Path(workspace_root) / path
    path = path.resolve()
    result["absolutePath"] = str(path)
    exists = path.exists()
    result["exists"] = exists
    result["checks"].append("local path exists" if exists else "local path missing")
    if not exists:
        result["status"] = "missing"
        return result

    git_root = git_toplevel_for(path)
    if not git_root:
        result["status"] = "not_in_git"
        result["checks"].append("no containing Git repository")
        return result

    rel_path = path.relative_to(git_root)
    is_dir = path.is_dir()
    source_ref = source.get("gitRef") or source.get("commit") or "HEAD"
    commit = run_git(git_root, "rev-parse", source_ref)
    tracked = git_path_exists_at_ref(git_root, rel_path, is_dir, commit)
    remote = run_git(git_root, "remote", "get-url", "origin")
    remote_https = git_remote_https(remote)
    branches = run_git(git_root, "branch", "-r", "--contains", commit)
    result.update(
        {
            "type": "git_path",
            "gitRoot": str(git_root),
            "gitRelPath": str(rel_path),
            "gitRef": source_ref,
            "gitHead": commit,
            "origin": remote,
            "originHttps": remote_https,
            "remoteBranchesContainingHead": [line.strip() for line in branches.splitlines() if line.strip()],
            "trackedAtHead": tracked,
        }
    )
    result["checks"].append("tracked at HEAD" if tracked else "not tracked at HEAD")
    if branches:
        result["checks"].append("HEAD is present in at least one local remote-tracking branch")
    else:
        result["checks"].append("no local remote-tracking branch contains HEAD")

    line_start = source.get("line") or source.get("lineStart")
    line_end = source.get("lineEnd") or line_start
    if not is_dir and line_start:
        count = git_blob_line_count(git_root, commit, rel_path)
        result["lineCount"] = count
        line_ok = count is not None and 1 <= int(line_start) <= count and int(line_end) <= count
        result["lineRangeValid"] = line_ok
        result["checks"].append("line range valid" if line_ok else "line range invalid")
    else:
        line_ok = True

    result["deepLink"] = git_blob_link(remote_https, commit, rel_path, line_start, line_end, is_dir=is_dir)
    result["status"] = "vetted" if tracked and line_ok and remote_https and branches else "needs_review"
    return result


def vet_links(sources_path, out_dir, workspace_root):
    sources_doc = json.loads(Path(sources_path).read_text(encoding="utf-8"))
    sources = sources_doc.get("sources", sources_doc if isinstance(sources_doc, list) else [])
    vetted = [vet_source(source, workspace_root) for source in sources]
    status_counts = Counter(item.get("status", "unknown") for item in vetted)
    result = {
        "schema": "tcaas_vetted_links_v1",
        "generatedAt": now(),
        "source": str(sources_path),
        "workspaceRoot": str(Path(workspace_root).resolve()),
        "statusCounts": dict(status_counts),
        "links": vetted,
    }
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "vetted_links.json"
    md_path = out / "vetted_links.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Vetted Evidence Links", "", f"Generated: `{result['generatedAt']}`", "", "## Status Counts", ""]
    lines.extend(f"- {status}: {count}" for status, count in sorted(status_counts.items()))
    lines.extend(["", "## Links", ""])
    for item in vetted:
        label = item.get("id") or item.get("target")
        lines.append(f"### {label}")
        lines.append("")
        lines.append(f"- Status: `{item.get('status')}`")
        lines.append(f"- Target: `{item.get('target')}`")
        if item.get("description"):
            lines.append(f"- Description: {item['description']}")
        if item.get("deepLink"):
            lines.append(f"- Deep link: {item['deepLink']}")
        if item.get("gitHead"):
            lines.append(f"- Commit: `{item['gitHead']}`")
        if item.get("checks"):
            lines.append(f"- Checks: {'; '.join(item['checks'])}")
        lines.append("")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "statusCounts": dict(status_counts)}


def parse_local_evidence_ref(ref, workspace_root):
    if re.match(r"^https?://", ref or ""):
        return {"type": "url", "target": ref, "exists": True, "lineRangeValid": None}
    raw = str(ref or "")
    line_start = None
    line_end = None
    match = re.match(r"^(.+?):(\d+)(?:-(\d+))?$", raw)
    if match:
        raw = match.group(1)
        line_start = int(match.group(2))
        line_end = int(match.group(3) or match.group(2))
    path = Path(raw)
    if not path.is_absolute():
        path = Path(workspace_root) / path
    path = path.resolve()
    exists = path.exists()
    result = {
        "type": "local_path",
        "target": ref,
        "absolutePath": str(path),
        "exists": exists,
        "lineStart": line_start,
        "lineEnd": line_end,
        "lineRangeValid": None,
    }
    if exists and line_start and path.is_file():
        count = line_count(path)
        result["lineCount"] = count
        result["lineRangeValid"] = count is not None and 1 <= line_start <= count and line_end <= count
    return result


def is_url(value):
    return bool(re.match(r"^https?://", value or ""))


def is_allowed_evidence_url(value):
    return any(str(value or "").startswith(prefix) for prefix in ALLOWED_EVIDENCE_URL_PREFIXES)


def is_vetted_git_evidence_url(value):
    return any(str(value or "").startswith(prefix) for prefix in VETTED_GIT_EVIDENCE_PREFIXES)


def answer_quality_report(answers_path, out_dir, vetted_links_path=None, workspace_root="."):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    vetted = {}
    if vetted_links_path and Path(vetted_links_path).exists():
        vetted_doc = json.loads(Path(vetted_links_path).read_text(encoding="utf-8"))
        for item in vetted_doc.get("links", []):
            if item.get("target"):
                vetted[item["target"]] = item
            if item.get("deepLink"):
                vetted[item["deepLink"]] = item

    german_rationale_re = re.compile(
        r"\b(Nicht zutreffend|Teilweise erf[uü]llt|Nicht erf[uü]llt|fuer T-CaaS|KI-System)\b",
        re.IGNORECASE,
    )
    issues = []
    rows = []
    counters = Counter()
    approved_statuses = {"ready_for_review", "approved_for_portal"}
    for item in payload.get("answers", []):
        answer = item.get("answer", {})
        statement = str(answer.get("statement") or "").strip().upper()
        status = str(answer.get("status") or "").strip()
        evidence = [str(entry) for entry in answer.get("evidence", []) if str(entry).strip()]
        explanation = str(answer.get("explanation") or "")
        note = str(answer.get("note") or "")
        key = item.get("answerKey", "")
        row_issues = []
        ref_checks = []

        if statement:
            counters["statement_rows"] += 1
            if not evidence:
                row_issues.append("statement_without_evidence")
            if statement in {"SOC", "SOPC", "SONC", "NA"} and not explanation.strip():
                row_issues.append("statement_without_explanation")
        else:
            counters["blank_rows"] += 1

        if status in approved_statuses:
            counters[f"status_{status}"] += 1
            if not statement:
                row_issues.append(f"{status}_without_statement")
            if not evidence:
                row_issues.append(f"{status}_without_evidence")
            if not explanation.strip():
                row_issues.append(f"{status}_without_explanation")

        if status == "approved_for_portal":
            review = answer.get("review", {})
            if not review.get("reviewedBy") or not review.get("reviewedAt"):
                row_issues.append("approved_without_review_metadata")

        if explanation and german_rationale_re.search(explanation):
            row_issues.append("explanation_contains_german_rationale_pattern")

        if statement and evidence:
            missing_note_refs = [ref for ref in evidence if ref not in note]
            if missing_note_refs:
                row_issues.append(f"evidence_not_in_note:{len(missing_note_refs)}")

        for ref in evidence:
            if not is_url(ref):
                check = parse_local_evidence_ref(ref, workspace_root)
                check["status"] = "not_allowed_for_portal_answer"
                ref_checks.append(check)
                row_issues.append(f"non_url_evidence_ref:{ref}")
                if not check.get("exists"):
                    row_issues.append(f"missing_evidence:{ref}")
                if check.get("lineRangeValid") is False:
                    row_issues.append(f"invalid_evidence_line:{ref}")
                continue

            if not is_allowed_evidence_url(ref):
                ref_checks.append({"target": ref, "type": "url", "status": "disallowed_url"})
                row_issues.append(f"disallowed_evidence_url:{ref}")
                continue

            if ref in vetted:
                status = vetted[ref].get("status", "vetted_manifest")
                ref_checks.append({"target": ref, "type": "url", "status": status})
                if is_vetted_git_evidence_url(ref) and status != "vetted":
                    row_issues.append(f"unvetted_git_evidence_url:{ref}")
                continue

            if is_vetted_git_evidence_url(ref):
                ref_checks.append({"target": ref, "type": "url", "status": "git_url_not_in_vetted_links"})
                row_issues.append(f"unvetted_git_evidence_url:{ref}")
                continue

            ref_checks.append({"target": ref, "type": "url", "status": "allowed_confluence_url"})

        for issue in row_issues:
            issues.append(
                {
                    "answerKey": key,
                    "sheet": item.get("sheet", {}).get("title", ""),
                    "number": item.get("requirement", {}).get("number", ""),
                    "statement": statement,
                    "status": status,
                    "issue": issue,
                }
            )
            counters[f"issue_{issue.split(':', 1)[0]}"] += 1

        rows.append(
            {
                "answerKey": key,
                "sheet": item.get("sheet", {}).get("title", ""),
                "number": item.get("requirement", {}).get("number", ""),
                "statement": statement,
                "status": status,
                "evidenceCount": len(evidence),
                "issueCount": len(row_issues),
                "issues": row_issues,
                "referenceChecks": ref_checks,
            }
        )

    summary = {
        "schema": "tcaas_answer_quality_report_v1",
        "generatedAt": now(),
        "answers": str(answers_path),
        "vettedLinks": str(vetted_links_path or ""),
        "workspaceRoot": str(Path(workspace_root).resolve()),
        "answerCount": len(payload.get("answers", [])),
        "issueCount": len(issues),
        "counters": dict(counters),
        "issues": issues,
        "rows": rows,
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "answer_quality_report.json"
    md_path = out / "answer_quality_report.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    issue_counts = Counter(issue["issue"].split(":", 1)[0] for issue in issues)
    lines = ["# Answer Quality Report", "", f"Generated: `{summary['generatedAt']}`", ""]
    lines.extend(
        [
            f"- Answer rows: {summary['answerCount']}",
            f"- Statement rows: {counters.get('statement_rows', 0)}",
            f"- Blank rows: {counters.get('blank_rows', 0)}",
            f"- Issues: {summary['issueCount']}",
            "",
            "## Issue Counts",
            "",
        ]
    )
    if issue_counts:
        lines.extend(f"- {issue}: {count}" for issue, count in sorted(issue_counts.items()))
    else:
        lines.append("- none")
    lines.extend(["", "## Issues", ""])
    for issue in issues[:300]:
        lines.append(
            f"- `{issue['answerKey']}` {issue['sheet']} Req {issue['number']}: `{issue['issue']}`"
        )
    if len(issues) > 300:
        lines.append(f"- ... {len(issues) - 300} more issues in JSON report")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "issueCount": len(issues)}


SOC_CAVEAT_RE = re.compile(
    r"\b(partially fulfilled|partial fulfillment|not fully|not proven|not verified|not yet|"
    r"did not find|no evidence|missing evidence|evidence missing|does not prove|cannot prove|"
    r"unproven|still needs?|requires .* evidence|remains partial|remains unverified)\b",
    re.IGNORECASE,
)

SONC_RATIONALE_RE = re.compile(
    r"\b(not fulfilled|not proven|no evidence|not found|does not prove|cannot prove|missing|gap|"
    r"no .* evidence|not implemented)\b",
    re.IGNORECASE,
)

SOPC_RATIONALE_RE = re.compile(
    r"\b(partially fulfilled|partial|partly|not fully|not exhaustively|not complete|not yet|"
    r"remaining|still needs?|scope limitation|limited to|does not prove every)\b",
    re.IGNORECASE,
)

NA_RATIONALE_RE = re.compile(
    r"\b(not applicable|not in scope|outside (the )?scope|outside reviewed scope|core scope|"
    r"t-caas core scope|does not use|not used|no .* component|no .* requirement|not relevant)\b",
    re.IGNORECASE,
)

SHEET_CONTEXT_TERMS = {
    "Künstliche Intelligenz": ["ai", "llm", "prompt", "agent", "ci", "mr", "development", "model"],
    "Machine Learning": ["ai", "ml", "llm", "model", "training", "ci", "agent", "prompt"],
    "Private Clouds": ["t-caas", "private cloud", "kubernetes", "cluster", "bm4x", "vsphere", "capi"],
    "Router und Switche": [
        "router",
        "switch",
        "vsr",
        "hbr",
        "frr",
        "bm4x",
        "kube-vip",
        "bgp",
        "network",
        "ssh",
        "host-local",
        "pam",
        "password",
    ],
    "Netzelemente": ["network", "netz", "vsr", "hbr", "frr", "dns", "infoblox", "calico", "multus", "bm4x"],
    "Container": [
        "container",
        "image",
        "pod",
        "kubernetes",
        "kyverno",
        "mondoo",
        "workload",
        "network policy",
        "network policies",
    ],
    "CICD Ketten": ["ci", "pipeline", "gitlab", "artifact", "runner", "kaniko", "helm", "merge request"],
    "Datenbanksysteme": ["database", "db", "etcd", "postgres", "mongodb", "grafana", "victoriametrics"],
    "Netzbasierte Speichersysteme": ["storage", "csi", "netapp", "nfs", "object", "s3", "bucket", "storagegrid", "pv"],
    "Orchestrator": [
        "kubernetes",
        "orchestrator",
        "kubelet",
        "api server",
        "cluster",
        "capi",
        "t-caas",
        "network policy",
        "network policies",
    ],
    "GCP Allgemeine Anforderungen": ["gcp", "gke", "google", "runner", "terraform", "audit"],
    "GCP Compute Engine": ["gcp", "compute", "vm", "runner", "image", "shielded"],
    "GCP GKE": ["gcp", "gke", "kubernetes", "autopilot", "workload identity"],
    "GCP IAM": ["gcp", "iam", "workload identity", "service account", "oidc"],
    "Web-Anwendungen": ["web", "browser", "http", "session", "csrf", "xss", "keycloak", "ingress"],
    "Microservice (Container basierter Web Service)": ["microservice", "api", "service", "container", "http", "tls", "ingress"],
    "Application Server": ["application", "server", "ingress", "http", "service", "runtime"],
    "IAM": ["iam", "rbac", "keycloak", "oidc", "identity", "account", "role"],
    "Secure Shell (SSH)": ["ssh", "opkssh", "host", "key", "kex", "cipher"],
    "Kryptographische Algorithmen und Sicherheitsprotokolle": [
        "tls",
        "certificate",
        "cipher",
        "ssh",
        "sops",
        "key",
        "encryption",
        "crypto",
    ],
    "Technischer Basisschutz von IT-/NT-Systemen": [
        "hardening",
        "mondoo",
        "host",
        "kubernetes",
        "patch",
        "vulnerability",
        "baseline",
        "platform",
        "keycloak",
        "identity",
        "logging",
        "password",
        "pam",
        "api",
        "validation",
    ],
    "Mandantentrennung": ["tenant", "namespace", "networkpolicy", "rbac", "cluster", "isolation"],
    "Löschen personenbezogener Daten": ["deletion", "delete", "retention", "backup", "bucket", "storage", "lifecycle"],
}


def sentence_preview(text, limit=220):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def text_has_context_term(text, term):
    haystack = str(text or "").lower()
    needle = str(term or "").lower()
    if not needle:
        return False
    if re.search(r"[^a-z0-9]", needle):
        return needle in haystack
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack))


def add_completeness_finding(findings, item, severity, issue, detail):
    answer = item.get("answer", {}) or {}
    findings.append(
        {
            "severity": severity,
            "issue": issue,
            "answerKey": item.get("answerKey", ""),
            "sheet": item.get("sheet", {}).get("title", ""),
            "number": item.get("requirement", {}).get("number", ""),
            "requirementId": item.get("requirement", {}).get("requirementId", ""),
            "statement": str(answer.get("statement") or "").strip().upper(),
            "status": str(answer.get("status") or "").strip(),
            "detail": detail,
            "explanationPreview": sentence_preview(answer.get("explanation", "")),
        }
    )


def load_single_source_reviews(path):
    review_path = Path(path) if path else None
    if not review_path or not review_path.exists():
        return {}, None
    payload = json.loads(review_path.read_text(encoding="utf-8"))
    rows = payload.get("reviews", [])
    reviews = {}
    for row in rows:
        answer_key = str(row.get("answerKey") or "").strip()
        if answer_key:
            reviews[answer_key] = row
    return reviews, str(review_path)


def valid_single_source_review(row):
    return (
        isinstance(row, dict)
        and row.get("decision") in {"single_source_sufficient", "negative_evidence_reviewed"}
        and bool(str(row.get("reviewedBy") or "").strip())
        and bool(str(row.get("reviewedAt") or "").strip())
        and len(str(row.get("rationale") or "").strip()) >= 80
    )


def answer_completeness_audit(answers_path, out_dir, single_source_review_path=None):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    answers = payload.get("answers", [])
    findings = []
    out = Path(out_dir)
    default_review_path = out / "single_source_evidence_review.json"
    single_source_reviews, loaded_review_path = load_single_source_reviews(
        single_source_review_path or default_review_path
    )
    reviewed_single_source = []
    statement_counts = Counter()
    for item in answers:
        answer = item.get("answer", {}) or {}
        answer_key = str(item.get("answerKey") or "").strip()
        statement = str(answer.get("statement") or "").strip().upper()
        explanation = str(answer.get("explanation") or "").strip()
        note = str(answer.get("note") or "").strip()
        evidence = [str(entry) for entry in answer.get("evidence", []) if str(entry).strip()]
        sheet = item.get("sheet", {}).get("title", "")
        combined = f"{explanation}\n{note}"
        statement_counts[statement or "BLANK"] += 1

        if statement == "SOC" and SOC_CAVEAT_RE.search(combined):
            add_completeness_finding(
                findings,
                item,
                "error",
                "soc_answer_contains_caveat",
                "A fulfilled answer contains wording that suggests partial or unproven fulfillment.",
            )
        elif statement == "SOPC" and not SOPC_RATIONALE_RE.search(combined):
            add_completeness_finding(
                findings,
                item,
                "review",
                "sopc_without_explicit_partial_rationale",
                "A partially fulfilled answer should explicitly state the proven part and remaining limitation.",
            )
        elif statement == "SONC" and not SONC_RATIONALE_RE.search(combined):
            add_completeness_finding(
                findings,
                item,
                "review",
                "sonc_without_explicit_negative_rationale",
                "A not fulfilled answer should explicitly state the missing or contradictory evidence.",
            )
        elif statement == "NA" and not NA_RATIONALE_RE.search(combined):
            add_completeness_finding(
                findings,
                item,
                "review",
                "na_without_explicit_scope_rationale",
                "A not-applicable answer should state the scope reason.",
            )

        min_chars = 90 if statement == "NA" else 140
        if len(explanation) < min_chars:
            add_completeness_finding(
                findings,
                item,
                "review",
                "short_explanation",
                f"Explanation is {len(explanation)} characters; expected at least {min_chars} for detailed review.",
            )

        if statement in {"SOC", "SOPC", "SONC"} and len(evidence) < 2:
            review = single_source_reviews.get(answer_key)
            if len(evidence) == 1 and valid_single_source_review(review):
                reviewed_single_source.append(
                    {
                        "answerKey": answer_key,
                        "sheet": sheet,
                        "number": item.get("requirement", {}).get("number", ""),
                        "statement": statement,
                        "decision": review.get("decision", ""),
                        "reviewedBy": review.get("reviewedBy", ""),
                        "reviewedAt": review.get("reviewedAt", ""),
                        "rationale": review.get("rationale", ""),
                    }
                )
            else:
                add_completeness_finding(
                    findings,
                    item,
                    "review",
                    "low_evidence_count",
                    f"Statement has {len(evidence)} evidence reference(s); review whether one reference proves the full answer.",
                )

        if "this psa row" in explanation.lower() and len(explanation) < 260:
            add_completeness_finding(
                findings,
                item,
                "review",
                "generic_row_wording",
                "Explanation uses fallback row wording and may need more component-specific context.",
            )

        context_terms = SHEET_CONTEXT_TERMS.get(sheet, [])
        if statement != "NA" and context_terms and not any(text_has_context_term(combined, term) for term in context_terms):
            add_completeness_finding(
                findings,
                item,
                "review",
                "missing_sheet_context_terms",
                f"Answer does not mention expected context terms for sheet '{sheet}'.",
            )

    severity_counts = Counter(finding["severity"] for finding in findings)
    issue_counts = Counter(finding["issue"] for finding in findings)
    summary = {
        "schema": "tcaas_answer_completeness_audit_v1",
        "generatedAt": now(),
        "answers": str(answers_path),
        "singleSourceReviewPath": loaded_review_path,
        "answerCount": len(answers),
        "findingCount": len(findings),
        "reviewedSingleSourceCount": len(reviewed_single_source),
        "severityCounts": dict(severity_counts),
        "issueCounts": dict(issue_counts),
        "statementCounts": dict(statement_counts),
        "reviewedSingleSource": reviewed_single_source,
        "findings": findings,
    }
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "answer_completeness_audit.json"
    md_path = out / "answer_completeness_audit.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Answer Completeness and Correctness Audit", "", f"Generated: `{summary['generatedAt']}`", ""]
    lines.extend(
        [
            f"- Answer rows: {summary['answerCount']}",
            f"- Findings: {summary['findingCount']}",
            f"- Reviewed single-source rows: {summary['reviewedSingleSourceCount']}",
            f"- Single-source review file: `{summary['singleSourceReviewPath'] or 'none'}`",
            f"- Severity counts: `{json.dumps(summary['severityCounts'], sort_keys=True)}`",
            "",
            "## Issue Counts",
            "",
        ]
    )
    if issue_counts:
        lines.extend(f"- {issue}: {count}" for issue, count in sorted(issue_counts.items()))
    else:
        lines.append("- none")
    lines.extend(["", "## Findings", ""])
    for finding in findings[:400]:
        lines.append(
            f"- `{finding['severity']}` `{finding['issue']}` "
            f"`{finding['answerKey']}` {finding['sheet']} Req {finding['number']}: {finding['detail']}"
        )
    if len(findings) > 400:
        lines.append(f"- ... {len(findings) - 400} more findings in JSON report")
    lines.extend(["", "## Reviewed Single-Source Rows", ""])
    if reviewed_single_source:
        for row in reviewed_single_source[:400]:
            lines.append(
                f"- `{row['decision']}` `{row['answerKey']}` {row['sheet']} Req {row['number']}: "
                f"{sentence_preview(row['rationale'], 180)}"
            )
    else:
        lines.append("- none")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "findingCount": len(findings),
        "reviewedSingleSourceCount": len(reviewed_single_source),
        "severityCounts": dict(severity_counts),
        "issueCounts": dict(issue_counts),
    }


def confluence_evidence_audit(answers_path, vetted_links_path, out_dir):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    vetted = {}
    if vetted_links_path and Path(vetted_links_path).exists():
        vetted_doc = json.loads(Path(vetted_links_path).read_text(encoding="utf-8"))
        for item in vetted_doc.get("links", []):
            status = item.get("status", "")
            for key in ("target", "deepLink"):
                if item.get(key):
                    vetted[item[key]] = status

    rows = []
    by_url = defaultdict(list)
    for item in payload.get("answers", []):
        answer = item.get("answer", {})
        evidence = [str(ref).strip() for ref in answer.get("evidence", []) if str(ref).strip()]
        for ref in evidence:
            if not ref.startswith("https://wiki.telekom.de/"):
                continue
            evidence_status = vetted.get(ref, "not_in_vetted_links")
            audit_status = "ok" if evidence_status == "vetted" else "needs_review"
            row = {
                "answerKey": item.get("answerKey", ""),
                "sheet": item.get("sheet", {}).get("title", ""),
                "number": item.get("requirement", {}).get("number", ""),
                "statement": str(answer.get("statement") or "").strip(),
                "answerStatus": str(answer.get("status") or "").strip(),
                "url": ref,
                "evidenceStatus": evidence_status,
                "auditStatus": audit_status,
            }
            rows.append(row)
            by_url[ref].append(row)

    issue_rows = [row for row in rows if row["auditStatus"] != "ok"]
    affected = sorted({row["answerKey"] for row in issue_rows})
    unique_urls = sorted(by_url)
    summary = {
        "schema": "tcaas_confluence_evidence_audit_v1",
        "generatedAt": now(),
        "answers": str(answers_path),
        "vettedLinks": str(vetted_links_path or ""),
        "confluenceReferenceCount": len(rows),
        "uniqueConfluenceUrlCount": len(unique_urls),
        "unvettedConfluenceReferenceCount": len(issue_rows),
        "affectedAnswerRowCount": len(affected),
        "affectedAnswerRows": affected,
        "rows": rows,
        "urls": [
            {
                "url": url,
                "referenceCount": len(url_rows),
                "auditStatus": "ok" if all(row["auditStatus"] == "ok" for row in url_rows) else "needs_review",
                "answerKeys": sorted({row["answerKey"] for row in url_rows}),
            }
            for url, url_rows in sorted(by_url.items())
        ],
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "confluence_evidence_audit.json"
    md_path = out / "confluence_evidence_audit.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Confluence Evidence Audit",
        "",
        f"Generated: `{summary['generatedAt']}`",
        "",
        f"- Confluence references: {summary['confluenceReferenceCount']}",
        f"- Unique Confluence URLs: {summary['uniqueConfluenceUrlCount']}",
        f"- Unvetted Confluence references: {summary['unvettedConfluenceReferenceCount']}",
        f"- Affected answered rows: {summary['affectedAnswerRowCount']}",
        "",
        "## URLs",
        "",
        "| Status | References | URL |",
        "|---|---:|---|",
    ]
    for entry in summary["urls"]:
        lines.append(f"| {entry['auditStatus']} | {entry['referenceCount']} | {entry['url']} |")

    lines.extend(["", "## Affected Rows", "", "| Answer Key | Sheet | Req | Statement | URL Status |", "|---|---|---:|---|---|"])
    for row in issue_rows:
        lines.append(
            f"| {row['answerKey']} | {row['sheet']} | {row['number']} | {row['statement']} | {row['evidenceStatus']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "confluenceReferenceCount": len(rows),
        "uniqueConfluenceUrlCount": len(unique_urls),
        "unvettedConfluenceReferenceCount": len(issue_rows),
        "affectedAnswerRowCount": len(affected),
    }


PLATFORM_COVERAGE_COMPONENTS = [
    {
        "id": "private_cloud",
        "label": "Private cloud platform",
        "patterns": ["private cloud", "private-cloud", "telco cloud", "t-caas private", "t-caas core"],
        "expectedSheets": ["Private Clouds", "Architektur Rechenzentrums- und Cloud-Infrastrukturen"],
    },
    {
        "id": "kubernetes_orchestrator",
        "label": "Kubernetes, cluster lifecycle, and orchestration",
        "patterns": ["kubernetes", "orchestrator", "cluster-api", "capi", "flux", "functiondefinition", "functioninstance"],
        "expectedSheets": ["Orchestrator", "Container", "GCP GKE"],
    },
    {
        "id": "tcaas_operator_tco",
        "label": "T-CaaS Operator / T-CO integration",
        "patterns": ["t-caas-operator-system", "t-caas operator", "t-co", "sharedconfig", "tcaastenant"],
        "expectedSheets": ["Orchestrator", "Private Clouds", "Architektur von Systemen"],
    },
    {
        "id": "cluster_api_capi",
        "label": "Cluster API (CAPI) lifecycle components",
        "patterns": ["cluster-api", "cluster api", "functions/capi", "kubeadmcontrolplane", "machinedeployment"],
        "expectedSheets": ["Private Clouds", "Architektur Rechenzentrums- und Cloud-Infrastrukturen"],
    },
    {
        "id": "caprf_redfish",
        "label": "CAPRF / Redfish provider",
        "patterns": ["caprf", "redfish", "cluster-api-provider-redfish", "bmc", "baremetalhost"],
        "expectedSheets": ["Private Clouds", "Netzelemente"],
    },
    {
        "id": "bm4x_operator",
        "label": "BM4X operator and bare-metal bootstrap",
        "patterns": ["bm4x", "bare metal", "baremetal", "networkprofiles/bm4x", "bootstrapconfig_bm4x"],
        "expectedSheets": ["Private Clouds", "Orchestrator", "Technischer Basisschutz von IT-/NT-Systemen"],
    },
    {
        "id": "networking_hbr_vsr_frr",
        "label": "Networking, 6WIND VSR/HBR, FRR, BM4X, Calico, Multus, SR-IOV",
        "patterns": ["6wind", "vsr", "hbr", "frr", "bm4x", "calico", "multus", "sriov", "sr-iov", "vrf", "bgp"],
        "expectedSheets": ["Router und Switche", "Netzelemente", "Architektur von Systemen"],
    },
    {
        "id": "calico",
        "label": "Calico network policy enforcement",
        "patterns": ["calico", "globalnetworkpolicy", "network-policies"],
        "expectedSheets": ["Private Clouds", "Container", "Orchestrator"],
    },
    {
        "id": "multus_cni",
        "label": "Multus CNI secondary networking",
        "patterns": ["multus", "networkattachmentdefinition", "secondary network"],
        "expectedSheets": ["Private Clouds", "Netzelemente"],
    },
    {
        "id": "sriov_device_plugin",
        "label": "SR-IOV device plugin and PCI passthrough",
        "patterns": ["sriov", "sr-iov", "vfio", "pci passthrough"],
        "expectedSheets": ["Private Clouds", "Router und Switche", "Netzelemente"],
    },
    {
        "id": "host_network_operator",
        "label": "Host Network Operator / VSR / HBN",
        "patterns": ["host-network-operator", "host network operator", "6wind", "vsr", "hbr", "frr", "hbn"],
        "expectedSheets": ["Router und Switche", "Netzelemente", "Private Clouds"],
    },
    {
        "id": "kube_vip_load_balancing",
        "label": "kube-vip and load-balancing paths",
        "patterns": ["kube-vip", "vip", "load balancer", "loadbalancer", "bgp"],
        "expectedSheets": ["Router und Switche", "Netzelemente", "Private Clouds"],
    },
    {
        "id": "network_binding_controller",
        "label": "NetworkBinding controller and intent-based network provisioning",
        "patterns": ["network-binding-controller", "networkbinding", "network binding", "networkbindings"],
        "expectedSheets": ["Router und Switche", "Netzelemente", "Private Clouds", "IAM", "CICD Ketten"],
    },
    {
        "id": "dns_infoblox",
        "label": "DNS operator and Infoblox TLS/credential controls",
        "patterns": ["dns-operator", "dns operator", "infobloxdnsprovider", "infoblox", "disabletlsverification"],
        "expectedSheets": ["Netzelemente", "Router und Switche", "Kryptographische Algorithmen und Sicherheitsprotokolle", "Private Clouds"],
    },
    {
        "id": "logging_operator",
        "label": "Platform logging and logging-operator",
        "patterns": [
            "logging-operator",
            "logging operator",
            "tdg-logging",
            "fluent",
            "hosttailer",
            "eventtailer",
            "soct",
            "cdi kafka",
            "audit log",
        ],
        "expectedSheets": ["Container", "Orchestrator", "Private Clouds"],
    },
    {
        "id": "iam_keycloak_rbac",
        "label": "IAM, Keycloak/OIDC, ZAM, RBAC, breakglass",
        "patterns": ["keycloak", "oidc", "rbac", "zam", "auth-operator", "breakglass", "idpprovider", "identity"],
        "expectedSheets": ["IAM", "Technischer Basisschutz von IT-/NT-Systemen", "Web-Anwendungen"],
    },
    {
        "id": "ingress_nginx",
        "label": "ingress-nginx web/API ingress",
        "patterns": ["ingress-nginx", "nginx ingress", "nginx-forwarder"],
        "expectedSheets": ["Application Server", "Web-Anwendungen", "Microservice (Container basierter Web Service)"],
    },
    {
        "id": "haproxy_ingress",
        "label": "HAProxy ingress",
        "patterns": ["haproxy", "ha proxy"],
        "expectedSheets": ["Application Server", "Web-Anwendungen", "Microservice (Container basierter Web Service)"],
    },
    {
        "id": "cicd_ai_mr",
        "label": "CI/CD, supply chain, and AI-assisted MR review",
        "patterns": ["gitlab ci", "ci/cd", "cicd", "pipeline", "merge request", "mr review", "ai summary", "llm", "gaia", "stargate"],
        "expectedSheets": ["CICD Ketten", "Künstliche Intelligenz", "Machine Learning"],
    },
    {
        "id": "gcp_dev_env",
        "label": "GCP development environment",
        "patterns": ["gcp", "gke autopilot", "workload identity federation", "iap", "os config", "secret manager"],
        "expectedSheets": ["GCP Allgemeine Anforderungen", "GCP GKE", "GCP IAM", "GCP Compute Engine"],
    },
    {
        "id": "storage_database",
        "label": "Storage, CSI, NetApp, Cinder/Ceph, and etcd/database scope",
        "patterns": ["storageclass", "csi", "netapp", "cinder", "ceph", "etcd", "database", "persistentvolume"],
        "expectedSheets": ["Netzbasierte Speichersysteme", "Datenbanksysteme"],
    },
    {
        "id": "csi_storage_backends",
        "label": "CSI storage backends",
        "patterns": ["csi-netapp", "trident", "ceph-csi", "cinder-csi", "vsphere-csi", "storageclass"],
        "expectedSheets": ["Netzbasierte Speichersysteme", "Private Clouds"],
    },
    {
        "id": "object_storage_s3",
        "label": "Object storage, ObjectStorageProfile, StorageGRID, CephRGW, MinIO",
        "patterns": ["objectstorageprofile", "objectstorageclaim", "object storage", "storagegrid", "cephrgw", "minio", "s3"],
        "expectedSheets": ["Netzbasierte Speichersysteme", "Private Clouds", "Löschen personenbezogener Daten"],
    },
    {
        "id": "vsphere_management",
        "label": "vSphere-backed management clusters, CAPV, and vSphere CSI",
        "patterns": ["vsphere", "capv", "vsphere csi", "vsphereinfrastructureconfig", "vsphereclusteridentity"],
        "expectedSheets": ["Private Clouds", "Netzbasierte Speichersysteme", "Architektur Rechenzentrums- und Cloud-Infrastrukturen"],
    },
    {
        "id": "mondoo_marcel1",
        "label": "marcel-1 live evidence and Mondoo policy results",
        "patterns": ["marcel-1", "mondoo", "policy check", "mondoo-analysis", "mondoo-findings"],
        "expectedSheets": ["Technischer Basisschutz von IT-/NT-Systemen", "Container", "Private Clouds"],
    },
    {
        "id": "prometheus_monitoring",
        "label": "Prometheus monitoring",
        "patterns": ["prometheus", "alertmanager", "servicemonitor"],
        "expectedSheets": ["Orchestrator", "Private Clouds"],
    },
    {
        "id": "kyverno_policy",
        "label": "Kyverno policy enforcement",
        "patterns": ["kyverno", "clusterpolicy", "policyexceptions", "policy exception"],
        "expectedSheets": ["Container", "Orchestrator", "Private Clouds"],
    },
    {
        "id": "tenant_isolation",
        "label": "Tenant isolation and namespace/network-policy boundaries",
        "patterns": ["tenant", "mandant", "mandantentrennung", "tcaastenant", "networkpolicy", "namespace"],
        "expectedSheets": ["Mandantentrennung", "Private Clouds", "Container"],
    },
    {
        "id": "backup_restore",
        "label": "Backup, restore, lifecycle, and deletion",
        "patterns": ["backup", "restore", "snapshot", "velero", "deletion", "retention"],
        "expectedSheets": ["Löschen personenbezogener Daten", "GCP Allgemeine Anforderungen", "Architektur von Systemen"],
    },
    {
        "id": "velero_backup",
        "label": "Velero backup/restore component",
        "patterns": ["velero", "backupstoragelocation", "volumesnapshot"],
        "expectedSheets": ["Private Clouds", "Architektur von Systemen"],
    },
    {
        "id": "image_sync_operator",
        "label": "image-sync-operator and registry synchronization",
        "patterns": ["image-sync-operator", "imagesync", "image synchronization"],
        "expectedSheets": ["Container", "CICD Ketten"],
    },
    {
        "id": "upstream_derived_components",
        "label": "Upstream-derived components and mirror provenance",
        "patterns": ["upstream", "cert-manager", "frr", "multus-cni", "multi-networkpolicy", "artifactory mirror"],
        "expectedSheets": ["CICD Ketten", "Container", "Kryptographische Algorithmen und Sicherheitsprotokolle"],
    },
    {
        "id": "dtt_scope",
        "label": "DT Technik / DTT architecture references in Core answers",
        "patterns": ["dt technik", "dtt", "tdg", "t-caas dt-technik", "t-caas dtt"],
        "expectedSheets": ["Betrieb in DT Technik", "GCP Allgemeine Anforderungen"],
        "deferredFilingScope": True,
    },
    {
        "id": "natco_scope",
        "label": "NatCo architecture references in Core answers",
        "patterns": ["natco", "national company", "mta", "tmcz", "austria", "czech", "slovak", "croatia"],
        "expectedSheets": ["Private Clouds", "Architektur von Systemen", "Mandantentrennung"],
        "deferredFilingScope": True,
    },
]


LOCAL_PORTAL_REF_RE = re.compile(r"/home/|(^|[^A-Za-z0-9_-])tcaas-psa/|(^|[^A-Za-z0-9_-])artifacts/|(^|[^A-Za-z0-9_-])analysis/")
GERMAN_PORTAL_TEXT_RE = re.compile(
    r"[ÄÖÜäöüß]|\b(erfüllt|teilweise|nicht erfüllt|nicht zutreffend|Begründung|Anforderung|Hinweis|Muss|muss|soll|zurücksetzen)\b",
    re.IGNORECASE,
)


def row_haystack(item):
    answer = item.get("answer", {}) or {}
    requirement = item.get("requirement", {}) or {}
    sheet = item.get("sheet", {}) or {}
    values = [
        item.get("answerKey", ""),
        sheet.get("title", ""),
        sheet.get("manifestName", ""),
        requirement.get("number", ""),
        requirement.get("requirementId", ""),
        requirement.get("text", ""),
        requirement.get("details", ""),
        requirement.get("motivation", ""),
        answer.get("statement", ""),
        answer.get("explanation", ""),
        answer.get("note", ""),
        " ".join(str(ref) for ref in answer.get("evidence", []) or []),
    ]
    return "\n".join(str(value) for value in values if value).lower()


def load_manifest_count(manifest_path):
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return len(manifest) if isinstance(manifest, list) else len(manifest.get("items", []))


def platform_coverage_audit(
    answers_path,
    out_dir,
    dtt_manifest_path=None,
    natco_manifest_path=None,
    require_natco_manifest=False,
):
    payload = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    answers = payload.get("answers", [])
    statement_counts = Counter()
    status_counts = Counter()
    sheet_summary = defaultdict(lambda: {"total": 0, "statements": Counter(), "statuses": Counter(), "evidenceRefs": 0})
    issues = []
    local_ref_rows = []
    non_english_rows = []
    durable_ref_issues = []
    missing_note_refs = []
    dtt_manifest_count = None
    natco_manifest_count = None

    for item in answers:
        answer = item.get("answer", {}) or {}
        requirement = item.get("requirement", {}) or {}
        statement = str(answer.get("statement") or "").strip().upper()
        status = str(answer.get("status") or "").strip()
        sheet = item.get("sheet", {}).get("title", "")
        explanation = str(answer.get("explanation") or "")
        note = str(answer.get("note") or "")
        evidence = [str(ref).strip() for ref in answer.get("evidence", []) or [] if str(ref).strip()]
        key = item.get("answerKey", "")

        statement_counts[statement or "blank"] += 1
        status_counts[status or "blank"] += 1
        sheet_summary[sheet]["total"] += 1
        sheet_summary[sheet]["statements"][statement or "blank"] += 1
        sheet_summary[sheet]["statuses"][status or "blank"] += 1
        sheet_summary[sheet]["evidenceRefs"] += len(evidence)

        if not statement:
            issues.append({"severity": "error", "type": "missing_statement", "answerKey": key, "sheet": sheet})
        if statement in {"SOPC", "SONC", "NA", "SOC"} and not explanation.strip():
            issues.append({"severity": "error", "type": "missing_explanation", "answerKey": key, "sheet": sheet})
        if not evidence:
            issues.append({"severity": "error", "type": "missing_evidence", "answerKey": key, "sheet": sheet})
        if LOCAL_PORTAL_REF_RE.search(explanation) or LOCAL_PORTAL_REF_RE.search(note):
            local_ref_rows.append({"answerKey": key, "sheet": sheet, "number": requirement.get("number", "")})
        if GERMAN_PORTAL_TEXT_RE.search(explanation) or GERMAN_PORTAL_TEXT_RE.search(note):
            non_english_rows.append({"answerKey": key, "sheet": sheet, "number": requirement.get("number", "")})
        missing = [ref for ref in evidence if ref not in note]
        if missing:
            missing_note_refs.append({"answerKey": key, "sheet": sheet, "number": requirement.get("number", ""), "missing": len(missing)})
        for ref in evidence:
            if not is_url(ref) or not is_allowed_evidence_url(ref):
                durable_ref_issues.append({"answerKey": key, "sheet": sheet, "number": requirement.get("number", ""), "ref": ref})

    component_summaries = []
    for component in PLATFORM_COVERAGE_COMPONENTS:
        pattern_hits = []
        sheets = Counter()
        statements = Counter()
        evidence_refs = set()
        for item in answers:
            text = row_haystack(item)
            if not any(pattern.lower() in text for pattern in component["patterns"]):
                continue
            answer = item.get("answer", {}) or {}
            pattern_hits.append(item.get("answerKey", ""))
            sheets[item.get("sheet", {}).get("title", "")] += 1
            statements[str(answer.get("statement") or "blank").strip().upper()] += 1
            evidence_refs.update(str(ref).strip() for ref in answer.get("evidence", []) or [] if str(ref).strip())
        missing_expected = [sheet for sheet in component.get("expectedSheets", []) if not any(sheet in hit_sheet for hit_sheet in sheets)]
        status = "covered" if pattern_hits else "missing"
        if missing_expected and pattern_hits:
            status = "covered_with_scope_note"
        if component.get("deferredFilingScope") and pattern_hits:
            status = "architecture_represented_core_only"
        component_summaries.append(
            {
                "id": component["id"],
                "label": component["label"],
                "status": status,
                "matchingRows": len(pattern_hits),
                "matchingSheets": dict(sheets.most_common()),
                "statementCounts": dict(statements),
                "uniqueEvidenceRefs": len(evidence_refs),
                "missingExpectedSheets": missing_expected,
            }
        )
        if not pattern_hits:
            issues.append({"severity": "error", "type": "component_without_answer_coverage", "component": component["id"]})
        elif missing_expected and not component.get("deferredFilingScope"):
            issues.append(
                {
                    "severity": "review",
                    "type": "component_missing_expected_sheet_coverage",
                    "component": component["id"],
                    "missingExpectedSheets": missing_expected,
                    "detail": f"{component['label']} is represented, but not in every expected sheet group.",
                }
            )

    dtt_sheet = sheet_summary.get("Betrieb in DT Technik")
    if dtt_sheet and dtt_sheet["statements"].get("NA", 0) == dtt_sheet["total"]:
        issues.append(
            {
                "severity": "deferred",
                "type": "dtt_operations_sheet_all_na_for_core_scope",
                "sheet": "Betrieb in DT Technik",
                "detail": "This is consistent with the current T-CaaS Core scope. DTT currently has no separate PSA SoCs to answer; keep DTT architecture differences documented until PSA exposes DTT SoCs.",
            }
        )

    if dtt_manifest_path:
        dtt_manifest_count = load_manifest_count(dtt_manifest_path)
        if dtt_manifest_count is not None:
            if dtt_manifest_count == 0:
                issues.append(
                    {
                        "severity": "deferred",
                        "type": "dtt_system_has_no_soc_manifest_rows",
                        "manifest": str(dtt_manifest_path),
                        "detail": "PSA currently exposes no SoC rows for the separate DTT system snapshot. Treat DTT filing as future scope and maintain architecture-difference evidence until PSA exposes DTT SoCs.",
                    }
                )
        else:
            issues.append(
                {
                    "severity": "blocker",
                    "type": "dtt_system_manifest_missing",
                    "manifest": str(dtt_manifest_path),
                    "detail": "The requested DTT system manifest path does not exist.",
                }
            )

    if natco_manifest_path:
        natco_manifest_count = load_manifest_count(natco_manifest_path)
        if natco_manifest_count is not None:
            if natco_manifest_count == 0:
                issues.append(
                    {
                        "severity": "deferred",
                        "type": "natco_system_has_no_soc_manifest_rows",
                        "manifest": str(natco_manifest_path),
                        "detail": "The supplied NatCo system snapshot has no SoC rows. Treat NatCo filing as future scope and maintain architecture-difference evidence until PSA exposes NatCo SoCs.",
                    }
                )
        else:
            issues.append(
                {
                    "severity": "blocker",
                    "type": "natco_system_manifest_missing",
                    "manifest": str(natco_manifest_path),
                    "detail": "The requested NatCo system manifest path does not exist.",
                }
            )
    elif require_natco_manifest:
        issues.append(
            {
                "severity": "deferred",
                "type": "natco_system_manifest_not_provided",
                "detail": "No separate NatCo system SoC manifest is currently available. Treat NatCo filing as future scope and maintain architecture-difference evidence until PSA exposes NatCo SoCs.",
            }
        )

    hygiene = {
        "localPathRows": len(local_ref_rows),
        "nonEnglishRows": len(non_english_rows),
        "durableReferenceIssues": len(durable_ref_issues),
        "missingNoteReferenceRows": len(missing_note_refs),
    }
    issue_counts = Counter(issue["type"] for issue in issues)
    summary = {
        "schema": "tcaas_platform_coverage_audit_v1",
        "generatedAt": now(),
        "answers": str(answers_path),
        "dttManifest": str(dtt_manifest_path or ""),
        "natcoManifest": str(natco_manifest_path or ""),
        "answerCount": len(answers),
        "statementCounts": dict(statement_counts),
        "statusCounts": dict(status_counts),
        "hygiene": hygiene,
        "componentCount": len(component_summaries),
        "sheetSummaries": [
            {
                "sheet": sheet,
                "total": data["total"],
                "statementCounts": dict(data["statements"]),
                "statusCounts": dict(data["statuses"]),
                "evidenceRefs": data["evidenceRefs"],
            }
            for sheet, data in sorted(sheet_summary.items())
        ],
        "componentSummaries": component_summaries,
        "dttManifestCount": dtt_manifest_count,
        "natcoManifestCount": natco_manifest_count,
        "issueCounts": dict(issue_counts),
        "issues": issues,
        "localPathRows": local_ref_rows[:200],
        "nonEnglishRows": non_english_rows[:200],
        "durableReferenceIssues": durable_ref_issues[:200],
        "missingNoteReferenceRows": missing_note_refs[:200],
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "platform_coverage_audit.json"
    md_path = out / "platform_coverage_audit.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Platform Coverage Audit",
        "",
        f"Generated: `{summary['generatedAt']}`",
        f"Answers: `{answers_path}`",
        "",
        "## Summary",
        "",
        f"- Answer rows: {len(answers)}",
        f"- Status counts: `{json.dumps(summary['statusCounts'], ensure_ascii=False)}`",
        f"- Statement counts: `{json.dumps(summary['statementCounts'], ensure_ascii=False)}`",
        f"- Hygiene: `{json.dumps(hygiene, ensure_ascii=False)}`",
        f"- DTT manifest rows: `{dtt_manifest_count}`",
        f"- NatCo manifest rows: `{natco_manifest_count}`",
        "",
        "## Component Coverage",
        "",
        "Coverage here means the component is represented in answer rows and evidence references. It does not mean the component is fully compliant; fulfillment is shown by the statement counts.",
        "",
        "DTT and NatCo component rows are architecture-reference coverage inside the T-CaaS Core answer set only. They are not separate DTT or NatCo SoC filing coverage because PSA currently exposes no separate rows for those scopes.",
        "",
        "| Status | Rows | Statements | Evidence refs | Component | Sheets |",
        "|---|---:|---|---:|---|---|",
    ]
    for component in component_summaries:
        sheets = ", ".join(f"{sheet}: {count}" for sheet, count in component["matchingSheets"].items())
        lines.append(
            f"| `{component['status']}` | {component['matchingRows']} | "
            f"`{json.dumps(component['statementCounts'], ensure_ascii=False)}` | {component['uniqueEvidenceRefs']} | "
            f"{component['label']} | {sheets or '-'} |"
        )
    lines.extend(["", "## Issues", ""])
    if issues:
        for issue in issues:
            detail = issue.get("detail") or issue.get("component") or issue.get("sheet") or issue.get("answerKey") or ""
            lines.append(f"- `{issue['severity']}` `{issue['type']}` {detail}")
    else:
        lines.append("- none")
    lines.extend(["", "## Sheet Coverage", "", "| Rows | Statements | Sheet |", "|---:|---|---|"])
    for sheet in summary["sheetSummaries"]:
        lines.append(f"| {sheet['total']} | `{json.dumps(sheet['statementCounts'], ensure_ascii=False)}` | {sheet['sheet']} |")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "answerCount": len(answers),
        "componentCount": len(component_summaries),
        "issueCounts": dict(issue_counts),
        "hygiene": hygiene,
    }


def redact_network_literals(value):
    text = str(value or "")
    text = NETWORK_IPV4_RE.sub("<redacted-ipv4>", text)
    text = NETWORK_IPV6_RE.sub(redact_ipv6_candidate, text)
    text = NETWORK_MAC_RE.sub("<redacted-mac>", text)
    return text


def redact_ipv6_candidate(match):
    candidate = match.group(0)
    suffix = ""
    if candidate.endswith(":") and not candidate.endswith("::"):
        candidate = candidate[:-1]
        suffix = ":"
    try:
        if "/" in candidate:
            ipaddress.ip_network(candidate, strict=False)
        else:
            ipaddress.ip_address(candidate)
    except ValueError:
        return f"{candidate}{suffix}"
    return f"<redacted-ipv6>{suffix}"


def sanitize_command_text(value):
    text = str(value or "")
    text = re.sub(
        r"(?i)(token|password|secret|credential|authorization)(\s*[:=]\s*)\S+",
        r"\1\2<redacted>",
        text,
    )
    text = re.sub(r"(?i)(client-certificate-data|client-key-data|certificate-authority-data):\s*\S+", r"\1: <redacted>", text)
    text = re.sub(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}", "<redacted-jwt>", text)
    text = redact_network_literals(text)
    return text[:50000]


def sanitize_remote_text(value):
    return sanitize_command_text(value)


def redact_address_value(value):
    if isinstance(value, list):
        return ["<redacted-address>" for _ in value]
    if isinstance(value, dict):
        return {key: "<redacted-address>" for key in value}
    if value in (None, ""):
        return value
    return "<redacted-address>"


def redact_env_item(item):
    if not isinstance(item, dict):
        return redact_for_storage(item)
    redacted = {}
    for key, value in item.items():
        if key == "value":
            redacted[key] = "<redacted-env-value>"
        else:
            redacted[key] = redact_for_storage(value)
    return redacted


def redact_for_storage(value):
    if isinstance(value, dict):
        redacted = {}
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower in {"data", "stringdata", "binarydata"} or SENSITIVE_VALUE_KEY_RE.search(key_text):
                redacted[key_text] = "<redacted>"
            elif key_lower == "env" and isinstance(child, list):
                redacted[key_text] = [redact_env_item(item) for item in child]
            elif ADDRESS_VALUE_KEY_RE.search(key_text):
                redacted[key_text] = redact_address_value(child)
            else:
                redacted[key_text] = redact_for_storage(child)
        return redacted
    if isinstance(value, list):
        return [redact_for_storage(item) for item in value]
    if isinstance(value, str):
        return sanitize_command_text(value)
    return value


def configure_no_proxy(env, no_proxy):
    if no_proxy is None:
        return
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"):
        env[key] = ""
    env["NO_PROXY"] = no_proxy
    env["no_proxy"] = no_proxy


def run_kubectl_json(
    kubectl,
    context,
    kubeconfig,
    xdg_runtime_dir,
    args,
    timeout=120,
    server=None,
    tls_server_name=None,
    no_proxy=None,
):
    command = [kubectl]
    if context:
        command.extend(["--context", context])
    if kubeconfig:
        command.extend(["--kubeconfig", kubeconfig])
    if server:
        command.extend(["--server", server])
    if tls_server_name:
        command.extend(["--tls-server-name", tls_server_name])
    command.extend(args)
    env = os.environ.copy()
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig
    if xdg_runtime_dir:
        Path(xdg_runtime_dir).mkdir(parents=True, exist_ok=True)
        env["XDG_RUNTIME_DIR"] = xdg_runtime_dir
    configure_no_proxy(env, no_proxy)
    started = time.time()
    completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout, env=env)
    elapsed = round(time.time() - started, 3)
    result = {
        "args": args,
        "returnCode": completed.returncode,
        "elapsedSeconds": elapsed,
        "stderr": sanitize_command_text(completed.stderr),
    }
    stdout = completed.stdout or ""
    if stdout.strip():
        try:
            result["json"] = redact_for_storage(json.loads(stdout))
            result["format"] = "json"
        except json.JSONDecodeError:
            result["text"] = sanitize_command_text(stdout)
            result["format"] = "text"
    return result


def run_kubectl_raw_json(
    kubectl,
    context,
    kubeconfig,
    xdg_runtime_dir,
    args,
    timeout=120,
    server=None,
    tls_server_name=None,
    no_proxy=None,
):
    command = [kubectl]
    if context:
        command.extend(["--context", context])
    if kubeconfig:
        command.extend(["--kubeconfig", kubeconfig])
    if server:
        command.extend(["--server", server])
    if tls_server_name:
        command.extend(["--tls-server-name", tls_server_name])
    command.extend(args)
    env = os.environ.copy()
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig
    if xdg_runtime_dir:
        Path(xdg_runtime_dir).mkdir(parents=True, exist_ok=True)
        env["XDG_RUNTIME_DIR"] = xdg_runtime_dir
    configure_no_proxy(env, no_proxy)
    completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout, env=env)
    if completed.returncode != 0:
        raise RuntimeError(sanitize_command_text(completed.stderr))
    return json.loads(completed.stdout or "{}")


def find_free_port(bind_host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind((bind_host, 0))
        return handle.getsockname()[1]


def wait_for_tcp(host, port, timeout=20):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, int(port)), timeout=1):
                return True
        except OSError as exc:
            last_error = exc
            time.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for {host}:{port}: {last_error}")


def open_ssh_tunnel(ssh, jump_host, target_host, target_port, local_bind="127.0.0.1", local_port=0):
    local_port = int(local_port or 0) or find_free_port(local_bind)
    forward = f"{local_bind}:{local_port}:{target_host}:{target_port}"
    command = [ssh, "-N", "-L", forward, jump_host]
    process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        wait_for_tcp(local_bind, local_port, timeout=20)
    except Exception:
        process.terminate()
        try:
            _stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            _stdout, stderr = process.communicate(timeout=5)
        raise RuntimeError(f"SSH tunnel failed: {sanitize_command_text(stderr)}")
    return process, f"https://{local_bind}:{local_port}"


def close_process(process):
    if not process:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def kitems(doc):
    if not isinstance(doc, dict):
        return []
    if isinstance(doc.get("json"), dict):
        return doc["json"].get("items", []) or []
    return doc.get("items", []) or []


def item_name(item):
    metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
    namespace = metadata.get("namespace")
    name = metadata.get("name", "")
    return f"{namespace}/{name}" if namespace else name


def node_roles(labels):
    roles = []
    for key in labels or {}:
        if key.startswith("node-role.kubernetes.io/"):
            role = key.rsplit("/", 1)[-1] or "worker"
            roles.append(role)
    return sorted(roles) or ["worker"]


def summarize_nodes(nodes):
    summary = {
        "count": len(nodes),
        "ready": 0,
        "roles": Counter(),
        "kubeletVersions": Counter(),
        "containerRuntimes": Counter(),
        "operatingSystems": Counter(),
        "kernelVersions": Counter(),
    }
    for node in nodes:
        status = node.get("status", {})
        labels = node.get("metadata", {}).get("labels", {})
        for role in node_roles(labels):
            summary["roles"][role] += 1
        for condition in status.get("conditions", []):
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                summary["ready"] += 1
        node_info = status.get("nodeInfo", {})
        for key, counter_name in [
            ("kubeletVersion", "kubeletVersions"),
            ("containerRuntimeVersion", "containerRuntimes"),
            ("osImage", "operatingSystems"),
            ("kernelVersion", "kernelVersions"),
        ]:
            value = node_info.get(key)
            if value:
                summary[counter_name][value] += 1
    for key, value in list(summary.items()):
        if isinstance(value, Counter):
            summary[key] = dict(value)
    return summary


def container_security_findings(pods):
    counts = Counter()
    examples = defaultdict(list)

    def add_example(kind, pod):
        if len(examples[kind]) < 10:
            examples[kind].append(item_name(pod))

    for pod in pods:
        spec = pod.get("spec", {})
        counts["pods"] += 1
        for field in ("hostNetwork", "hostPID", "hostIPC"):
            if spec.get(field):
                counts[field] += 1
                add_example(field, pod)
        containers = []
        containers.extend(spec.get("initContainers", []) or [])
        containers.extend(spec.get("containers", []) or [])
        for container in containers:
            counts["containers"] += 1
            security_context = container.get("securityContext", {}) or {}
            resources = container.get("resources", {}) or {}
            if security_context.get("privileged"):
                counts["privilegedContainers"] += 1
                add_example("privilegedContainers", pod)
            if security_context.get("allowPrivilegeEscalation") is not False:
                counts["allowPrivilegeEscalationNotFalse"] += 1
                add_example("allowPrivilegeEscalationNotFalse", pod)
            if security_context.get("runAsNonRoot") is not True:
                counts["runAsNonRootNotTrue"] += 1
                add_example("runAsNonRootNotTrue", pod)
            if security_context.get("readOnlyRootFilesystem") is not True:
                counts["readOnlyRootFilesystemNotTrue"] += 1
                add_example("readOnlyRootFilesystemNotTrue", pod)
            if not (resources.get("requests") or {}).get("cpu"):
                counts["missingCpuRequest"] += 1
                add_example("missingCpuRequest", pod)
            if not (resources.get("requests") or {}).get("memory"):
                counts["missingMemoryRequest"] += 1
                add_example("missingMemoryRequest", pod)
            if not (resources.get("limits") or {}).get("cpu"):
                counts["missingCpuLimit"] += 1
                add_example("missingCpuLimit", pod)
            if not (resources.get("limits") or {}).get("memory"):
                counts["missingMemoryLimit"] += 1
                add_example("missingMemoryLimit", pod)
            if not container.get("readinessProbe"):
                counts["missingReadinessProbe"] += 1
                add_example("missingReadinessProbe", pod)
            if not container.get("livenessProbe"):
                counts["missingLivenessProbe"] += 1
                add_example("missingLivenessProbe", pod)
    return {"counts": dict(counts), "examples": dict(examples)}


def summarize_pods(pods):
    phases = Counter()
    namespaces = Counter()
    image_registries = Counter()
    for pod in pods:
        phases[pod.get("status", {}).get("phase", "unknown")] += 1
        namespace = pod.get("metadata", {}).get("namespace", "default")
        namespaces[namespace] += 1
        spec = pod.get("spec", {})
        containers = []
        containers.extend(spec.get("initContainers", []) or [])
        containers.extend(spec.get("containers", []) or [])
        for container in containers:
            image = container.get("image", "")
            registry = image.split("/", 1)[0] if "/" in image else "docker.io"
            image_registries[registry] += 1
    return {
        "count": len(pods),
        "phases": dict(phases),
        "namespaces": dict(namespaces),
        "imageRegistries": dict(image_registries),
        "securityFindings": container_security_findings(pods),
    }


def summarize_services(services):
    types = Counter()
    for service in services:
        types[service.get("spec", {}).get("type", "ClusterIP")] += 1
    return {"count": len(services), "types": dict(types)}


def summarize_collection(collections):
    nodes = kitems(collections.get("nodes", {}))
    namespaces = kitems(collections.get("namespaces", {}))
    pods = kitems(collections.get("pods_all", {}))
    services = kitems(collections.get("services_all", {}))
    network_policies = kitems(collections.get("networkpolicies_all", {}))
    storageclasses = kitems(collections.get("storageclasses", {}))
    pvs = kitems(collections.get("persistentvolumes", {}))
    pvcs = kitems(collections.get("persistentvolumeclaims_all", {}))
    roles = kitems(collections.get("roles_all", {}))
    clusterroles = kitems(collections.get("clusterroles", {}))
    flux = kitems(collections.get("flux_sources", {}))
    tcaas_clusters = kitems(collections.get("tcaas_clusters", {}))
    np_by_ns = Counter(item.get("metadata", {}).get("namespace", "cluster") for item in network_policies)
    namespace_labels = {
        item.get("metadata", {}).get("name", ""): item.get("metadata", {}).get("labels", {})
        for item in namespaces
    }
    return {
        "nodes": summarize_nodes(nodes),
        "namespaces": {"count": len(namespaces), "podSecurityLabels": namespace_labels},
        "pods": summarize_pods(pods),
        "services": summarize_services(services),
        "networkPolicies": {"count": len(network_policies), "byNamespace": dict(np_by_ns)},
        "storage": {
            "storageClasses": [item.get("metadata", {}).get("name", "") for item in storageclasses],
            "persistentVolumes": len(pvs),
            "persistentVolumeClaims": len(pvcs),
        },
        "rbac": {"namespacedRoleObjects": len(roles), "clusterRoleObjects": len(clusterroles)},
        "gitOps": {"fluxObjects": len(flux), "tcaasClusters": [item_name(item) for item in tcaas_clusters]},
    }


def compact_counter(values, limit=40):
    counter = Counter(value for value in values if value not in (None, ""))
    return dict(counter.most_common(limit))


def image_registry(image):
    if not image:
        return ""
    return image.split("/", 1)[0] if "/" in image else "docker.io"


def container_refs(spec):
    containers = []
    containers.extend(spec.get("initContainers", []) or [])
    containers.extend(spec.get("containers", []) or [])
    return containers


def compact_rule_shape(rules):
    api_groups = Counter()
    resources = Counter()
    verbs = Counter()
    for rule in rules or []:
        for value in rule.get("apiGroups", []) or [""]:
            api_groups[value or "core"] += 1
        for value in rule.get("resources", []) or []:
            resources[value] += 1
        for value in rule.get("verbs", []) or []:
            verbs[value] += 1
    return {
        "ruleCount": len(rules or []),
        "apiGroups": dict(api_groups.most_common(30)),
        "resources": dict(resources.most_common(50)),
        "verbs": dict(verbs.most_common(30)),
    }


def compact_pod_security_signals(pod):
    spec = pod.get("spec", {}) or {}
    signals = {}
    for field in ("hostNetwork", "hostPID", "hostIPC"):
        if spec.get(field):
            signals[field] = True
    counts = Counter()
    for container in container_refs(spec):
        security_context = container.get("securityContext", {}) or {}
        resources = container.get("resources", {}) or {}
        if security_context.get("privileged"):
            counts["privilegedContainers"] += 1
        if security_context.get("allowPrivilegeEscalation") is not False:
            counts["allowPrivilegeEscalationNotFalse"] += 1
        if security_context.get("runAsNonRoot") is not True:
            counts["runAsNonRootNotTrue"] += 1
        if security_context.get("readOnlyRootFilesystem") is not True:
            counts["readOnlyRootFilesystemNotTrue"] += 1
        if not (resources.get("requests") or {}).get("cpu"):
            counts["missingCpuRequest"] += 1
        if not (resources.get("requests") or {}).get("memory"):
            counts["missingMemoryRequest"] += 1
        if not (resources.get("limits") or {}).get("cpu"):
            counts["missingCpuLimit"] += 1
        if not (resources.get("limits") or {}).get("memory"):
            counts["missingMemoryLimit"] += 1
        if not container.get("readinessProbe"):
            counts["missingReadinessProbe"] += 1
        if not container.get("livenessProbe"):
            counts["missingLivenessProbe"] += 1
    if counts:
        signals["containerCounts"] = dict(counts)
    return signals


def compact_kube_item(collection_name, item):
    metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
    spec = item.get("spec", {}) if isinstance(item, dict) else {}
    kind = item.get("kind", "") if isinstance(item, dict) else ""
    entry = {
        "kind": kind,
        "name": metadata.get("name", ""),
    }
    namespace = metadata.get("namespace")
    if namespace:
        entry["namespace"] = namespace

    if collection_name == "nodes":
        status = item.get("status", {}) or {}
        node_info = status.get("nodeInfo", {}) or {}
        labels = metadata.get("labels", {}) or {}
        entry.update(
            {
                "roles": node_roles(labels),
                "kubeletVersion": node_info.get("kubeletVersion", ""),
                "containerRuntimeVersion": node_info.get("containerRuntimeVersion", ""),
                "osImage": node_info.get("osImage", ""),
                "kernelVersion": node_info.get("kernelVersion", ""),
                "ready": any(
                    condition.get("type") == "Ready" and condition.get("status") == "True"
                    for condition in status.get("conditions", []) or []
                ),
            }
        )
    elif collection_name == "namespaces":
        labels = metadata.get("labels", {}) or {}
        entry["podSecurityLabels"] = {
            key: value
            for key, value in labels.items()
            if key.startswith("pod-security.kubernetes.io/")
        }
        entry["phase"] = (item.get("status", {}) or {}).get("phase", "")
    elif collection_name == "pods_all":
        containers = container_refs(spec)
        entry.update(
            {
                "phase": (item.get("status", {}) or {}).get("phase", ""),
                "serviceAccountName": spec.get("serviceAccountName", ""),
                "containerCount": len(containers),
                "imageRegistries": sorted({image_registry(container.get("image", "")) for container in containers if container.get("image")}),
            }
        )
        signals = compact_pod_security_signals(item)
        if signals:
            entry["securitySignals"] = signals
    elif collection_name == "workloads_all":
        template_spec = ((spec.get("template") or {}).get("spec") or {})
        containers = container_refs(template_spec)
        entry.update(
            {
                "replicas": spec.get("replicas", ""),
                "serviceAccountName": template_spec.get("serviceAccountName", ""),
                "containerCount": len(containers),
                "imageRegistries": sorted({image_registry(container.get("image", "")) for container in containers if container.get("image")}),
            }
        )
    elif collection_name == "services_all":
        entry.update(
            {
                "type": spec.get("type", "ClusterIP"),
                "portCount": len(spec.get("ports", []) or []),
            }
        )
    elif collection_name == "networkpolicies_all":
        entry.update(
            {
                "policyTypes": spec.get("policyTypes", []),
                "ingressRuleCount": len(spec.get("ingress", []) or []),
                "egressRuleCount": len(spec.get("egress", []) or []),
            }
        )
    elif collection_name == "serviceaccounts_all":
        entry.update(
            {
                "automountServiceAccountToken": spec.get("automountServiceAccountToken", ""),
            }
        )
    elif collection_name in {"roles_all", "clusterroles"}:
        if kind in {"Role", "ClusterRole"}:
            entry.update(compact_rule_shape(item.get("rules", []) or []))
        elif kind in {"RoleBinding", "ClusterRoleBinding"}:
            subjects = item.get("subjects", []) or []
            entry.update(
                {
                    "roleRefKind": (item.get("roleRef", {}) or {}).get("kind", ""),
                    "roleRefName": (item.get("roleRef", {}) or {}).get("name", ""),
                    "subjectCount": len(subjects),
                    "subjectKinds": compact_counter(subject.get("kind", "") for subject in subjects),
                    "subjectNamespaces": compact_counter(subject.get("namespace", "") for subject in subjects),
                }
            )
    elif collection_name == "storageclasses":
        entry.update(
            {
                "provisioner": item.get("provisioner", ""),
                "reclaimPolicy": item.get("reclaimPolicy", ""),
                "volumeBindingMode": item.get("volumeBindingMode", ""),
                "allowVolumeExpansion": item.get("allowVolumeExpansion", ""),
            }
        )
    elif collection_name == "persistentvolumes":
        entry.update(
            {
                "phase": (item.get("status", {}) or {}).get("phase", ""),
                "storageClassName": spec.get("storageClassName", ""),
                "accessModes": spec.get("accessModes", []),
            }
        )
    elif collection_name == "persistentvolumeclaims_all":
        entry.update(
            {
                "phase": (item.get("status", {}) or {}).get("phase", ""),
                "storageClassName": spec.get("storageClassName", ""),
                "accessModes": spec.get("accessModes", []),
            }
        )
    elif collection_name == "crds":
        names = spec.get("names", {}) or {}
        versions = spec.get("versions", []) or []
        entry.update(
            {
                "group": spec.get("group", ""),
                "scope": spec.get("scope", ""),
                "kindName": names.get("kind", ""),
                "plural": names.get("plural", ""),
                "versions": [
                    {
                        "name": version.get("name", ""),
                        "served": version.get("served", ""),
                        "storage": version.get("storage", ""),
                    }
                    for version in versions
                ],
            }
        )
    elif collection_name == "flux_sources":
        entry.update(
            {
                "suspend": spec.get("suspend", ""),
                "interval": spec.get("interval", ""),
            }
        )
    elif collection_name == "tcaas_clusters":
        entry["provider"] = spec.get("provider", "")

    return {key: value for key, value in entry.items() if value not in ("", None, [], {})}


def compact_collection_result(name, result, item_limit=1000):
    compact = {
        "args": result.get("args", []),
        "returnCode": result.get("returnCode"),
        "elapsedSeconds": result.get("elapsedSeconds"),
        "stderr": result.get("stderr", ""),
        "format": result.get("format", ""),
    }
    if result.get("format") == "text":
        compact["textPreview"] = preview_text(result.get("text", ""), limit=2000)
        return compact
    items = kitems(result)
    if not items:
        if isinstance(result.get("json"), dict):
            compact["kind"] = result["json"].get("kind", "")
            compact["apiVersion"] = result["json"].get("apiVersion", "")
        return compact

    compact["itemCount"] = len(items)
    compact["kindCounts"] = compact_counter(item.get("kind", "") for item in items)
    compact["namespaceCounts"] = compact_counter(
        (item.get("metadata", {}) or {}).get("namespace", "cluster") for item in items
    )
    selected = items[:item_limit]
    compact["itemLimit"] = item_limit
    compact["itemsTruncated"] = len(items) > len(selected)
    compact["items"] = [compact_kube_item(name, item) for item in selected]
    if name == "pods_all":
        compact["summary"] = summarize_pods(items)
    elif name == "nodes":
        compact["summary"] = summarize_nodes(items)
    elif name == "services_all":
        compact["summary"] = summarize_services(items)
    return compact


def write_compact_kubectl_collections(collections, out_dir, item_limit=1000):
    compact = {
        "schema": "tcaas_marcel1_compact_kubectl_collections_v1",
        "generatedAt": now(),
        "itemLimit": item_limit,
        "collections": {},
    }
    for name, _args, _required in KUBECTL_COLLECTIONS:
        if name not in collections:
            continue
        compact["collections"][name] = compact_collection_result(name, collections[name], item_limit=item_limit)
    path = Path(out_dir) / "marcel1_cluster_collections_compact.json"
    path.write_text(json.dumps(compact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path), compact


def write_marcel1_markdown(result, out_dir):
    summary = result["summary"]
    lines = [
        "# marcel-1 Live Cluster Collection",
        "",
        f"Generated: `{result['generatedAt']}`",
        f"Context: `{result['context']}`",
        f"Kubeconfig: `{result['kubeconfig']}`",
        "",
        "## Command Status",
        "",
    ]
    for name, status in result["commandStatus"].items():
        marker = "ok" if status["returnCode"] == 0 else "failed"
        lines.append(f"- `{name}`: {marker}, returnCode={status['returnCode']}, elapsed={status['elapsedSeconds']}s")
    lines.extend(
        [
            "",
            "## Cluster Facts",
            "",
            f"- Nodes: {summary['nodes']['ready']}/{summary['nodes']['count']} ready",
            f"- Node roles: `{json.dumps(summary['nodes']['roles'], sort_keys=True)}`",
            f"- Kubelet versions: `{json.dumps(summary['nodes']['kubeletVersions'], sort_keys=True)}`",
            f"- Operating systems: `{json.dumps(summary['nodes']['operatingSystems'], sort_keys=True)}`",
            f"- Namespaces: {summary['namespaces']['count']}",
            f"- Pods: {summary['pods']['count']} with phases `{json.dumps(summary['pods']['phases'], sort_keys=True)}`",
            f"- Services: {summary['services']['count']} with types `{json.dumps(summary['services']['types'], sort_keys=True)}`",
            f"- NetworkPolicies: {summary['networkPolicies']['count']}",
            f"- StorageClasses: `{', '.join(summary['storage']['storageClasses'])}`",
            f"- PV/PVC: {summary['storage']['persistentVolumes']} PVs, {summary['storage']['persistentVolumeClaims']} PVCs",
            f"- RBAC objects: {summary['rbac']['namespacedRoleObjects']} namespaced, {summary['rbac']['clusterRoleObjects']} cluster-scoped",
            f"- T-CaaS cluster objects: `{', '.join(summary['gitOps']['tcaasClusters'])}`",
            "",
            "## Pod Security Signals",
            "",
        ]
    )
    security = summary["pods"]["securityFindings"]
    for key, value in sorted(security["counts"].items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Notes", ""])
    lines.append("- This collection is read-only and redacts kubeconfig material, tokens, secret data, env values, and address fields.")
    lines.append("- Findings are evidence for analysis, not automatic compliance claims. Some system components legitimately require elevated networking or host access.")
    if result.get("compactCollections"):
        lines.append(f"- Compact collection details: `{result['compactCollections']}`")
    if result.get("rawCollectionsWritten"):
        lines.append(f"- Raw collection files were written under `{RAW_COLLECTION_DIRNAME}/`; keep them out of Git unless explicitly needed.")
    md_path = Path(out_dir) / "marcel1_cluster_summary.md"
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return str(md_path)


def collect_marcel1_cluster(
    context,
    kubeconfig,
    out_dir,
    kubectl="kubectl",
    xdg_runtime_dir="/tmp/xdg-runtime-a92615428",
    server=None,
    tls_server_name=None,
    no_proxy=None,
    api_tunnel_jump=None,
    api_tunnel_target=None,
    api_tunnel_target_port=6443,
    api_tunnel_local_port=0,
    ssh="ssh",
    write_raw_collections=False,
    compact_limit=1000,
):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_out = out / RAW_COLLECTION_DIRNAME
    if write_raw_collections:
        raw_out.mkdir(exist_ok=True)
    collections = {}
    command_status = {}
    tunnel = None
    tunnel_info = None
    if api_tunnel_jump and api_tunnel_target:
        tunnel, server = open_ssh_tunnel(
            ssh,
            api_tunnel_jump,
            api_tunnel_target,
            api_tunnel_target_port,
            local_port=api_tunnel_local_port,
        )
        tunnel_info = {
            "jumpHost": api_tunnel_jump,
            "targetHost": "<redacted-address>",
            "targetPort": api_tunnel_target_port,
            "server": server,
        }
        no_proxy = no_proxy or "127.0.0.1,localhost"
    try:
        for name, args, _required in KUBECTL_COLLECTIONS:
            result = run_kubectl_json(
                kubectl,
                context,
                kubeconfig,
                xdg_runtime_dir,
                args,
                server=server,
                tls_server_name=tls_server_name,
                no_proxy=no_proxy,
            )
            collections[name] = result
            command_status[name] = {
                "returnCode": result.get("returnCode"),
                "elapsedSeconds": result.get("elapsedSeconds"),
                "stderr": result.get("stderr", ""),
            }
            if write_raw_collections:
                (raw_out / f"{name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        close_process(tunnel)

    summary = summarize_collection(collections)
    compact_path, _compact = write_compact_kubectl_collections(collections, out, item_limit=compact_limit)
    result = {
        "schema": "tcaas_marcel1_cluster_collection_v1",
        "generatedAt": now(),
        "context": context,
        "kubeconfig": Path(kubeconfig).name if kubeconfig else "",
        "kubectl": kubectl,
        "server": server or "",
        "tlsServerName": tls_server_name or "",
        "apiTunnel": tunnel_info,
        "compactCollections": compact_path,
        "compactLimit": compact_limit,
        "rawCollectionsWritten": write_raw_collections,
        "commandStatus": command_status,
        "summary": summary,
    }
    json_path = out / "marcel1_cluster_summary.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = write_marcel1_markdown(result, out)
    result["json"] = str(json_path)
    result["markdown"] = md_path
    return result


def compact_existing_marcel1_cluster(in_dir, out_dir=None, compact_limit=1000, remove_raw=False):
    source = Path(in_dir)
    out = Path(out_dir) if out_dir else source
    out.mkdir(parents=True, exist_ok=True)
    previous_summary = {}
    previous_summary_path = source / "marcel1_cluster_summary.json"
    if previous_summary_path.exists():
        try:
            previous_summary = json.loads(previous_summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous_summary = {}
    collections = {}
    command_status = {}
    removed = []
    missing = []
    for name, _args, _required in KUBECTL_COLLECTIONS:
        path = source / f"{name}.json"
        if not path.exists():
            missing.append(name)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        collections[name] = data
        command_status[name] = {
            "returnCode": data.get("returnCode"),
            "elapsedSeconds": data.get("elapsedSeconds"),
            "stderr": data.get("stderr", ""),
        }
    if not collections:
        raise ValueError(f"No kubectl collection JSON files found in {source}")

    compact_path, _compact = write_compact_kubectl_collections(collections, out, item_limit=compact_limit)
    summary = summarize_collection(collections)
    result = {
        "schema": "tcaas_marcel1_cluster_collection_v1",
        "generatedAt": now(),
        "context": previous_summary.get("context", "from-existing-capture"),
        "kubeconfig": previous_summary.get("kubeconfig", ""),
        "kubectl": previous_summary.get("kubectl", ""),
        "server": previous_summary.get("server", ""),
        "tlsServerName": previous_summary.get("tlsServerName", ""),
        "apiTunnel": previous_summary.get("apiTunnel"),
        "compactCollections": compact_path,
        "compactLimit": compact_limit,
        "rawCollectionsWritten": False,
        "sourceDirectory": str(source),
        "missingCollections": missing,
        "commandStatus": command_status,
        "summary": summary,
    }
    json_path = out / "marcel1_cluster_summary.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = write_marcel1_markdown(result, out)

    if remove_raw:
        for name in collections:
            path = source / f"{name}.json"
            if path.exists():
                path.unlink()
                removed.append(str(path))

    return {
        "json": str(json_path),
        "markdown": md_path,
        "compactCollections": compact_path,
        "collectionsCompacted": len(collections),
        "missingCollections": missing,
        "removedRawFiles": removed,
    }


def node_internal_targets(nodes_doc, prefer_ipv6=True):
    targets = []
    for node in nodes_doc.get("items", []) or []:
        metadata = node.get("metadata", {})
        status = node.get("status", {})
        addresses = status.get("addresses", []) or []
        internal = [item.get("address", "") for item in addresses if item.get("type") == "InternalIP"]
        host = ""
        if prefer_ipv6:
            host = next((value for value in internal if ":" in value), "")
        if not host:
            host = next((value for value in internal if value), "")
        labels = metadata.get("labels", {})
        targets.append(
            {
                "name": metadata.get("name", ""),
                "host": host,
                "roles": node_roles(labels),
                "providerID": node.get("spec", {}).get("providerID", ""),
                "kubeletVersion": status.get("nodeInfo", {}).get("kubeletVersion", ""),
                "osImage": status.get("nodeInfo", {}).get("osImage", ""),
                "kernelVersion": status.get("nodeInfo", {}).get("kernelVersion", ""),
            }
        )
    return [target for target in targets if target.get("name") and target.get("host")]


def parse_node_specs(values):
    specs = []
    for value in values or []:
        parts = str(value).split("=", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(f"Invalid --node value {value!r}; expected name=host")
        specs.append({"name": parts[0], "host": parts[1], "roles": []})
    return specs


def run_node_command(ssh, jump_host, user, host, command_text, timeout=45, connect_timeout=10):
    target = f"{user}@{host}" if user else host
    remote = f"set -o pipefail 2>/dev/null; {command_text}"
    command = [
        ssh,
        "-6" if ":" in host else "-4",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
        "-o",
        "StrictHostKeyChecking=no",
    ]
    if jump_host:
        command.extend(["-J", jump_host])
    command.extend([target, "sh", "-lc", shlex.quote(remote)])
    started = time.time()
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        return {
            "returnCode": completed.returncode,
            "elapsedSeconds": round(time.time() - started, 3),
            "stdout": sanitize_remote_text(completed.stdout),
            "stderr": sanitize_remote_text(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returnCode": 124,
            "elapsedSeconds": round(time.time() - started, 3),
            "stdout": sanitize_remote_text(exc.stdout or ""),
            "stderr": f"timeout after {timeout}s",
        }


def summarize_node_shell(node_results):
    summary = {
        "nodesAttempted": len(node_results),
        "nodesWithAnySuccess": 0,
        "commandTotals": Counter(),
        "failedCommands": Counter(),
        "skippedCommands": 0,
        "nodeFacts": [],
    }
    for node in node_results:
        commands = node.get("commands", {})
        ok_count = sum(1 for item in commands.values() if item.get("returnCode") == 0)
        if ok_count:
            summary["nodesWithAnySuccess"] += 1
        for name, result in commands.items():
            summary["commandTotals"][name] += 1
            if result.get("returnCode") != 0:
                summary["failedCommands"][name] += 1
        service_stdout = commands.get("service_active", {}).get("stdout", "").strip().splitlines()
        skipped_commands = len(node.get("skippedCommands", []))
        summary["skippedCommands"] += skipped_commands
        fact = {
            "name": node.get("name"),
            "roles": node.get("roles", []),
            "kubeletVersion": node.get("kubeletVersion", ""),
            "osImage": node.get("osImage", ""),
            "kernelVersion": node.get("kernelVersion", ""),
            "shellAvailable": node.get("shellAvailable", False),
            "successfulCommands": ok_count,
            "failedCommands": len(commands) - ok_count,
            "skippedCommands": skipped_commands,
            "shellBlocker": node.get("shellBlocker", ""),
            "serviceActiveLines": service_stdout[:8],
        }
        summary["nodeFacts"].append(fact)
    summary["commandTotals"] = dict(summary["commandTotals"])
    summary["failedCommands"] = dict(summary["failedCommands"])
    return summary


def write_node_shell_markdown(result, out_dir):
    lines = [
        "# marcel-1 Node Shell Collection",
        "",
        f"Generated: `{result['generatedAt']}`",
        f"SSH user: `{result['sshUser']}`",
        f"Jump host: `{result['jumpHost']}`",
        "",
        "## Summary",
        "",
        f"- Nodes attempted: {result['summary']['nodesAttempted']}",
        f"- Nodes with at least one successful command: {result['summary']['nodesWithAnySuccess']}",
        "",
        "## Node Facts",
        "",
    ]
    for fact in result["summary"]["nodeFacts"]:
        lines.append(f"### {fact['name']}")
        lines.append("")
        lines.append(f"- Roles: `{', '.join(fact.get('roles') or [])}`")
        lines.append(f"- Kubelet: `{fact.get('kubeletVersion') or 'n/a'}`")
        lines.append(f"- OS: `{fact.get('osImage') or 'n/a'}`")
        lines.append(f"- Kernel: `{fact.get('kernelVersion') or 'n/a'}`")
        lines.append(f"- Shell available: `{fact.get('shellAvailable')}`")
        lines.append(f"- Commands ok/failed/skipped: {fact['successfulCommands']}/{fact['failedCommands']}/{fact['skippedCommands']}")
        if fact.get("shellBlocker"):
            lines.append(f"- Shell blocker: `{fact['shellBlocker'][:300]}`")
        if fact.get("serviceActiveLines"):
            lines.append(f"- Service active output: `{'; '.join(fact['serviceActiveLines'])}`")
        lines.append("")
    lines.extend(["## Command Failures", ""])
    if result["summary"]["failedCommands"]:
        lines.extend(f"- {name}: {count}" for name, count in sorted(result["summary"]["failedCommands"].items()))
    else:
        lines.append("- none")
    lines.extend(["", "## Notes", ""])
    lines.append("- This collection uses read-only shell commands and stores redacted output.")
    lines.append("- IP addresses, MAC addresses, JWT-like tokens, and obvious secret values are redacted before writing files.")
    lines.append("- Private key material, kubeconfigs, and Kubernetes PKI files are not read.")
    md_path = Path(out_dir) / "marcel1_node_shell_summary.md"
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return str(md_path)


def collect_marcel1_node_shell(
    out_dir,
    nodes,
    context=None,
    kubeconfig=None,
    kubectl="kubectl",
    xdg_runtime_dir="/tmp/xdg-runtime-a92615428",
    server=None,
    tls_server_name=None,
    no_proxy=None,
    api_tunnel_jump=None,
    api_tunnel_target=None,
    api_tunnel_target_port=6443,
    api_tunnel_local_port=0,
    ssh="ssh",
    jump_host="schiff-ztn-jump",
    ssh_user="debug",
    command_timeout=45,
    connect_timeout=10,
):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tunnel = None
    tunnel_info = None
    targets = parse_node_specs(nodes)
    if api_tunnel_jump and api_tunnel_target:
        tunnel, server = open_ssh_tunnel(
            ssh,
            api_tunnel_jump,
            api_tunnel_target,
            api_tunnel_target_port,
            local_port=api_tunnel_local_port,
        )
        tunnel_info = {
            "jumpHost": api_tunnel_jump,
            "targetHost": "<redacted-address>",
            "targetPort": api_tunnel_target_port,
            "server": server,
        }
        no_proxy = no_proxy or "127.0.0.1,localhost"
    try:
        if not targets:
            if not kubeconfig:
                raise ValueError("Provide --node name=host entries or --kubeconfig for node discovery.")
            nodes_doc = run_kubectl_raw_json(
                kubectl,
                context,
                kubeconfig,
                xdg_runtime_dir,
                ["get", "nodes", "-o", "json"],
                server=server,
                tls_server_name=tls_server_name,
                no_proxy=no_proxy,
            )
            targets = node_internal_targets(nodes_doc)
    finally:
        close_process(tunnel)

    node_results = []
    for target in targets:
        commands = {}
        preflight = run_node_command(
            ssh,
            jump_host,
            ssh_user,
            target["host"],
            "true",
            timeout=min(command_timeout, 10),
            connect_timeout=connect_timeout,
        )
        commands["ssh_preflight"] = preflight
        shell_available = preflight.get("returnCode") == 0
        skipped_commands = []
        shell_blocker = ""
        if shell_available:
            for name, command_text in NODE_SHELL_COMMANDS:
                commands[name] = run_node_command(
                    ssh,
                    jump_host,
                    ssh_user,
                    target["host"],
                    command_text,
                    timeout=command_timeout,
                    connect_timeout=connect_timeout,
                )
        else:
            skipped_commands = [name for name, _command_text in NODE_SHELL_COMMANDS]
            shell_blocker = (preflight.get("stderr") or preflight.get("stdout") or "").strip()
        record = {
            "name": target.get("name"),
            "host": "<redacted-address>",
            "roles": target.get("roles", []),
            "providerID": sanitize_remote_text(target.get("providerID", "")),
            "kubeletVersion": target.get("kubeletVersion", ""),
            "osImage": target.get("osImage", ""),
            "kernelVersion": target.get("kernelVersion", ""),
            "shellAvailable": shell_available,
            "shellBlocker": shell_blocker[:5000] if not shell_available else "",
            "skippedCommands": skipped_commands,
            "commands": commands,
        }
        node_results.append(record)
        safe_name = safe_slug(target.get("name", "node"))
        (out / f"{safe_name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    result = {
        "schema": "tcaas_marcel1_node_shell_collection_v1",
        "generatedAt": now(),
        "sshUser": ssh_user,
        "jumpHost": jump_host,
        "apiTunnel": tunnel_info,
        "commandNames": ["ssh_preflight", *[name for name, _command_text in NODE_SHELL_COMMANDS]],
        "summary": summarize_node_shell(node_results),
        "nodes": node_results,
    }
    json_path = out / "marcel1_node_shell_summary.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = write_node_shell_markdown(result, out)
    result["json"] = str(json_path)
    result["markdown"] = md_path
    return result


def parse_mondoo_summary(path):
    summary = {}
    if not path.exists():
        return summary
    current_table = None
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        total = re.match(r"- \*\*Total findings\*\*: (\d+)", line)
        space = re.match(r"- \*\*Space\*\*: (.+)", line)
        critical_high = re.match(r"## Critical \+ High Findings: (\d+)", line)
        if total:
            summary["totalFindings"] = int(total.group(1))
        if space:
            summary["space"] = space.group(1)
        if critical_high:
            summary["criticalHighFindings"] = int(critical_high.group(1))
        if line.startswith("## By "):
            current_table = normalize_title(line.removeprefix("## By "))
            summary[current_table] = {}
            continue
        table_row = re.match(r"\| ([^|]+) \| (\d+) \|", line)
        if current_table and table_row and table_row.group(1).lower() not in {"type", "rating", "state"}:
            summary[current_table][table_row.group(1).strip()] = int(table_row.group(2))
    return summary


def categorize_mondoo_check(title):
    haystack = title.casefold()
    categories = []
    for category, needles in MONDOO_CATEGORY_RULES.items():
        for needle in needles:
            if needle.casefold() in haystack:
                categories.append(category)
                break
    return categories or ["general_security"]


def parse_mondoo_policy_checks(path):
    checks = []
    if not path.exists():
        return checks
    current = None
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.rstrip()
        heading = re.match(r"^### (.+)$", line)
        if heading:
            if current:
                checks.append(current)
            current = {"title": heading.group(1).strip(), "categories": categorize_mondoo_check(heading.group(1)), "sampleAssets": []}
            continue
        if not current:
            continue
        count = re.match(r"- \*\*Count\*\*: (\d+) \| \*\*Ratings\*\*: (.+?) \| \*\*Assets\*\*: (\d+)", line)
        if count:
            current["count"] = int(count.group(1))
            current["ratings"] = count.group(2)
            current["assets"] = int(count.group(3))
            continue
        risk = re.match(r"- \*\*Risk scores\*\*: (.+)", line)
        if risk:
            current["riskScores"] = risk.group(1)
            continue
        sample = re.match(r"- \*\*Sample assets\*\*: (.+)", line)
        if sample:
            current["sampleAssets"] = [item.strip() for item in sample.group(1).split(",")[:10]]
    if current:
        checks.append(current)
    return checks


def mondoo_check_id(check):
    title = check.get("title", "")
    digest = sha1(title.encode("utf-8")).hexdigest()[:12]
    return f"mondoo-check-{digest}"


def compact_mondoo_check(check):
    return {
        "title": check.get("title", ""),
        "categories": check.get("categories", []),
        "count": check.get("count", 0),
        "ratings": check.get("ratings", ""),
        "assets": check.get("assets", 0),
        "riskScores": check.get("riskScores", ""),
        "sampleAssets": (check.get("sampleAssets", []) or [])[:5],
    }


def soc_text_for_match(answer):
    req = answer.get("requirement", {})
    parts = [
        answer.get("sheet", {}).get("title", ""),
        answer.get("sheet", {}).get("manifestName", ""),
        req.get("section", ""),
        req.get("text", ""),
        req.get("details", ""),
        req.get("motivation", ""),
    ]
    return " ".join(parts).casefold()


def matched_mondoo_categories(answer):
    haystack = soc_text_for_match(answer)
    matches = []
    for category, hints in SOC_CATEGORY_HINTS.items():
        if any(hint.casefold() in haystack for hint in hints):
            matches.append(category)
    return matches


def cross_reference_mondoo_socs(answers_path, mondoo_dir, out_dir, console_url="https://console.mondoo.telekom.de"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    mondoo_dir = Path(mondoo_dir)
    summary = parse_mondoo_summary(mondoo_dir / "00-summary.md")
    checks = parse_mondoo_policy_checks(mondoo_dir / "01-policy-checks.md")
    check_catalog = {mondoo_check_id(check): compact_mondoo_check(check) for check in checks}
    check_ids_by_title = {check.get("title", ""): mondoo_check_id(check) for check in checks}
    checks_by_category = defaultdict(list)
    for check in checks:
        for category in check.get("categories", []):
            checks_by_category[category].append(check)
    for category in checks_by_category:
        checks_by_category[category].sort(key=lambda item: item.get("count", 0), reverse=True)

    answers = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    matches = []
    for answer in answers.get("answers", []):
        categories = matched_mondoo_categories(answer)
        if not categories:
            continue
        matched_checks = []
        for category in categories:
            matched_checks.extend(checks_by_category.get(category, [])[:5])
        dedup_ids = []
        seen = set()
        for check in matched_checks:
            title = check.get("title", "")
            if title and title not in seen:
                check_id = check_ids_by_title.get(title)
                if check_id:
                    dedup_ids.append(check_id)
                seen.add(title)
        if not dedup_ids:
            continue
        matches.append(
            {
                "answerKey": answer.get("answerKey"),
                "sheet": answer.get("sheet", {}).get("title", ""),
                "number": answer.get("requirement", {}).get("number", ""),
                "requirementId": answer.get("requirement", {}).get("requirementId", ""),
                "categories": categories,
                "mondooCheckIds": dedup_ids[:8],
                "noteReferenceText": (
                    "References: " + console_url + " (Mondoo marcel-1 policy results); "
                    "use GitLab/GitHub/Confluence links from answer.evidence for portal evidence."
                ),
            }
        )

    result = {
        "schema": "tcaas_mondoo_soc_cross_reference_v2",
        "generatedAt": now(),
        "answers": str(answers_path),
        "mondooDir": str(mondoo_dir),
        "consoleUrl": console_url,
        "summary": summary,
        "checkCount": len(checks),
        "categoryCounts": {category: len(items) for category, items in sorted(checks_by_category.items())},
        "checks": check_catalog,
        "matches": matches,
    }
    json_path = out / "mondoo_soc_crossreference.json"
    md_path = out / "mondoo_soc_crossreference.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Mondoo to SoC Cross-Reference",
        "",
        f"Generated: `{result['generatedAt']}`",
        f"Mondoo console: {console_url}",
        "",
        "## Summary",
        "",
        f"- Checks parsed: {len(checks)}",
        f"- SoC rows with Mondoo-relevant matches: {len(matches)}",
        f"- Total findings: {summary.get('totalFindings', 'n/a')}",
        f"- Critical + high findings: {summary.get('criticalHighFindings', 'n/a')}",
        "",
        "## Categories",
        "",
    ]
    lines.extend(f"- {category}: {count}" for category, count in sorted(result["categoryCounts"].items()))
    lines.extend(["", "## Matched SoC Rows", ""])
    for match in matches[:250]:
        lines.append(f"### {match['sheet']} Req {match['number']} ({match['requirementId']})")
        lines.append("")
        lines.append(f"- Answer key: `{match['answerKey']}`")
        lines.append(f"- Categories: `{', '.join(match['categories'])}`")
        for check_id in match["mondooCheckIds"][:5]:
            check = check_catalog.get(check_id, {})
            lines.append(f"- Mondoo check: {check.get('title')} (count={check.get('count')}, ratings={check.get('ratings')})")
        lines.append("")
    if len(matches) > 250:
        lines.append(f"- ... {len(matches) - 250} more matches in JSON")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "matchCount": len(matches), "checkCount": len(checks)}


def preview_text(value, limit=240):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def compact_workbook_row(row):
    evidence = row.get("suggestedEvidence", []) or []
    return {
        "answerKey": row.get("answerKey", ""),
        "sheet": row.get("sheet", ""),
        "manifestName": row.get("manifestName", ""),
        "number": row.get("number", ""),
        "requirementId": row.get("requirementId", ""),
        "topics": row.get("topics", []),
        "currentStatement": row.get("currentStatement", ""),
        "draftStatement": row.get("draftStatement", ""),
        "researchStatus": row.get("researchStatus", ""),
        "suggestedEvidenceCount": len(evidence),
        "suggestedEvidenceSample": evidence[:3],
        "requirementTextPreview": preview_text(row.get("requirementText", "")),
    }


def write_soc_workbook(workbook, out_dir, write_full_json=False, write_jsonl=False):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "soc_research_workbook.json"
    full_json_path = out / "soc_research_workbook.full.json"
    jsonl_path = out / "soc_research_workbook.jsonl"
    tsv_path = out / "soc_research_workbook.tsv"
    md_path = out / "soc_research_summary.md"
    sheet_counts = Counter(row["sheet"] for row in workbook["rows"])
    status_counts = Counter(row["researchStatus"] for row in workbook["rows"])
    compact_rows = [compact_workbook_row(row) for row in workbook["rows"]]
    compact_workbook = {
        "schema": "tcaas_soc_research_workbook_compact_v1",
        "generatedAt": workbook["generatedAt"],
        "source": workbook.get("source", ""),
        "rowCount": len(workbook["rows"]),
        "statusCounts": dict(status_counts),
        "sheetCounts": dict(sheet_counts),
        "fullRowsOmitted": not write_full_json,
        "jsonlWritten": write_jsonl,
        "rows": compact_rows,
    }
    json_path.write_text(json.dumps(compact_workbook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if write_full_json:
        full_json_path.write_text(json.dumps(workbook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if write_jsonl:
        with jsonl_path.open("w", encoding="utf-8") as handle:
            for row in compact_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["answerKey", "sheet", "number", "requirementId", "topics", "draftStatement", "researchStatus", "requirementText"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in workbook["rows"]:
            output = {}
            for key in fieldnames:
                value = ";".join(row[key]) if key == "topics" else row.get(key, "")
                output[key] = "[empty]" if key == "requirementText" and not value else value
            writer.writerow(output)
    lines = ["# SoC Research Workbook Summary", "", f"Generated: `{workbook['generatedAt']}`", ""]
    lines.extend(
        [
            f"- Rows: {len(workbook['rows'])}",
            f"- Compact JSON: `{json_path}`",
            f"- TSV: `{tsv_path}`",
            f"- Full JSON written: `{write_full_json}`",
            f"- JSONL written: `{write_jsonl}`",
            "",
        ]
    )
    lines.extend(["## Status Counts", ""])
    lines.extend(f"- {status}: {count}" for status, count in sorted(status_counts.items()))
    lines.extend(["", "## Sheet Counts", ""])
    lines.extend(f"- {sheet}: {count}" for sheet, count in sheet_counts.most_common())
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    result = {"json": str(json_path), "tsv": str(tsv_path), "markdown": str(md_path)}
    if write_full_json:
        result["fullJson"] = str(full_json_path)
    if write_jsonl:
        result["jsonl"] = str(jsonl_path)
    return result


class CdpClient:
    def __init__(self, port, url_contains=None):
        self.port = port
        targets = requests.get(f"http://127.0.0.1:{port}/json/list", timeout=10).json()
        pages = [target for target in targets if target.get("type") == "page"]
        if not pages:
            raise RuntimeError(f"No browser page target found on port {port}")
        self.target = pages[0]
        if url_contains:
            for page in pages:
                if url_contains in page.get("url", ""):
                    self.target = page
                    break
        self.ws = websocket.create_connection(self.target["webSocketDebuggerUrl"], timeout=30, suppress_origin=True)
        self.next_id = 1

    def close(self):
        self.ws.close()

    def call(self, method, params=None):
        msg_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") != msg_id:
                continue
            if "error" in message:
                raise RuntimeError(f"{method} failed: {message['error']}")
            return message.get("result", {})

    def evaluate(self, expression, await_promise=False):
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True,
            },
        )
        if "exceptionDetails" in result:
            raise RuntimeError(json.dumps(result["exceptionDetails"], indent=2))
        return result.get("result", {}).get("value")

    def evaluate_json(self, expression, await_promise=False):
        value = self.evaluate(f"JSON.stringify(({expression}))", await_promise=await_promise)
        return json.loads(value)


def filename_from_url(url, default="download.bin"):
    path = unquote(urlparse(url).path)
    name = Path(path).name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name) or default


def safe_slug(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    value = value.strip("._")
    return value[:90] or "page"


CAPTURE_PAGE_SCRIPT = r"""(() => {
  const clean = (value) => (value || "").replace(/\s+/g, " ").trim();
  const links = Array.from(document.links).map((a) => ({
    text: clean(a.innerText || a.textContent || ""),
    title: a.title || "",
    href: a.href,
    download: a.getAttribute("download") || "",
    type: a.type || ""
  }));
  const attachments = links.filter((link) =>
    /download\/attachments|attachments|\.pdf($|[?#])|preview|viewfile/i.test(link.href + " " + link.text + " " + link.title)
  );
  return {
    href: location.href,
    title: document.title,
    capturedAt: new Date().toISOString(),
    readyState: document.readyState,
    text: document.body ? document.body.innerText : "",
    html: document.documentElement ? document.documentElement.outerHTML : "",
    links,
    attachments
  };
})()"""


FETCH_ATTACHMENT_SCRIPT = r"""async (url) => {
  const response = await fetch(url, {credentials: "include"});
  const contentType = response.headers.get("content-type") || "";
  const contentDisposition = response.headers.get("content-disposition") || "";
  const buffer = await response.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return {
    ok: response.ok,
    status: response.status,
    url: response.url,
    contentType,
    contentDisposition,
    base64: btoa(binary)
  };
}"""


def capture_browser_page(port, out_dir, slug, url_contains=None, download_attachments=False, proxy=None, navigate_url=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    attachments_dir = out / "attachments"
    attachments_dir.mkdir(exist_ok=True)
    cdp = CdpClient(port, url_contains=url_contains)
    try:
        if navigate_url:
            cdp.call("Page.navigate", {"url": navigate_url})
        for _ in range(30):
            state = cdp.evaluate_json("(() => ({readyState: document.readyState, href: location.href}))()")
            if state.get("readyState") == "complete":
                break
            time.sleep(1)
        data = cdp.evaluate_json(CAPTURE_PAGE_SCRIPT)
        html_path = out / f"{slug}.html"
        text_path = out / f"{slug}.txt"
        json_path = out / f"{slug}.json"
        links_path = out / f"{slug}_links.json"
        html_path.write_text(data["html"], encoding="utf-8")
        text_path.write_text(data["text"], encoding="utf-8")
        links_path.write_text(json.dumps(data["links"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        downloaded = []
        if download_attachments:
            cookies = cdp.call("Network.getAllCookies").get("cookies", [])
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(
                    cookie.get("name"),
                    cookie.get("value"),
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                )
            proxies = {"http": proxy, "https": proxy} if proxy else None
            seen = set()
            for attachment in data.get("attachments", []):
                href = attachment.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)
                try:
                    response = session.get(href, timeout=90, allow_redirects=True, proxies=proxies)
                    if not response.ok:
                        downloaded.append({"href": href, "ok": False, "status": response.status_code})
                        continue
                    suffix = ".bin"
                    content_type = response.headers.get("content-type", "")
                    if "pdf" in content_type.lower() or ".pdf" in href.lower():
                        suffix = ".pdf"
                    name = filename_from_url(response.url or href)
                    if "." not in Path(name).name:
                        name += suffix
                    target = attachments_dir / name
                    counter = 1
                    while target.exists():
                        target = attachments_dir / f"{Path(name).stem}-{counter}{Path(name).suffix}"
                        counter += 1
                    target.write_bytes(response.content)
                    downloaded.append(
                        {
                            "href": href,
                            "saved": str(target),
                            "bytes": target.stat().st_size,
                            "contentType": content_type,
                        }
                    )
                except Exception as exc:
                    downloaded.append({"href": href, "ok": False, "error": str(exc)})
        data["downloadedAttachments"] = downloaded
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {
            "json": str(json_path),
            "html": str(html_path),
            "text": str(text_path),
            "links": str(links_path),
            "attachmentCount": len(data.get("attachments", [])),
            "downloadedAttachments": downloaded,
        }
    finally:
        cdp.close()


def capture_browser_links(port, links_json, out_dir, include_regex, limit=None, proxy=None):
    links = json.loads(Path(links_json).read_text(encoding="utf-8"))
    pattern = re.compile(include_regex, re.IGNORECASE)
    selected = []
    seen = set()
    for link in links:
        label = link.get("text") or link.get("title") or link.get("href", "")
        href = link.get("href", "")
        if not href or href in seen:
            continue
        haystack = f"{label} {href}"
        if pattern.search(haystack):
            selected.append({"label": label, "href": href})
            seen.add(href)
        if limit and len(selected) >= limit:
            break

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    cdp = CdpClient(port)
    try:
        for item in selected:
            slug = safe_slug(item["label"] or filename_from_url(item["href"], "page"))
            cdp.call("Page.navigate", {"url": item["href"]})
            for _ in range(45):
                state = cdp.evaluate_json("(() => ({readyState: document.readyState, href: location.href}))()")
                if state.get("readyState") == "complete":
                    break
                time.sleep(1)
            data = cdp.evaluate_json(CAPTURE_PAGE_SCRIPT)
            page_dir = out / slug
            page_dir.mkdir(exist_ok=True)
            (page_dir / f"{slug}.html").write_text(data["html"], encoding="utf-8")
            (page_dir / f"{slug}.txt").write_text(data["text"], encoding="utf-8")
            (page_dir / f"{slug}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (page_dir / f"{slug}_links.json").write_text(json.dumps(data["links"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            results.append(
                {
                    "label": item["label"],
                    "href": item["href"],
                    "capturedUrl": data.get("href"),
                    "title": data.get("title"),
                    "text": str(page_dir / f"{slug}.txt"),
                    "json": str(page_dir / f"{slug}.json"),
                    "linkCount": len(data.get("links", [])),
                    "attachmentCount": len(data.get("attachments", [])),
                }
            )
    finally:
        cdp.close()
    manifest = {"generatedAt": now(), "sourceLinks": str(links_json), "includeRegex": include_regex, "pages": results}
    manifest_path = out / "captured_pages_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Captured Confluence Pages", "", f"Generated: `{manifest['generatedAt']}`", ""]
    for item in results:
        lines.append(f"- {item['label']}: `{item['text']}`")
    md_path = out / "captured_pages_manifest.md"
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"manifest": str(manifest_path), "markdown": str(md_path), "pageCount": len(results)}


def command_inventory(args):
    result = inventory_roots(args.root)
    print(json.dumps(write_inventory(result, args.out_dir), indent=2, ensure_ascii=False))


def command_scan_evidence(args):
    scan = scan_evidence(args.root)
    print(
        json.dumps(
            write_evidence(
                scan,
                args.out_dir,
                write_full_records=args.write_full_records,
                sample_limit=args.sample_limit,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


def command_build_soc_workbook(args):
    workbook = build_soc_workbook(args.answers, args.evidence)
    print(
        json.dumps(
            write_soc_workbook(
                workbook,
                args.out_dir,
                write_full_json=args.full_json,
                write_jsonl=args.jsonl,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


def command_seed_scope_drafts(args):
    result = seed_scope_drafts(
        answers_path=args.answers,
        plan_path=args.sheet_plan,
        out_path=args.out,
        include_mixed=args.include_mixed,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_apply_answer_batch(args):
    result = apply_answer_batch(
        answers_path=args.answers,
        batch_path=args.batch,
        out_path=args.out,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_rebuild_answer_draft(args):
    result = rebuild_answer_draft(
        manifest_path=args.manifest,
        out_path=args.out,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_sync_answer_notes(args):
    result = sync_answer_notes(
        answers_path=args.answers,
        out_path=args.out,
        only_empty=args.only_empty,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_export_fillable_answers(args):
    result = export_fillable_answers(
        answers_path=args.answers,
        out_path=args.out,
        include_empty=args.include_empty,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_export_answer_markdown(args):
    result = export_answer_markdown(
        answers_path=args.answers,
        out_path=args.out,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_capture_browser(args):
    result = capture_browser_page(
        port=args.port,
        out_dir=args.out_dir,
        slug=args.slug,
        url_contains=args.url_contains,
        download_attachments=args.download_attachments,
        proxy=args.proxy,
        navigate_url=args.navigate_url,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_capture_links(args):
    result = capture_browser_links(
        port=args.port,
        links_json=args.links_json,
        out_dir=args.out_dir,
        include_regex=args.include_regex,
        limit=args.limit,
        proxy=args.proxy,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_vet_links(args):
    result = vet_links(args.sources_json, args.out_dir, args.workspace_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_answer_quality(args):
    result = answer_quality_report(
        answers_path=args.answers,
        out_dir=args.out_dir,
        vetted_links_path=args.vetted_links,
        workspace_root=args.workspace_root,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_answer_completeness(args):
    result = answer_completeness_audit(
        answers_path=args.answers,
        out_dir=args.out_dir,
        single_source_review_path=args.single_source_review,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_confluence_evidence_audit(args):
    result = confluence_evidence_audit(
        answers_path=args.answers,
        vetted_links_path=args.vetted_links,
        out_dir=args.out_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_coverage_ledger(args):
    result = build_coverage_ledger(
        answers_path=args.answers,
        sheet_plan_path=args.sheet_plan,
        out_dir=args.out_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_platform_coverage_audit(args):
    result = platform_coverage_audit(
        answers_path=args.answers,
        out_dir=args.out_dir,
        dtt_manifest_path=args.dtt_manifest,
        natco_manifest_path=args.natco_manifest,
        require_natco_manifest=args.require_natco_manifest,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_collect_marcel1(args):
    result = collect_marcel1_cluster(
        context=args.context,
        kubeconfig=args.kubeconfig,
        out_dir=args.out_dir,
        kubectl=args.kubectl,
        xdg_runtime_dir=args.xdg_runtime_dir,
        server=args.server,
        tls_server_name=args.tls_server_name,
        no_proxy=args.no_proxy,
        api_tunnel_jump=args.api_tunnel_jump,
        api_tunnel_target=args.api_tunnel_target,
        api_tunnel_target_port=args.api_tunnel_target_port,
        api_tunnel_local_port=args.api_tunnel_local_port,
        ssh=args.ssh,
        write_raw_collections=args.write_raw_collections,
        compact_limit=args.compact_limit,
    )
    print(
        json.dumps(
            {
                "json": result["json"],
                "markdown": result["markdown"],
                "compactCollections": result["compactCollections"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def command_compact_marcel1(args):
    result = compact_existing_marcel1_cluster(
        in_dir=args.in_dir,
        out_dir=args.out_dir,
        compact_limit=args.compact_limit,
        remove_raw=args.remove_raw,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def command_collect_marcel1_node_shell(args):
    result = collect_marcel1_node_shell(
        out_dir=args.out_dir,
        nodes=args.node,
        context=args.context,
        kubeconfig=args.kubeconfig,
        kubectl=args.kubectl,
        xdg_runtime_dir=args.xdg_runtime_dir,
        server=args.server,
        tls_server_name=args.tls_server_name,
        no_proxy=args.no_proxy,
        api_tunnel_jump=args.api_tunnel_jump,
        api_tunnel_target=args.api_tunnel_target,
        api_tunnel_target_port=args.api_tunnel_target_port,
        api_tunnel_local_port=args.api_tunnel_local_port,
        ssh=args.ssh,
        jump_host=args.jump_host,
        ssh_user=args.ssh_user,
        command_timeout=args.command_timeout,
        connect_timeout=args.connect_timeout,
    )
    print(json.dumps({"json": result["json"], "markdown": result["markdown"]}, indent=2, ensure_ascii=False))


def command_cross_reference_mondoo(args):
    result = cross_reference_mondoo_socs(
        answers_path=args.answers,
        mondoo_dir=args.mondoo_dir,
        out_dir=args.out_dir,
        console_url=args.console_url,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description="Reusable T-CaaS SoC analysis tooling.")
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="Inventory local repository roots.")
    inventory.add_argument("--root", action="append", required=True, help="Root directory to inventory.")
    inventory.add_argument("--out-dir", required=True, help="Output directory.")
    inventory.set_defaults(func=command_inventory)

    scan = sub.add_parser("scan-evidence", help="Scan local files for SoC-relevant evidence.")
    scan.add_argument("--root", action="append", required=True, help="Root directory to scan.")
    scan.add_argument("--out-dir", required=True, help="Output directory.")
    scan.add_argument("--write-full-records", action="store_true", help="Write the complete evidence_records.jsonl stream.")
    scan.add_argument("--sample-limit", type=int, default=2000, help="Maximum sampled records to write when full records are omitted.")
    scan.set_defaults(func=command_scan_evidence)

    workbook = sub.add_parser("build-soc-workbook", help="Build SoC research workbook from psa_answers_v1.")
    workbook.add_argument("--answers", required=True, help="PSA answers JSON.")
    workbook.add_argument("--evidence", help="Evidence index JSON.")
    workbook.add_argument("--out-dir", required=True, help="Output directory.")
    workbook.add_argument("--full-json", action="store_true", help="Also write the full nested workbook JSON.")
    workbook.add_argument("--jsonl", action="store_true", help="Also write a compact JSONL row stream.")
    workbook.set_defaults(func=command_build_soc_workbook)

    seed = sub.add_parser("seed-scope-drafts", help="Create a review copy with scope-based NA drafts from the sheet plan.")
    seed.add_argument("--answers", required=True, help="PSA answers JSON.")
    seed.add_argument("--sheet-plan", required=True, help="Sheet research plan JSON.")
    seed.add_argument("--out", required=True, help="Output PSA answers JSON.")
    seed.add_argument("--include-mixed", action="store_true", help="Also draft likely_na_mixed sheets as draft NA.")
    seed.set_defaults(func=command_seed_scope_drafts)

    batch = sub.add_parser("apply-answer-batch", help="Apply a versioned answer patch batch by answerKey.")
    batch.add_argument("--answers", required=True, help="Input PSA answers JSON.")
    batch.add_argument("--batch", required=True, help="Answer batch JSON.")
    batch.add_argument("--out", required=True, help="Output PSA answers JSON.")
    batch.set_defaults(func=command_apply_answer_batch)

    rebuild = sub.add_parser("rebuild-answer-draft", help="Rebuild the full answer draft from the template, sheet plan, and ordered answer batches.")
    rebuild.add_argument("--manifest", required=True, help="Answer rebuild manifest JSON.")
    rebuild.add_argument("--out", help="Output PSA answers JSON. Defaults to the manifest out value.")
    rebuild.set_defaults(func=command_rebuild_answer_draft)

    notes = sub.add_parser("sync-answer-notes", help="Copy answer.evidence references into answer.note.")
    notes.add_argument("--answers", required=True, help="Input PSA answers JSON.")
    notes.add_argument("--out", required=True, help="Output PSA answers JSON.")
    notes.add_argument("--only-empty", action="store_true", help="Only populate empty notes.")
    notes.set_defaults(func=command_sync_answer_notes)

    compact_answers = sub.add_parser(
        "export-fillable-answers",
        help="Write a compact psa_answers_v1 file containing only portal-fillable answer rows.",
    )
    compact_answers.add_argument("--answers", required=True, help="Input PSA answers JSON.")
    compact_answers.add_argument("--out", required=True, help="Output compact PSA answers JSON.")
    compact_answers.add_argument("--include-empty", action="store_true", help="Keep unanswered rows too.")
    compact_answers.set_defaults(func=command_export_fillable_answers)

    answer_markdown = sub.add_parser(
        "export-answer-markdown",
        help="Write a human-readable markdown document with every SoC row, answer, note, and evidence.",
    )
    answer_markdown.add_argument("--answers", required=True, help="Input PSA answers JSON.")
    answer_markdown.add_argument("--out", required=True, help="Output markdown path.")
    answer_markdown.set_defaults(func=command_export_answer_markdown)

    capture = sub.add_parser("capture-browser-page", help="Capture an authenticated browser page through Chrome DevTools.")
    capture.add_argument("--port", type=int, default=9224, help="Chrome DevTools port.")
    capture.add_argument("--url-contains", help="Select a browser tab whose URL contains this value.")
    capture.add_argument("--navigate-url", help="Navigate the selected tab before capture.")
    capture.add_argument("--slug", required=True, help="Output filename prefix.")
    capture.add_argument("--out-dir", required=True, help="Output directory.")
    capture.add_argument("--download-attachments", action="store_true", help="Fetch same-origin attachment links through the browser session.")
    capture.add_argument("--proxy", help="HTTP(S) proxy to use for attachment downloads.")
    capture.set_defaults(func=command_capture_browser)

    capture_links = sub.add_parser("capture-browser-links", help="Batch-capture selected links through Chrome DevTools.")
    capture_links.add_argument("--port", type=int, default=9224, help="Chrome DevTools port.")
    capture_links.add_argument("--links-json", required=True, help="Links JSON from capture-browser-page.")
    capture_links.add_argument("--include-regex", required=True, help="Regex matched against link text and URL.")
    capture_links.add_argument("--limit", type=int, help="Maximum pages to capture.")
    capture_links.add_argument("--out-dir", required=True, help="Output directory.")
    capture_links.add_argument("--proxy", help="Reserved for parity with capture-browser-page.")
    capture_links.set_defaults(func=command_capture_links)

    vet = sub.add_parser("vet-links", help="Create pinned GitLab/GitHub deep links from curated evidence sources.")
    vet.add_argument("--sources-json", required=True, help="Curated source JSON with path/url entries.")
    vet.add_argument("--out-dir", required=True, help="Output directory.")
    vet.add_argument("--workspace-root", default=".", help="Workspace root for relative paths.")
    vet.set_defaults(func=command_vet_links)

    quality = sub.add_parser("answer-quality", help="Check answer rows for evidence, rationale, status, and reference issues.")
    quality.add_argument("--answers", required=True, help="PSA answers JSON.")
    quality.add_argument("--vetted-links", help="Optional vetted_links.json manifest.")
    quality.add_argument("--out-dir", required=True, help="Output directory.")
    quality.add_argument("--workspace-root", default=".", help="Workspace root for relative evidence paths.")
    quality.set_defaults(func=command_answer_quality)

    completeness = sub.add_parser(
        "answer-completeness-audit",
        help="Check answer wording for statement consistency, detail level, and component context.",
    )
    completeness.add_argument("--answers", required=True, help="PSA answers JSON.")
    completeness.add_argument("--out-dir", required=True, help="Output directory.")
    completeness.add_argument(
        "--single-source-review",
        help="Optional single_source_evidence_review.json file; defaults to out-dir/single_source_evidence_review.json when present.",
    )
    completeness.set_defaults(func=command_answer_completeness)

    confluence_audit = sub.add_parser("confluence-evidence-audit", help="Report Confluence evidence URLs that are not explicitly vetted.")
    confluence_audit.add_argument("--answers", required=True, help="PSA answers JSON.")
    confluence_audit.add_argument("--vetted-links", required=True, help="vetted_links.json manifest.")
    confluence_audit.add_argument("--out-dir", required=True, help="Output directory.")
    confluence_audit.set_defaults(func=command_confluence_evidence_audit)

    coverage = sub.add_parser("coverage-ledger", help="Write compact coverage ledger for all answered and unanswered SoC rows.")
    coverage.add_argument("--answers", required=True, help="PSA answers JSON.")
    coverage.add_argument("--sheet-plan", help="Optional sheet research plan JSON.")
    coverage.add_argument("--out-dir", required=True, help="Output directory.")
    coverage.set_defaults(func=command_coverage_ledger)

    platform_coverage = sub.add_parser(
        "platform-coverage-audit",
        help="Check platform/component coverage and portal-reference hygiene for a prepared answer file.",
    )
    platform_coverage.add_argument("--answers", required=True, help="PSA answers JSON.")
    platform_coverage.add_argument("--out-dir", required=True, help="Output directory.")
    platform_coverage.add_argument("--dtt-manifest", help="Optional DTT system SoC manifest JSON for scope checks.")
    platform_coverage.add_argument("--natco-manifest", help="Optional NatCo system SoC manifest JSON for scope checks.")
    platform_coverage.add_argument(
        "--require-natco-manifest",
        action="store_true",
        help="Record a deferred filing note when no separate NatCo manifest is supplied.",
    )
    platform_coverage.set_defaults(func=command_platform_coverage_audit)

    collect = sub.add_parser("collect-marcel1-cluster", help="Run read-only redacted kubectl collection for marcel-1.")
    collect.add_argument("--context", default="marcel-1-admin@marcel-1", help="kubectl context.")
    collect.add_argument("--kubeconfig", default="/home/a92615428/marcel.k", help="Kubeconfig path.")
    collect.add_argument("--kubectl", default="kubectl", help="kubectl executable.")
    collect.add_argument("--xdg-runtime-dir", default="/tmp/xdg-runtime-a92615428", help="Writable XDG_RUNTIME_DIR for snap kubectl.")
    collect.add_argument("--server", default="", help="Override Kubernetes API server URL, e.g. https://127.0.0.1:16443.")
    collect.add_argument("--tls-server-name", default="", help="TLS server name when using a local API tunnel.")
    collect.add_argument("--no-proxy", default=None, help="Set NO_PROXY and clear proxy environment variables for kubectl.")
    collect.add_argument("--api-tunnel-jump", default="", help="SSH jump host used to open a temporary API tunnel.")
    collect.add_argument("--api-tunnel-target", default="", help="API target host for a temporary SSH tunnel; IPv6 literals are supported.")
    collect.add_argument("--api-tunnel-target-port", type=int, default=6443, help="API target port for the temporary SSH tunnel.")
    collect.add_argument("--api-tunnel-local-port", type=int, default=0, help="Local API tunnel port, or 0 for automatic.")
    collect.add_argument("--ssh", default="ssh", help="ssh executable.")
    collect.add_argument("--compact-limit", type=int, default=1000, help="Maximum compact items to keep per collection.")
    collect.add_argument("--write-raw-collections", action="store_true", help=f"Also write full redacted collection JSON under {RAW_COLLECTION_DIRNAME}/.")
    collect.add_argument("--out-dir", required=True, help="Output directory.")
    collect.set_defaults(func=command_collect_marcel1)

    compact_marcel = sub.add_parser("compact-marcel1-cluster", help="Compact an existing marcel-1 raw kubectl capture.")
    compact_marcel.add_argument("--in-dir", required=True, help="Directory containing per-collection raw kubectl JSON files.")
    compact_marcel.add_argument("--out-dir", help="Output directory. Defaults to --in-dir.")
    compact_marcel.add_argument("--compact-limit", type=int, default=1000, help="Maximum compact items to keep per collection.")
    compact_marcel.add_argument("--remove-raw", action="store_true", help="Remove the raw per-collection JSON files after compacting.")
    compact_marcel.set_defaults(func=command_compact_marcel1)

    node_shell = sub.add_parser("collect-marcel1-node-shell", help="Run read-only redacted SSH collection on marcel-1 nodes.")
    node_shell.add_argument("--context", default="marcel-1-admin@marcel-1", help="kubectl context for node discovery.")
    node_shell.add_argument("--kubeconfig", default="/home/a92615428/marcel.k", help="Kubeconfig path for node discovery.")
    node_shell.add_argument("--kubectl", default="kubectl", help="kubectl executable.")
    node_shell.add_argument("--xdg-runtime-dir", default="/tmp/xdg-runtime-a92615428", help="Writable XDG_RUNTIME_DIR for snap kubectl.")
    node_shell.add_argument("--server", default="", help="Override Kubernetes API server URL, e.g. https://127.0.0.1:16443.")
    node_shell.add_argument("--tls-server-name", default="", help="TLS server name when using a local API tunnel.")
    node_shell.add_argument("--no-proxy", default=None, help="Set NO_PROXY and clear proxy environment variables for kubectl.")
    node_shell.add_argument("--api-tunnel-jump", default="", help="SSH jump host used to open a temporary API tunnel for node discovery.")
    node_shell.add_argument("--api-tunnel-target", default="", help="API target host for a temporary SSH tunnel; IPv6 literals are supported.")
    node_shell.add_argument("--api-tunnel-target-port", type=int, default=6443, help="API target port for the temporary SSH tunnel.")
    node_shell.add_argument("--api-tunnel-local-port", type=int, default=0, help="Local API tunnel port, or 0 for automatic.")
    node_shell.add_argument("--node", action="append", default=[], help="Explicit node target as name=host. Repeatable. If omitted, nodes are discovered with kubectl.")
    node_shell.add_argument("--ssh", default="ssh", help="ssh executable.")
    node_shell.add_argument("--jump-host", default="schiff-ztn-jump", help="SSH jump host for node shell access.")
    node_shell.add_argument("--ssh-user", default="debug", help="SSH user configured by Redfish opkssh policy.")
    node_shell.add_argument("--command-timeout", type=int, default=45, help="Per-command SSH timeout in seconds.")
    node_shell.add_argument("--connect-timeout", type=int, default=10, help="SSH connect timeout in seconds.")
    node_shell.add_argument("--out-dir", required=True, help="Output directory.")
    node_shell.set_defaults(func=command_collect_marcel1_node_shell)

    mondoo = sub.add_parser("cross-reference-mondoo-socs", help="Map Mondoo marcel-1 policy exports to SoC rows.")
    mondoo.add_argument("--answers", required=True, help="PSA answers JSON.")
    mondoo.add_argument("--mondoo-dir", required=True, help="Directory with Mondoo markdown exports.")
    mondoo.add_argument("--out-dir", required=True, help="Output directory.")
    mondoo.add_argument("--console-url", default="https://console.mondoo.telekom.de", help="Mondoo console URL for notes/provenance.")
    mondoo.set_defaults(func=command_cross_reference_mondoo)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
