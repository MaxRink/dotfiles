---
name: ai4dev-product-managment-create-comms
description: Create stakeholder communications — status updates, release notes, meeting agendas, and executive summaries. Use this skill when a user needs to write a status report, sprint review summary, release announcement, stakeholder email, steering committee update, meeting agenda, changelog, or any product communication directed at stakeholders, leadership, or cross-functional teams. Also trigger for 'write an update', 'prepare release notes', 'draft an agenda', or 'summarize for leadership'.
argument-hint: "[type: status|release-notes|agenda|executive-summary] [context]"
allowed-tools: Read, Grep, Glob, Write
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/create-comms by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Stakeholder Communications

Generate clear, audience-appropriate product communications.

**Detect type** from $ARGUMENTS or ask: "What type of communication? Status update, release notes, meeting agenda, or executive summary?"

## 1. Status Update / Sprint Review

```markdown
# Product Status Update
**Period:** [Sprint X / Week of Date]
**Product:** [Name]
**Author:** [PM Name]

## Summary
[2-3 sentences: what happened, overall health, key decisions needed]

## Health Indicators
| Area | Status | Trend |
|------|--------|-------|
| Schedule | On Track / At Risk / Delayed | Improving / Stable / Declining |
| Scope | Stable / Growing / Reduced | |
| Quality | Good / Acceptable / Concerning | |
| Team | Healthy / Stretched / Blocked | |

## What We Shipped
- [Feature] — [impact]

## In Progress
| Item | Owner | Status | ETA | Blockers |
|------|-------|--------|-----|----------|
| | | | | |

## Key Decisions Needed
- [ ] **[Decision]** — Context: [why], Options: [A/B/C], Recommendation: [X], Deadline: [date]

## Risks & Blockers
| Issue | Impact | Owner | Mitigation |
|-------|--------|-------|------------|
| | | | |

## Next Sprint Focus
- Priority 1: [what and why]

## Metrics
| Metric | Last Period | This Period | Target | Trend |
|--------|-----------|-------------|--------|-------|
| | | | | |
```

## 2. Release Notes

```markdown
# Release Notes: [Product] [Version]
**Release Date:** [Date]

## Highlights
[1-2 paragraph summary for users]

## New Features
### [Feature Name]
[User-friendly description]

## Improvements
- [Improvement] — [what changed]

## Bug Fixes
- Fixed an issue where [user-visible symptom]

## Known Issues
- [Issue] — Workaround: [if any]

## Migration Notes
[Breaking changes or user actions needed]
```

## 3. Meeting Agenda

```markdown
# [Meeting Name] Agenda
**Date:** [Date] | **Time:** [Time] | **Duration:** [X min]
**Attendees:** [Names/Roles]

## Pre-Read
- [Document to review before meeting]

## Agenda
| # | Topic | Owner | Time | Type |
|---|-------|-------|------|------|
| 1 | [Topic] | [Name] | X min | Info / Discussion / Decision |

## Action Items (from previous meeting)
- [ ] [Action] — Owner: [Name] — Status: [Done/In Progress]
```

## 4. Executive Summary

```markdown
# Executive Summary: [Initiative]
**Date:** [Date] | **Author:** [Name]

## TL;DR
[3 sentences max: what, so what, now what]

## Business Context
[Why this matters — revenue, users, strategy]

## Current State
[Where we are, key metrics]

## Achievements This Period
- [Achievement with quantified impact]

## Challenges & Risks
| Challenge | Business Impact | Action Required |
|-----------|----------------|-----------------|
| | | |

## Ask / Decision Needed
[What you need from leadership]

## Outlook
[What's coming, confidence level, key dates]
```

## Writing Guidelines

- **Lead with the headline**: Most important thing first
- **Quantify impact**: "Reduced load time by 40% (3.2s to 1.9s)" not "improved performance"
- **Be honest about risks**: Sugar-coating erodes trust
- **Keep it scannable**: Tables, bullets, headers — no walls of text
- Save output as `[type]-[date-or-context].md`
