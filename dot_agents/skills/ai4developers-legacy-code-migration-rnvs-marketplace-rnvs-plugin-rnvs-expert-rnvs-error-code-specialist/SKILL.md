---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-rnvs-error-code-specialist
description: This skill should be used when the user asks general RNVS error code questions, needs to "identify which specialized skill to use", asks about "error code organization", or mentions error code prefixes without specific context (ECRM, PFM, WFA, WFB, WFC, RNBFM, AFM, A1P, BFM, BHM, KFM, VFM, LWL). Router skill for 2000+ RNVS internal error codes organized across 4 specialized domain skills - CRM integration (226 codes), porting workflows (170+ codes), number assignment (230+ codes), and booking/distribution (135+ codes).
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/rnvs-error-code-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# RNVS Error Code Specialist Skill (Router)

## Purpose

This skill serves as a **router and overview** for **2000+ RNVS internal error codes** organized across **4 specialized domain skills**. Use this skill to understand the RNVS error code architecture and determine which specialized skill to use for your specific problem.

## Specialized Skills by Domain

RNVS error codes have been organized into 4 domain-specific skills for better focus and usability:

### 1. **crm-integration-error-specialist** (226 codes)
**Domain:** CRM Portal integration and customer-facing operations
- **ECRM** (ECRMP/ERESP) - 226 codes
- **Use when:** Debugging CRM portal failures, number booking issues, callnumber availability, ownership conflicts, process locking (ECRMP080), porting collisions

**Common Error Prefixes:** `ECRMP`, `ERESP`

**Example Errors:**
- ECRMP001 - No free callnumber available
- ECRMP005 - Callnumber already occupied
- ECRMP080 - Process lock conflict
- ECRMP043/044 - Porting message exists

### 2. **porting-workflow-error-specialist** (170+ codes)
**Domain:** Porting workflows and carrier coordination
- **PFM** (37 codes) - Porting flow messages
- **WFA** (20 codes) - Workflow A (carrier actions)
- **WFB** (10-20 codes) - Workflow B (intermediate coordination)
- **WFC** (50+ codes) - Workflow C (advanced coordination)
- **RNBFM** (39 codes) - RNB file message validation
- **RNPS** (10-15 codes) - RNB process status tracking
- **Use when:** Debugging porting workflows, carrier coordination, RNB file validation, U-Teil/K-Teil structure, AT timing rules, TNB communication

**Common Error Prefixes:** `PFM`, `WFA`, `WFB`, `WFC`, `RNBFM`, `RNPS`

**Example Errors:**
- PFM001 - Competitor missing for T-Com message
- PFM004 - DTAG export missing
- RNBFM021 - Less than 20 AT between dates
- WFA0137 - U-Teil not completely filled

### 3. **number-assignment-error-specialist** (230+ codes)
**Domain:** Number assignment and allocation workflows
- **AFM** (129 codes) - KONTES assignment flows
- **A1P** (50+ codes) - Assignment Phase 1 (allocation)
- **A2R** (15-20 codes) - Assignment Phase 2 (reservation)
- **A3R** (5-10 codes) - Assignment Phase 3 (release)
- **AHM** (15-20 codes) - Assignment history management
- **AKFM** (15-20 codes) - Assignment correction flows
- **Use when:** Debugging KONTES workflows, assignment operations, Kontingent management, allocation conflicts, portability validation (AFM130)

**Common Error Prefixes:** `AFM`, `A1P`, `A2R`, `A3R`, `AHM`, `AKFM`

**Example Errors:**
- AFM130 - Porting with Level = U3 exists
- AFM289 - Kontingent incompletely ported
- AFM261 - Number has Besitzer Telekom

### 4. **booking-distribution-error-specialist** (135+ codes)
**Domain:** Booking operations, customer flows, and distribution
- **BFM/BHM** (100+ codes) - Booking flows & history
- **KFM** (15-20 codes) - Customer flow messages
- **VFM** (15-20 codes) - Distribution flow messages
- **LWL** (5-10 codes) - Fiber optic integration
- **Use when:** Debugging booking workflows, customer operations, distribution logic, TK-Anlage (PBX) integration, Stornierung (cancellation), fiber optic coordination

