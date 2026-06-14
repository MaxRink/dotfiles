# Completion Summary Template

## Quality Score

Calculate quality score (0–100). Each criterion awards points proportionally:

| Criterion | Max Points | Formula |
|-----------|-----------|---------|
| Files documented vs total | 25 | `(files_documented / files_total) × 25` where `files_total` = source + supporting files from Step 0, and `files_documented` = files matched by file_index patterns |
| Modules documented vs detected | 25 | `(modules_documented / modules_detected) × 25` |
| API endpoints documented vs detected | 20 | `(apis_documented / apis_detected) × 20` |
| Data models documented vs detected | 15 | `(models_documented / models_detected) × 15` |
| Cross-cutting docs produced vs applicable | 15 | `(cross_cutting_produced / cross_cutting_applicable) × 15` |

**Total** = sum of all five criteria, rounded to the nearest integer.

Record the score in `metadata.quality_score` and the raw numbers in `metadata.coverage` as structured numeric fields:

```json
"coverage": {
  "files_documented": 56,
  "files_total": 120,
  "modules_documented": 3,
  "modules_detected": 3,
  "apis_documented": 26,
  "apis_detected": 26,
  "models_documented": 12,
  "models_detected": 12,
  "cross_cutting_produced": 6,
  "cross_cutting_applicable": 7
}
```

## Summary Message

Print this to the user after all files are written:

```text
Deep exploration complete for <name>:
  Tier: <small|medium|large|xl> (<N> files)
  Languages: <list>
  Frameworks: <list>
  Modules: <N> documented, <M> detected
  APIs: <N> endpoints documented
  Data Models: <N> entities documented
  Output: .migration/docs/
  Quality: <score>/100

  Files produced:
  .migration/docs/index.json                          (manifest)
  .migration/docs/overview/folder-structure.md         (directory layout)
  .migration/docs/overview/tech-stack.md               (technology stack)
  .migration/docs/overview/entry-points.md             (entry points)
  .migration/docs/overview/components.md               (modules and services)
  .migration/docs/overview/dependency-graph.md         (Mermaid dependency diagram)
  .migration/docs/modules/<name>.md                    (per-module documentation)
  .migration/docs/cross-cutting/<name>.md              (cross-cutting concerns)
  ...
```
