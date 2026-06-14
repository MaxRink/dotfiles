# Git Graphs

For branch and merge history visualization.

## Syntax

```mermaid
gitGraph
  commit id: "init" tag: "v0.1"
  branch develop
  commit id: "feature-work"
  branch feature/auth
  commit id: "auth-impl"
  commit id: "auth-tests"
  checkout develop
  merge feature/auth
  checkout main
  merge develop tag: "v1.0"
```

**Commands:** `commit`, `branch`, `checkout`, `merge`, `cherry-pick`
**Commit types:** `NORMAL` (default), `REVERSE` (crossed circle), `HIGHLIGHT` (filled rect)
**Orientation:** `gitGraph LR:` or `gitGraph TB:` or `gitGraph BT:`
