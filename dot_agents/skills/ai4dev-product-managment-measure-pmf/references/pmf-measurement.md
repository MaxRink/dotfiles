# PMF Measurement — Extended Reference

## Table of Contents
1. Sean Ellis Test Deep Dive
2. Retention Curve Methodology
3. Engagement Scoring Patterns
4. Segmented PMF Analysis
5. PMF Recovery Patterns

## 1. Sean Ellis Test Deep Dive

### Survey Design
The core question: "How would you feel if you could no longer use [product]?"

**Who to survey:**
- Users who have experienced the core value (activated users only)
- Recent usage (active in last 2 weeks)
- Sufficient sample: minimum 40 responses for statistical relevance
- Exclude: churned users, users still in trial/onboarding

**Supplementary questions:**
1. "What type of people do you think would most benefit from [product]?" — helps identify ICP
2. "What is the main benefit you receive from [product]?" — surfaces positioning language
3. "How can we improve [product] for you?" — prioritization input

### Interpreting Results
| Very Disappointed % | Signal | Action |
|---------------------|--------|--------|
| >40% | Strong PMF | Scale acquisition, optimize monetization |
| 25-40% | Emerging PMF | Double down on what "very disappointed" users love |
| <25% | No PMF | Pivot or significantly change value proposition |

### Improving the Score
Focus on what "very disappointed" users have in common:
- What features do they use most?
- How did they discover the product?
- What job are they hiring the product for?
- Build more of what they love, not what "somewhat disappointed" users want

## 2. Retention Curve Methodology

### Cohort Construction
- **Time-based cohorts**: Group by signup week/month
- **Behavioral cohorts**: Group by first action, acquisition channel, or plan type
- **Metric**: % of cohort still active at each time interval

### Curve Shapes
```
Flattening (PMF)         Declining (No PMF)       Smile (Re-engagement)
|                        |                        |
|\.                      |\                       |\.
|  \.___________         | \.                     |  \.
|               \_____   |   \.                   |    \.___
|                         |     \.                |         /
|                         |       \.              |       /
+------- time             +------- time           +------- time
```

### Benchmarks by Product Type
| Product Type | D1 | D7 | D30 | D90 |
|-------------|-----|-----|------|------|
| Social/Communication | 40-60% | 25-40% | 15-25% | 10-15% |
| SaaS B2B | 80-95% | 60-80% | 40-60% | 30-50% |
| E-commerce | 20-30% | 10-20% | 5-15% | 3-8% |
| Mobile games | 30-40% | 15-25% | 5-10% | 2-5% |

These are rough industry benchmarks — your specific category and business model will vary.

## 3. Engagement Scoring Patterns

### Activation Definition Framework
Define activation as the moment a user "gets it":

| Product Type | Activation Event | Typical Window |
|-------------|-----------------|----------------|
| Project management | Creates first project + invites 1 team member | 7 days |
| Analytics | Connects data source + views first report | 14 days |
| Communication | Sends 5th message | 3 days |
| SaaS tool | Completes core workflow 3 times | 14 days |

### Power User Curves
Plot the distribution of users by usage frequency:
- **Smile shape**: Most users are highly engaged — strong PMF
- **L shape**: A few power users, most barely use it — find what power users do differently
- **Flat line**: All users are mildly engaged — no one loves it enough

## 4. Segmented PMF Analysis

PMF is never uniform. Always segment:

| Segment | Why It Matters |
|---------|---------------|
| ICP vs non-ICP | You might have PMF in your ideal segment but not broadly |
| Free vs paid | Paid users self-select for higher engagement |
| Self-serve vs sales | Different value propositions and expectations |
| Company size | Feature needs differ dramatically |
| Geography | Cultural and regulatory differences affect adoption |
| Acquisition channel | Different channels bring different intent levels |

### Segmented PMF Matrix
| Segment | Sean Ellis | Retention | Engagement | Overall PMF |
|---------|-----------|-----------|------------|-------------|
| [Segment A] | X% | Flattening at Y% | High | Strong |
| [Segment B] | X% | Declining | Low | No PMF |

## 5. PMF Recovery Patterns

When PMF is lost or never achieved:

### Common Causes
1. **Market shift**: Customer needs changed (new regulations, technology shift)
2. **Competitive pressure**: Better alternative emerged
3. **Feature bloat**: Core value buried under complexity
4. **Wrong segment**: Building for users who don't need you
5. **Price mismatch**: Value delivered doesn't justify cost

### Recovery Playbook
1. **Identify your best segment**: Who are the "very disappointed" users? What do they have in common?
2. **Strip to core value**: What's the one thing your best users love? Remove everything that doesn't serve it
3. **Re-validate**: Run fresh discovery with current users and prospects
4. **Re-position**: Maybe the product is right but the framing is wrong
5. **Measure again**: Run Sean Ellis + retention analysis after changes
