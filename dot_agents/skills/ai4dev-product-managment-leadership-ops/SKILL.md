---
name: ai4dev-product-managment-leadership-ops
description: PM leadership and team operations — 1:1 meeting templates, feedback delivery (SBI model), negotiation prep (Voss method), post-incident debriefs (A3), and stakeholder management. Use this skill when a user wants to prepare for a 1:1, give or receive feedback, prepare for a difficult conversation, manage stakeholders, handle pushback, run a retrospective, do a post-mortem, or navigate team dynamics. Also trigger for 'how do I give feedback', 'prepare for my 1:1', 'stakeholder pushback', 'difficult conversation', 'post-mortem', 'retrospective template', or any PM leadership and people management situation.
argument-hint: "[type: 1on1|feedback|negotiation|debrief|stakeholder] [context]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/leadership-ops by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PM Leadership & Ops

Templates and frameworks for the people side of product management.

**Detect type** from $ARGUMENTS or ask: "What do you need? 1:1 template, feedback preparation, negotiation prep, post-incident debrief, or stakeholder management plan?"

## 1. 1:1 Meeting Template

```markdown
# 1:1 Meeting: [Your Name] / [Other Person]
**Date:** [Date] | **Duration:** [30 min]

## Check-In (5 min)
- How are you doing? (genuine, not performative)
- Energy level this week?

## Their Topics (15 min)
*Let them go first. Listen more than you talk.*
- [ ] [Topic they raised]
- [ ] [Topic they raised]

## Your Topics (5 min)
- [ ] [Feedback or update]
- [ ] [Ask or alignment item]

## Progress & Blockers
| Initiative | Status | Blocker | Help Needed |
|-----------|--------|---------|-------------|
| | | | |

## Growth & Development
- Current growth area: [skill they're developing]
- Progress: [observations]
- Suggestion: [specific, actionable]

## Action Items
| Action | Owner | Due |
|--------|-------|-----|
| | | |

## Notes
[Key takeaways from the conversation]
```

## 2. Feedback Template (SBI Model)

Situation-Behavior-Impact: specific, objective, and actionable.

```markdown
# Feedback Preparation

## Context
- **Relationship:** [Your role relative to theirs]
- **Goal:** [What you want to achieve with this feedback]
- **Tone:** [Supportive / Direct / Coaching]

## SBI Framework

### Situation
*When and where did this happen? Be specific.*
"In [meeting/context] on [date]..."

### Behavior
*What did they do? Observable actions only, no interpretation.*
"You [specific action — what they said or did]..."

### Impact
*What was the effect? On you, the team, the project.*
"The impact was [specific consequence]..."

## Request
*What would you like them to do differently?*
"Going forward, I'd appreciate if you [specific alternative behavior]..."

## Prepare for Responses
| They might say | Your response |
|---------------|---------------|
| "I didn't mean to..." | "I understand. Let's focus on the impact and how we move forward." |
| "That's not fair..." | "I hear you. Can you help me understand your perspective?" |
| "Nobody else has said that..." | "I can only share my experience. Here's what I observed..." |
```

### Feedback Principles
- Give feedback within 48 hours while context is fresh
- Positive feedback should be specific too — "great job" is as useless as "do better"
- Ask permission: "Can I share some feedback about [topic]?"
- Focus on behavior, not character ("you interrupted" not "you're rude")
- Offer support: "How can I help with this?"

## 3. Negotiation One-Sheet (Voss Method)

Based on Chris Voss's "Never Split the Difference" — prepare before any difficult conversation.

