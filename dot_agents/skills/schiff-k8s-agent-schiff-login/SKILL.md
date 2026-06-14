---
name: schiff-k8s-agent-schiff-login
description: "Imported local skill: Skill: schiff-login"
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/schiff-login by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Skill: schiff-login

## Purpose

Log in to a Schiff Kubernetes cluster and set the kubectl context using the `schiff login` CLI.

## Naming Convention

All cluster names and kubectl context names follow the same pattern:

```text
<cluster_name>.<env>.<location>
```

Examples:

- `ship-lab-1.dev.bn461`
- `schiff-canary-1.dev.bn461`
- `a4-3.reftmdc.n`
- `schiff-cp-1.reftmdc.n`

The CAPI namespace on the management cluster encodes env and location:

```text
metal3-<env>-<location>   →   e.g. metal3-dev-bn461  →  env=dev, location=bn461
vsphere-<env>-<location>  →   e.g. vsphere-reftmdc-bn → env=reftmdc, location=bn
```

Use this to derive the correct `schiff login` target when you only know the CAPI namespace.

## Login

```bash
schiff login <cluster_name>.<env>.<location>
# e.g.
schiff login ship-lab-1.dev.bn461
```

After login the context is added to kubeconfig with the same name as the argument.

## Switch context

```bash
kubectl config use-context <cluster_name>.<env>.<location>
```

## Check existing contexts first

Before running `schiff login`, check if the context already exists:

```bash
kubectl config get-contexts | grep <cluster_name>
```

If it is listed, just use `kubectl config use-context` — no login needed.

## Management cluster lookup

The management cluster for a tenant cluster is stored in the SchiffCluster YAML
(`spec.internal.managementCluster`). Use the `find-mgnt-cluster` skill to resolve it.

CAPI resources (Machine, MachineDeployment, BareMetalHost, Metal3Machine) live on the
**management cluster**, not on the tenant cluster.

## Common pitfalls

- `schiff login` with the wrong env/location will fail with `Forwarding failure` or
  `notresolvable` — double-check the env/location from the CAPI namespace name.
- After a failed `schiff login` the context may still be written but point to an
  unreachable endpoint — verify with `kubectl cluster-info` after switching.
- Some lab/dev clusters (`dev.*`) may be unreachable from the jump host. In that case
  work exclusively from the management cluster using CAPI resources.
