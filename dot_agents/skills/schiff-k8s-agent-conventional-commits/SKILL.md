---
name: schiff-k8s-agent-conventional-commits
description: Format all Git commit messages according to the Conventional Commits v1.0.0 specification. Use this skill whenever creating commits, MRs, or reviewing commit messages.
---

<!-- Imported from schiff/platform/infrastructure/k8s-agent/.opencode/skills/conventional-commits by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Conventional Commits

All commits in this project MUST follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

## Commit message format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Allowed types

| Type | When to use |
|---|---|
| `feat` | A new feature (correlates with SemVer MINOR) |
| `fix` | A bug fix (correlates with SemVer PATCH) |
| `docs` | Documentation-only changes |
| `style` | Formatting, whitespace, missing semicolons — no code logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Changes to build system or external dependencies |
| `ci` | CI/CD configuration changes (pipelines, GitHub Actions, etc.) |
| `chore` | Other changes that don't modify src or test files |
| `revert` | Reverts a previous commit |

## Rules

1. **Type is required.** Always prefix the commit subject with one of the types above.
2. **Scope is optional** but encouraged. Use a noun describing the area of change in parentheses: `feat(parser): ...`, `fix(auth): ...`.
3. **Description** must immediately follow the colon and space. Use imperative mood, lowercase first letter, no period at the end.
4. **Body** is optional. Separate from description with a blank line. Explain *what* and *why*, not *how*.
5. **Footer(s)** are optional. Use for:
   - `BREAKING CHANGE: <description>` — indicates a breaking API change (SemVer MAJOR).
   - Issue/ticket references: `Refs: #123`, `Closes: #456`.
   - Co-authors: `Co-authored-by: Name <email>`.
6. **Breaking changes** can also be indicated by appending `!` after the type/scope: `feat!:` or `feat(api)!:`.
7. Use **lowercase** for the type. `BREAKING CHANGE` in footers must be uppercase.

## Examples

### Simple feature

```text
feat(skills): add conventional-commits skill
```

### Bug fix with scope

```text
fix(auth): prevent token refresh race condition
```

### Breaking change

```text
feat(api)!: remove deprecated /v1/users endpoint

BREAKING CHANGE: The /v1/users endpoint has been removed. Use /v2/users instead.
```

### Docs change

```text
docs: update README with new setup instructions
```

### Multi-paragraph body with footer

```text
fix(drain): prevent PDB deadlock during node drain

Introduce a check for single-replica deployments with minAvailable=1
PDBs before initiating drain. Temporarily scale the deployment to 2
replicas to allow eviction to proceed.

Refs: #789
```

### Revert

```text
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## MR titles

MR (merge request) titles MUST also follow the conventional commit format since they become the squash-merge commit message:

```text
feat(scope): short description
```

## Procedure

When creating a commit or MR:

1. Determine the **type** from the table above based on the nature of the change.
2. Identify a **scope** if the change is localized to a specific component or area.
3. Write a concise **description** in imperative mood (e.g., "add", "fix", "remove" — not "added", "fixed", "removed").
4. Add a **body** if the change is non-trivial and needs explanation.
5. Add **footers** for breaking changes, issue references, or co-authors.
6. Validate the message matches the pattern: `<type>[optional scope]: <description>`.

## Common mistakes to avoid

- Using past tense: `fixed bug` instead of `fix bug`.
- Missing type prefix: `update dependencies` instead of `build: update dependencies`.
- Capitalizing the description: `Fix: Add feature` instead of `fix: add feature`.
- Using a period at the end of the subject line.
- Mixing multiple unrelated changes in one commit — prefer separate commits per concern.
