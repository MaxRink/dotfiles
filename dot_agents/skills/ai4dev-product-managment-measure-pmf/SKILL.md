---
name: ai4dev-product-managment-measure-pmf
description: Measure and track Product-Market Fit using surveys, retention analysis, and engagement scoring. Use this skill when a user wants to measure PMF, run a Sean Ellis survey, analyze retention curves, score user engagement, audit feature usage, or understand if their product has found its market. Also trigger for 'do we have product-market fit', 'retention analysis', 'Sean Ellis test', 'are users sticking around', 'churn analysis', 'activation rate', 'feature audit', or any question about whether users find the product valuable enough to keep using.
argument-hint: "[type: sean-ellis|retention|engagement|feature-audit|full] [context]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/measure-pmf by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Product-Market Fit Measurement

PMF is not a binary event. It's a signal you measure across multiple dimensions, continuously, segmented by user type.

**Detect type** from $ARGUMENTS or ask: "What do you need? Sean Ellis survey, retention curve analysis, engagement scoring, feature audit, or a full PMF assessment?"

## 1. Sean Ellis Test

Survey users: "How would you feel if you could no longer use [product]?"

```markdown
# PMF Survey: [Product Name]
**Date:** [Date] | **Respondents:** [N]

## Sean Ellis Question
"How would you feel if you could no longer use [product]?"

| Response | Count | % | Target |
|----------|-------|---|--------|
| Very disappointed | | | >40% for PMF signal |
| Somewhat disappointed | | | |
| Not disappointed | | | |

## PMF Signal: [Yes/No/Emerging]

## Supporting Questions

### For "Very Disappointed" respondents:
- What is the primary benefit you receive from [product]?
- What would you use as an alternative?
- How would you rate [product] on a scale of 1-10? (NPS proxy)

### For "Not Disappointed" respondents:
- What would make [product] more valuable to you?
- What are you using instead?

### Usage Frequency
| Frequency | Count | % |
|-----------|-------|---|
| Daily | | |
| Weekly | | |
| Monthly | | |
| Rarely | | |

## Segment Analysis
| Segment | N | Very Disappointed % | PMF Signal |
|---------|---|--------------------|-----------|
| [ICP users] | | | |
| [Non-ICP users] | | | |
| [Free tier] | | | |
| [Paid tier] | | | |

## Key Findings
1. [Finding with data]
2. [Finding with data]

## Recommendations
- [Action based on findings]
```

## 2. Retention Curve Analysis

```markdown
# Retention Analysis: [Product Name]
**Period:** [Date range] | **Cohort size:** [Weekly/Monthly]

## Cohort Retention Table
| Cohort | Week 0 | Week 1 | Week 2 | Week 4 | Week 8 | Week 12 |
|--------|--------|--------|--------|--------|--------|---------|
| [Date] | 100% | | | | | |

## Curve Shape Assessment
- **Flattening curve** = PMF signal (users who stay, stay)
- **Declining curve** = No PMF (even retained users eventually leave)
- **Smile curve** = Re-engagement working (users come back)

**Current shape:** [Flattening / Declining / Smile / Insufficient data]
**Flattening at:** [X]% at week [Y]

## Segment Comparison
| Segment | Week 1 Retention | Week 4 Retention | Week 12 Retention | Trend |
|---------|-----------------|-----------------|-------------------|-------|
| | | | | |

## Benchmarks
| Metric | Our Product | Industry Avg | Best-in-Class |
|--------|------------|-------------|---------------|
| D1 retention | | | |
| D7 retention | | | |
| D30 retention | | | |

## Recommendations
- [Action to improve retention based on drop-off points]
```

## 3. Engagement Scoring

Define what "activated" and "engaged" actually mean for your product.

```markdown
# Engagement Framework: [Product Name]
**Date:** [Date]

## Activation Definition
- **Activation event:** [Specific action that indicates a user "gets it"]
- **Activation window:** [First X days after signup]
- **Current activation rate:** [X]%
- **Target activation rate:** [Y]%

## Engagement Tiers
| Tier | Definition | % of Users | Behavior Pattern |
|------|-----------|-----------|-----------------|
| Power users | [criteria: actions/frequency] | | |
| Active users | [criteria] | | |
| Casual users | [criteria] | | |
| Dormant users | [criteria] | | |

## Key Engagement Metrics
| Metric | Formula | Current | Target | Data Source |
|--------|---------|---------|--------|------------|
| DAU/MAU ratio | Daily active / Monthly active | | >X% | |
| Feature breadth | Avg features used per session | | | |
| Session frequency | Sessions per user per week | | | |
| Time to value | Time from signup to activation | | | |

## Engagement Drivers
| Feature/Action | Correlation with Retention | Usage % |
|---------------|--------------------------|---------|
| | Strong / Medium / Weak | |
```

## 4. Feature Audit

Identify what to keep, improve, or remove.

```markdown
# Feature Audit: [Product Name]
**Date:** [Date] | **Active Users:** [N]

## Feature Usage Matrix
| Feature | Monthly Active Users | % of Total | Trend | Support Cost | Verdict |
|---------|---------------------|-----------|-------|-------------|---------|
| | | | Rising/Stable/Falling | High/Med/Low | Keep/Improve/Sunset |

## Classification
### Top 20% by usage — Invest and polish
- [Feature]: [usage stats] — Action: [specific improvement]

### Middle 60% — Maintain, don't expand
- [Feature]: [usage stats]

### Bottom 20% — Candidate for removal or redesign
- [Feature]: [usage stats] — Recommendation: [sunset/redesign/investigate]

### High support cost relative to usage — Redesign or sunset
- [Feature]: [usage vs support tickets]

## Sunset Candidates
| Feature | Usage | Support Cost | Recommendation | Migration Plan |
|---------|-------|-------------|----------------|---------------|
| | | | Remove / Redesign / Bridge migrate | |
```

## 5. Full PMF Assessment

Combine all signals into a comprehensive assessment.

```markdown
# PMF Assessment: [Product Name]
**Date:** [Date]

## PMF Scorecard
| Dimension | Signal | Score (1-5) | Evidence |
|-----------|--------|------------|----------|
| Sean Ellis (>40% very disappointed) | | | |
| Retention curve flattening | | | |
| Organic growth / word-of-mouth | | | |
| Activation rate | | | |
| Revenue retention (NRR) | | | |

## Overall PMF Status: [No PMF / Emerging / Strong / Scaling]

## Segment-Level PMF
| Segment | PMF Status | Strongest Signal | Weakest Signal |
|---------|-----------|-----------------|----------------|
| | | | |

## What's Working
- [Evidence-backed strength]

## What's Not Working
- [Evidence-backed gap]

## Next Steps
1. [Highest priority action to strengthen PMF]
2. [Second priority]
```

## Guidelines

- PMF varies by segment — always measure separately for ICP vs non-ICP, free vs paid, etc.
- Define every metric precisely: formula + timeframe + data source
- Measure PMF continuously, not once — it can be lost as markets shift
- Retention curves tell you more than surveys — look at behavior, not just stated preferences
- For deeper methodology, read `${CLAUDE_SKILL_DIR}/references/pmf-measurement.md`