**Common Error Prefixes:** `BFM`, `BHM`, `KFM`, `VFM`, `LWL`

**Example Errors:**
- BFM005 - Number not available for booking
- BFM071 - Cancellation not allowed
- BFM035 - TK-Anlage rule violation
- LWL001 - Fiber connection not available

## Quick Decision Guide

**"I have an error code, which skill should I use?"**

| Error Code Prefix | Use This Skill |
|------------------|----------------|
| ECRMP, ERESP | crm-integration-error-specialist |
| PFM, WFA, WFB, WFC, RNBFM, RNPS | porting-workflow-error-specialist |
| AFM, A1P, A2R, A3R, AHM, AKFM | number-assignment-error-specialist |
| BFM, BHM, KFM, VFM, LWL | booking-distribution-error-specialist |

**"I have a problem, which skill should I use?"**

| Problem Domain | Use This Skill |
|----------------|----------------|
| CRM portal failures, number booking, availability checks | crm-integration-error-specialist |
| Porting workflows, carrier coordination, RNB files, PDA messages | porting-workflow-error-specialist |
| KONTES integration, assignment lifecycle, Kontingent management | number-assignment-error-specialist |
| Booking operations, customer workflows, distribution, TK-Anlage | booking-distribution-error-specialist |

## RNVS vs PDA Error Codes

**RNVS Codes (this skill family):**
- **Purpose:** Internal system validation and workflow
- **Scope:** 17 modules, 2000+ codes
- **Format:** PREFIX + NUMBER (e.g., ECRMP045, AFM130, RNBFM021)
- **Location:** PL/SQL packages (pack_crm.sql, pack_val.sql, pack_body_*.sql)

**PDA Codes (porting-data-exchange-specialist skill):**
- **Purpose:** External TNB communication
- **Scope:** 72 codes
- **Format:** 4-digit (0000-6200), 2-digit (20-61, 00/25/26, 01-05)
- **Location:** pack_body_generator.sql, pack_body_pm.sql, pack_body_rfnr.sql

## Error Code Architecture

### Module Organization

**By Business Process:**
```
CRM Integration
├── ECRM (CRM portal validation)

Porting Workflows
├── PFM (porting flow messages)
├── WFA/WFB/WFC (carrier coordination)
├── RNBFM (RNB file messages)
└── RNPS (RNB process status)

Number Assignment
├── AFM (KONTES assignment)
├── A1P/A2R/A3R (assignment phases)
├── AHM (assignment history)
└── AKFM (assignment correction)

Booking & Distribution
├── BFM/BHM (booking flows & history)
├── KFM (customer flows)
├── VFM (distribution flows)
└── LWL (fiber optic)
```

### Code Structure Pattern

```
[PREFIX][NUMBER]
├── PREFIX: 2-6 characters (module identifier)
└── NUMBER: 1-4 digits (error sequence)

Examples:
- ECRMP045  → CRM Portal error #45
- PFM030    → Porting flow error #30
- AFM130    → Assignment flow error #130
- RNBFM021  → RNB file message error #21
- BFM071    → Booking flow error #71
```

## When to Use This Skill vs Specialized Skills

**Use this skill (rnvs-error-code-specialist) when:**
- You need to identify which specialized skill to use
- You want a high-level overview of all RNVS error codes
- You're comparing error codes across different modules
- You need general RNVS error code architecture information

**Use a specialized skill when:**
- You have a specific error code to debug (use the appropriate domain skill)
- You're working on a specific domain (CRM, porting, assignment, booking)
- You need detailed implementation locations and debugging scenarios
- You need domain-specific validation rules and business logic

## Integration with Other VNRM Skills

