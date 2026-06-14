# Velero CloudSettings

Velero backup configuration is defined in the `mom-factory-adopted` repo (`tdi-caas/mom-factory-adopted` on GitLab), in the file `settings.tpl.yaml`.

> **Always fetch the live config** from GitLab when answering questions about Velero — do not rely on the examples below, as they may be outdated. The snippets here are for orientation only.

The velero config is nested under each cloud's `settings.velero` key and consumed by the `velero` function definition via `.CloudSettings`.

## How to Look It Up

Use the **`gitlab` skill** to fetch the live file from GitLab:

- **Repository:** `tdi-caas/mom-factory-adopted`
- **File:** `settings.tpl.yaml` (branch: `master`)
- Search for `velero:` sections, or filter lines containing `velero`, `s3Url`, `s3Region`, `authUrl`, `s3AccessKey`

The gitlab skill can retrieve file contents directly — invoke it and ask for the file `settings.tpl.yaml` from `tdi-caas/mom-factory-adopted`.

## Two Providers (examples — check live config for current values)

### 1. `radosgw` — used by most clusters

Uses OpenStack Keystone auth (no S3 URL). Example structure:

```yaml
velero: &veleroRadosGW
  provider: radosgw
  config:
    clouds:
      - name: <cloud-name>
        authUrl: https://keystone.<cloud>.in.pan-net.eu:5000/v3
        projectName: caas-velero-backup-<cloud>
        username: "{{ .velero_rados_gw_<cloud>_username }}"
        password: "{{ .velero_rados_gw_<cloud>_password }}"
        schedule: "0 3 * * *"
```

### 2. `s3` — used by OTE clusters only

Uses AWS-style S3 endpoint. Example structure:

```yaml
velero: &veleroS3OTE
  provider: s3
  config:
    clouds:
      - name: <cloud-name>
        s3Url: 'https://<s3-endpoint>'
        s3Region: <region>
        s3AccessKeyId: "{{ .<cloud>.s3AccessKeyId }}"
        s3SecretAccessKey: "{{ .<cloud>.s3SecretAccessKey }}"
        schedule: "0 4 * * *"
        insecure: "true"
```

## How the Function Uses It

In `velero-2.2.6` (function definition in `tdi-caas/caas-bundles`), the provider is read from `.Settings.velero.provider` and the clouds list from `.Settings.velero.config.clouds`. The `s3Url` field maps to the `s3Url` key in the `BackupStorageLocation` via the `velero-customer-backup-resources` helm release.

## Credentials

Velero credentials (passwords, access keys) are templated variables resolved at deploy time — they are **not stored in plaintext** in `settings.tpl.yaml`.

## Repo References

- **CloudSettings file:** `tdi-caas/mom-factory-adopted` → `settings.tpl.yaml`
- **Function definition:** `tdi-caas/caas-bundles` → `functions/velero/velero-<version>.yaml`
- **Cluster templates:** `tdi-caas/mom-factory-adopted` → `clusters/<cluster>/caasCluster.tpl.yaml`
