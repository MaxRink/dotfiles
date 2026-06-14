---
name: schiff-k8s-agent-clean-stuck-bmh
description: Release a BareMetalHost that is stuck in provisioning, deprovisioning, Ironic clean wait/clean failed, or registration error caused by an orphaned Ironic node (MAC conflict). Covers DXE INIT / IPA-unresponsive hosts and RegistrationError scenarios.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/clean-stuck-bmh by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Skill: clean-stuck-bmh

## Release a BareMetalHost stuck in provisioning / Ironic cleaning

Use this skill when a BMH cannot leave `provisioning`, `deprovisioning`, or when Ironic is stuck in `clean wait` / `clean failed` because the physical host is unresponsive (e.g. stuck in DXE INIT, no Ironic agent heartbeat).

## When to use

- BMH state stuck in `provisioning` or `deprovisioning` for an extended time (> 30 min).
- Ironic node in `clean wait` with no active reservation and no callback from the IPA agent.
- Ironic cleaning fails repeatedly with errors like:
  - `Timeout reached while waiting for callback for node <uuid>`
  - `The attribute Links/ManagedBy is missing from the resource /redfish/v1/Systems/1`
- Power cycle was attempted but the host still does not respond.
- Goal is to either re-provision the host or hand it back to DC-ops (`ReturnRequested`).

Do **not** use this skill for transient errors (e.g. a single reboot that is in progress). Wait at least 30 minutes and confirm via Ironic that no callback is arriving before intervening.

## Inputs

- BMH FQDN, e.g. `kln20com5i5u.inf.bm4x.telekom.de`
- Management cluster context, e.g. `schiff-mgmt-3.tmdc.b`
- Metal3 namespace, e.g. `metal3-tst-kln20`
- Ironic node UUID (read from `status.provisioning.ID` on the BMH)
- Whether the host should be re-provisioned or handed back to DC-ops

## Key facts about the stack

```text
BMH (Kubernetes CRD)
  └── watched by BMO (baremetal-operator, ns: bmo-system)
        └── drives Ironic via REST API
              └── Ironic conducts PXE boot / IPA agent / cleaning on physical host
```

**Important:** BMO continuously reconciles the BMH and will re-set `automated_clean=true` in Ironic if you patch the Ironic node directly while BMO is running. You **must** pause BMO reconciliation on the BMH before patching Ironic cleaning settings.

## Step-by-step procedure

### 1. Identify BMH, Ironic UUID and Compute

```bash
# Find the BMH
kubectl --context=<mgmt-ctx> get bmh -A | grep <hostname>

# Get Ironic node UUID and current state
kubectl --context=<mgmt-ctx> get bmh -n <namespace> <fqdn> \
  -o jsonpath='state={.status.provisioning.state} uuid={.status.provisioning.ID}{"\n"}'

# Find associated Compute
kubectl --context=<mgmt-ctx> get computes -A | grep <hostname>
```

Record: BMH namespace, Ironic UUID, Compute name.

### 2. Check if a CAPI Machine / tenant node is bound

```bash
kubectl --context=<mgmt-ctx> get compute <compute-name> -n <namespace> \
  -o jsonpath='{.spec.consumerRef}{"\n"}'
```

- **No consumerRef** → proceed directly to step 3.
- **consumerRef present** → the Compute is bound to a tenant cluster Machine. Check whether the K8s node actually exists in the tenant cluster:

  ```bash
  kubectl --context=<tenant-ctx> get nodes | grep <hostname>
  ```

  - If the node **never joined** (Machine in `Provisioning` state, no K8s node) → delete the CAPI Machine directly:

    ```bash
    kubectl --context=<mgmt-ctx> delete machine <machine-name> -n <namespace>
    ```

  - If the node **is part of a running cluster** → drain the node first, confirm with the tenant owner, then delete the Machine.

### 3. Check Ironic node state via API

Ironic credentials are in `bmo-system/baremetal-operator-ironic-credentials`.

