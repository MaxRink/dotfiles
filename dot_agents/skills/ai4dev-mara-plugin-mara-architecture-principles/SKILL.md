---
name: ai4dev-mara-plugin-mara-architecture-principles
description: Comprehensive guide for applying MARA (Magenta AI-Centric Reference Architecture) principles to architecture design, evaluation, and decision-making. This skill should be used when designing AI-first platforms, evaluating existing architectures against MARA standards, making architecture decisions for Deutsche Telekom projects, identifying patterns and anti-patterns in AI systems, or reviewing architecture proposals for MARA compliance.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/mara-plugin/skills/mara-architecture-principles by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# MARA Architecture Principles

## Overview

This skill provides comprehensive guidance on applying MARA (Magenta AI-Centric Reference Architecture) principles to design, evaluate, and improve AI-first architectures at Deutsche Telekom.
The skill enables architectural decision-making aligned with the 13 Global Platform Design Principles, AI architecture patterns, and best practices for AI-centric systems.

## When to Use This Skill

Apply this skill when:

1. **Designing new platforms or services** - Use MARA principles as the primary architectural guide
2. **Evaluating existing architectures** - Assess alignment with MARA standards and identify gaps
3. **Making architecture decisions** - Consider trade-offs and ensure decisions align with MARA principles
4. **Identifying patterns and anti-patterns** - Recognize proven solutions and common pitfalls
5. **Reviewing architecture proposals** - Validate compliance with MARA standards
6. **Planning migrations or transformations** - Apply transition principles for incremental improvements

## Core Capabilities

### 1. Architecture Design Guidance

When designing new architectures or components:

**Apply the 13 Global Platform Design Principles:**

1. 80/20 Architecture - Balance standardization with local extensibility
2. Composable & Modular - Design for microservices and independent delivery
3. Canary & Feature Flag Support - Enable safe, incremental rollouts
4. Config-Driven Localization - Use declarative configs for local variations
5. Policy-as-Code & Compliance Adapters - Automate compliance enforcement
6. Unified Observability - Implement shared monitoring and diagnostics
7. Self-Service Enablement - Provide no-code/low-code interfaces for teams
8. Federated Security Model - Implement zero-trust with federated IdP
9. AI-by-Default - Embed AI capabilities in platform APIs
10. Business Rule Transparency - Maintain machine-readable business logic
11. Marketplace for Reuse - Build for component sharing and reuse
12. Data Sharing - Implement data mesh principles with standardized interfaces
13. Continuous Learning for Adapting - Enable feedback-driven improvements

**Process:**

1. Start by identifying which principles are most relevant to the design problem
2. Reference `references/global-platform-design-principles.md` for detailed implementation guidance
3. For each principle, consider: Problem it solves, Solution approach, Rationale, How to implement
4. Document architectural decisions with explicit reference to supporting principles
5. Consider principle interactions and potential trade-offs

### 2. Architecture Evaluation

When evaluating existing architectures against MARA:

**Evaluation Framework:**

1. **Principle Alignment Assessment**
   - Review each of the 13 principles
   - Rate alignment: Compliant / Partial / Non-Compliant / Not Applicable
   - Document gaps and violations
   - Prioritize improvements by business impact

2. **Pattern Recognition**
   - Identify implemented patterns (see `references/ai-patterns-antipatterns.md`)
   - Detect anti-patterns and technical debt
   - Assess pattern effectiveness and maturity

3. **Metrics Analysis**
   - Compare against MARA success metrics:
     - Platforms per capability (target: 1-2 vs 5-10)
     - Time to market (target: 4-8 weeks vs 6-12 months)
     - AI-enabled platforms (target: >70% vs <10%)
     - IT cost reduction (target: -30%)
     - Developer productivity (target: +50%)

4. **Recommendations**
   - Prioritize improvements by impact and feasibility
   - Suggest specific patterns to adopt
   - Identify anti-patterns to remediate
   - Provide implementation roadmap

### 3. Pattern Application

When implementing AI capabilities or system components:

**Using AI Architecture Patterns:**

Consult `references/ai-patterns-antipatterns.md` for detailed pattern descriptions. Key patterns include:

**Tooling Patterns:**

- Knowledge Hub - AI for architecture work

**Optimisation Patterns:**

- Multi-Model Pattern - Choose models based on task requirements
- Model-in-the-Loop Pattern - Modular AI components

**Responsible AI Patterns:**

- Human-in-the-Loop - Human oversight for critical decisions

**Intuitive Learning Patterns:**

- Ensemble Pattern - Combine models for improved accuracy
- Feedback Loop Pattern - Continuous learning from user feedback

**Application Patterns:**

- DPS vs Agentic AI - Decision framework for architecture selection

**Data Patterns:**

- Data Access Pattern - API-based data access with local caching

**Agent Patterns:**

- Hierarchical Agents - Scalable decision-making architecture
- Federated Learning - Privacy-preserving collaborative learning

**Pattern Selection Process:**

