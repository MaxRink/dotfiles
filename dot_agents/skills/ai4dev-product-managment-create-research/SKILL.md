---
name: ai4dev-product-managment-create-research
description: Product discovery and research tools — user interview scripts, competitive analysis, hypothesis tracking, and research plans. Use this skill when a user wants to prepare for user interviews, analyze competitors, track product hypotheses, create research plans, write survey questions, or do any product discovery work. Also trigger for 'customer research', 'market analysis', 'user testing plan', 'what do our competitors do', 'validate this idea', or any request to understand users or the market before building.
argument-hint: "[type: interview|competitive|hypothesis|research-plan] [context]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-research by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Product Discovery & Research

Tools for validating product ideas, understanding users, and analyzing the market before committing to building.

**Detect type** from $ARGUMENTS or ask: "What do you need? User interview script, competitive analysis, hypothesis tracker, or research plan?"

## 1. User Interview Script

```markdown
# User Interview Script: [Research Topic]
**Research Goal:** [What we want to learn]
**Target Persona:** [Who we're interviewing]
**Duration:** [30-60 min]

## Introduction (5 min)
> Hi, thanks for joining. We're exploring [topic area] and your perspective is really valuable. There are no right or wrong answers. Is it OK if I record this?

## Warm-Up (5 min)
1. Tell me about your role and a typical day.
2. How does [relevant topic] fit into your work?

## Core Questions (20-30 min)

### Current Behavior
3. Walk me through the last time you [relevant activity].
4. What tools do you currently use for [task]?
5. What's the most frustrating part?

### Exploring the Problem
6. How often does [problem] come up?
7. What have you tried to solve it?
8. How do you work around it today?

### Validating the Opportunity
9. If you could change one thing about [area], what would it be?
10. How would [proposed concept] fit into your workflow?

## Wrap-Up (5 min)
11. Anything I should have asked but didn't?
12. Open to trying an early version?

## Key Insights Template
| # | Quote/Observation | Theme | Implication |
|---|-------------------|-------|-------------|
| 1 | "[exact quote]" | | |
```

## 2. Competitive Analysis

```markdown
# Competitive Analysis: [Product/Feature Area]
**Date:** [Date]

## Market Overview
[Brief description of market, size, trends]

## Feature Comparison
| Feature | Our Product | Competitor A | Competitor B | Competitor C |
|---------|------------|-------------|-------------|-------------|
| | | | | |

**Legend:** Full | Partial | None | Unknown

## Competitor Deep Dives

### [Competitor Name]
- **Strengths:** What they do well
- **Weaknesses:** Where they fall short
- **Pricing:** Model and tiers
- **Recent Moves:** Latest features, funding
- **Threat Level:** Low / Medium / High

## SWOT (Our Product)
| Strengths | Weaknesses |
|-----------|------------|
| | |
| **Opportunities** | **Threats** |
| | |

## Strategic Implications
1. **Differentiation opportunity:** [where we can win]
2. **Table stakes gap:** [what we must have]
3. **Avoid:** [where competitors are entrenched]
```

## 3. Hypothesis Tracker

```markdown
# Hypothesis Tracker: [Product/Feature]
**Last Updated:** [Date]

### H1: [Hypothesis Name]
**Statement:** We believe that [action] for [users] will [outcome] because [rationale].
**Status:** Untested | Testing | Validated | Invalidated
**Confidence:** Low | Medium | High
**Test Method:** [interview, prototype, A/B test, data analysis]
**Results:** [Findings once tested]
**Decision:** Build | Pivot | Kill | Need more data

## Hypothesis Board
| ID | Hypothesis | Status | Confidence | Next Step |
|----|-----------|--------|------------|-----------|
| H1 | [short form] | Testing | Medium | Run 5 more interviews |
```

## 4. Research Plan

```markdown
# Research Plan: [Topic]
**Objective:** [What we want to learn]
**Timeline:** [Start] - [End]

## Research Questions
1. [Primary question]
2. [Secondary question]

## Methodology
| Method | Participants | Timeline | Output |
|--------|-------------|----------|--------|
| User Interviews | 5-8 users | Week 1-2 | Summaries |
| Survey | 50+ responses | Week 2 | Quantitative data |
| Competitive Analysis | 3-5 competitors | Week 1 | Comparison matrix |

## Participant Criteria
- **Include:** [who to talk to]
- **Exclude:** [who would skew results]

## Deliverables
- Research findings report
- Key insights presentation
- Updated hypothesis tracker
```

## Guidelines

- Interview questions should be open-ended — never lead the witness
- Competitive analysis should be factual — note verified vs. assumed
- Hypotheses must be falsifiable
- After discovery, offer to help create a PRD from the findings
- Save output as `[type]-[topic].md`