```bash
USER=$(kubectl --context=<mgmt-ctx> get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.username}' | base64 -d)
PASS=$(kubectl --context=<mgmt-ctx> get secret -n bmo-system baremetal-operator-ironic-credentials \
  -o jsonpath='{.data.password}' | base64 -d)
UUID=<ironic-node-uuid>

kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
import urllib.request, base64, json
def ironic_req(method, path, body=None):
    url = 'http://ironic-standalone-api.ironic-system.svc:6387' + path
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', 'Basic ' + base64.b64encode(b'${USER}:${PASS}').decode())
    req.add_header('X-OpenStack-Ironic-API-Version', '1.56')
    req.add_header('Accept', 'application/json')
    if body is not None:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
s,r = ironic_req('GET', '/v1/nodes/${UUID}?fields=provision_state,target_provision_state,last_error,automated_clean,reservation')
print(json.dumps(json.loads(r), indent=2))
"
```

Expected stuck states: `clean wait`, `cleaning`, `clean failed`.

### 4. Pause BMO reconciliation on the BMH

This is **critical** — without this, BMO re-sets `automated_clean=true` in Ironic after every patch.

```bash
kubectl --context=<mgmt-ctx> annotate bmh -n <namespace> <fqdn> \
  baremetalhost.metal3.io/paused=true --overwrite
```

Also remove detached annotation if previously set:

```bash
kubectl --context=<mgmt-ctx> annotate bmh -n <namespace> <fqdn> \
  baremetalhost.metal3.io/detached=true --overwrite
```

### 5. Abort Ironic cleaning (if in `clean wait`)

Wait until Ironic has no active reservation on the node (reservation=None), then abort:

```bash
# Poll until reservation is clear
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
import urllib.request, base64, json
...  # use ironic_req helper from step 3
s,r = ironic_req('PUT', '/v1/nodes/${UUID}/states/provision', {'target': 'abort'})
print(f'abort: HTTP {s}')
"
```

If node is locked (HTTP 409), wait for the reservation to clear and retry.

### 6. Disable automated_clean + transition to available

Once Ironic is in `clean failed` with no reservation, run in a single sequence to avoid BMO re-enabling cleaning:

```bash
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
import urllib.request, base64, json, time
def ironic_req(method, path, body=None):
    url = 'http://ironic-standalone-api.ironic-system.svc:6387' + path
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', 'Basic ' + base64.b64encode(b'<USER>:<PASS>').decode())
    req.add_header('X-OpenStack-Ironic-API-Version', '1.56')
    req.add_header('Accept', 'application/json')
    if body is not None:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req) as r: return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
NODE = '<ironic-uuid>'
# 1. Disable automated cleaning directly in Ironic
s,r = ironic_req('PATCH', f'/v1/nodes/{NODE}', [{'op': 'replace', 'path': '/automated_clean', 'value': False}])
print(f'1. automated_clean=false: HTTP {s}')
time.sleep(2)
# 2. Move to manageable
s,r = ironic_req('PUT', f'/v1/nodes/{NODE}/states/provision', {'target': 'manage'})
print(f'2. manage: HTTP {s}')
time.sleep(10)
# 3. Move to available (no cleaning because automated_clean=false)
s,r = ironic_req('PUT', f'/v1/nodes/{NODE}/states/provision', {'target': 'provide'})
print(f'3. provide: HTTP {s}')
time.sleep(5)
# 4. Verify
s,r = ironic_req('GET', f'/v1/nodes/{NODE}?fields=provision_state,automated_clean')
d = json.loads(r)
print(f'4. final state={d[\"provision_state\"]} automated_clean={d.get(\"automated_clean\")}')
"
```

Expected final output: `state=available automated_clean=False`

### 7. Re-enable BMO (remove pause annotation)

```bash
kubectl --context=<mgmt-ctx> annotate bmh -n <namespace> <fqdn> \
  baremetalhost.metal3.io/paused- \
  baremetalhost.metal3.io/detached- \
  cluster.x-k8s.io/paused- 2>/dev/null || true
```

Poll until BMH reaches `available`:

```bash
watch kubectl --context=<mgmt-ctx> get bmh -n <namespace> <fqdn> \
  -o jsonpath='{.status.provisioning.state}{"\n"}'
```

### 8. Mark Compute as ReturnRequested (if hardware defect)

If the goal is to return the host to DC-ops, patch the Compute:

