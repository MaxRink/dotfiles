---
name: ai4dev-product-managment-pm-best-practices
description: Product management best practices for PRD writing, user story creation, and agile delivery. This skill provides background knowledge about PM workflows and should be used whenever Claude is helping with product management tasks — writing PRDs, creating user stories, planning sprints, or communicating with stakeholders. It ensures consistent quality and adherence to PM best practices.
user-invocable: false
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/pm-best-practices by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Product Management Best Practices

## PRD Writing

### Template Selection
| Scenario | Template | Reasoning |
|----------|----------|-----------|
| New product launch | Full PRD | Comprehensive alignment across teams |
| Major feature (>1 quarter) | Full PRD | Complexity warrants thorough docs |
| Small feature (<1 sprint) | Lean PRD | Quick to write, easy to iterate |
| Experiment / A/B test | Lean PRD | Focus on hypothesis and metrics |
| Platform/infra change | Full PRD | Technical considerations are critical |
| Bug fix initiative | None | Use Jira stories directly |

### Writing Good User Stories

**Format:** As a [specific persona], I want [concrete action] so that [measurable benefit].

**Common Mistakes:**
- Too vague: "As a user, I want a better experience"
- Too technical: "As a user, I want the API to use GraphQL"
- Missing benefit: "As a PM, I want a dashboard"

**Good Examples:**
- "As a hiring manager, I want to filter candidates by skill match percentage so that I spend time only on the most qualified applicants."

### Acceptance Criteria

**Given-When-Then (Preferred):**
```
Given I am a logged-in premium user
When I navigate to the analytics dashboard
Then I see data from the last 30 days by default
```

**Checklist Style (Simple cases):**
```
- [ ] Page loads in under 2 seconds
- [ ] Works on mobile viewports (320px+)
- [ ] Accessible with screen readers (WCAG 2.1 AA)
```

### PRD Review Checklist
- [ ] Problem statement backed by data or research
- [ ] Success metrics are measurable with targets
- [ ] Scope clearly defined (in AND out)
- [ ] User stories cover primary persona's journey
- [ ] Acceptance criteria are testable
- [ ] Technical considerations reviewed with engineering
- [ ] Dependencies identified with owners
- [ ] Risks have mitigations
- [ ] Timeline realistic for team capacity
- [ ] Open questions have owners and deadlines

For detailed reference material, read `${CLAUDE_SKILL_DIR}/references/writing-guide.md`.

## Agile Delivery

### Story Point Calibration
| Points | Complexity | Example |
|--------|-----------|---------|
| 1 | Trivial | Config change, copy update |
| 2 | Small | Simple UI change, add a field |
| 3 | Medium | New component, API endpoint |
| 5 | Large | Feature with multiple components |
| 8 | Very Large | Cross-system feature |
| 13 | Epic-sized | Should be broken down |

### Sprint Planning Rules
- Never plan at 100% capacity — reserve 15-20% buffer
- Average velocity over last 3 sprints, not best sprint
- Carry-over items get re-estimated, not auto-included
- Sprint goal should be one measurable sentence

### Communication Principles
- Lead with the headline — most important thing first
- Quantify impact: "Reduced load time by 40%" not "improved performance"
- Be honest about risks — sugar-coating erodes trust
- Keep it scannable: tables, bullets, headers

## Decision Tree: Choosing the Right Workflow

```
User needs: [Product Work Type]
    |-- Discovery / Validation?
    |   |-- Customer insights? --> create-research (interview)
    |   |-- Hypothesis testing? --> create-research (hypothesis)
    |   |-- Opportunity mapping? --> product-strategy (ost)
    |   |-- PMF check? --> measure-pmf
    |
    |-- Strategy / Vision?
    |   |-- Long-term direction? --> product-strategy (vision)
    |   |-- Market positioning? --> product-strategy (positioning)
    |   |-- Amazon-style spec? --> product-strategy (prfaq)
    |   |-- Opportunity size? --> product-strategy (opportunity-assessment)
    |
    |-- Planning / Roadmap?
    |   |-- Outcome roadmap? --> create-roadmap
    |   |-- Metrics / OKRs? --> create-okrs
    |   |-- Sprint plan? --> plan-sprint
    |
    |-- Prioritization / Focus?
    |   |-- What to build next? --> prioritize
    |   |-- What to stop? --> prioritize (kill criteria)
    |   |-- Feature audit? --> measure-pmf (feature-audit)
    |
    |-- Specs / Requirements?
    |   |-- Full PRD? --> create-prd --full
    |   |-- Lean PRD? --> create-prd --lean
    |   |-- Jira stories? --> create-jira-stories
    |
    |-- Communication?
    |   |-- Status update? --> create-comms (status)
    |   |-- Release notes? --> create-comms (release-notes)
    |   |-- Exec summary? --> create-comms (executive-summary)
    |   |-- Meeting agenda? --> create-comms (agenda)
    |
    |-- Leadership / Team?
        |-- 1:1 meeting? --> leadership-ops (1on1)
        |-- Give feedback? --> leadership-ops (feedback)
        |-- Difficult conversation? --> leadership-ops (negotiation)
        |-- Post-incident? --> leadership-ops (debrief)
        |-- Stakeholder pushback? --> leadership-ops (stakeholder)
```

## Modern PM Principles

- **Evidence quality beats confidence**: Label signals as strong/medium/weak; write what would change your mind
- **Outcomes over output**: Roadmaps are bets with measurable impact and guardrails, not feature inventories
- **Metrics must be defined**: Formula + timeframe + data source, or it's not actionable
- **Privacy, security, accessibility are requirements**, not afterthoughts
- **Discovery de-risks value**: Validate before building; prioritize by evidence, not opinions
- **Kill criteria before starting**: Every initiative should have pre-defined stop conditions
- **Measure PMF continuously**: It varies by segment and can be lost as markets shift

## Do

- Start from the decision: what are we deciding, by when, and with what evidence
- Define metrics precisely (formula + timeframe + data source) and add guardrails
- Use discovery to de-risk value before building
- Write "match vs ignore" competitive decisions, not feature grids
- Define kill criteria before starting any initiative
- Measure PMF across segments, not as a binary yes/no

## Avoid

- Roadmap theater (shipping lists) without outcomes and learning loops
- Vanity KPIs (raw signups, impressions) without activation/retention definitions
- "Build-first validation" (shipping MVPs without falsifiable hypotheses)
- Feature creep without kill criteria
- Saying "yes" to stakeholder requests without trade-off analysis
- Measuring PMF once instead of continuously across segments
- Building for engineering elegance instead of user value

## Anti-Patterns to Avoid
1. **Feature Factory**: Building without validating real problems
2. **HiPPO**: Highest Paid Person's Opinion drives roadmap
3. **Scope Creep**: Must Haves growing after planning
4. **Vanity Metrics**: Numbers that look good but don't indicate value
5. **Waterfall PRDs**: 50-page docs nobody reads
6. **Estimation Theater**: False precision — ranges are more honest
7. **No Kill Criteria**: Starting initiatives without defining when to stop
8. **Build-First Validation**: Shipping MVPs without falsifiable hypotheses
9. **One-Time PMF**: Measuring product-market fit once instead of continuously
