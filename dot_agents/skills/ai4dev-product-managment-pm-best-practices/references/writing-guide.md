# PRD Writing Guide — Extended Reference

## Table of Contents
1. Problem Statement Patterns
2. Metrics Framework
3. Stakeholder Management
4. Documentation Lifecycle

## 1. Problem Statement Patterns

### Data-Driven Pattern
> "Support tickets related to [area] increased 45% QoQ (from 200 to 290/month). User interviews (N=12) confirm that [specific friction]. This costs approximately [X hours/month] of support time and contributes to [Y% churn] in the affected segment."

### User-Research Pattern
> "In 8 of 12 user interviews, participants described [specific pain]. The current workaround involves [manual steps], taking an average of [X minutes] per occurrence. Participants rated this pain as [X/10] severity."

### Strategic Pattern
> "Competitor [X] launched [feature] in Q3, and we've seen [Y] prospects mention it in sales calls. Our win rate against [X] dropped from [A%] to [B%] in deals where [feature area] was a key criterion."

## 2. Metrics Framework

### HEART Framework (for UX metrics)
| Dimension | Metric | Signal | How to Measure |
|-----------|--------|--------|---------------|
| Happiness | User satisfaction | NPS/CSAT score | Survey |
| Engagement | Feature adoption | DAU/MAU ratio | Analytics |
| Adoption | New user activation | % completing onboarding | Funnel |
| Retention | User return rate | D7/D30 retention | Cohort |
| Task Success | Completion rate | % completing core flow | Analytics |

### North Star Metric Selection
A good North Star Metric:
- Reflects value delivered to users
- Is a leading indicator of revenue
- Is actionable by the product team
- Can be decomposed into input metrics

## 3. Stakeholder Management

### RACI Matrix Rules
- Every row has exactly ONE Accountable
- Consulted means two-way communication (before the decision)
- Informed means one-way communication (after the decision)
- Minimize the number of Consulted parties to avoid bottlenecks

### Communication Cadence
| Stakeholder Type | Frequency | Format | Content |
|-----------------|-----------|--------|---------|
| Executive sponsor | Bi-weekly | 1-pager | Health, risks, decisions needed |
| Engineering team | Daily/sprint | Stand-up/review | Progress, blockers |
| Design team | Weekly | Sync | UX review, feedback |
| Sales/CS | Monthly | Deck/email | Roadmap updates, launch plans |
| Customers | Quarterly | Blog/email | Release highlights, what's coming |

## 4. Documentation Lifecycle

### PRD States
```
Draft → In Review → Approved → In Development → Shipped → Archived
```

### When to Update vs. Create New
- **Update existing PRD**: Scope changes, new learnings, timeline shifts
- **Create new PRD**: Fundamentally different approach, new initiative
- **Archive**: Feature shipped, or initiative cancelled — don't delete, archive with status note
