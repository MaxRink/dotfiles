---
name: ai4dev-telekom-archi-migration-planning
description: >
  Plan and execute architecture migrations — monolith to microservices, on-prem to cloud, legacy
  modernization, database migrations, and technology stack upgrades. Use this skill when the user
  asks about migration planning, modernization strategy, strangler fig pattern, lift-and-shift,
  re-platforming, refactoring legacy systems, or creating migration roadmaps. Also trigger for
  "how do I break up this monolith", "move to the cloud", "migrate from X to Y",
  "modernize this system", or any request to plan a phased transition between architectures.
argument-hint: "[source system] to [target system]"
allowed-tools: Read, Glob, Grep, Write
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telekom-archi/skills/migration-planning by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Migration Planning Skill

You help users plan safe, incremental migrations between architectures. The cardinal rule: never do a big bang rewrite. Migrations succeed through small, reversible steps with continuous delivery of value.

## Migration Strategies (The 7 Rs)

| Strategy | Description | When to Use | Risk | Effort |
|----------|-------------|-------------|------|--------|
| **Rehost** (Lift & Shift) | Move as-is to cloud | Quick win, minimal changes needed | Low | Low |
| **Replatform** (Lift & Reshape) | Minor optimizations during move | Database upgrade, managed services | Low | Medium |
| **Refactor** | Re-architect for cloud-native | Performance, scalability needs | Medium | High |
| **Repurchase** | Replace with SaaS/COTS | Commodity functionality (CRM, HR) | Medium | Medium |
| **Retire** | Decommission | No longer needed | Low | Low |
| **Retain** | Keep as-is | Too risky/costly to move now | Low | None |
| **Relocate** | Move to different cloud region/provider | Compliance, latency, cost | Low | Medium |

## Monolith to Microservices

### Strangler Fig Pattern

The safest approach — gradually replace monolith functionality with new services:

```mermaid
graph LR
  subgraph Phase1["Phase 1: Facade"]
    Client1[Client] --> Proxy1[API Proxy]
    Proxy1 --> Mono1[Monolith<br/>100% traffic]
  end

  subgraph Phase2["Phase 2: Extract"]
    Client2[Client] --> Proxy2[API Gateway]
    Proxy2 -->|Orders| NewSvc[Order Service]
    Proxy2 -->|Everything else| Mono2[Monolith<br/>80% traffic]
    NewSvc --> NewDB[(New DB)]
    NewSvc -.->|Sync| Mono2
  end

  subgraph Phase3["Phase 3: Expand"]
    Client3[Client] --> Proxy3[API Gateway]
    Proxy3 -->|Orders| Svc1[Order Service]
    Proxy3 -->|Payments| Svc2[Payment Service]
    Proxy3 -->|Catalog| Svc3[Catalog Service]
    Proxy3 -->|Auth,Legacy| Mono3[Monolith<br/>30% traffic]
  end

  subgraph Phase4["Phase 4: Complete"]
    Client4[Client] --> GW[API Gateway]
    GW --> MS1[Order Svc]
    GW --> MS2[Payment Svc]
    GW --> MS3[Catalog Svc]
    GW --> MS4[User Svc]
    GW --> MS5[Auth Svc]
  end

  style Mono1 fill:#ff6666,color:#fff
  style Mono2 fill:#ff9966,color:#fff
  style Mono3 fill:#ffcc66
  style Phase4 fill:#ccffcc
```

### Decomposition Strategy

**Step 1: Identify Bounded Contexts**
```mermaid
graph TD
  subgraph Monolith["Current Monolith"]
    Orders[Order Management]
    Payments[Payment Processing]
    Catalog[Product Catalog]
    Users[User Management]
    Notify[Notifications]
    Reports[Reporting]
  end

  Orders ---|High coupling| Payments
  Orders ---|Medium coupling| Catalog
  Orders ---|Low coupling| Users
  Payments ---|Low coupling| Notify
  Reports ---|Read-only| Orders
  Reports ---|Read-only| Payments

  style Orders fill:#ff9900
  style Payments fill:#ff9900
  style Catalog fill:#4CAF50
  style Users fill:#2196F3
  style Notify fill:#9C27B0
  style Reports fill:#607D8B
```

**Step 2: Prioritize extraction** by:
1. Business value of independent deployment
2. Team ownership clarity
3. Coupling level (extract loosely-coupled first)
4. Technical risk

**Step 3: Extract one service at a time:**
1. Create the new service with its own database
2. Implement the Anti-Corruption Layer (ACL) between old and new
3. Dual-write or CDC to sync data during transition
4. Route traffic gradually (canary/feature flags)
5. Validate, then cut over
6. Remove old code from monolith

### Data Migration Strategy

```mermaid
stateDiagram-v2
  [*] --> DualWrite: Start migration
  DualWrite --> Verify: Run consistency checks
  Verify --> Cutover: Data matches
  Verify --> DualWrite: Discrepancies found
  Cutover --> Cleanup: All traffic on new DB
  Cleanup --> [*]: Remove old schema

  state DualWrite {
    [*] --> WriteOldAndNew
    WriteOldAndNew --> SyncBackfill
    SyncBackfill --> ReadFromNew
  }

  note right of DualWrite: Both DBs receive writes
  note right of Cutover: Feature flag switches reads
```

## Cloud Migration

### Migration Roadmap (Timeline)

```mermaid
timeline
  title Cloud Migration Roadmap
  section Phase 0 - Assessment (Month 1-2)
    Inventory : Application discovery
              : Dependency mapping
              : Cost baseline
  section Phase 1 - Foundation (Month 3-4)
    Landing Zone : VPC and networking
                 : IAM and security baseline
                 : CI/CD pipeline setup
  section Phase 2 - Quick Wins (Month 5-7)
    Lift and Shift : Stateless web servers
                   : Static assets to CDN/S3
                   : DNS cutover
  section Phase 3 - Modernize (Month 8-12)
    Replatform : Database to managed (RDS)
               : Containers (EKS)
               : Event-driven refactoring
  section Phase 4 - Optimize (Month 13+)
    Cloud Native : Auto-scaling
                 : Serverless where appropriate
                 : Cost optimization
```

### Migration Risk Checklist

- [ ] Rollback plan for every migration step
- [ ] Data backup verified and tested
- [ ] Performance baseline established (before vs after)
- [ ] Network latency between cloud and on-prem measured
- [ ] DNS TTL lowered before cutover
- [ ] Feature flags for gradual traffic shifting
- [ ] Monitoring and alerting in place for new environment
- [ ] Team trained on new platform
- [ ] Compliance review completed
- [ ] Cost projections validated

## Technology Stack Migration

For framework/language migrations (e.g., Java 8 to 17, Angular to React):

1. **Assess** — Inventory all affected components, estimate effort
2. **Isolate** — Create adapter/facade around the component being migrated
3. **Implement** — Build new version behind the facade
4. **Test** — Run old and new in parallel, compare results
5. **Switch** — Gradual traffic shift
6. **Cleanup** — Remove old implementation and facade

## Output Format

Produce:
1. **Current state diagram** (C4 Context or Container)
2. **Target state diagram** (C4 Context or Container)
3. **Migration roadmap** (Mermaid timeline)
4. **Phase breakdown** with deliverables and risks per phase
5. **Strangler fig / decomposition plan** (Mermaid flowchart)
6. **Risk checklist**

Save to `docs/architecture/migration-plan.md`.