```markdown
# Negotiation Prep: [Topic]
**Date:** [Date] | **Counterpart:** [Name/Role]

## Goal
- **Best outcome:** [What you ideally want]
- **Acceptable outcome:** [Minimum you'd accept]
- **Walk-away point:** [When you say no]

## Their Perspective
- **What do they want?** [Their stated position]
- **Why do they want it?** [Underlying interests/fears]
- **What pressures are they under?** [Timeline, boss, budget]

## Calibrated Questions (open-ended "how" and "what")
Prepare 3-5 questions that make them solve your problems:
1. "How am I supposed to [your constraint]?"
2. "What about this is important to you?"
3. "How does this affect [shared goal]?"
4. "What happens if we don't do this?"
5. "How can we make this work for both sides?"

## Labels (acknowledge their emotions)
- "It seems like you're concerned about..."
- "It sounds like [priority] is really important to you..."
- "It feels like there's a lot of pressure on..."

## Tactical Empathy Summary
*Describe their perspective so well they say "that's right":*
"From your perspective, [their situation and concerns]..."

## Trade-Offs to Offer
| You Give | You Get | Net Value |
|----------|---------|-----------|
| | | |

## Potential Black Swans
[Unknown information that could change everything if revealed]
```

## 4. Post-Incident Debrief (A3 Method)

A structured format for learning from what went wrong — blameless and action-oriented.

```markdown
# Post-Incident Debrief: [Incident Title]
**Date:** [Date] | **Facilitator:** [Name]
**Severity:** [S1/S2/S3] | **Duration:** [X hours]

## What Happened
**Timeline:**
| Time | Event |
|------|-------|
| [HH:MM] | [What happened] |

## Intent vs Actual
| Aspect | What We Intended | What Actually Happened | Gap |
|--------|-----------------|----------------------|-----|
| | | | |

## Root Cause Analysis (5 Whys)
1. Why did [incident] happen? → Because [cause 1]
2. Why did [cause 1] happen? → Because [cause 2]
3. Why did [cause 2] happen? → Because [cause 3]
4. Why did [cause 3] happen? → Because [cause 4]
5. Why did [cause 4] happen? → Because [root cause]

**Root cause:** [Summary]

## Contributing Factors
- [ ] Process gap: [description]
- [ ] Communication failure: [description]
- [ ] Technical debt: [description]
- [ ] Missing monitoring: [description]

## What Went Well
- [Positive aspect of the response]

## Action Items
| Action | Owner | Due Date | Priority | Status |
|--------|-------|----------|----------|--------|
| | | | | |

## Lessons Learned
1. [Key takeaway]
2. [Key takeaway]

## Prevention
What systemic change prevents this class of incident?
- [Change 1]
```

## 5. Stakeholder Management

```markdown
# Stakeholder Map: [Initiative/Product]
**Date:** [Date]

## Stakeholder Matrix
| Stakeholder | Role | Interest Level | Influence Level | Stance | Strategy |
|-------------|------|---------------|----------------|--------|----------|
| | | High/Med/Low | High/Med/Low | Champion/Neutral/Critic | |

## Communication Plan
| Stakeholder Type | Frequency | Format | Content |
|-----------------|-----------|--------|---------|
| Board / Investors | Monthly | Narrative memo | Metrics + decisions + asks |
| Executive sponsor | Bi-weekly | 1-pager | Health, risks, decisions |
| Engineering | Daily/Sprint | Stand-up/Review | Progress, blockers |
| Sales/CS | Monthly | Email/Deck | Roadmap updates, launches |
| Customers | Quarterly | Blog/Email | Highlights, what's coming |

## Managing Pushback
When stakeholders push for features or changes:

| Pushback Type | Response Pattern |
|--------------|-----------------|
| "Add this feature" | "We can add X if we cut Y — which matters more for [goal]?" |
| "Why isn't this done?" | Share status with context, not excuses. "Here's where we are, here's the blocker, here's the plan." |
| "Competitor has this" | "Let me share our match vs ignore analysis for that feature." |
| "My customer needs..." | "Let's validate how many customers need this. Can you connect me with 3 more?" |
| "Just make it happen" | "I want to get this right. Here are 3 options with trade-offs — which aligns best with our goals?" |

## Key Relationships to Maintain
| Person | Why They Matter | Last Touchpoint | Next Action |
|--------|----------------|----------------|-------------|
| | | | |
```

## Guidelines

- 1:1s are their meeting, not yours — let them set the agenda first
- Feedback is a gift, but timing and delivery matter — don't ambush people
- Negotiation is not about winning — it's about understanding the other side so well you can find creative solutions
- Post-incident debriefs must be blameless — the goal is learning, not punishment
- Stakeholder management is ongoing, not one-time — update your map quarterly