1. Identify the architectural challenge or requirement
2. Review relevant pattern categories
3. Match patterns to specific needs considering:
   - Business impact (High/Medium/Low)
   - Technical challenge (High/Medium/Low)
   - Alignment with MARA principles
   - Available reference implementations
4. Consider pattern combinations and interactions
5. Document pattern selection rationale

### 4. Anti-Pattern Detection

Actively identify and remediate anti-patterns:

**Common Anti-Patterns:**

**Agent Anti-Patterns:**

- **Monolithic Intelligence** - Single monolithic agent or distributed monolith
  - Violation: Composable & Modular principle
  - Remediation: Decompose into bounded, focused agents

- **Agent Sprawl** - Many tiny agents with unclear responsibilities
  - Impact: Operational complexity, coordination overhead
  - Remediation: Consolidate, define clear boundaries, use hierarchical patterns

- **Semantic Drift Agent** - Agent learns without monitoring, deviates from goals
  - Violation: Unified Observability, Continuous Learning principles
  - Remediation: Implement monitoring, feedback loops, versioning

**Data Anti-Patterns:**

- **Data Lake Fallacy** - Collecting data without quality standards
  - Violation: Data Sharing principle
  - Remediation: Implement data governance, quality standards, mesh principles

**Detection Process:**

1. Review architecture for anti-pattern indicators
2. Assess impact and risk
3. Document violations with evidence
4. Prioritize remediation by risk and business impact
5. Suggest specific remediation approaches aligned with MARA patterns

### 5. Decision-Making Support

When making architectural trade-offs and decisions:

**Decision Framework:**

1. **Principle Considerations**
   - Which MARA principles apply to this decision?
   - Are there conflicts between principles?
   - What trade-offs are involved?

2. **Pattern Guidance**
   - Do existing patterns address this problem?
   - What have similar implementations chosen?
   - Are there known anti-patterns to avoid?

3. **Impact Assessment**
   - Business impact (time to market, cost, scalability)
   - Technical impact (complexity, maintainability, performance)
   - Organizational impact (team structure, skills, processes)

4. **Documentation**
   - Document the decision and rationale
   - Reference specific principles and patterns
   - Explain trade-offs and alternatives considered
   - Define success criteria and metrics

**Common Decision Scenarios:**

- **Monolithic vs Microservices:** Apply Composable & Modular principle
- **Centralized vs Federated:** Consider 80/20 Architecture, Federated Security
- **Build vs Reuse:** Consult Marketplace for Reuse principle
- **AI Model Selection:** Use Multi-Model Pattern, AI-by-Default principle
- **Data Architecture:** Apply Data Sharing principle, Data Mesh concepts
- **Deployment Strategy:** Reference Canary & Feature Flag Support principle

### 6. Architecture Review

When reviewing architecture proposals or designs:

**Review Checklist:**

1. **Principle Compliance**
   - [ ] Design references relevant MARA principles
   - [ ] Principle application is correctly understood
   - [ ] Trade-offs are explicitly documented
   - [ ] Deviations are justified with rationale

2. **Pattern Usage**
   - [ ] Appropriate patterns are identified and applied
   - [ ] Anti-patterns are avoided or mitigated
   - [ ] Pattern combinations are coherent
   - [ ] Reference implementations are considered

3. **AI-First Design**
   - [ ] AI capabilities are embedded (not bolted on)
   - [ ] AI-by-Default principle is followed
   - [ ] Model lifecycle management is addressed
   - [ ] Human-in-the-Loop where appropriate

4. **Scalability & Flexibility**
   - [ ] 80/20 split for standardization vs extensibility
   - [ ] Config-driven localization approach
   - [ ] Composable, modular architecture
   - [ ] Clear domain boundaries

5. **Operations & Governance**
   - [ ] Unified observability strategy
   - [ ] Policy-as-code for compliance
   - [ ] Canary deployment support
   - [ ] Continuous learning mechanisms

6. **Data & Integration**
   - [ ] Data mesh principles applied
   - [ ] Standardized interfaces (MAPIs)
   - [ ] Clear data ownership
   - [ ] Federation where appropriate

**Review Process:**

1. Understand the architectural context and requirements
2. Apply the review checklist systematically
3. Identify strengths and alignment with MARA
4. Highlight gaps, violations, or risks
5. Provide specific, actionable recommendations
6. Prioritize feedback by impact
7. Suggest patterns or principles to address issues

## Reference Materials

This skill includes comprehensive reference documentation:

### references/mara-framework-overview.md

Overview of the MARA framework including:

- Framework structure and philosophy
- Core concepts (AI-first, composability, platform economy)
- Success metrics and expected outcomes
- Application areas and relationship to other frameworks
- Common questions and getting started guidance

**When to reference:** For general understanding of MARA, explaining the framework to others, or understanding how MARA relates to other architectural approaches.

### references/global-platform-design-principles.md

Complete details on all 13 Global Platform Design Principles:

- Problem each principle addresses
- Solution approach
- Rationale and benefits
- Concrete implementation guidance
- Expected outcomes and metrics