```bash
kubectl --context=<mgmt-ctx> patch compute <compute-name> -n <namespace> \
  --type=merge \
  -p '{"spec":{"problem":{"reason":"ReturnRequested","details":"<short description of defect>"}}}'
```

Verify operator reaction (should transition within seconds):

```bash
kubectl --context=<mgmt-ctx> get compute <compute-name> -n <namespace> \
  -o jsonpath='{.status.conditions}' | python3 -m json.tool
```

Expected: `Ready=False`, `BoundHostReady=False (ComputeDeletionPending)`.

### 9. Verify no active alerts

```text
alertmanager_list_alerts(filter=["instance=~\"<hostname>.*\""], active=true)
```

Silence if needed (see mark-bmh-defect skill).

### 10. Document in KB

```text
kb_store_incident(
  title="<hostname> stuck in DXE INIT / clean wait — released and ReturnRequested",
  affected_component="cluster/<tenant>, node/<fqdn>, namespace/<metal3-ns>",
  root_cause="<hardware symptom + Ironic error>",
  resolution="<steps taken>",
  tags="dxe-init,ironic,cleaning,return-requested,automated-clean,metal3"
)
```

## State machine reference

```text
Ironic provision states (relevant subset):
  enroll → manageable → available → active (provisioned)
                    ↑         ↑
                 manage    provide
                    ↓
               cleaning → clean wait (waiting for IPA) → clean failed
                    ↑
               (provide triggers cleaning if automated_clean=true)

Key transitions used in this skill:
  clean wait  --[abort]-->  clean failed
  clean failed --[manage]--> manageable
  manageable  --[provide]--> available   (no cleaning if automated_clean=false)
```

## Common errors and their meaning

| Error | Meaning |
|---|---|
| `Timeout reached while waiting for callback for node <uuid>` | IPA agent on physical host never responded — host is unresponsive |
| `The attribute Links/ManagedBy is missing from the resource /redfish/v1/Systems/1` | Redfish/BMC issue during cleaning prepare step — usually accompanies DXE INIT stuck |
| HTTP 409 on provision state change | Node locked by a conductor (`reservation` field set) — wait and retry |
| HTTP 400 on `provide` from `clean failed` | Cannot `provide` from `clean failed` directly — must go via `manage` first |
| `automated_clean` reverts to `true` after patch | BMO is overwriting it — pause BMO first via `baremetalhost.metal3.io/paused=true` |

## Safety rules

- **Always pause BMO** (`baremetalhost.metal3.io/paused=true`) before patching Ironic settings directly — BMO will overwrite them otherwise.
- **Always remove the pause annotation** after the operation is complete.
- **Never force-delete** the BMH or Compute object — always use the operator workflow.
- **Confirm no active tenant workloads** before deleting a CAPI Machine.
- If the CAPI Machine was never joined to K8s (state `Provisioning`), it is safe to delete without draining.
  - If in doubt whether the host will be re-provisioned or returned, complete the BMH release to `available` first and then decide.

---

## Scenario: BMH stuck in RegistrationError — MAC conflict with orphaned Ironic node

Use this scenario when a BMH shows `errorType: registration error` and the BMO logs / BMH `errorMessage` indicate that Ironic already has a node with the same MAC address or name — even though no BMH object for that name exists in the current namespace.

### Root cause

When a BMH is deleted from one namespace (e.g. `metal3-prd-kln20`) but the corresponding Ironic node is **not cleaned up** (e.g. due to a failed deprovision or manual BMH deletion), the Ironic node stays in the database. Ironic performs a global MAC-address uniqueness check when a new BMH in a different namespace tries to register the same physical host. This blocks registration with an error like:

```text
failed to create a new Ironic node: ... already exists with name metal3-prd-kln20~<fqdn>
```

The orphaned Ironic node may be in state `clean failed` with `maintenance=true` and its BMC is no longer reachable.

### When to use

- BMH stuck in `registrationError` for > 10 minutes.
- `kubectl describe bmh` shows `errorType: registration error` and the error message references an existing Ironic node name from a **different namespace** (e.g. `metal3-prd-*` when the BMH is in `metal3-tst-*`).
- Searching Ironic confirms a node with the matching FQDN exists but has no corresponding BMH object.

### Inputs

