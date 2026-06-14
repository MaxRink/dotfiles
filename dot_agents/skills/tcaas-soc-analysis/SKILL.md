---
name: tcaas-soc-analysis
description: Use when researching T-CaaS code, configuration, Confluence/documentation exports, implementation repositories, and PSA SoC answer files to produce evidence-backed SoC answers and reusable project analysis artifacts.
---

<!-- Imported from tcaas-psa/skill/tcaas-soc-analysis by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# T-CaaS SoC Analysis

Use this skill for repeatable T-CaaS project analysis and PSA SoC answering.

## Workflow

1. Prefer scripts in `scripts/tcaas_analysis.py` over ad hoc prompts.
2. Treat local code/config evidence as read-only. Do not decrypt secrets or run cluster mutation commands.
3. Store all research outputs under `tcaas-psa/analysis/`.
4. Keep SoC answers in `psa_answers_v1` JSON from the `psa-portal-soc-capture` skill.
5. Treat `analysis/soc-answers/answer_rebuild_manifest.json` plus the versioned batch files as the source of truth for reviewed answers. The full `analysis/soc-answers/tcaas-core_scope_draft_answers.json` file is generated and ignored because it duplicates the template plus batches.
6. Every final answer must have evidence or be marked `research_needed`; `NA` is valid only with a concrete scoping reason.
7. Keep answer explanations in English.
8. Do not treat AI/ML, Private Clouds, or Router und Switche as blanket `NA`:
   - AI/ML applies to development and CI review tooling where T-CaaS uses AI.
   - Private Clouds applies because T-CaaS is a private cloud / telco cloud managed Kubernetes platform.
   - Router und Switche can apply to 6WIND vSR/HBR and FRR reference/network-operator areas.
9. Portal-answer evidence must be a GitLab, GitHub, or Confluence URL. Local captures under `tcaas-psa/artifacts/` are provenance only and must not be used as final answer references.
10. Put the human-readable reference list into `answer.note` so the PSA portal "Meine Notiz" field contains the reviewed links.
11. For server, Kubernetes, container, network, IAM, hardening, and other actual runtime configuration questions, verify the marcel-1 cluster with the read-only collector before marking a row ready.
12. Use Mondoo policy results as verification/provenance, but do not treat policy presence alone as proof of fulfillment when the policy result contains open findings.
13. For platform logging rows, use the harmonized logging-operator evidence pattern:
   - Fact Sheet: platform logs are routed to CDI/SOCT or TDI logging backends.
   - `cit/t-caas/functions/tdg-logging`: Logging Operator, Fluent Bit, Fluentd, EventTailer, HostTailer, platform/tenant Logging resources, CDI Kafka output, and image definitions.
   - `cit/t-caas/functions/network-policies`: tdg-logging fluentd egress to CDI Kafka and ingress from Fluent Bit/Prometheus.
   - `schiff/platform/clusters/.../mondoo-analysis`: marcel-1 cross-checks for deployed observability workloads and logging images.
   Treat local/central retention and SIEM correlation/alarm ownership conservatively: mark `SOPC` unless backend retention/correlation policy evidence is linked.
14. Before declaring platform coverage complete, review `analysis/research/component_coverage_inventory.{json,md}` and ensure every component marked `evidence_cataloged_answer_gap` has either reviewed row-level answers or a documented reason it remains evidence-missing.
15. Treat `network-binding-controller`, DNS/Infoblox, ObjectStorageProfile/S3, and vSphere management clusters as explicit component classes. Do not let broad BM4X/Kubernetes/storage wording hide these components.
16. Do not classify ObjectStorageProfile/S3 as a DBMS. Cover it in networked storage, private cloud storage, and deletion/lifecycle rows; keep DBMS rows limited to actual database systems such as PostgreSQL, MongoDB, etcd, VictoriaMetrics, and Grafana storage.
17. vSphere management clusters are in platform scope for cloud/infrastructure, virtualization, compute profile, storage class, and management-plane rows. Do not leave whole-platform vSphere rows as blanket `NA` when the `schiff/platform/clusters` management-cluster definitions and `cit/t-caas/software/bundles` vSphere bundles exist.
18. Treat upstream mirrors and public GitHub provenance explicitly. For portal-ready evidence prefer internal GitLab mirror/function/configuration links; use public GitHub URLs only when a row specifically needs upstream provenance and the URL is reviewed. At minimum consider cert-manager, Coil, FRR, multi-networkpolicy-iptables, Multus, and `telekom/das-schiff-network-operator`.
19. Core coverage does not prove future separate DTT or NatCo filing coverage. DTT and NatCo currently do not have separate SoCs; keep architectural differences documented now, and run separate capture/answer/gate workflows only when PSA exposes those SoCs.

