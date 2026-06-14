"""
BMC connectivity configuration for CaaS baremetal clusters.

Maps NetBox tenants to the management cluster whose sshuttle tunnel
provides access to the BOR network (BMC IPs).

Built from `kubectl get cc -A` on all prod mgmt clusters (2026-02-23).
"""

# Static tenant → mgmt cluster mapping.
# For adopted tenants, the mgmt cluster is in a different cloud but manages
# the baremetal workloads via CAPI adoption.
TENANT_MGMT_MAP = {
    # === HC tenants with native mgmt clusters ===
    "hc-czbrnc1": "mgmt-38-prod",   # adopted; mgmt-41-prod is non-baremetal
    "hc-hrrijf1": "mgmt-25-prod",
    "hc-hrspif1": "mgmt-34-prod",
    "hc-hrvart1": "mgmt-26-prod",
    "hc-hrvart2": "mgmt-15-prod",
    "hc-plkrac1": "mgmt-40-prod",
    "hc-plpozc1": "mgmt-37-prod",   # adopted; mgmt-39-prod is non-baremetal
    "hc-plwarc1": "mgmt-35-prod",
    "hc-plwarc2": "mgmt-42-prod",
    # === HC tenants with adopted mgmt clusters (no native mgmt in tenant) ===
    "hc-czprgc1": "mgmt-29-prod",   # adopted
    "hc-czthpc1": "mgmt-23-prod",   # adopted
    "hc-czthpc2": "mgmt-27-prod",   # adopted
    "hc-hudpxc1": "mgmt-11-prod",   # adopted (osvar: hc-hudpxf1)
    "hc-hufehc1": "mgmt-10-prod",   # adopted (osvar: hc-hufehf1)
    "hc-skbrac1": "mgmt-12-prod",   # adopted
    "hc-skbrac2": "mgmt-20-prod",   # adopted
    "hc-skbrac3": "mgmt-30-prod",   # adopted
    "hc-skkosc1": "mgmt-24-prod",   # adopted
    "hc-skkosc2": "mgmt-28-prod",   # adopted
    # === IC tenants ===
    "ic-atgraf1": "mgmt-16-prod",
    "ic-atsalf1": "mgmt-14-prod",
    "ic-atvief1": "mgmt-08-prod",
    "ic-debamf3": "mgmt-04-prod",   # iot-bm clusters
    "ic-defraf2": "mgmt-05-prod",   # iot-bm clusters
    "ic-hrzagt4": "mgmt-06-prod",   # managed from ic-hrzagt5
    "ic-hrzagt5": "mgmt-06-prod",
    "ic-mebjef1": "mgmt-18-prod",   # managed from ic-hrzagt5
    "ic-mepodf1": "mgmt-19-prod",   # managed from ic-hrzagt5
    "ic-mkskof2": "mgmt-13-prod",   # managed from ic-hrzagt5
    "ic-mkstuf2": "mgmt-17-prod",   # managed from ic-hrzagt5
    # === CL (Central Lab) tenants ===
    "cl-hrzagt6": "mgmt-06-prod",   # managed from ic-hrzagt5
    "cl-hubudt1": "mgmt-02-prod",   # managed from ic-hubudb3
}

# Extra subnets per mgmt cluster (beyond the default 100.64.0.0/10)
EXTRA_SUBNETS = {
    "mgmt-35-prod": ["10.242.140.0/24", "10.242.141.0/24"],
}

DEFAULT_SUBNET = "100.64.0.0/10"
