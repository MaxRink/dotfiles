# Troubleshooting Runbooks

Common CaaS alert troubleshooting patterns using read-only kubectl commands.

## Table of Contents

1. [TargetDown (kube-state-metrics)](#targetdown-kube-state-metrics)
2. [TargetDown (generic)](#targetdown-generic)
3. [Pod CrashLoopBackOff / OOMKilled](#pod-crashloopbackoff--oomkilled)
4. [Node NotReady](#node-notready)
5. [etcd Issues](#etcd-issues)
6. [Persistent Volume Issues](#persistent-volume-issues)
7. [Certificate Issues](#certificate-issues)
8. [DNS Issues](#dns-issues)
9. [Resource Pressure](#resource-pressure)

---

## TargetDown (kube-state-metrics)

**Alert:** `TargetDown` for job `kube-state-metrics` in `kube-system`

```bash
# 1. Check pod status
kubectl_ro.py CLUSTER get pods -n kube-system -l app.kubernetes.io/name=kube-state-metrics -o wide

# 2. Describe the pod (look for OOMKilled, resource limits, events)
kubectl_ro.py CLUSTER describe pod -n kube-system -l app.kubernetes.io/name=kube-state-metrics

# 3. Check resource usage on the node where it runs
kubectl_ro.py CLUSTER top nodes

# 4. Count cluster resources (high counts → more memory needed)
kubectl_ro.py CLUSTER get pods -A --no-headers | wc -l
kubectl_ro.py CLUSTER get deployments -A --no-headers | wc -l
kubectl_ro.py CLUSTER get statefulsets -A --no-headers | wc -l
```

**Common cause:** OOMKilled — memory limit (often 256Mi) too low for large clusters. Fix by increasing memory limit to 512Mi–1Gi in Helm values.

---

## TargetDown (generic)

**Alert:** `TargetDown` for any Prometheus scrape target

```bash
# 1. Find the affected pods
kubectl_ro.py CLUSTER get pods -A | grep -i <job-name>

# 2. Check pod status and describe
kubectl_ro.py CLUSTER describe pod <pod-name> -n <namespace>

# 3. Check the service and endpoints
kubectl_ro.py CLUSTER get svc -A | grep <job-name>
kubectl_ro.py CLUSTER get endpoints -A | grep <job-name>

# 4. Check if the ServiceMonitor exists
kubectl_ro.py CLUSTER get servicemonitors -A | grep <job-name>
```

---

## Pod CrashLoopBackOff / OOMKilled

```bash
# 1. Find crashing pods
kubectl_ro.py CLUSTER get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# 2. Describe the pod (look for Last State, Exit Code, Events)
kubectl_ro.py CLUSTER describe pod <pod-name> -n <namespace>

# 3. Check logs (current and previous crash)
kubectl_ro.py CLUSTER logs <pod-name> -n <namespace> --tail=100
kubectl_ro.py CLUSTER logs <pod-name> -n <namespace> --previous --tail=100

# 4. Check resource limits vs actual usage
kubectl_ro.py CLUSTER top pods -n <namespace>

# 5. Check node resources
kubectl_ro.py CLUSTER top nodes
```

**Key indicators:**
- Exit code 137 → OOMKilled (increase memory limits)
- Exit code 1 → Application error (check logs)
- Exit code 255 → Unknown crash (check describe events)

---

## Node NotReady

```bash
# 1. Check node status
kubectl_ro.py CLUSTER get nodes -o wide

# 2. Describe the NotReady node (check Conditions, Taints, Events)
kubectl_ro.py CLUSTER describe node <node-name>

# 3. Check pods on the affected node
kubectl_ro.py CLUSTER get pods -A --field-selector spec.nodeName=<node-name> -o wide

# 4. Check system pod health on that node
kubectl_ro.py CLUSTER get pods -n kube-system --field-selector spec.nodeName=<node-name>

# 5. Check recent events
kubectl_ro.py CLUSTER get events -A --sort-by='.lastTimestamp' | tail -30
```

**Common causes:**
- kubelet not running → check via SSH/BMC
- Network partition → check TOR switches (use caas-network-diag skill)
- Disk pressure → check Conditions in describe output
- Memory pressure → check Conditions in describe output

---

## etcd Issues

```bash
# 1. Check etcd pods
kubectl_ro.py CLUSTER get pods -n kube-system -l component=etcd -o wide

# 2. Describe etcd pods
kubectl_ro.py CLUSTER describe pods -n kube-system -l component=etcd

# 3. Check etcd logs
kubectl_ro.py CLUSTER logs -n kube-system -l component=etcd --tail=100

# 4. Check control plane node health
kubectl_ro.py CLUSTER get nodes -l node-role.kubernetes.io/control-plane= -o wide
kubectl_ro.py CLUSTER top nodes -l node-role.kubernetes.io/control-plane=
```

---

## Persistent Volume Issues

```bash
# 1. Check PV and PVC status
kubectl_ro.py CLUSTER get pv
kubectl_ro.py CLUSTER get pvc -A

# 2. Find pending PVCs
kubectl_ro.py CLUSTER get pvc -A --field-selector=status.phase=Pending

# 3. Describe pending PVC (check Events for binding issues)
kubectl_ro.py CLUSTER describe pvc <pvc-name> -n <namespace>

# 4. Check storage classes
kubectl_ro.py CLUSTER get storageclasses

# 5. Check CSI pods
kubectl_ro.py CLUSTER get pods -A | grep -i csi
```

---

## Certificate Issues

```bash
# 1. Check certificate resources
kubectl_ro.py CLUSTER get certificates -A
kubectl_ro.py CLUSTER get certificaterequests -A

# 2. Check cert-manager pods
kubectl_ro.py CLUSTER get pods -n cert-manager

# 3. Describe failing certificate
kubectl_ro.py CLUSTER describe certificate <cert-name> -n <namespace>

# 4. Check CSR status
kubectl_ro.py CLUSTER get csr
```

---

## DNS Issues

```bash
# 1. Check CoreDNS pods
kubectl_ro.py CLUSTER get pods -n kube-system -l k8s-app=kube-dns -o wide

# 2. Describe CoreDNS pods
kubectl_ro.py CLUSTER describe pods -n kube-system -l k8s-app=kube-dns

# 3. Check CoreDNS logs
kubectl_ro.py CLUSTER logs -n kube-system -l k8s-app=kube-dns --tail=50

# 4. Check DNS service
kubectl_ro.py CLUSTER get svc -n kube-system kube-dns
kubectl_ro.py CLUSTER get endpoints -n kube-system kube-dns
```

---

## Resource Pressure

```bash
# 1. Node resource overview
kubectl_ro.py CLUSTER top nodes

# 2. Pod resource usage (sorted by memory in a specific namespace)
kubectl_ro.py CLUSTER top pods -A --sort-by=memory

# 3. Check resource quotas
kubectl_ro.py CLUSTER get resourcequotas -A

# 4. Check limit ranges
kubectl_ro.py CLUSTER get limitranges -A

# 5. Check node conditions for pressure
kubectl_ro.py CLUSTER describe nodes | grep -A5 "Conditions:"
```
