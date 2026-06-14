---
name: ai4dev-product-managment-prioritize
description: Apply prioritization frameworks to rank features and initiatives. Use this skill when a user wants to prioritize a backlog, score features, rank ideas, decide what to build next, or apply frameworks like RICE, MoSCoW, weighted scoring, or impact/effort analysis. Also trigger for 'which feature should we build first', 'help me rank these', 'backlog grooming priorities', 'stack rank', or any decision-making about what to build and in what order.
argument-hint: "[features-list-or-file] [--framework=rice|moscow|impact-effort|weighted]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/prioritize by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Feature Prioritization

Help PMs make data-driven prioritization decisions using established frameworks.

## Workflow

1. Gather the feature list from $ARGUMENTS, a file, or ask the user
2. Select framework based on user preference or recommend the best fit
3. Score each item — guide the user or auto-score with stated assumptions
4. Rank and present with rationale
5. Save to `prioritization-[name].md`

Use the pm-frameworks skill for detailed scoring guidance.

## Framework Selection

| Framework | Best For |
|-----------|---------|
| RICE | Quantitative scoring when you have reach/impact data |
| MoSCoW | Quick categorization for a release or MVP |
| Impact/Effort | Visual 2x2 for team workshops and quick decisions |
| Weighted Scoring | Custom criteria specific to your business |

If no framework specified, recommend RICE for data-driven teams or Impact/Effort for quick decisions.

## RICE Output

```markdown
# RICE Prioritization: [Context]
**Date:** [Date] | **Scored by:** [Name]

## Scoring Criteria
- **Reach**: Users affected per quarter
- **Impact**: 3=Massive, 2=High, 1=Medium, 0.5=Low, 0.25=Minimal
- **Confidence**: 100%=High, 80%=Medium, 50%=Low
- **Effort**: Person-months

| Feature | Reach | Impact | Confidence | Effort | RICE Score | Rank |
|---------|-------|--------|------------|--------|------------|------|
| | | | | | | |

**Formula:** RICE = (Reach x Impact x Confidence) / Effort
```

## MoSCoW Output

```markdown
# MoSCoW Prioritization: [Release/Context]

## Must Have (Non-negotiable for launch)
| Feature | Rationale |
|---------|-----------|
| | |

## Should Have (Important but not critical)
| Feature | Rationale | Risk if Deferred |
|---------|-----------|------------------|
| | | |

## Could Have (Nice to have)
| Feature | Rationale | Effort |
|---------|-----------|--------|
| | | |

## Won't Have (Explicitly excluded this time)
| Feature | Reason | Revisit When |
|---------|--------|-------------|
| | | |
```

## Impact/Effort Matrix Output

```markdown
# Impact/Effort Matrix: [Context]

## Quick Wins (High Impact, Low Effort) — Do first
- [ ] Feature — Impact: [why], Effort: [estimate]

## Big Bets (High Impact, High Effort) — Plan carefully
- [ ] Feature — Impact: [why], Effort: [estimate]

## Fill-Ins (Low Impact, Low Effort) — Spare capacity
- [ ] Feature

## Money Pit (Low Impact, High Effort) — Avoid
- [ ] Feature — Reason to reconsider: [if any]
```

## Weighted Scoring Output

```markdown
# Weighted Scoring: [Context]

## Criteria & Weights
| Criterion | Weight | Description |
|-----------|--------|-------------|
| | | |

## Scores (1-5 scale)
| Feature | [Criterion 1] | [Criterion 2] | ... | Weighted Score | Rank |
|---------|---------------|---------------|-----|---------------|------|
| | | | | | |
```

## ICE Output

```markdown
# ICE Prioritization: [Context]

| Feature | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Score | Rank |
|---------|--------------|-------------------|-------------|-----------|------|
| | | | | | |

**Formula:** ICE = Impact x Confidence x Ease
```

## Opportunity Scoring Output

For discovery-driven, JTBD-aligned prioritization:

```markdown
# Opportunity Scoring: [Context]

| Job / Outcome | Importance (1-10) | Satisfaction (1-10) | Opportunity Score | Rank |
|--------------|-------------------|--------------------|--------------------|------|
| | | | | |

**Formula:** Opportunity = Importance + (Importance - Satisfaction)
High importance + low satisfaction = biggest opportunity
```

## Kill Criteria

Every initiative should have pre-defined stop conditions. When prioritizing, define these alongside scores so teams know when to stop, not just when to start.

```markdown
## Kill Criteria: [Initiative Name]

| Condition | Threshold | Timeframe | Action if Triggered |
|-----------|-----------|-----------|---------------------|
| Usage adoption | <X% of target users | Y weeks post-launch | Stop and re-evaluate |
| Cost ceiling | >X person-days | During development | Pause and re-scope |
| Time limit | Not shipped within X weeks | From kickoff | Kill or radically descope |
| Metric guardrail | [Guardrail metric] degrades >X% | Post-launch | Roll back immediately |
```

Use kill criteria to prevent the most common PM failure: building everything, killing nothing, and running out of time before impact.

## Feature Bridge Migration

When replacing an existing feature with a new one, don't hard-kill the old feature. Use a bridge migration to prevent user loss.

1. Ship new feature alongside old feature
2. Default new users to new experience
3. Migrate existing users gradually (progressive rollout)
4. Monitor: absorption rate, retention by cohort, support tickets
5. Kill rule: new feature absorbs >=80% of old-feature users for 14 consecutive days with no retention regression
6. Only then remove the old feature

**When NOT to bridge**: Security vulnerabilities, compliance requirements, or features with <1% MAU — these can be killed directly with notice.

## Scope Negotiation

When stakeholders push for more scope:
- Reframe as trade-offs: "We can add X if we cut Y — which matters more?"
- Anchor on outcomes: "The goal is [metric]. Does this addition move it?"
- Offer phased delivery: "V1 without this; measure; add in V2 if data supports it."
- Document non-goals explicitly in every spec

## Guidelines

- Always state assumptions clearly when auto-scoring
- Encourage the user to validate scores with their team
- Offer to re-score if the user disagrees with individual scores
- Pick one framework and use it consistently — the framework matters less than the discipline of scoring everything the same way
- Every prioritized initiative should have kill criteria defined before work begins
- After prioritizing, offer to help update the roadmap or create Jira stories from the ranked list
