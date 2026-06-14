# Framework Details — Extended Reference

## Table of Contents
1. RICE Worked Examples
2. Weighted Scoring Setup
3. Impact/Effort Calibration
4. Framework Selection Decision Tree

## 1. RICE Worked Examples

### Example: "Add bulk export to CSV"
- **Reach**: 2,000 users/quarter (based on analytics: 2,000 monthly active users of the data table)
- **Impact**: 1 (Medium — saves time but not a core pain)
- **Confidence**: 80% (usage data is solid, impact is estimated)
- **Effort**: 0.5 person-months
- **RICE**: (2000 x 1 x 0.8) / 0.5 = **3,200**

### Example: "Redesign onboarding flow"
- **Reach**: 500 new users/quarter
- **Impact**: 3 (Massive — current activation rate is 30%, targeting 60%)
- **Confidence**: 50% (hypothesis from 3 interviews, no A/B data yet)
- **Effort**: 3 person-months
- **RICE**: (500 x 3 x 0.5) / 3 = **250**

The CSV export scores higher despite being "boring" — this is the value of RICE: it surfaces non-obvious priorities.

## 2. Weighted Scoring Setup

### Choosing Criteria
Good criteria are:
- **Independent**: Don't overlap (revenue impact and ARR increase measure the same thing)
- **Measurable**: Can be scored consistently by different people
- **Relevant**: Directly tied to your current strategy

### Common Criteria Sets

**B2B SaaS:**
| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Revenue impact | 30% | Drives growth |
| Customer retention | 25% | Reduces churn |
| Strategic alignment | 25% | Fits 2026 roadmap |
| Implementation effort (inverse) | 20% | Prefer lower effort |

**Consumer Product:**
| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| User engagement | 30% | Core growth metric |
| Virality potential | 25% | Organic acquisition |
| Monetization | 25% | Revenue sustainability |
| Technical debt reduction | 20% | Platform health |

### Calibration Process
1. Score 3 well-understood features first to calibrate the scale
2. Have 2-3 people score independently, then discuss discrepancies
3. If scores diverge by >2 points on any criterion, the criterion needs clearer definition

## 3. Impact/Effort Calibration

### Effort Buckets (T-shirt sizing)
| Size | Person-Days | Typical Scope |
|------|------------|---------------|
| XS | 1-2 | Config change, copy, simple fix |
| S | 3-5 | Single component, straightforward |
| M | 5-15 | Multiple components, some complexity |
| L | 15-30 | Cross-system, design + dev + test |
| XL | 30+ | Multi-sprint initiative |

### Impact Levels
| Level | Definition | Evidence Required |
|-------|-----------|-------------------|
| Very High | Changes a core metric by >20% | Data or strong user research |
| High | Moves a metric 5-20% | Some data or multiple user signals |
| Medium | Noticeable improvement, <5% metric change | Reasonable assumption |
| Low | Minor polish, few users affected | Gut feel is OK |

## 4. Framework Selection Decision Tree

```
Do you have quantitative reach/usage data?
├── Yes → Do you need precise ranking?
│   ├── Yes → RICE
│   └── No → Impact/Effort Matrix
└── No → Are you scoping a specific release?
    ├── Yes → MoSCoW
    └── No → Do you have custom business criteria?
        ├── Yes → Weighted Scoring
        └── No → Impact/Effort Matrix (simplest default)
```
