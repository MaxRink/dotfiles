---
name: ai4dev-mara-plugin-application-transformation-guide
description: This skill should be used when analyzing legacy applications for transformation, deciding between DPS and Agentic AI approaches, identifying AI agent candidates, selecting architecture patterns, or planning application modernization roadmaps within the MARA framework. Use this skill for transformation strategy, architecture decisions, and migration planning.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/application-transformation-guide by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Application Transformation Guide

## Overview

This skill provides comprehensive guidance for transforming legacy applications and Digital Platform Services (DPS) toward AI-enabled and agentic
architectures within the MARA (Magenta AI-Centric Reference Architecture) framework.
Use this skill to make informed decisions about transformation paths, identify suitable AI agent candidates, select appropriate architecture patterns, and plan transformation roadmaps.

## When to Use This Skill

Use this skill when:

- Analyzing legacy applications for modernization opportunities
- Deciding between Legacy → DPS or Legacy → Agentic AI transformation paths
- Evaluating whether to enhance existing DPS with AI or transform to agentic architecture
- Identifying business capabilities suitable for AI agent implementation
- Selecting architecture patterns (Decoupled Intelligence vs Embedded Reasoning)
- Assessing AI readiness and data availability
- Planning transformation roadmaps and prioritizing initiatives
- Evaluating risks and defining mitigation strategies
- Applying MARA principles to transformation decisions

## Transformation Decision Workflow

### Step 1: Understand the Current State

Start by analyzing the application or system being considered for transformation.

**Key Questions to Answer:**

1. What is the current architecture? (Monolithic, microservices, legacy mainframe, etc.)
2. What are the primary business capabilities and user workflows?
3. What are the key pain points? (Performance, maintainability, scalability, user experience)
4. What is the technical debt level?
5. What are the integration dependencies?
6. What data is available and what is its quality?

**Analysis Activities:**

- Review architecture documentation
- Interview stakeholders (business owners, technical teams, users)
- Examine codebase and dependencies
- Assess data landscape
- Identify regulatory and compliance requirements

**Document Findings:**
Create a current state assessment covering architecture, capabilities, pain points, technical debt, and constraints.

### Step 2: Define Target Outcomes

Clarify what success looks like after transformation.

**Key Questions to Answer:**

1. What business outcomes are desired? (Cost reduction, faster time to market, better UX, etc.)
2. What user experience improvements are needed?
3. What operational efficiencies are targeted?
4. What scalability requirements exist?
5. What innovation capabilities are needed?
6. What is the appetite for change and risk?

**Define Success Metrics:**

- Technical metrics (availability, latency, error rates)
- Business metrics (user satisfaction, cost savings, time to market)
- AI-specific metrics (automation rate, accuracy, learning improvement)

### Step 3: Choose the Transformation Path

Use the transformation decision framework to select the optimal path.

**Primary Decision: DPS vs Agentic AI**

Read `references/transformation-decision-framework.md` for comprehensive guidance. Key decision factors:

**Choose Legacy → DPS when:**

- Application has stable, well-defined business logic
- Requirements are predictable and rule-based
- Need deterministic, consistent outcomes
- Limited need for autonomous decision-making
- Lower risk tolerance
- Faster initial implementation needed

**Choose Legacy → Agentic AI when:**

- Application requires adaptive, context-aware decision-making
- Natural language interaction adds significant value
- Business processes benefit from autonomous problem-solving
- High variability in user requests
- Personalization and learning are critical
- Ready to invest in AI capabilities

**Consider DPS → Embedded AI when:**

- Existing DPS needs AI enhancement
- Want to minimize transformation risk
- Core business logic remains deterministic
- AI provides supplementary value
- Gradual AI adoption preferred

**Consider DPS → Agentic AI when:**

- Business needs evolved beyond DPS capabilities
- Increasing demand for personalization and adaptability
- Complex, dynamic user interactions
- ROI justifies transformation investment

**Apply Decision Criteria Matrix:**

| Criteria | DPS Fit | Agentic AI Fit |
|----------|---------|----------------|
| Business logic | Stable, rule-based | Adaptive, context-dependent |
| User interaction | API/UI forms | Natural language |
| Variability | Low | High |
| Decision-making | Deterministic | Autonomous, learning |
| Time to market | Fast | Medium-slow |
| Risk tolerance | Low | Medium-high |
| AI maturity | Low | Medium-high |