## Commands

Inventory local source roots:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  inventory \
  --root cit/t-caas \
  --root schiff/platform/clusters \
  --root cit/t-caas/gcp-dev-env \
  --out-dir tcaas-psa/analysis/research
```

Scan local files for SoC-relevant evidence. By default this writes the curated index and a bounded sample only; add `--write-full-records` only for temporary local analysis because the full stream is intentionally ignored by Git.

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  scan-evidence \
  --root cit/t-caas \
  --root schiff/platform/clusters \
  --root cit/t-caas/gcp-dev-env \
  --out-dir tcaas-psa/analysis/evidence
```

Build a SoC research workbook from the PSA answer template. By default this writes compact JSON, TSV, and markdown; add `--full-json` or `--jsonl` only for temporary local analysis.

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  build-soc-workbook \
  --answers tcaas-psa/answers/tcaas-core_answers.template.json \
  --evidence tcaas-psa/analysis/evidence/evidence_index.json \
  --out-dir tcaas-psa/analysis/soc-answers
```

Create a review copy with scope-based `NA` drafts from the sheet plan. This does not change the canonical template:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  seed-scope-drafts \
  --answers tcaas-psa/answers/tcaas-core_answers.template.json \
  --sheet-plan tcaas-psa/analysis/soc-answers/sheet_research_plan.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json
```

Apply reviewed answer changes from a versioned batch file:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  apply-answer-batch \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --batch tcaas-psa/analysis/soc-answers/batches/example_answer_batch.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json
```

Rebuild the generated full draft from the template, scope plan, and ordered answer batches:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  rebuild-answer-draft \
  --manifest tcaas-psa/analysis/soc-answers/answer_rebuild_manifest.json
```

Copy answer evidence URLs into PSA note fields before portal filling:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  sync-answer-notes \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json
```

Export a compact but still fillable answer file. Prefer this for PSA dry-runs and portal filling after notes are synced. Rebuild the ignored full draft JSON locally when scripts need every requirement text, motivation, current portal value, and field inspection.

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  export-fillable-answers \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json
```

Export a human-readable markdown review document containing every SoC row, requirement text, details, motivation, answer explanation, note, and evidence:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  export-answer-markdown \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --out tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.md
```

Audit answer wording for statement consistency, explanation depth, evidence depth, and expected component context. Treat `error` findings as blockers; treat `review` findings as prompts for manual evidence/depth review:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  answer-completeness-audit \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json \
  --out-dir tcaas-psa/analysis/soc-answers
```

Generate pinned, line-level GitLab/GitHub deep links from curated evidence:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  vet-links \
  --sources-json tcaas-psa/analysis/evidence/curated_sources.json \
  --out-dir tcaas-psa/analysis/evidence \
  --workspace-root /home/a92615428/git/devops.telekom.de
```

Audit the prepared answer file for platform/component coverage, portal-reference hygiene, and deferred DTT/NatCo filing notes:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  platform-coverage-audit \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_fillable_answers.json \
  --dtt-manifest tcaas-psa/artifacts/dtt/snapshots/dtt_soc_manifest.json \
  --out-dir tcaas-psa/analysis/soc-answers
```

Do not pass `--require-natco-manifest` unless a separate NatCo PSA system snapshot actually exists and should be treated as required input. DTT and NatCo currently have no separate SoCs; this audit should record architecture-only representation for those scopes, not row-level filing coverage.

Run the complete repeatable readiness gate before manual review or portal fill. This wrapper runs answer quality, answer completeness, Confluence evidence, platform coverage, and portal preflight, then writes a compact summary instead of another large workbook:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/run_soc_gates.py \
  --repo-root tcaas-psa
```

Collect live, redacted marcel-1 cluster evidence:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  collect-marcel1-cluster \
  --context marcel-1-admin@marcel-1 \
  --kubeconfig /home/a92615428/marcel.k \
  --out-dir tcaas-psa/analysis/research/marcel-1/live-cluster
```

