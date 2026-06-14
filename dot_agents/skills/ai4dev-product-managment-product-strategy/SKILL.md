---
name: ai4dev-product-managment-product-strategy
description: Create product vision, positioning, opportunity assessments, and strategic documents. Use this skill when a user wants to define product vision, position against competitors, write a PR/FAQ (Amazon-style), map opportunities with an Opportunity Solution Tree, assess a market opportunity, or plan product strategy. Also trigger for 'product vision', 'how do we position this', 'competitive positioning', 'opportunity assessment', 'PR/FAQ', 'product strategy', 'where should we invest', or any request about long-term product direction and market positioning.
argument-hint: "[type: vision|positioning|prfaq|opportunity-assessment|ost] [context]"
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/product-managment/skills/product-strategy by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Product Strategy

Create strategic product documents that define direction, positioning, and opportunity.

**Detect type** from $ARGUMENTS or ask: "What do you need? Product vision, competitive positioning, PR/FAQ, opportunity assessment, or opportunity solution tree?"

## 1. Product Vision

A 3-5 year narrative of where the product is going and why.

```markdown
# Product Vision: [Product Name]
**Author:** [Name] | **Date:** [Date] | **Horizon:** [3-5 years]

## From → To
**From:** [Current state — what the world looks like today for your users]
**To:** [Future state — what the world looks like when your product succeeds]

## Vision Statement
[One paragraph. Aspirational but grounded. Describes the change you're making in the world.]

## Who We Serve
**Primary audience:** [Specific persona with context]
**Their biggest pain:** [The core problem, stated in their words]
**Their desired outcome:** [What success looks like for them]

## Strategic Pillars (3-5)
| Pillar | Description | 1-Year Milestone | 3-Year Ambition |
|--------|-------------|-----------------|-----------------|
| | | | |

## What We Won't Do
[Explicit list of areas we will NOT pursue. Saying no is as important as saying yes.]

## How We Win
[2-3 paragraphs on competitive advantage, moat, and differentiation]

## Key Bets
| Bet | Thesis | Evidence | Risk if Wrong |
|-----|--------|----------|---------------|
| | | | |

## Success in 3 Years Looks Like
- [Quantified outcome 1]
- [Quantified outcome 2]
- [Quantified outcome 3]
```

## 2. Competitive Positioning (Dunford Method)

Based on April Dunford's positioning framework — start from competitive alternatives, not your product.

```markdown
# Positioning: [Product Name]
**Date:** [Date] | **Method:** Obviously Awesome (Dunford)

## Step 1: Competitive Alternatives
What would customers use if your product didn't exist?
| Alternative | Type | Limitation |
|------------|------|-----------|
| | Direct competitor / Manual process / Status quo | |

## Step 2: Unique Attributes
What do you have that alternatives don't?
| Attribute | Why It's Unique |
|-----------|----------------|
| | |

## Step 3: Value
What value do those attributes enable for users?
| Attribute | Value Delivered | Evidence |
|-----------|----------------|----------|
| | | |

## Step 4: Target Segment
Who cares the most about this value?
- **Best-fit customer:** [Description with specifics]
- **Characteristics:** [What makes them ideal]
- **They care because:** [Why this value matters to them specifically]

## Step 5: Market Category
What context makes your value obvious?
- **Category:** [The frame of reference you're setting]
- **Why this category:** [How it helps customers understand your value]

## Positioning Statement
For [target segment] who [key need/pain], [product] is a [category] that [key differentiator]. Unlike [primary alternative], we [unique value].

## Match vs Ignore Decisions
| Competitor Feature | Our Response | Rationale |
|-------------------|-------------|-----------|
| | Match / Ignore / Differentiate | |
```

## 3. PR/FAQ (Amazon-Style Working Backwards)

Start from the press release announcing the finished product, then work backwards.

```markdown
# PR/FAQ: [Feature/Product Name]

## Press Release

### [Headline: One sentence announcing the product]
**[City, Date]** — [Company] today announced [product/feature], which [primary benefit for customers].

[Paragraph 2: Problem the customer has]

[Paragraph 3: How the product solves it]

"[Quote from a leader explaining why this matters]" — [Name, Title]

[Paragraph 4: How it works at a high level]

"[Quote from a beta customer or persona]" — [Name, Company]

[Paragraph 5: Call to action — how to get started]

## FAQ

### Customer FAQ
1. **Q: [Question a customer would ask]**
   A: [Answer]

2. **Q: [Question about pricing/availability]**
   A: [Answer]

3. **Q: [Question about migration/switching]**
   A: [Answer]

### Internal FAQ
1. **Q: Why now?**
   A: [Market timing, competitive pressure, or user demand]

2. **Q: What's the estimated investment?**
   A: [Resources, timeline, cost]

3. **Q: What are the biggest risks?**
   A: [Risks and mitigations]

4. **Q: How will we measure success?**
   A: [Metrics and targets]
```

## 4. Opportunity Assessment

Evaluate whether a market opportunity is worth pursuing.

```markdown
# Opportunity Assessment: [Opportunity Name]
**Date:** [Date] | **Author:** [Name]

## Opportunity Summary
[One paragraph describing the opportunity]

## Market Size
| Metric | Estimate | Source/Method |
|--------|----------|--------------|
| TAM | | |
| SAM | | |
| SOM | | |

## Customer Problem
- **Who:** [Target segment]
- **Problem:** [Specific pain]
- **Current solutions:** [How they solve it today]
- **Willingness to pay:** [Evidence]

## Strategic Fit
| Criterion | Score (1-5) | Notes |
|-----------|------------|-------|
| Aligns with vision | | |
| Leverages existing strengths | | |
| Defensible advantage | | |
| Revenue potential | | |
| Team capability | | |

## Competitive Landscape
| Player | Strength | Weakness | Our Advantage |
|--------|----------|----------|---------------|
| | | | |

## Investment Required
- **Team:** [Headcount/skills needed]
- **Timeline:** [Estimated time to market]
- **Cost:** [Rough estimate]

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| | | | |

## Recommendation
**Go / No-Go / Investigate Further**
[Reasoning]
```

## 5. Opportunity Solution Tree (OST)

Map the path from desired outcome to testable solutions.

```markdown
# Opportunity Solution Tree: [Desired Outcome]

## Desired Outcome
[Measurable business or user outcome]

## Opportunities (User problems/needs discovered through research)

### Opportunity 1: [Problem/need]
**Evidence:** [How we know this is real — interviews, data, support tickets]
**Solutions:**
- Solution A: [Description] — Effort: [S/M/L] — Confidence: [H/M/L]
- Solution B: [Description] — Effort: [S/M/L] — Confidence: [H/M/L]
**Experiments:**
- [ ] [Experiment to validate Solution A]
- [ ] [Experiment to validate Solution B]

### Opportunity 2: [Problem/need]
**Evidence:** [Source]
**Solutions:**
- Solution C: [Description]
**Experiments:**
- [ ] [Experiment to validate]

## Assumption Tests
| Assumption | Test Method | Success Criteria | Status |
|-----------|-------------|-----------------|--------|
| Users have [problem] | 5 interviews | 4/5 confirm | |
| [Solution] solves it | Prototype test | Task completion >80% | |
| Users will pay for it | Fake door test | >5% click-through | |
```

## Guidelines

- Evidence quality beats confidence: label signals as strong/medium/weak; write what would change your mind
- Positioning is about what you WON'T do as much as what you will
- PR/FAQs should be written in real press release language — if it doesn't excite you to read it, the product isn't compelling enough
- For deeper strategy patterns, read `${CLAUDE_SKILL_DIR}/references/strategy-patterns.md`