### Step 4: Identify AI Agent Candidates (for Agentic AI Path)

If pursuing the Agentic AI path, use the AgentFit Framework to identify suitable agent candidates.

Read `references/agentfit-framework.md` for the complete 8-step process. Summary:

**AgentFit 8-Step Process:**

1. **Domain Analysis** - Map business processes, capabilities, and data flows
2. **Candidate Identification** - Score candidates on autonomy, complexity, NL value, context awareness, learning opportunity
3. **Agent Capability Definition** - Define goals, responsibilities, decision authority, collaborations
4. **Data Availability Assessment** - Validate training data, operational data, context data, feedback data
5. **Interaction Pattern Design** - Design user interaction and agent-to-agent communication patterns
6. **Architecture Pattern Selection** - Choose between Decoupled Intelligence and Embedded Reasoning
7. **Risk Assessment & Mitigation** - Identify technical, business, operational risks and define mitigations
8. **Prioritization & Roadmap** - Score candidates and create phased implementation roadmap

**AgentFit Scoring (Step 2):**

For each candidate, score 1-5 on:

- Autonomy Potential: Can it operate independently?
- Decision Complexity: Requires judgment vs simple rules?
- Natural Language Value: Benefits from NL interaction?
- Context Awareness: Needs situational understanding?
- Learning Opportunity: Can improve with feedback?

**Interpretation:**

- Score 20-25: Excellent agent candidate (High Priority)
- Score 15-19: Good candidate with conditions (Medium Priority)
- Score < 15: Better as traditional service (Low Priority)

**Example Agent Candidates:**

- Customer service assistant (natural language, context-aware support)
- Data insight delivery agent (analyzes data, provides recommendations)
- Document processing agent (extracts, classifies, routes documents)
- Order fulfillment coordinator (orchestrates multi-step workflows)
- Mobile number portability agent (manages complex telecom process)

### Step 5: Select Architecture Patterns

Choose appropriate architecture patterns based on requirements.

Read `references/architecture-patterns.md` for detailed pattern descriptions. Key patterns:

**Pattern 1: Decoupled Intelligence**

- AI capabilities separate from core business logic
- AI provides advisory/analytical functions
- **Use when:** Business logic is stable, graceful degradation needed, compliance requires rules
- **Example:** Credit scoring with AI insights alongside rule-based decisions

**Pattern 2: Embedded Reasoning**

- AI agent owns the business logic and decision-making
- Traditional services provide data and action execution
- **Use when:** Natural language is primary interface, complex context-dependent decisions, personalization critical
- **Example:** Customer service chatbot that understands intent and takes action

**Pattern 3: Progressive Enhancement**

- Start with traditional DPS, progressively add AI capabilities
- Phased approach: Traditional → AI-Augmented → AI-First
- **Use when:** Uncertain about AI value, want to minimize risk, building AI capability gradually

**Pattern 4: Hierarchical Agents**

- Agents organized in tiers with delegation and specialization
- **Use when:** Complex problems requiring decomposition, clear specialization opportunities
- **Example:** Order fulfillment with inventory, shipping, notification agents

**Pattern 5: Human-in-the-Loop**

- Human approval required for critical decisions
- Confidence-based escalation
- **Use when:** High-risk decisions, regulatory requirements, building trust in AI

**Pattern 6: Multi-Model**

- Choose model based on need (cost, accuracy, speed)
- **Use when:** Cost optimization needed, variable latency requirements

**Pattern Selection Decision Tree:**

```text
Is natural language primary interface?
  Yes → Consider Embedded Reasoning
  No → Continue

Is business logic stable and deterministic?
  Yes → Consider Decoupled Intelligence
  No → Continue

Need multiple specialized capabilities?
  Yes → Consider Hierarchical Agents
  No → Continue

Uncertain about AI value?
  Yes → Use Progressive Enhancement
  No → Continue

High-risk decisions?
  Yes → Add Human-in-the-Loop
  No → Continue

Variable cost/performance needs?
  Yes → Use Multi-Model Pattern
```