- BMH FQDN, e.g. `kln20com5i3a.inf.bm4x.telekom.de`
- Management cluster context, e.g. `schiff-mgmt-3.tmdc.b`
- Metal3 namespace of the **new** BMH (the one in error), e.g. `metal3-tst-kln20`

### Ironic API connection details

> **Note:** Ironic credentials differ from what is referenced in the stuck-provisioning scenario above.
> Use the secret in `ironic-system`, not `bmo-system`.

```bash
# Credentials
USER=$(kubectl --context=<mgmt-ctx> get secret -n ironic-system ironic-standalone-secret \
  -o jsonpath='{.data.ironicUsername}' | base64 -d)
PASS=$(kubectl --context=<mgmt-ctx> get secret -n ironic-system ironic-standalone-secret \
  -o jsonpath='{.data.ironicPassword}' | base64 -d)

# API base URL (port 6387, not 6385)
IRONIC_URL="http://ironic-standalone-api.ironic-system.svc:6387"

# Required header — without this Ironic returns HTTP 406
# Use version 1.80 or higher
IRONIC_API_VERSION="1.80"
```

Run all Ironic API calls from inside the conductor pod:

```bash
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "..."
```

### Step-by-step procedure

#### 1. Confirm the RegistrationError

```bash
kubectl --context=<mgmt-ctx> get bmh -n <namespace> <fqdn> \
  -o jsonpath='state={.status.provisioning.state} errorType={.status.errorType}{"\n"}errorMsg={.status.errorMessage}{"\n"}'
```

Expected output includes `errorType=registration error` and a message like:
`Node of name metal3-prd-kln20~<fqdn> already exists`.

#### 2. Find the orphaned Ironic node

Search by name (namespace~fqdn format):

```bash
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
import urllib.request, base64, json, urllib.parse
USER='<user>'; PASS='<pass>'
BASE='http://ironic-standalone-api.ironic-system.svc:6387'
FQDN='<fqdn>'

def ironic_req(method, path):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header('Authorization', 'Basic ' + base64.b64encode(f'{USER}:{PASS}'.encode()).decode())
    req.add_header('X-OpenStack-Ironic-API-Version', '1.80')
    req.add_header('Accept', 'application/json')
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, e.read().decode()

# List all nodes containing the FQDN in their name
s, r = ironic_req('GET', '/v1/nodes?detail=true&limit=500')
nodes = [n for n in r['nodes'] if FQDN in n.get('name','')]
for n in nodes:
    print(f'uuid={n[\"uuid\"]} name={n[\"name\"]} state={n[\"provision_state\"]} maintenance={n[\"maintenance\"]}')
"
```

Note the UUID of the orphaned node (will be in a namespace like `metal3-prd-*`).

Also verify there is no corresponding BMH object for this node:

```bash
kubectl --context=<mgmt-ctx> get bmh -A | grep <fqdn>
```

Only the new BMH (in the TST namespace, in error state) should appear. If a BMH still exists for the PRD namespace node, **do not delete the Ironic node** — investigate why the BMH still exists.

#### 3. Check the orphaned node has no active ports / reservations

```bash
# Check ports (MAC associations)
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
...  # use ironic_req helper
s, r = ironic_req('GET', '/v1/ports?node=<orphaned-uuid>&detail=true')
print(json.dumps(r, indent=2))
"

# Check node details: reservation, target_provision_state
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
...
s, r = ironic_req('GET', '/v1/nodes/<orphaned-uuid>?fields=provision_state,target_provision_state,reservation,maintenance,last_error')
print(json.dumps(r, indent=2))
"
```

It is safe to delete if:

- `reservation` is `null`
- The node is **not** in an active transition (`target_provision_state` is `null`)
- No corresponding BMH object exists in any namespace

#### 4. Delete the orphaned Ironic node

```bash
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
import urllib.request, base64, json
USER='<user>'; PASS='<pass>'
BASE='http://ironic-standalone-api.ironic-system.svc:6387'
UUID='<orphaned-uuid>'

req = urllib.request.Request(BASE + f'/v1/nodes/{UUID}', method='DELETE')
req.add_header('Authorization', 'Basic ' + base64.b64encode(f'{USER}:{PASS}'.encode()).decode())
req.add_header('X-OpenStack-Ironic-API-Version', '1.80')
try:
    with urllib.request.urlopen(req) as r:
        print(f'DELETE HTTP {r.status}')   # expect 204
except urllib.error.HTTPError as e:
    print(f'ERROR HTTP {e.code}: {e.read().decode()}')
"
```