**When to reference:** During architecture design, when making decisions that involve specific principles, or when evaluating architecture against MARA standards.

### references/ai-patterns-antipatterns.md

Comprehensive catalog of AI architecture patterns and anti-patterns:

- Pattern categories (Tooling, Optimisation, Responsible AI, etc.)
- Detailed pattern descriptions with business impact and technical complexity
- Anti-patterns with remediation guidance
- Pattern selection guidelines
- Implementation considerations

**When to reference:** When designing AI capabilities, identifying reusable solutions, detecting architectural problems, or selecting appropriate architectural approaches for AI systems.

## Working with MARA Principles

### Principle Prioritization

Not all principles apply equally to every project. Prioritize based on:

1. **Project Scope and Phase**
   - Early stage: Focus on foundational principles (Composable & Modular, AI-by-Default)
   - Scaling phase: Emphasize 80/20 Architecture, Config-Driven Localization
   - Mature systems: Prioritize Continuous Learning, Marketplace for Reuse

2. **Domain and Context**
   - Customer-facing: Self-Service Enablement, Canary & Feature Flags
   - Data-intensive: Data Sharing, Cognitive Data Products
   - Compliance-critical: Policy-as-Code, Federated Security

3. **Business Priorities**
   - Time to market: Marketplace for Reuse, Composable & Modular
   - Cost reduction: 80/20 Architecture, Unified Observability
   - Innovation: AI-by-Default, Continuous Learning

### Handling Principle Conflicts

When principles appear to conflict:

1. **Document the Trade-off**
   - Clearly state which principles are in tension
   - Explain the specific context causing the conflict
   - Describe the implications of each option

2. **Seek Balance**
   - Look for solutions that partially satisfy both principles
   - Consider phased approaches (satisfy one principle now, the other later)
   - Explore creative architectural patterns

3. **Prioritize by Impact**
   - Assess business and technical impact of each option
   - Consider strategic alignment and long-term implications
   - Choose based on explicit criteria, not arbitrary preference

4. **Get Input**
   - Consult with architecture team and stakeholders
   - Review reference implementations facing similar conflicts
   - Document the decision and rationale

### Incremental Adoption

For existing systems that violate MARA principles:

1. **Assess Current State**
   - Document principle violations and gaps
   - Understand root causes and constraints
   - Identify quick wins and major refactoring needs

2. **Prioritize Improvements**
   - High impact, low effort: Implement immediately
   - High impact, high effort: Plan carefully, phase the work
   - Low impact: Defer or accept as technical debt

3. **Define Migration Path**
   - Create incremental steps toward MARA compliance
   - Ensure each step delivers value
   - Maintain system stability throughout transition

4. **Measure Progress**
   - Track MARA alignment metrics over time
   - Celebrate improvements and learn from setbacks
   - Adjust approach based on feedback

## Communication and Documentation

### Explaining MARA to Others

When communicating MARA principles:

1. **Start with Context**
   - Explain the business drivers (efficiency, time to market, AI transformation)
   - Connect to Deutsche Telekom's strategic goals
   - Highlight expected outcomes (see metrics in references)

2. **Use Concrete Examples**
   - Reference real implementations within Deutsche Telekom
   - Show before/after scenarios
   - Demonstrate measurable improvements

3. **Focus on Benefits**
   - Reduce duplication and operational costs
   - Accelerate delivery and innovation
   - Improve quality and consistency

4. **Address Concerns**
   - Acknowledge transition challenges
   - Emphasize incremental adoption approach
   - Provide support and resources

### Documenting Architectural Decisions

When documenting architecture with MARA:

1. **Reference Principles Explicitly**
   - State which principles guided the decision
   - Explain how the design satisfies each principle
   - Note any principles that don't apply and why

2. **Identify Patterns**
   - Name the patterns used
   - Link to pattern documentation
   - Explain why these patterns fit the context

3. **Acknowledge Trade-offs**
   - Be transparent about limitations and compromises
   - Explain why certain principles were prioritized
   - Document alternatives considered

4. **Define Success Criteria**
   - Specify measurable outcomes
   - Align with MARA metrics where applicable
   - Establish monitoring and review process

## Tips for Effective Use

1. **Keep Learning:** MARA is a living framework. Stay updated on new patterns and reference implementations.

2. **Be Pragmatic:** Principles are guides, not absolute rules. Context matters.

3. **Collaborate:** Engage with the MARA community. Share learnings and patterns.

4. **Measure Impact:** Track how MARA adoption affects key metrics (time to market, costs, quality).

5. **Iterate:** Start with core principles, expand adoption gradually, refine based on feedback.

6. **Document:** Record decisions, patterns, and learnings to help others.

7. **Balance:** Don't over-engineer. Apply principles proportionally to system complexity and business impact.

## Getting Help

- **MARA Wiki:** <https://wiki.telekom.de/spaces/EIAD/pages/3389124369>
- **Community Meetings:** Weekly discussions (Wed 1pm CEST)
- **Pattern Repository:** Internal marketplace for reference implementations
- **Architecture Team:** Reach out for specific guidance and reviews