The cluster collector writes `marcel1_cluster_summary.json`, `marcel1_cluster_summary.md`, and `marcel1_cluster_collections_compact.json` by default. Add `--write-raw-collections` only for temporary local debugging; raw collection files are intentionally ignored by Git.

If the marcel-1 API is only reachable over IPv6 from the ZTN jump host, let the collector open the temporary SSH tunnel itself:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  collect-marcel1-cluster \
  --context marcel-1-admin@marcel-1 \
  --kubeconfig /home/a92615428/marcel.k \
  --api-tunnel-jump schiff-ztn-jump \
  --api-tunnel-target '[2a01:598:40a:5480::a0:1]' \
  --tls-server-name kube.marcel-1.dev.bn461.t-caas.telekom.de \
  --out-dir tcaas-psa/analysis/research/marcel-1/live-cluster
```

Compact an existing raw live-cluster capture and remove the raw per-collection JSON files after the compact summary is written:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  compact-marcel1-cluster \
  --in-dir tcaas-psa/analysis/research/marcel-1/live-cluster \
  --remove-raw
```

Collect read-only, redacted node-shell evidence. Refresh opkssh first when the local token is stale:

```bash
opkssh login tcaas --configure
```

Then run the node collector. It discovers current nodes through the same API tunnel and uses `debug` via `schiff-ztn-jump` for SSH:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  collect-marcel1-node-shell \
  --context marcel-1-admin@marcel-1 \
  --kubeconfig /home/a92615428/marcel.k \
  --api-tunnel-jump schiff-ztn-jump \
  --api-tunnel-target '[2a01:598:40a:5480::a0:1]' \
  --tls-server-name kube.marcel-1.dev.bn461.t-caas.telekom.de \
  --jump-host schiff-ztn-jump \
  --ssh-user debug \
  --out-dir tcaas-psa/analysis/research/marcel-1/node-shell
```

Cross-reference existing Mondoo exports with SoC rows:

```bash
tcaas-psa/.venv/bin/python \
  tcaas-psa/skill/tcaas-soc-analysis/scripts/tcaas_analysis.py \
  cross-reference-mondoo-socs \
  --answers tcaas-psa/analysis/soc-answers/tcaas-core_scope_draft_answers.json \
  --mondoo-dir schiff/platform/clusters/mgmt-clusters/t-caas-mgmt-1.dev.n/clusters/marcel-1.dev.bn461/mondoo-analysis \
  --out-dir tcaas-psa/analysis/research/mondoo
```

## Evidence Rules

- Evidence records should include path, line, category, and a short non-secret excerpt.
- Files or paths containing `secret`, `sops`, `kubeconfig`, `token`, `credential`, `password`, `private`, or `key` are recorded by path only unless they are public documentation.
- Confluence/fact-sheet evidence should be exported to files first, then referenced from the generated analysis artifacts.
- GCP roles, tools, WIF, hardening, audit, and operations evidence should come first from `cit/t-caas/gcp-dev-env`.
- Vetted Git links must pin a path to a commit and line range where possible. The `vet-links` command must confirm that the path exists at the cited commit, the line range is valid at that commit, and the commit is contained in at least one remote-tracking branch before a GitLab/GitHub URL is treated as portal-ready.
- Use `gitRef` in `analysis/evidence/curated_sources.json` when the local checkout is on a local-only commit but an equivalent remote-backed commit should be used for evidence URLs.
- GitLab/GitHub answer evidence must come from `analysis/evidence/vetted_links.json`; Confluence answer evidence must be a captured and reviewed `https://wiki.telekom.de/...` page URL from the Confluence export/link manifest.
- Do not use local paths, artifact captures, extracted PDFs, or generated analysis files as `answer.evidence` in portal-ready rows.
- Mondoo console and local marcel-1 collection outputs can be mentioned in `answer.note` as review provenance, but portal-answer `answer.evidence` still needs GitLab/GitHub/Confluence URLs unless the user explicitly changes the evidence rule.
- The raw broad scan stream `analysis/evidence/evidence_records.jsonl`, raw marcel-1 collection dumps, optional full workbook JSON, and optional workbook JSONL are intentionally ignored by Git because they are large and noisy. Keep curated summaries, compact collection details, sheet plans, and answer drafts versioned.