**Avoid Anti-Patterns:**

- Monolithic Intelligence: Single large AI agent handling everything
- Agent Sprawl: Too many tiny agents without clear responsibilities
- Semantic Drift: Agent learns without monitoring, deviates from goals
- Tight Coupling: Direct dependencies between agents
- No Fallback: No graceful degradation when AI fails

### Step 6: Apply MARA Principles

Ensure transformation aligns with MARA framework principles.

Read `references/mara-principles.md` for complete principle descriptions. Key principles:

**For All Transformations:**

- **Composable & Modular:** Design as independent, composable units
- **Config-Driven:** Make behavior configurable, not hardcoded
- **Unified Observability:** Implement comprehensive logging and monitoring
- **Business Rule Transparency:** Document decision logic clearly
- **80/20 Architecture:** Build reusable patterns, allow local customization

**For Agentic AI Specifically:**

- **AI-by-Default:** Consider AI capabilities from the start
- **Autonomous Agent Orchestration:** Enable agents to coordinate with minimal manual intervention
- **Human-AI Collaboration:** Design for partnership, not replacement
- **Cognitive Data Products:** Agents consume intelligent, self-describing data products
- **Responsible AI:** Ensure explainability, fairness, privacy, security

**Governance Considerations:**

- Model governance (versioning, A/B testing, monitoring)
- Data governance (quality, privacy, access controls)
- Agent governance (registry, behavior monitoring, ethical guidelines)
- Operational governance (deployment standards, incident response)

### Step 7: Assess Risks and Define Mitigations

Identify and mitigate transformation risks.

**Risk Categories:**

**Technical Risks:**

- Model accuracy/reliability
- Performance/latency issues
- Integration complexity
- Data quality problems
- Scalability challenges

**Business Risks:**

- Incorrect decisions impact
- User adoption resistance
- ROI uncertainty
- Regulatory compliance
- Competitive pressure

**Operational Risks:**

- Monitoring/observability gaps
- Incident response capability
- Skills/knowledge gaps
- Vendor dependencies
- Maintenance complexity

**Mitigation Strategies:**

- Human-in-the-Loop for critical decisions
- Confidence thresholds with escalation
- Fallback mechanisms to traditional logic
- Gradual rollout (canary deployments, A/B testing)
- Comprehensive monitoring and alerts
- Circuit breakers for automatic failure isolation
- Shadow mode for parallel validation

### Step 8: Create Transformation Roadmap

Develop a phased implementation roadmap with clear milestones.

**Prioritization Framework:**

For each initiative (agent or DPS service), score:

1. Business Value (1-5): Impact on KPIs
2. Technical Feasibility (1-5): Complexity and readiness
3. Data Readiness (1-5): Data availability/quality
4. Risk Level (1-5, inverse): Lower risk = higher score
5. Dependencies (1-5, inverse): Fewer dependencies = higher score

**Priority Score = (Business Value × 2) + Technical Feasibility + Data Readiness + Risk Level + Dependencies**

**Roadmap Waves:**

- **Wave 1 (0-6 months):** Quick wins, high value, low risk (Score > 20)
- **Wave 2 (6-12 months):** Medium complexity, good value (Score 15-20)
- **Wave 3 (12-18 months):** High complexity or lower value (Score < 15)

**Roadmap Considerations:**

- Infrastructure readiness (AI platform, monitoring)
- Data platform capabilities
- Skills and training needs
- Governance frameworks
- Change management
- Parallel operations during transition
- Migration strategies (Strangler Fig, Parallel Run, Phased Migration)

**Example Roadmap:**

```text
Wave 1 (0-6 months):
- Customer FAQ Chatbot (Score: 27) - High volume, proven patterns, quick win
- Document Classification Agent (Score: 24) - Clear ROI, data available

Wave 2 (6-12 months):
- Order Fulfillment Orchestrator (Score: 18) - Complex but high value
- Data Insight Delivery Agent (Score: 17) - Requires data platform maturity

Wave 3 (12-18 months):
- Legacy System Complete Transformation (Score: 14) - High complexity
- Advanced Personalization Agent (Score: 13) - Requires learning curve
```

