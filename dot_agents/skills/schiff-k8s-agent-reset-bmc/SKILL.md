---
name: schiff-k8s-agent-reset-bmc
description: Reset a BareMetalHost's BMC (iLO or Lenovo XCC) using AuxReset.sh to recover from BMC faults such as stuck deprovisioning, Redfish errors, or untrusted TLS certificate loops.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/reset-bmc by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# BMC Reset via AuxReset.sh

Use this skill when a BareMetalHost is stuck due to a BMC-level fault that cannot be resolved by Ironic retries alone. The most common trigger is a Lenovo XCC that has cached an untrusted TLS certificate from the ironic-boot endpoint and rejects all Redfish VirtualMedia cleaning requests with HTTP 500.

## When to use

- BMH is stuck in `deprovisioning` / Ironic node in `clean failed` with a persistent Redfish error (e.g. `LenovoExtendedWarning.1.0.ReceivedUntrustedCertificate`, `HTTP 500` from VirtualMedia endpoint).
- MachineDeployment stuck in `ScalingDown` because the old Machine cannot be deleted — blocked by a BMH that won't finish deprovisioning.
- BMC is behaving erratically (wrong power state reported, Redfish timeouts) and a BMC restart is the recommended recovery step.
- Error count on the BMH is growing (hundreds or thousands) and retries have not recovered for hours or days.

Do **not** use this for transient network blips or short provisioning errors — wait for a few Ironic retry cycles first.

## Tool location

```text
/home/a11873341/git/schiff/ops-manifests/bin/AuxReset.sh
```

Supports both **HPE iLO** (AuxCycle) and **Lenovo XCC** (Manager.Reset ForceRestart). Vendor is auto-detected via Redfish.

Usage:

```bash
BMC_PASSWORD='<password>' bash /home/a11873341/git/schiff/ops-manifests/bin/AuxReset.sh \
  -i <bmc-fqdn>
```

The default username is `bm4xoperator`. Pass `-u <user>` to override.

## Inputs needed

- BMH FQDN (e.g. `stgt10com5i75.inf.bm4x.telekom.de`)
- Management cluster context where the BMH namespace lives
- BMH namespace (e.g. `metal3-ref-stgt10`)

## Procedure

### 1. Confirm the problem

Check Ironic node state and BMH error:

```bash
# Ironic node state
IRONICUSER=$(kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.username}' | base64 -d)
IRONICPASS=$(kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.password}' | base64 -d)

# Get Ironic UUID from BMH annotation or by name match
IRONIC_UUID=$(kubectl get bmh -n <namespace> <bmh-fqdn> \
  -o jsonpath='{.metadata.annotations.metal3\.io/hardware-details}' 2>/dev/null || \
  kubectl exec -n ironic-system ironic-standalone-conductor-0 -- baremetal \
    --os-endpoint http://ironic-standalone-api:6387 \
    --os-auth-type http_basic \
    --os-username "$IRONICUSER" --os-password "$IRONICPASS" \
    node list --fields uuid name | grep <bmh-fqdn-short> | awk '{print $2}')

kubectl exec -n ironic-system ironic-standalone-conductor-0 -- baremetal \
  --os-endpoint http://ironic-standalone-api:6387 \
  --os-auth-type http_basic \
  --os-username "$IRONICUSER" --os-password "$IRONICPASS" \
  node show <ironic-uuid> \
  --fields provision_state power_state target_provision_state last_error
```

Expected stuck state: `provision_state = clean failed`, `last_error` contains Redfish 500 / TLS certificate error.

Also check BMH error count:

```bash
kubectl get bmh -n <namespace> <bmh-fqdn> \
  -o jsonpath='{.status.errorCount}{"\t"}{.status.errorMessage}{"\n"}'
```

### 2. Get BMC credentials from the BMH secret

The BMH `spec.bmc.credentialsName` points to a Secret in the same namespace:

```bash
kubectl get bmh -n <namespace> <bmh-fqdn> \
  -o jsonpath='{.spec.bmc.credentialsName}{"\n"}'
# -> returns e.g. "stgt10com5i75.inf.bm4x.telekom.de"

BMC_PASSWORD=$(kubectl get secret -n <namespace> <credentials-secret> \
  -o jsonpath='{.data.password}' | base64 -d)
```

The BMC FQDN is the BMH name itself (same as the secret name).

