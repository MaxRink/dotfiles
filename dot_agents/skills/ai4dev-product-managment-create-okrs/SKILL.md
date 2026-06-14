---
name: ai4dev-product-managment-create-okrs
description: Define OKRs, metric trees, and success metrics for products and teams. Use this skill when a user wants to write OKRs, define key results, build a metric tree, set up a measurement framework, define KPIs, or structure goals for a product or team. Also trigger for 'what should we measure', 'define success metrics', 'OKRs for next quarter', 'metric tree', 'north star metric', 'HEART framework', or any request to define measurable product goals.
argument-hint: "[type: okrs|metric-tree|heart] [context]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-okrs by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# OKRs & Metrics

Define measurable goals, metric trees, and success frameworks.

**Detect type** from $ARGUMENTS or ask: "What do you need? OKRs, a metric tree, or a HEART framework?"

## 1. OKR Template

```markdown
# OKRs: [Team/Product] — [Quarter Year]
**Author:** [Name] | **Date:** [Date]

## Objective 1: [Qualitative, inspiring goal]
*Why this matters: [Business context]*

| # | Key Result | Current | Target | Owner | Status |
|---|-----------|---------|--------|-------|--------|
| KR1 | [Measurable outcome] | [baseline] | [target] | [name] | Not Started |
| KR2 | [Measurable outcome] | [baseline] | [target] | [name] | Not Started |
| KR3 | [Measurable outcome] | [baseline] | [target] | [name] | Not Started |

**Initiatives** (how we plan to achieve these KRs):
- [ ] [Initiative 1] → Contributes to KR1, KR2
- [ ] [Initiative 2] → Contributes to KR2, KR3

---

## Objective 2: [Qualitative, inspiring goal]
[Same structure]

---

## Guardrail Metrics
Metrics that must NOT degrade while pursuing the OKRs above.

| Guardrail | Current | Floor (don't go below) |
|-----------|---------|----------------------|
| [e.g., page load time] | [current] | [threshold] |
| [e.g., customer satisfaction] | [current] | [threshold] |

## Scoring Guide
- 0.0-0.3: Failed to make progress
- 0.4-0.6: Made progress but fell short
- 0.7-0.9: Strong delivery (target zone)
- 1.0: Achieved fully (may indicate target was too easy)
```

## OKR Writing Rules

**Good Objectives:**
- Qualitative and inspiring ("Become the go-to tool for...")
- Time-bound (one quarter)
- Achievable but ambitious (70% expected completion = well-calibrated)
- 1-3 per team per quarter

**Good Key Results:**
- Measurable with a number (not "improve X" but "increase X from A to B")
- Outcome-based, not output-based ("Reduce churn to 3%" not "Ship retention features")
- 2-4 per objective
- Each has a baseline, target, data source, and owner

**Common mistakes:**
- KRs that are just tasks disguised as metrics ("Launch feature X" is a task, not a KR)
- Too many OKRs — 1-3 objectives max, focus beats breadth
- No baseline — if you don't know where you are, you can't set a meaningful target
- Missing guardrails — optimizing one metric often degrades another

## 2. Metric Tree

A metric tree connects your North Star to the inputs you can influence.

```markdown
# Metric Tree: [Product Name]

## North Star Metric
**Metric:** [The one metric that best captures the value your product delivers]
**Formula:** [How it's calculated]
**Current:** [Value] | **Target:** [Value] | **Timeframe:** [Period]

## Input Metrics (Level 1)
North Star = f(Input A, Input B, Input C)

| Input Metric | Formula | Current | Target | Owner | Lever |
|-------------|---------|---------|--------|-------|-------|
| [e.g., Weekly active users] | | | | | Acquisition |
| [e.g., Actions per user] | | | | | Engagement |
| [e.g., Revenue per action] | | | | | Monetization |

## Driver Metrics (Level 2)
Each input metric breaks down further.

### [Input A] Drivers
| Driver | Formula | Current | Target |
|--------|---------|---------|--------|
| [e.g., Signup rate] | | | |
| [e.g., Activation rate] | | | |
| [e.g., Referral rate] | | | |

### [Input B] Drivers
| Driver | Formula | Current | Target |
|--------|---------|---------|--------|
| | | | |

## Counter-Metrics (Guardrails)
| Counter-Metric | Why It Matters | Floor |
|---------------|---------------|-------|
| | Prevents gaming the North Star | |
```

### North Star Selection

A good North Star Metric:
- Reflects value delivered to users (not just revenue)
- Is a leading indicator of business success
- Is actionable by the product team
- Can be decomposed into input metrics the team can influence

## 3. HEART Framework

Google's framework for measuring UX quality.

```markdown
# HEART Metrics: [Product/Feature]
**Date:** [Date]

| Dimension | Goal | Signal | Metric | Current | Target |
|-----------|------|--------|--------|---------|--------|
| **Happiness** | [User satisfaction goal] | [NPS/CSAT responses] | [NPS score / CSAT %] | | |
| **Engagement** | [Feature adoption goal] | [Usage frequency/depth] | [DAU/MAU / actions per session] | | |
| **Adoption** | [New user activation goal] | [New users completing activation] | [Activation rate %] | | |
| **Retention** | [User return goal] | [Users returning after X days] | [D7/D30 retention %] | | |
| **Task Success** | [Core flow completion goal] | [Users completing core task] | [Completion rate % / time on task] | | |
```

### HEART + Goals-Signals-Metrics (GSM)

For each HEART dimension:
1. **Goal:** What UX outcome do you want? (qualitative)
2. **Signal:** What user behavior indicates progress? (observable)
3. **Metric:** How do you quantify the signal? (formula + timeframe + data source)

## Guidelines

- Every metric needs a precise definition: formula + timeframe + data source
- Vanity metrics (raw signups, page views) are noise — focus on activation, retention, and engagement
- Always define guardrails alongside target metrics to prevent optimization tunnel vision
- Review and update OKRs mid-quarter — they're living documents, not set-and-forget
- After defining OKRs, offer to build a roadmap or prioritize features against these goals