## Common Transformation Scenarios

### Scenario 1: Legacy Mainframe Transformation

**Context:** Monolithic mainframe application with stable business logic

**Recommended Path:** Legacy → DPS

- Decompose into microservices using domain-driven design
- Expose capabilities via APIs
- Modernize data access layer
- Implement event-driven communication
- Use Strangler Fig pattern for gradual migration

**Consider AI Enhancement:**

- Add AI for analytics and insights (Decoupled Intelligence)
- Intelligent monitoring and anomaly detection
- Predictive maintenance

### Scenario 2: Customer Service Portal Transformation

**Context:** Web portal with forms and FAQ, high volume of repetitive queries

**Recommended Path:** Legacy → Agentic AI

- Implement customer service chatbot (Embedded Reasoning)
- Natural language interface as primary interaction
- Agent handles common queries autonomously
- Escalates complex issues to humans (Human-in-the-Loop)
- Learns from interactions to improve

**AgentFit Score:** Typically 20-25 (excellent candidate)

- High autonomy potential
- Natural language adds significant value
- Context-aware (customer history, current issue)
- Learning opportunity from user feedback

### Scenario 3: E-commerce Platform Enhancement

**Context:** Modern microservices-based e-commerce platform (DPS), wants personalization

**Recommended Path:** DPS → Embedded AI (Progressive Enhancement)

- Phase 1: Add AI recommendations (Decoupled Intelligence)
- Phase 2: Personalized product discovery agent
- Phase 3: Conversational shopping assistant (Embedded Reasoning)
- Gradual transition with value validation at each phase

**Architecture:** Multi-Model Pattern

- Light model for real-time recommendations
- Heavy model for complex personalization
- Cost optimization through model selection

### Scenario 4: Complex Business Process Automation

**Context:** Multi-step approval workflow with many exceptions and edge cases

**Recommended Path:** Legacy → Agentic AI (Hierarchical Agents)

- Orchestrator agent coordinates overall workflow
- Specialized agents for each approval stage
- Exception handling agent for edge cases
- Human escalation for high-value or uncertain decisions

**Architecture:** Hierarchical Agents + Human-in-the-Loop

- Clear delegation and specialization
- Autonomous operation with human oversight
- Event-driven communication between agents

### Scenario 5: Document Processing System

**Context:** Manual document review and data extraction process

**Recommended Path:** New Agentic AI Implementation

- Document analysis agent (Embedded Reasoning)
- Extracts information using ML/NLP
- Classifies and routes documents
- Validates against business rules
- Escalates ambiguous cases

**AgentFit Score:** Typically 18-23 (good to excellent candidate)

- High decision complexity
- Learning improves accuracy
- Context-aware classification
- Natural language understanding valuable

## Best Practices

### 1. Start with Business Value

Focus on outcomes, not technology. Choose transformation path based on business needs, not AI hype.

### 2. Validate Data Availability Early

AI/ML capabilities depend on quality data. Assess data availability in Step 4 before committing to Agentic AI path.

### 3. Use Progressive Enhancement for Uncertainty

If unsure about AI value, start with DPS and add AI capabilities incrementally. Validate value at each step.

### 4. Always Plan for Failure

Implement fallback mechanisms, confidence thresholds, human escalation, circuit breakers, and monitoring.

### 5. Apply Human-in-the-Loop for High-Risk Decisions

Never let AI make critical decisions without human oversight, especially in early stages.

### 6. Monitor and Iterate

Track technical, business, and AI-specific metrics. Use production data to guide improvements.

### 7. Build Organizational Capability

Invest in skills, training, and change management. Transformation is not just technology.

### 8. Define Clear Agent Boundaries

Avoid agent sprawl and monolithic intelligence. Use AgentFit Framework to define clear responsibilities.

### 9. Version Everything

Models, prompts, configurations, APIs - version control and track changes.

### 10. Implement Comprehensive Observability

Logging, monitoring, tracing, explainability from day one. Cannot improve what you cannot measure.

## Success Metrics

### Technical Metrics

- System availability (target: 99.9%+)
- Response time (DPS: <500ms, Agents: <2s)
- Error rates (target: <0.1%)
- Model accuracy (domain-specific targets)

