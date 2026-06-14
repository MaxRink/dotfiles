# Metrics & OKRs — Extended Reference

## Table of Contents
1. North Star Metric Examples
2. OKR Writing Patterns
3. Metric Tree Examples
4. Common Metric Pitfalls
5. Measurement Infrastructure

## 1. North Star Metric Examples

| Company Type | North Star | Why It Works |
|-------------|-----------|-------------|
| Marketplace | Transactions completed per week | Captures both supply and demand engagement |
| SaaS B2B | Weekly active teams | Teams, not users — reflects organizational value |
| Media/Content | Total engaged time per user per week | Quality of attention, not just visits |
| E-commerce | Revenue per customer per month | Balances acquisition and monetization |
| Communication | Messages sent per day | Core value action, high frequency |
| Developer tool | Deploys per week | Measures actual value delivered |

### Choosing Your North Star
Ask:
1. Does it measure value delivered to users (not just captured from them)?
2. Does it predict long-term revenue?
3. Can the product team influence it directly?
4. Does it decompose into inputs the team can work on?

## 2. OKR Writing Patterns

### Pattern: Outcome + Leading Indicator + Guardrail

**Objective**: Become the fastest way for teams to ship software

| KR | Type | Formula |
|----|------|---------|
| Reduce median deploy time from 45min to 15min | Outcome | Median time from merge to production |
| Increase weekly deployments from 3 to 10 per team | Leading indicator | Count of production deploys / active teams / week |
| Maintain rollback rate below 5% | Guardrail | Rollbacks / total deploys |

### Anti-Pattern Examples

| Bad KR | Problem | Better KR |
|--------|---------|-----------|
| "Launch feature X" | Task, not outcome | "X% of users complete [workflow] successfully" |
| "Improve performance" | Not measurable | "P95 latency < 200ms" |
| "Increase engagement" | No baseline or target | "Increase DAU/MAU from 15% to 25%" |
| "Make customers happy" | Not actionable | "Increase NPS from 30 to 45" |

### Scoring OKRs
At quarter end, score each KR:
- 0.0: No progress
- 0.3: Some progress, significant miss
- 0.5: Halfway there
- 0.7: Strong delivery (this is the target — 70% means well-calibrated)
- 1.0: Fully achieved (might be too easy if consistently hitting 1.0)

## 3. Metric Tree Examples

### SaaS B2B Example
```
Monthly Recurring Revenue (MRR)
├── New MRR
│   ├── Leads generated
│   ├── Trial-to-paid conversion rate
│   └── Average contract value
├── Expansion MRR
│   ├── Upgrade rate
│   └── Seat expansion rate
└── Churned MRR (negative)
    ├── Logo churn rate
    └── Revenue contraction rate
```

### Consumer App Example
```
Weekly Active Users (WAU)
├── New users
│   ├── Organic signups
│   ├── Paid acquisition
│   └── Referral signups
├── Retained users
│   ├── D7 retention rate
│   └── Reactivation rate
└── Engagement depth
    ├── Sessions per user per week
    └── Core actions per session
```

## 4. Common Metric Pitfalls

| Pitfall | Example | Fix |
|---------|---------|-----|
| **Vanity metric** | Total signups (ever-increasing, no insight) | Use activation rate or WAU instead |
| **Lagging only** | Revenue (tells you what happened, not what will happen) | Add leading indicators (pipeline, engagement) |
| **No guardrail** | Optimizing conversion rate (at the expense of quality) | Add satisfaction or refund rate as guardrail |
| **Missing formula** | "Engagement" (everyone defines it differently) | "Users who performed [action] at least [N] times in [period]" |
| **Wrong timeframe** | Monthly metrics for a daily-use product | Match metric frequency to product usage cadence |
| **Aggregate only** | Average across all users | Segment by ICP, plan, cohort |

## 5. Measurement Infrastructure

### Minimum Viable Measurement
Before defining sophisticated metrics, ensure you can:
1. Track unique users (not just sessions)
2. Record key events with timestamps
3. Create cohorts by signup date
4. Segment by at least 3 dimensions (plan, source, persona)
5. Calculate retention curves

### Data Quality Checklist
- [ ] Events fire consistently (no missing data)
- [ ] User identity resolves across devices/sessions
- [ ] Timestamps are in UTC with timezone awareness
- [ ] PII is handled according to policy
- [ ] Historical data is backfilled for baseline metrics
- [ ] Dashboards refresh at least daily