- **porting-data-exchange-specialist** - External PDA codes (0000-6200, 20-61, etc.)
- **german-glossary** - Translate German error descriptions
- **vnrm-prt-architecture** - Map porting errors to VNRM PRT microservices
- **vnrm-num-architecture** - Map number management errors to VNRM NUM microservices
- **multi-language-code-analyzer** - Discover error code usage in legacy codebase

## Migration Planning

### Mapping RNVS Errors to VNRM Microservices

**CRM Integration (ECRM) → VNRM Services:**
- Availability checks → NUM microservice
- Booking operations → COR microservice
- Porting collisions → PRT microservice

**Porting Workflows (PFM/WFA/RNBFM) → VNRM Services:**
- Message pairing → PRT microservice
- RNB operations → NUM microservice
- Carrier coordination → PRT microservice

**Assignment (AFM/A1P-A3R) → VNRM Services:**
- KONTES integration → NUM microservice
- Assignment lifecycle → COR microservice
- Portability checks → PRT microservice

**Booking (BFM/KFM/VFM) → VNRM Services:**
- Booking workflows → COR microservice
- Customer flows → CRM integration layer
- Distribution logic → NUM microservice

## Best Practices

1. **Identify Error Domain First** - Use prefix to determine which specialized skill to consult
2. **Use Specialized Skills** - Go directly to domain-specific skill for detailed debugging
3. **Cross-Module Errors** - Some errors span multiple domains (e.g., AFM130 involves both assignment and porting)
4. **PDA vs RNVS** - Distinguish external PDA codes from internal RNVS codes
5. **German Translation** - Use german-glossary for error message translation
6. **Module Context** - Understand which PL/SQL package owns the error code
7. **Validation Sequence** - Errors often cascade (fix earlier validation before later stages)
8. **Historical Context** - Many codes enforce legacy business rules required for migration

## Common Cross-Domain Scenarios

**Scenario 1: Porting + Assignment Conflict**
- **Error**: AFM130 (number-assignment-error-specialist)
- **Related**: PFM codes (porting-workflow-error-specialist)
- **Resolution**: Coordinate between assignment and porting workflows

**Scenario 2: CRM Portal + Porting**
- **Error**: ECRMP043/044 (crm-integration-error-specialist)
- **Related**: PFM/WFA codes (porting-workflow-error-specialist)
- **Resolution**: Check porting status before allowing booking

**Scenario 3: Booking + Assignment**
- **Error**: BFM005 (booking-distribution-error-specialist)
- **Related**: AFM codes (number-assignment-error-specialist)
- **Resolution**: Verify assignment status before booking

## Progressive Disclosure

**This Skill (Overview):**
- High-level architecture
- Skill routing guide
- Module organization

**Specialized Skills (Detailed):**
- **[crm-integration-error-specialist](../crm-integration-error-specialist/SKILL.md)** - ECRM codes and CRM portal validation
- **[porting-workflow-error-specialist](../porting-workflow-error-specialist/SKILL.md)** - PFM/WFA/RNBFM codes and porting workflows
- **[number-assignment-error-specialist](../number-assignment-error-specialist/SKILL.md)** - AFM/A1P-A3R codes and assignment lifecycle
- **[booking-distribution-error-specialist](../booking-distribution-error-specialist/SKILL.md)** - BFM/KFM/VFM codes and booking operations

**Reference Files:**
- Each specialized skill contains detailed reference files in their `references/` subdirectories
- Complete code tables with implementation locations
- Domain-specific validation rules and business logic

## Key External References

- **RNVS Architecture** - Legacy system architecture documentation
- **Module Integration Specifications** - CRM-T, KONTES, WSSt integration guides
- **BNetzA Regulations** - Federal Network Agency compliance rules
- **AT Calculation Rules** - German working day (Arbeitstage) calculation logic

---

**For detailed error code information, consult the appropriate specialized skill:**
- **CRM/Portal errors** → crm-integration-error-specialist
- **Porting/Carrier errors** → porting-workflow-error-specialist
- **Assignment/KONTES errors** → number-assignment-error-specialist
- **Booking/Distribution errors** → booking-distribution-error-specialist