Expected: `DELETE HTTP 204` — the node is gone.

Confirm deletion:

```bash
# Should return 404
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
...
s, r = ironic_req('GET', '/v1/nodes/<orphaned-uuid>')
print(f'HTTP {s}')
"
```

#### 5. Reset BMH error state

The BMH is in an error backoff loop and will not retry immediately. Reset the error counters via a status patch:

```bash
kubectl --context=<mgmt-ctx> patch bmh -n <namespace> <fqdn> \
  --subresource=status \
  --type=merge \
  -p '{"status":{"errorCount":0,"errorMessage":"","errorType":"registration error"}}'
```

#### 6. Trigger BMO reconcile

Annotate the BMH to force BMO to reconcile immediately (without waiting for the next watch event):

```bash
TS=$(date +%s)
kubectl --context=<mgmt-ctx> annotate bmh -n <namespace> <fqdn> \
  "force-reconcile-${TS}=true" --overwrite
```

#### 7. Monitor re-registration

Poll the BMH state — it should move from `registrationError` → `registering` → `available` (or `inspecting`) within a few minutes:

```bash
watch kubectl --context=<mgmt-ctx> get bmh -n <namespace> <fqdn> \
  -o jsonpath='{.status.provisioning.state}  errorType={.status.errorType}  errorMsg={.status.errorMessage}{"\n"}'
```

Confirm in Ironic that a **new** node UUID was created for the correct namespace:

```bash
# Should now find a node named <namespace>~<fqdn> with a new UUID
kubectl --context=<mgmt-ctx> exec -n ironic-system ironic-standalone-conductor-0 -- \
  python3 -c "
...
s, r = ironic_req('GET', '/v1/nodes?detail=false&limit=500')
nodes = [n for n in r['nodes'] if '<fqdn>' in n.get('name','')]
for n in nodes: print(n['uuid'], n['name'], n['provision_state'])
"
```

### Error table

| Error | Meaning / Action |
|---|---|
| `already exists with name <ns>~<fqdn>` in BMH errorMessage | Orphaned Ironic node from old namespace — follow this scenario |
| HTTP 409 on DELETE | Node is locked by a conductor — wait for `reservation` to clear, retry |
| HTTP 400 on DELETE with `"Cannot delete a node ... in manageable"` | Set node to `enroll` state first: `PUT /v1/nodes/<uuid>/states/provision {"target":"enroll"}`, then DELETE |
| BMH stays in `registrationError` after step 6 | Check BMO logs: `kubectl --context=<mgmt-ctx> logs -n bmo-system deploy/baremetal-operator-controller-manager --since=5m` |
| New Ironic node not appearing | BMO may still be in error backoff — repeat step 5 (reset errorCount) and step 6 (force-reconcile) |

### Safety rules specific to this scenario

- **Verify no BMH exists for the orphaned node** before deleting it from Ironic — deleting an Ironic node that is still managed by a BMH will break the BMH permanently.
- **Do not delete** from Ironic if the node has `reservation != null` — a conductor is actively working on it.
- The Ironic node name format is `<k8s-namespace>~<bmh-fqdn>` — use this to distinguish which namespace originally owned the node.
- After the fix the BMH should register with a **new UUID** in Ironic. The old UUID is gone and must not be referenced again.

### Document in KB

```text
kb_store_incident(
  title="<hostname> RegistrationError — orphaned Ironic node MAC conflict",
  affected_component="cluster/<mgmt-cluster>, node/<fqdn>, namespace/<metal3-ns>",
  alert_name="BareMetalHostRegistrationError",
  root_cause="Orphaned Ironic node from namespace <old-ns> blocked re-registration via MAC uniqueness check",
  resolution="Deleted orphaned Ironic node via DELETE /v1/nodes/<uuid>, reset BMH errorCount, triggered force-reconcile",
  tags="ironic,registration-error,orphaned-node,mac-conflict,metal3,bmh"
)
```
