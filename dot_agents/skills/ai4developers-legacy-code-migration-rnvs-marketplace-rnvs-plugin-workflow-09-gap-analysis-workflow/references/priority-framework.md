# Priority Framework Reference

## Priority Scoring Formula

```
Priority Score = (Business Impact × 3) + (Technical Urgency × 2) + (Dependencies × 1)
```

**Maximum Score**: 5×3 + 5×2 + 5×1 = 30
**Minimum Score**: 1×3 + 1×2 + 1×1 = 6

## Scoring Criteria

### Business Impact (1-5)

| Score | Description | Examples |
|-------|-------------|----------|
| 5 | Blocks critical business operations | Core porting functionality, BNetzA compliance |
| 4 | Significant business disruption | Major workflow blocked, customer impact |
| 3 | Moderate business impact | Important but workarounds exist |
| 2 | Minor business impact | Nice-to-have features |
| 1 | No business impact | Internal improvements only |

### Technical Urgency (1-5)

| Score | Description | Examples |
|-------|-------------|----------|
| 5 | Blocking other development work | Foundation component needed by others |
| 4 | High technical debt if delayed | Complex refactoring needed later |
| 3 | Moderate technical debt | Some rework needed |
| 2 | Minor technical debt | Small cleanup possible |
| 1 | No technical urgency | Can be done anytime |

### Dependencies (1-5)

| Score | Description | Examples |
|-------|-------------|----------|
| 5 | Blocks multiple other gaps | Core API needed by 5+ services |
| 4 | Blocks 2-3 other gaps | Shared component |
| 3 | Blocks 1 other gap | Direct dependency |
| 2 | Soft dependency | Would be nice to have first |
| 1 | No dependencies | Independent work |

## Priority Levels

| Priority | Score Range | Sprint | Description | Action |
|----------|-------------|--------|-------------|--------|
| **P0 (Critical)** | ≥20 | Sprint 1 | Must complete first | Immediate action |
| **P1 (High)** | 15-19 | Sprint 1-2 | Important, early | Schedule in Sprint 1-2 |
| **P2 (Medium)** | 10-14 | Sprint 2-3 | Nice-to-have | Plan for later sprints |
| **P3 (Low)** | <10 | Backlog | Future consideration | Backlog item |

## Priority Calculation Examples

### Example 1: Critical Gap
```
Gap: Missing BNetzA compliance validation

Business Impact: 5 (regulatory requirement)
Technical Urgency: 4 (blocks certification)
Dependencies: 3 (needed by porting workflow)

Score = (5 × 3) + (4 × 2) + (3 × 1)
      = 15 + 8 + 3
      = 26

Priority: P0 (Critical) - Score ≥20
```

### Example 2: High Priority Gap
```
Gap: Missing pagination in API response

Business Impact: 3 (moderate - large queries slow)
Technical Urgency: 4 (architectural pattern)
Dependencies: 2 (soft dependency from UI)

Score = (3 × 3) + (4 × 2) + (2 × 1)
      = 9 + 8 + 2
      = 19

Priority: P1 (High) - Score 15-19
```

### Example 3: Medium Priority Gap
```
Gap: Missing audit logging

Business Impact: 2 (nice-to-have for debugging)
Technical Urgency: 2 (no urgency)
Dependencies: 1 (independent)

Score = (2 × 3) + (2 × 2) + (1 × 1)
      = 6 + 4 + 1
      = 11

Priority: P2 (Medium) - Score 10-14
```

## Effort Estimation (T-shirt Sizing)

| Size | Duration | Story Points | Description |
|------|----------|--------------|-------------|
| **XS** | 1-2 hours | 1 | Trivial fix, single line change |
| **S** | 2-8 hours | 2-3 | Half day to full day |
| **M** | 1-3 days | 5-8 | Moderate complexity, some research |
| **L** | 3-10 days | 13-21 | 1-2 weeks, complex implementation |
| **XL** | 10+ days | 21+ | 2+ weeks, may need breakdown |

## Risk Level Matrix

| | Low Tech Complexity | Med Tech Complexity | High Tech Complexity |
|---|:---:|:---:|:---:|
| **High Business Impact** | High | Critical | Critical |
| **Med Business Impact** | Medium | High | High |
| **Low Business Impact** | Low | Medium | Medium |

## Sprint Planning Guidelines

### Sprint 1 Capacity Planning
- Total P0 effort should not exceed 80% of sprint capacity
- Reserve 20% for unexpected issues
- P1 items only if P0 work is done

### Sprint 2-3 Capacity Planning
- Mix of P1 and P2 items
- Consider dependencies from Sprint 1
- Allow buffer for P0 carryover

### Backlog Management
- P3 items reviewed monthly
- Re-prioritize as requirements evolve
- Archive items not touched in 3 months