### 3. Run AuxReset.sh

```bash
BMC_PASSWORD='<password>' bash /home/a11873341/git/schiff/ops-manifests/bin/AuxReset.sh \
  -i <bmh-fqdn>
```

Expected successful output:

- Vendor detected: `lenovo` or `hpe`
- HTTP response: **`204 No Content`** (Lenovo) or `200 OK` (HPE)

A `204` means the BMC accepted the reset command and is rebooting. The BMC will be unreachable for ~90–120 seconds.

### 4. Retrigger Ironic cleaning

After the BMC restarts, move the Ironic node from `clean failed` → `manageable` → `available` (which triggers a fresh cleaning cycle):

```bash
IRONICUSER=$(kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.username}' | base64 -d)
IRONICPASS=$(kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.password}' | base64 -d)

IRONIC_CMD="kubectl exec -n ironic-system ironic-standalone-conductor-0 -- baremetal \
  --os-endpoint http://ironic-standalone-api:6387 \
  --os-auth-type http_basic \
  --os-username $IRONICUSER --os-password $IRONICPASS"

# Step 1: move to manageable
$IRONIC_CMD node manage <ironic-uuid>

# Step 2: verify manageable
$IRONIC_CMD node show <ironic-uuid> \
  --fields provision_state power_state target_provision_state last_error

# Step 3: trigger cleaning
$IRONIC_CMD node provide <ironic-uuid>

# Step 4: monitor
$IRONIC_CMD node show <ironic-uuid> \
  --fields provision_state power_state target_provision_state last_error
```

Expected progression: `clean failed` → `manageable` → `cleaning` → `available`

**Wait ~90 seconds** after AuxReset before running `node manage` — the BMC needs time to restart fully.

### 5. Verify BMH recovers

Once Ironic reaches `available`, the Metal3/BMO controller will pick it up and transition the BMH from `deprovisioning` to `available`. Watch:

```bash
kubectl get bmh -n <namespace> <bmh-fqdn> -w
```

The MachineDeployment stuck in `ScalingDown` should then progress — the old Machine will complete deletion and the alert will clear.

## Finding the Ironic UUID

The easiest way is to match by node name in Ironic. Ironic names follow the pattern `<namespace>~<bmh-fqdn>`:

```bash
IRONICUSER=...; IRONICPASS=...
kubectl exec -n ironic-system ironic-standalone-conductor-0 -- baremetal \
  --os-endpoint http://ironic-standalone-api:6387 \
  --os-auth-type http_basic \
  --os-username "$IRONICUSER" --os-password "$IRONICPASS" \
  node list --fields uuid name | grep <bmh-fqdn>
```

## Ironic credentials

The BMO Ironic credentials (for the `baremetal` CLI) are in:

```bash
kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.username}' | base64 -d
kubectl get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.password}' | base64 -d
```

The Ironic API endpoint (ClusterIP, only reachable from inside the cluster via exec):

```text
http://ironic-standalone-api:6387
```

Auth type: `http_basic`

## If cleaning fails again after BMC reset

The TLS certificate issue on Lenovo XCC is caused by the BMC caching the ironic-boot certificate as untrusted. A BMC reset clears this cache. If it fails again after a reset:

1. Check whether the ironic-boot TLS certificate was recently rotated — a new cert may cause the same issue on first contact.
2. Consider disabling automated cleaning on the BMH as a temporary workaround:

   ```bash
   kubectl patch bmh -n <namespace> <bmh-fqdn> \
     --type=merge -p '{"spec":{"automatedCleaningMode":"disabled"}}'
   ```

   Then retrigger from `clean failed` → `manageable` → `available`. With cleaning disabled, Ironic skips VirtualMedia entirely and the BMH becomes available without disk wiping. Re-enable cleaning once the cert issue is resolved.
3. If hardware is persistently unreachable, escalate to DC-ops using the **`mark-bmh-defect`** skill.

## Safety rules

- **Confirm** with the user before running AuxReset — it causes a ~2 minute BMC outage and interrupts any in-progress Redfish operations on the node.
- **Do not run** on a BMH that is currently provisioned and serving workloads — a BMC reset may disrupt power management and health monitoring for a running node.
- The `node manage` + `node provide` steps are **safe to retry** if the BMC is still starting up — Ironic will return an error and you can re-run after waiting longer.
- Record the incident in the KB after resolution.