### Business Metrics

- User satisfaction (NPS target: >70)
- Time to market reduction (target: 50%+)
- Operational cost reduction (target: 30%+)
- Task completion rate

### AI-Specific Metrics (for Agentic AI)

- Agent task success rate (target: >85%)
- User intent recognition accuracy
- Human escalation rate (target: <15%)
- Learning curve improvement (month-over-month)
- Automation percentage
- Responsible AI compliance (100%)

## Resources

This skill includes comprehensive reference documentation:

### references/transformation-decision-framework.md

Complete framework for choosing transformation paths (Legacy → DPS, Legacy → Agentic AI, DPS → Embedded AI, DPS → Agentic AI).
Includes decision criteria matrix, evaluation process, anti-patterns, success metrics, and migration strategies.

**When to reference:** Step 3 (Choose Transformation Path) or when comparing DPS vs Agentic AI approaches.

### references/agentfit-framework.md

Detailed 8-step process for identifying and evaluating AI agent candidates.
Includes scoring framework, capability definition templates, data assessment checklist, prioritization framework, and example scorecards.

**When to reference:** Step 4 (Identify AI Agent Candidates) or when systematically evaluating business capabilities for agent suitability.

### references/architecture-patterns.md

Comprehensive catalog of AI architecture patterns including Decoupled Intelligence, Embedded Reasoning, Progressive Enhancement, Hierarchical Agents, Human-in-the-Loop, Multi-Model, and more.
Includes pattern selection decision tree, anti-patterns, and implementation best practices.

**When to reference:** Step 5 (Select Architecture Patterns) or when designing agent/DPS architecture.

### references/mara-principles.md

Summary of MARA framework principles including Global Platform Design Principles, AI-specific principles, pattern guardrails, and governance considerations.
Shows how principles apply to transformation decisions.

**When to reference:** Step 6 (Apply MARA Principles) or when validating transformation approach against framework standards.

## Common Questions

**Q: How do I know if my application is a good candidate for Agentic AI?**
A: Use the AgentFit Framework (Step 4). Score candidates on autonomy, decision complexity, natural language value, context awareness, and learning opportunity.
Scores above 20/25 are excellent candidates. Also validate data availability and organizational readiness.

**Q: What if I'm not sure whether to choose DPS or Agentic AI?**
A: Use Progressive Enhancement pattern (Step 5). Start with DPS foundation, add AI capabilities incrementally (advisory AI → embedded AI → agentic AI), and validate value at each phase.
This minimizes risk and allows course correction.

**Q: How do I handle the risk of AI making wrong decisions?**
A: Implement multiple mitigation strategies (Step 7): Human-in-the-Loop for critical decisions, confidence thresholds with escalation, fallback mechanisms, gradual rollout with A/B testing,
comprehensive monitoring, and circuit breakers.

**Q: Should I build one large agent or many small agents?**
A: Avoid both extremes (anti-patterns in Step 5). Use Hierarchical Agents pattern with clear specialization and delegation.
Define agent boundaries using domain-driven design and the AgentFit Framework.

**Q: What metrics should I track after transformation?**
A: Track three categories (Step 2):Technical metrics (availability, latency, errors), Business metrics (user satisfaction, time to market, cost
reduction), and AI-specific metrics (task success rate, escalation rate, learning improvement).
Define targets before transformation.

**Q: How long should transformation take?**
A: Use phased approach (Step 8). Wave 1 (quick wins): 0-6 months, Wave 2 (medium complexity): 6-12 months, Wave 3 (high complexity): 12-18 months. Avoid big bang transformations.
Deliver incremental value.

**Q: What if my data quality is poor?**
A: Address data quality before pursuing Agentic AI path (Step 4).
Options: Improve data quality first (recommended), start with DPS and enhance later,
use hybrid approach where AI handles only high-quality data scenarios, or choose traditional DPS path.

**Q: How do I get stakeholder buy-in for Agentic AI?**
A: Focus on business outcomes not technology (Step 2).
Start with pilot/POC to demonstrate value. Use Progressive Enhancement to show incremental benefits.
Implement Human-in-the-Loop to build trust. Track and communicate metrics. Share success stories.
