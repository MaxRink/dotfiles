# Leadership & Operations Frameworks — Extended Reference

## Table of Contents
1. SBI Feedback Deep Dive
2. Voss Negotiation Patterns
3. A3 Problem-Solving Method
4. Stakeholder Influence Strategies
5. Difficult Conversation Playbooks

## 1. SBI Feedback Deep Dive

### Situation-Behavior-Impact Framework

**Why SBI works**: It separates observation from interpretation. Most feedback fails because it describes intent ("you weren't paying attention") rather than behavior ("you checked your phone three times during the demo").

### Positive Feedback Examples

| Situation | Behavior | Impact |
|-----------|----------|--------|
| "In yesterday's sprint review..." | "you walked the stakeholders through each demo with clear context before showing the feature" | "The stakeholders asked better questions and left with a clear understanding of progress" |
| "During the incident on Tuesday..." | "you immediately set up a war room, assigned roles, and posted status updates every 15 minutes" | "The team stayed focused and we resolved it 2 hours faster than the last similar incident" |

### Constructive Feedback Examples

| Situation | Behavior | Impact |
|-----------|----------|--------|
| "In the planning meeting today..." | "you presented the deadline as final without asking the team for input on the estimate" | "Two engineers told me afterward they felt unheard and are worried about unrealistic expectations" |
| "Over the past two sprints..." | "requirements changes came in after stories were committed, three times per sprint" | "The team's velocity dropped 30% and morale around predictability is low" |

### Escalation Patterns
If feedback doesn't land the first time:
1. **First time**: SBI conversation, collaborative
2. **Second time**: SBI + explicit request + timeline for change
3. **Third time**: SBI + consequences + documented agreement
4. **Fourth time**: Formal process (HR, skip-level, etc.)

## 2. Voss Negotiation Patterns

### Core Techniques

**Mirroring**: Repeat the last 3 words (or key words) the other person said. This encourages them to elaborate without feeling interrogated.
- Them: "We can't possibly ship by Q2."
- You: "Can't possibly ship by Q2?"
- Them: "Well, the API integration alone would take..."

**Labeling**: Name the emotion behind their words. Starts with "It seems like..." or "It sounds like..."
- "It seems like you're frustrated with the timeline..."
- "It sounds like there's a lot of pressure from leadership on this..."

**Calibrated Questions**: Open-ended "how" and "what" questions that make them solve your problem:
- "How am I supposed to do that?" (not hostile — genuinely curious)
- "What makes this important to you?"
- "How does this affect the rest of the team?"
- "What happens if we don't do this?"

**"That's Right"**: Summarize their perspective so accurately they say "that's right" (not "you're right" — different thing). This indicates genuine understanding.

### PM-Specific Scenarios

| Scenario | Technique | Example |
|----------|-----------|---------|
| Stakeholder wants a feature NOW | Calibrated question | "How should we handle the other commitments we've made for this sprint?" |
| Engineer says estimate is too low | Label + mirror | "It sounds like there's more complexity than the story captures. More complexity?" |
| Exec overrides your prioritization | Tactical empathy | "I understand this is important for the board presentation. How do we balance this with the retention work we committed to?" |
| Customer threatens to churn | Label + calibrated | "It seems like this is really blocking your team. What would make the biggest difference right now?" |

## 3. A3 Problem-Solving Method

### Origin
Toyota's A3 report forces complex problems onto a single page (A3 paper size), driving clarity and action.

### Structure
1. **Background**: Why are we looking at this?
2. **Current condition**: What's happening now? (Data, not opinions)
3. **Goal**: What should be happening?
4. **Root cause analysis**: Why is the gap there? (5 Whys)
5. **Countermeasures**: What will we change?
6. **Implementation plan**: Who, what, when?
7. **Follow-up**: How will we know it worked?

### 5 Whys Best Practices
- Each "why" should lead to a cause, not a person
- Stop when you reach a systemic cause the team can fix
- Multiple root causes are common — map them all
- Verify each causal link with evidence

### Common Traps
- Stopping at the first "why" (treating symptoms)
- Blaming individuals instead of systems
- Proposing solutions before understanding the problem
- No follow-up to verify countermeasures worked

## 4. Stakeholder Influence Strategies

### Influence Without Authority

| Strategy | When to Use | How |
|----------|------------|-----|
| **Data-driven persuasion** | Skeptical stakeholder | Present metrics, benchmarks, user quotes |
| **Social proof** | Conservative stakeholder | "Teams X and Y did this with [results]" |
| **Incremental buy-in** | Risk-averse stakeholder | "Let's try a 2-week experiment and review data" |
| **Co-creation** | Controlling stakeholder | Involve them in the solution design |
| **Escalation** | Persistent blocker | Go through proper channels with documentation |

### Managing Up (Your Manager/Exec)
- **No surprises**: Flag risks early, not after they explode
- **Options, not problems**: "Here are 3 options with trade-offs" not "this is broken"
- **Their priorities**: Frame your request in terms of what they care about
- **Written summaries**: After verbal agreements, follow up in writing

### Managing Across (Peers)
- **Reciprocity**: Help them first, ask later
- **Shared goals**: Find the metric you both care about
- **Regular touchpoints**: Don't only reach out when you need something
- **Credit sharing**: Publicly recognize their contributions

## 5. Difficult Conversation Playbooks

### "We Need to Cut Your Feature"
1. Acknowledge the investment: "I know your team has put significant work into this"
2. Share the data: "Here's what usage looks like and what it's costing us"
3. Explain the trade-off: "By sunsetting this, we can [better outcome]"
4. Offer alternatives: "Here's the migration path for affected users"
5. Commit to a timeline: "We'll do this gradually over [timeframe]"

### "Your Estimate is Too High"
1. Don't challenge directly — ask to understand
2. "Walk me through the complexity — what am I missing?"
3. "Are there ways to reduce scope and still deliver the core value?"
4. "What if we split this into phases?"
5. Respect the expertise — engineering estimates should be the team's, not yours

### "We Missed the Target"
1. Own it: "We committed to X and delivered Y. Here's why."
2. No excuses: State facts, not justifications
3. Root cause: "The gap was caused by [specific factors]"
4. Learning: "Here's what we're changing to prevent this"
5. Reset: "Here's the revised target and our confidence level"
