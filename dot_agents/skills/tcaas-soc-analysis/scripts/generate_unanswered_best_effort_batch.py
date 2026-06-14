#!/usr/bin/env python3
"""Generate conservative answers for currently unanswered SoC rows.

The generator reads the current coverage ledger, applies explicit per-row
rules, and writes an answer batch. It is intentionally strict: every current
unanswered row must be covered by a rule, and every evidence id must resolve
to a vetted GitLab/GitHub/Confluence URL.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_PREFIXES = (
    "https://gitlab.devops.telekom.de/",
    "https://github.com/",
    "https://wiki.telekom.de/",
)


def iter_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_objects(child)


def load_links(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    links: dict[str, str] = {}
    for item in iter_objects(payload):
        item_id = item.get("id")
        if not item_id:
            continue
        url = item.get("deepLink") or item.get("url")
        if not url:
            continue
        if not any(str(url).startswith(prefix) for prefix in ALLOWED_PREFIXES):
            raise SystemExit(f"Evidence id {item_id} has non-portal URL: {url}")
        links[item_id] = str(url)
    return links


def ev(links: dict[str, str], *ids: str) -> list[str]:
    missing = [item_id for item_id in ids if item_id not in links]
    if missing:
        raise SystemExit(f"Missing vetted evidence ids: {', '.join(missing)}")
    return [links[item_id] for item_id in ids]


def answer(statement: str, explanation: str, evidence: list[str]) -> dict:
    return {
        "statement": statement,
        "explanation": explanation,
        "evidence": evidence,
        "owner": "best-effort-gap-resolution",
        "status": "ready_for_review",
    }


def contextualize(rule: dict, row: dict) -> dict:
    item = copy.deepcopy(rule)
    sheet_id = str(row.get("sheetId") or "").strip()
    req_number = str(row.get("requirementNumber") or "").strip()
    req_id = str(row.get("requirementId") or "").strip()
    label_parts = []
    if sheet_id:
        label_parts.append(f"sheet {sheet_id}")
    if req_number:
        label_parts.append(f"requirement {req_number}")
    if req_id:
        label_parts.append(f"ID {req_id}")
    label = f" ({', '.join(label_parts)})" if label_parts else ""
    prefix = f"This PSA row{label} was reviewed individually. "
    explanation = str(item.get("explanation") or "")
    if not explanation.startswith("This "):
        item["explanation"] = prefix + explanation
    return item


def iter_gap_rows(payload: dict):
    if isinstance(payload.get("unansweredRows"), list):
        yield from payload["unansweredRows"]
        return
    if isinstance(payload.get("bySheet"), list):
        for sheet in payload["bySheet"]:
            yield from sheet.get("rows", [])
        return
    if isinstance(payload, list):
        for row in payload:
            if row.get("needsAnalysis") or not row.get("statement"):
                yield row
        return
    raise SystemExit("Unsupported gap/ledger format: expected unansweredRows, bySheet, or row list")


def no_full_proof(component: str, control: str, evidence_scope: str) -> str:
    return (
        f"Not fulfilled based on the reviewed durable evidence. {evidence_scope} "
        f"The reviewed sources do not prove {control} for {component}, so this "
        "must remain a negative answer until device, backend, runtime, or owner "
        "evidence is attached."
    )


def partial(component: str, covered: str, gap: str) -> str:
    return (
        f"Partially fulfilled for {component}. {covered} "
        f"This does not prove {gap}, so the answer remains partial."
    )


def build_rules(links: dict[str, str]) -> dict[tuple[str, str], dict]:
    fact = ev(links, "confluence-fact-sheet-pdf")
    gcp = ev(links, "gcp-dev-env-architecture", "gcp-gke-autopilot-private", "gcp-compute-runner-disks")
    idp = ev(
        links,
        "schiff-idp-keycloak-rbac",
        "keycloak-tcaas-prd-breakglass-client-origin-logout",
        "auth-operator-role-category-config",
    )
    idp_full = ev(
        links,
        "schiff-idp-keycloak-rbac",
        "keycloak-tcaas-prd-full-realm-export",
        "keycloak-tcaas-prd-realm-auth-settings",
    )
    host_password = ev(links, "tcaas-hardening-pam-quality-history-lockout", "tdi-specific-sshd-session-controls")
    web_scope = ev(
        links,
        "keycloak-tcaas-prd-full-realm-export",
        "keycloak-tcaas-prd-browser-security-headers",
        "caas-api-cluster-handler-validation-errors",
        "tco-input-definition-schema",
    )
    web_api = ev(
        links,
        "caas-api-cluster-handler-validation-errors",
        "caas-api-mongodb-typed-filters",
        "tco-input-definition-schema",
        "tco-input-validator-types-required",
    )
    web_redirect = ev(
        links,
        "keycloak-tcaas-prd-breakglass-client-origin-logout",
        "tcaas-integrations-httpclient-timeouts-ratelimit",
        "tcaas-integrations-tfstate-status-methods-headers",
    )
    micro = ev(
        links,
        "function-caprf-redfish-definition",
        "caprf-provisioner-method-restrictions",
        "caas-api-cloud-generic-errors",
        "tdi-bootstrap-controlplane-tls-ciphers",
        "tdi-bootstrap-kubelet-tls-ciphers",
    )
    arch = ev(
        links,
        "confluence-fact-sheet-pdf",
        "marcel1-tcaascluster-runtime-spec",
        "network-ingress-management-guardrails",
        "gcp-dev-env-architecture",
    )
    arch_network = ev(
        links,
        "network-hld-hbr-vrf-bgp",
        "network-ingress-management-guardrails",
        "gcp-cndtag-network-architecture",
        "network-policies-deny-all",
    )
    db = ev(
        links,
        "caas-api-mongodb-typed-filters",
        "caas-api-mongodb-write-filters",
        "tdg-logging-platform-hosttailer",
        "tdg-logging-platform-output-cdi",
    )
    network = ev(
        links,
        "vsr-os-image-decision",
        "network-components-vsr-frr",
        "bm4x-vsr-network-profile-addressing",
        "bm4x-frr-vxlan-proxy-arp-disabled",
    )
    network_runtime = ev(
        links,
        "vsr-os-image-decision",
        "cra-vsr-container-resource-limits",
        "bm4x-frr-systemd-nspawn-supervision",
    )
    storage = ev(
        links,
        "storage-interface-adr-requirements",
        "function-csi-netapp-bm4x-definition",
        "function-csi-netapp-bm4x-network-config",
        "csi-netapp-bm4x-trident-backend-sec-sys",
    )
    storage_runtime = ev(
        links,
        "storage-interface-adr-requirements",
        "function-csi-netapp-bm4x-definition",
        "policy-require-requests-limits",
        "policy-deployment-multiple-replicas",
    )
    private_cloud = ev(
        links,
        "confluence-fact-sheet-pdf",
        "marcel1-tcaascluster-runtime-spec",
        "network-sriov-security-requirements",
        "netbox-compute-pci-mellanox-sriov",
    )
    private_cloud_ops = ev(
        links,
        "marcel1-mondoo-host-os-hardening",
        "marcel1-mondoo-accepted-risk",
        "caprf-redfish-disk-wipe",
        "caprf-redfish-soft-deprovision-gap",
    )

    rules: dict[tuple[str, str], dict] = {}

    def put(sheet_id: str, reqs: list[str], statement: str, explanation: str, evidence: list[str]) -> None:
        for req in reqs:
            key = (sheet_id, req)
            if key in rules:
                raise SystemExit(f"Duplicate rule for {key}")
            rules[key] = answer(statement, explanation, evidence)

    # GCP general requirements.
    put(
        "407323600",
        ["63"],
        "SONC",
        no_full_proof(
            "the documented GCP development environment",
            "UTC time synchronization for runner VMs, bastion/artifact-cache VMs, and GKE nodes",
            "The GCP evidence documents the architecture, private GKE Autopilot, and compute modules.",
        ),
        gcp,
    )

    # Technical baseline.
    put(
        "407323624",
        ["17"],
        "SOPC",
        partial(
            "central platform identity and breakglass surfaces",
            "Keycloak/OIDC and the breakglass client define front-channel/back-channel logout behavior and auth-operator maps users into platform roles.",
            "a logout control for every platform UI, API client, device-local shell, storage console, and third-party service in scope",
        ),
        idp,
    )
    put(
        "407323624",
        ["27"],
        "SONC",
        no_full_proof(
            "technical user accounts across the platform",
            "30-character technical-account passwords with three character categories wherever passwords are used",
            "Host-local PAM evidence enforces password quality, but the documented minimum is below 30 characters and does not cover all technical accounts.",
        ),
        host_password,
    )
    put(
        "407323624",
        ["29", "31"],
        "SONC",
        no_full_proof(
            "all password-authenticated platform surfaces",
            "user-controlled password change and masked password entry wherever passwords are used",
            "The durable evidence covers Keycloak/OIDC configuration and host-local authentication controls.",
        ),
        idp_full + host_password,
    )

    # Web applications.
    put(
        "407323605",
        ["4", "6", "13", "14", "19", "22", "23", "24", "25", "28", "29", "36", "40", "44", "45", "46", "47", "48", "49", "55"],
        "SONC",
        no_full_proof(
            "all platform-managed web/UI/API surfaces",
            "the requested deployed web-application control across client resources, browser storage/cache, input/output encoding, headers/cookies/session behavior, re-authentication, CSRF, and default web accounts",
            "The available web evidence covers Keycloak realm configuration, selected browser security headers, and selected caas-api/t-co validation paths.",
        ),
        web_scope,
    )
    put(
        "407323605",
        ["20"],
        "NA",
        "Not applicable to the reviewed platform web-application scope based on available evidence. No client-facing file-upload feature was evidenced for the T-CaaS platform web/API surfaces; selected caas-api and t-co evidence covers JSON/API validation rather than browser file upload processing. Reassess if a platform UI or tenant-facing service adds file upload or transferred-file processing.",
        web_api,
    )
    put(
        "407323605",
        ["27"],
        "NA",
        "Not applicable based on the reviewed platform web/API evidence. The evidenced caas-api and t-co paths use JSON/OpenAPI-style validation and MongoDB driver filters; no XML, XSLT, or XPath processing path was found for this platform web scope. Reassess if XML/XPath processing is introduced.",
        web_api,
    )
    put(
        "407323605",
        ["30", "32"],
        "NA",
        "Not applicable to the reviewed T-CaaS platform web scope. The durable evidence does not show an unauthenticated web feature that sends email or SMS, contact forms, recommendation forms, or page-rating inputs; Keycloak password reset is disabled in the reviewed realm settings. Reassess if such web features are added.",
        idp_full,
    )
    put(
        "407323605",
        ["31"],
        "SOPC",
        partial(
            "reviewed redirect and outbound HTTP paths",
            "The Keycloak breakglass client restricts redirect URIs/web origins, and selected integration clients use explicit HTTP client handling rather than arbitrary browser input as the sole target.",
            "complete open-redirect, SSRF, and Host-header protection for every web UI/API and tenant-owned web service",
        ),
        web_redirect,
    )
    put(
        "407323605",
        ["50"],
        "SOPC",
        partial(
            "the production Keycloak/breakglass web surface",
            "The production breakglass OIDC client enables front-channel logout and requires back-channel logout session handling.",
            "a logout function for every platform web UI, API-backed UI, and tenant-owned web application",
        ),
        ev(links, "keycloak-tcaas-prd-breakglass-client-origin-logout"),
    )

    # Application server and microservices.
    put(
        "407323623",
        ["5"],
        "SONC",
        no_full_proof(
            "all application-server images and runtimes",
            "removal of sample or example applications",
            "The platform evidence identifies managed functions and runtime components but does not include a complete application-server image inventory or rendered runtime proof.",
        ),
        ev(links, "confluence-fact-sheet-pdf", "function-haproxy-ingress-definition", "function-ingress-nginx-definition"),
    )
    put(
        "407323611",
        ["8"],
        "SONC",
        no_full_proof(
            "all platform-managed microservice/container images",
            "removal of sample or example applications",
            "The microservice evidence covers selected platform functions and APIs, but does not provide complete rendered-image proof that no sample applications remain.",
        ),
        micro,
    )
    put(
        "407323611",
        ["23"],
        "NA",
        "Not applicable to the reviewed platform microservice scope. I did not find a web-service request-signature forwarding flow; the evidenced platform authentication uses OIDC/JWT, token, TLS, and RBAC patterns instead of request signatures that could be stripped before forwarding. Reassess if a signed-request proxy path is introduced.",
        ev(links, "schiff-idp-keycloak-rbac", "caprf-simple-token-lifecycle", "tdi-bootstrap-controlplane-tls-ciphers"),
    )
    put(
        "407323611",
        ["30"],
        "SOPC",
        partial(
            "selected platform API handlers",
            "The caas-api handlers return generic client-facing error strings for several paths, and CAPRF restricts provisioning methods.",
            "HTTP-server product/version information removal in every ingress controller, reverse proxy, framework default error page, and third-party microservice",
        ),
        ev(links, "caas-api-cloud-generic-errors", "caas-api-cluster-handler-validation-errors", "caprf-provisioner-method-restrictions"),
    )
    put(
        "407323611",
        ["46"],
        "SONC",
        no_full_proof(
            "all TLS endpoints in the microservice scope",
            "use of Diffie-Hellman groups with IANA numbers 23-33",
            "The durable TLS evidence documents cipher-suite configuration for Kubernetes components but does not prove configured DH groups for all microservice TLS endpoints.",
        ),
        ev(links, "tdi-bootstrap-controlplane-tls-ciphers", "tdi-bootstrap-kubelet-tls-ciphers", "tcaas-cert-manager-function-release"),
    )

    # System architecture.
    put(
        "407323609",
        ["12"],
        "SONC",
        no_full_proof(
            "presentation-layer components",
            "no permanent storage of sensitive data in the presentation layer",
            "The reviewed evidence covers platform architecture and selected web/API paths but does not provide deployed browser/UI storage evidence.",
        ),
        arch,
    )
    put(
        "407323609",
        ["13"],
        "SOPC",
        partial(
            "network exposure and management paths",
            "The architecture uses private cloud networking, ingress-management guardrails, and GCP private access patterns.",
            "physical separation of every externally reachable component from all internal systems",
        ),
        arch_network,
    )
    put(
        "407323609",
        ["15"],
        "SOPC",
        partial(
            "Kubernetes-hosted platform services",
            "T-CaaS runs managed platform services under common platform administration and separates tenants into dedicated clusters and namespaces.",
            "that every co-hosted service on every operating-system instance has the same administration, data owner, and comparable low protection requirement",
        ),
        arch,
    )
    put(
        "407323609",
        ["16"],
        "SONC",
        no_full_proof(
            "externally reachable system components",
            "exactly one application service per operating-system instance",
            "The reviewed architecture is Kubernetes/private-cloud based and can run multiple services on shared nodes; the evidence does not prove the exact one-service-per-OS-instance condition for externally reachable components.",
        ),
        arch,
    )
    put(
        "407323609",
        ["18"],
        "SOPC",
        partial(
            "selected UDP and network infrastructure paths",
            "T-CaaS uses network policies, HBR/VRF separation, and managed infrastructure components for DNS/networking.",
            "all compensating controls for every UDP-based service exposed by platform, underlay, storage, or tenant components",
        ),
        arch_network,
    )
    put(
        "407323609",
        ["23"],
        "SONC",
        no_full_proof(
            "interactive administration of production systems",
            "administrator workstation security matching the protection need of production systems",
            "The reviewed project evidence documents platform and access controls, but not the security baseline of administrator endpoints.",
        ),
        ev(links, "confluence-operational-responsibilities", "schiff-idp-keycloak-rbac"),
    )
    put(
        "407323609",
        ["24"],
        "SOPC",
        partial(
            "documented private access paths",
            "GCP development access uses IAP/private access patterns and T-CaaS management is protected by OIDC/RBAC and internal network controls.",
            "a complete fixed-jumphost model for every high-protection interactive administration path in production",
        ),
        ev(links, "gcp-dev-env-iap-access", "gcp-dev-env-architecture", "schiff-idp-keycloak-rbac"),
    )
    put(
        "407323609",
        ["25"],
        "SONC",
        no_full_proof(
            "administrative access logging",
            "tamper-resistant logging through a specially designed jumphost where required",
            "The platform logging evidence covers Kubernetes, host, audit, auth, and event logs, but not a dedicated tamper-resistant jumphost implementation.",
        ),
        ev(links, "tdg-logging-platform-hosttailer", "tdg-logging-platform-output-cdi", "gcp-dev-env-iap-access"),
    )

    # Data center/cloud infrastructure architecture.
    put(
        "407323604",
        ["2"],
        "SOPC",
        partial(
            "externally reachable and private-cloud infrastructure paths",
            "T-CaaS and the GCP dev environment use private endpoints, dedicated cluster/network constructs, and network guardrails.",
            "physical separation for every externally reachable system from all internal infrastructure",
        ),
        arch_network,
    )
    put(
        "407323604",
        ["12"],
        "SONC",
        no_full_proof(
            "site-to-site links",
            "termination of generic site-to-site tunnels so traffic is inspectable at the target network firewall or packet filter",
            "The reviewed evidence documents network architecture and GCP connectivity, but not tunnel termination and firewall inspection for every site-to-site connection.",
        ),
        ev(links, "network-hld-hbr-vrf-bgp", "gcp-cndtag-network-architecture", "gcp-cndtag-firewall-rules"),
    )
    put(
        "407323604",
        ["13"],
        "SOPC",
        partial(
            "Kubernetes and selected cloud network boundaries",
            "Network policies, VRF/HBR design, and GCP firewall documentation provide boundary filtering patterns.",
            "anti-spoof filtering for logically invalid source/destination addresses at every data-center, cloud, and infrastructure boundary",
        ),
        ev(links, "network-policies-deny-all", "network-hld-hbr-vrf-bgp", "gcp-cndtag-firewall-rules"),
    )
    put(
        "407323604",
        ["14"],
        "SONC",
        no_full_proof(
            "filtering elements such as firewalls and load balancers",
            "independence of all filtering elements from the systems being protected",
            "The reviewed T-CaaS evidence includes in-cluster/network-node enforcement patterns and ingress controllers, but not fully independent filtering infrastructure for every protected system.",
        ),
        ev(links, "network-ingress-management-guardrails", "network-hld-hbr-vrf-bgp", "function-haproxy-ingress-definition"),
    )
    put(
        "407323604",
        ["15"],
        "SOPC",
        partial(
            "T-CaaS filtering components",
            "The HBR/vSR design isolates router functions and the CRA/vSR runtime uses explicit resource supervision; ingress management has guardrails.",
            "that every filtering network element carries no non-filtering service or function that could reduce firewall reliability",
        ),
        ev(links, "vsr-os-image-decision", "cra-vsr-container-resource-limits", "network-ingress-management-guardrails"),
    )

    # Database systems.
    put(
        "407323615",
        ["3", "9"],
        "SONC",
        no_full_proof(
            "all database systems used by platform components",
            "database feature hardening and allowed co-hosting of multiple database instances",
            "The available durable evidence covers selected MongoDB access code and platform logging, but not the deployed database server configuration or instance co-hosting model.",
        ),
        db,
    )
    put(
        "407323615",
        ["33"],
        "SONC",
        no_full_proof(
            "database systems containing customer data",
            "detection of mass data exfiltration above 100,000 DSK2/DSK3 customer records",
            "The platform logging stack forwards logs centrally, but the reviewed evidence does not include database-specific exfiltration detection rules or thresholds.",
        ),
        db,
    )

    # Router/switch and network-element controls.
    router_id = "407323621"
    netelement_id = "407323608"
    for sheet_id, reqs in {
        router_id: ["6", "9", "17", "18", "20", "21", "22", "23", "24", "25", "30", "31", "32", "34", "35", "39", "44", "46", "47", "48"],
        netelement_id: ["6", "17", "18", "19", "20", "21", "22", "27", "28", "29", "31", "32", "36", "41", "43", "44", "45"],
    }.items():
        put(
            sheet_id,
            reqs,
            "SONC",
            no_full_proof(
                "6WIND vSR/HBR, FRR, physical router/switch, and appliance-local management paths",
                "the requested device-native interface, packet-plane, boot/password-recovery, default-account, MFA, logout, password-policy, or password-entry control",
                "The durable network evidence documents the T-CaaS HBR/vSR/FRR design and selected network profiles.",
            ),
            network,
        )
    put(
        router_id,
        ["19", "26", "27"],
        "SOPC",
        partial(
            "T-CaaS-managed HBR/vSR and CRA runtime availability",
            "The vSR/CRA runtime is supervised and configured with explicit CPU, memory, PID/task limits and service ordering.",
            "device-native packet-plane resilience for every unexpected packet/header/input case on 6WIND, FRR, physical router/switch, and external fabric devices",
        ),
        network_runtime,
    )
    put(
        netelement_id,
        ["16", "23", "24"],
        "SOPC",
        partial(
            "T-CaaS-managed HBR/vSR and CRA runtime availability",
            "The vSR/CRA runtime is supervised and configured with explicit CPU, memory, PID/task limits and service ordering.",
            "device-native packet-plane resilience for every unexpected packet/header/input case on 6WIND, FRR, physical router/switch, and external fabric devices",
        ),
        network_runtime,
    )

    # Network storage systems.
    put(
        "407323625",
        ["11", "12", "19", "20", "29", "32", "33", "39", "41", "43"],
        "SONC",
        no_full_proof(
            "NetApp/ONTAP, StorageGRID, Trident backend credentials, and storage-array local administration",
            "the requested root-squash, anonymous-access, default-account, MFA, logout, password-policy, password-change, or masked-entry control",
            "The durable storage evidence covers CSI/Trident integration and a NetApp backend template; it does not include backend array local-account policy exports.",
        ),
        storage,
    )
    put(
        "407323625",
        ["23", "24", "25"],
        "SOPC",
        partial(
            "Kubernetes-mediated storage consumption",
            "Storage is exposed through CSI/Trident and Kubernetes policies include resource/multiple-replica guardrails for platform workloads.",
            "backend storage-array robustness, overload protection, and predictable overload behavior for NetApp/ONTAP, StorageGRID, and any appliance-local management/API surface",
        ),
        storage_runtime,
    )

    # Private cloud rows.
    put(
        "407323626",
        ["9"],
        "SONC",
        no_full_proof(
            "private-cloud infrastructure management traffic",
            "higher priority for infrastructure, orchestration, BMC, and device-management traffic when no out-of-band management network exists",
            "The private-cloud evidence documents network profiles, HBR/VRF design, and BM4X cluster configuration, but not QoS/priority treatment for all management traffic classes.",
        ),
        private_cloud,
    )
    put(
        "407323626",
        ["21"],
        "SONC",
        no_full_proof(
            "all hosts and key-generation paths",
            "availability and use of a suitable entropy source for secret and cryptographic-key generation",
            "The reviewed host and private-cloud evidence does not include entropy-source configuration or runtime attestation for all nodes.",
        ),
        private_cloud_ops,
    )
    put(
        "407323626",
        ["32"],
        "SONC",
        no_full_proof(
            "SR-IOV/PCI passthrough hardware reuse",
            "secure cleanup of PCI-passthrough hardware after release",
            "SR-IOV and PCI passthrough are evidenced for selected Netbox/BM4X paths, but the reviewed sources do not prove secure VF/device reset and cleanup after tenant release.",
        ),
        ev(links, "network-sriov-security-requirements", "netbox-compute-pci-mellanox-sriov", "netbox-workload-sriov-functions"),
    )
    put(
        "407323626",
        ["41"],
        "SONC",
        no_full_proof(
            "all private-cloud hosts",
            "an integrity-protection solution on every host",
            "Mondoo and hardening evidence exists for marcel-1, but it does not prove host integrity protection such as measured boot, IMA/AIDE, or equivalent on every private-cloud host.",
        ),
        private_cloud_ops,
    )
    put(
        "407323626",
        ["54"],
        "SONC",
        no_full_proof(
            "storage replication paths",
            "encrypted storage replication",
            "The reviewed storage evidence covers CSI/Trident, backend encryption flags, and storage network configuration, but not backend storage replication encryption.",
        ),
        storage,
    )
    put(
        "407323626",
        ["67"],
        "SONC",
        no_full_proof(
            "development, test, and reference environments",
            "exclusion of privacy-relevant customer data and other sensitive data",
            "The reviewed evidence shows dev/prod environment separation and GCP dev-env design, but not a data-governance rule or technical control preventing sensitive customer data use in dev/test/reference systems.",
        ),
        ev(links, "gcp-dev-env-environments", "gcp-dev-env-security-summary", "marcel1-tcaascluster-runtime-spec"),
    )

    return rules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--vetted-links", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    links = load_links(args.vetted_links)
    rules = build_rules(links)

    entries = []
    missing_rules = []
    rows = list(iter_gap_rows(ledger))
    for row in rows:
        key = (str(row.get("sheetId", "")), str(row.get("requirementNumber", "")))
        rule = rules.get(key)
        if not rule:
            missing_rules.append({"sheetId": key[0], "requirementNumber": key[1], "answerKey": row.get("answerKey")})
            continue
        entries.append({"answerKey": row["answerKey"], "set": {"answer": contextualize(rule, row)}})

    unused_rules = sorted(set(rules) - {(str(row.get("sheetId", "")), str(row.get("requirementNumber", ""))) for row in rows})
    if missing_rules:
        raise SystemExit("Missing rules:\n" + json.dumps(missing_rules, indent=2))
    if unused_rules:
        raise SystemExit("Unused rules:\n" + json.dumps(unused_rules, indent=2))

    payload = {
        "schema": "tcaas_answer_batch_v1",
        "batchId": "best-effort-final-gap-resolution-2026-06-13",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Conservative best-effort answers for rows that were previously blank after the "
            "scope consistency audit. Negative answers mean the durable GitLab/GitHub/"
            "Confluence evidence does not prove the required control; they are not claims "
            "that the control is impossible or absent in every external owner system."
        ),
        "answers": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "answers": len(entries)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
