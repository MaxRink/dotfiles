---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-booking-distribution-error-specialist
description: This skill should be used when the user asks to "debug booking workflows", "resolve BFM errors", "understand Stornierung rules", "fix customer flow issues", "resolve distribution errors", or mentions booking codes (BFM, BHM, KFM, VFM, LWL). Provides expert knowledge of 135+ RNVS booking and distribution error codes covering number booking workflows, customer flow validation, distribution operations, booking history management, cancellation (Stornierung) rules, TK-Anlage (PBX) integration, and fiber optic (Lichtwellenleiter) network coordination.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/booking-distribution-error-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Booking & Distribution Error Code Specialist Skill

## Purpose

Provides **expert-level knowledge** of **135+ RNVS booking and distribution error codes** that govern number booking operations, customer-specific workflows, distribution processes, and fiber optic network integration. These codes manage the booking lifecycle from initial request through history tracking and cancellation.

### Error Code Modules (135+ Total)

| Module | Prefix | Code Count | Purpose |
|--------|--------|------------|---------|
| **BFM/BHM** | BFM/BHM | 100+ | Booking flow messages & history management |
| **KFM** | KFM | 15-20 | Customer flow messages (Kundenflowmeldungen) |
| **VFM** | VFM | 15-20 | Distribution flow messages (Verteilungsflowmeldungen) |
| **LWL** | LWL | 5-10 | Fiber optic (Lichtwellenleiter) integration |

## When to Use

Use this skill when you need to:
- **Debug booking workflows** - Resolve BFM message processing failures
- **Booking history issues** - Track and audit booking changes (BHM)
- **Customer flow validation** - Debug customer-specific workflows (KFM)
- **Distribution operations** - Resolve number distribution errors (VFM)
- **TK-Anlage integration** - Debug PBX system booking rules
- **Stornierung (cancellation)** - Understand booking cancellation rules
- **Buchungskennzeichen** - Validate booking indicator logic
- **LWL coordination** - Resolve fiber optic network integration errors
- **Booking conflicts** - Debug concurrent booking attempts
- **Migration planning** - Map booking logic to VNRM microservices

## Quick Reference

### Critical Error Categories

#### 1. Booking Flow Messages (BFM 001-100+)

**Booking Request Validation (001-030):**
- **BFM001** - Invalid booking request format
- **BFM005** - Number not available for booking
- **BFM010** - Customer not authorized
- **BFM015** - Booking capacity exceeded
- **BFM020** - Invalid booking date/time
- **BFM025** - Duplicate booking request

**TK-Anlage (PBX) Rules (031-050):**
- **BFM031** - TK-Anlage booking rule violation
- **BFM035** - PBX MSN group size invalid
- **BFM040** - PBX capacity limit exceeded
- **BFM045** - PBX configuration conflict

**Buchungskennzeichen (Booking Indicator) (051-070):**
- **BFM051** - Booking indicator invalid
- **BFM055** - Indicator state conflict
- **BFM060** - Indicator transition not allowed
- **BFM065** - Missing required indicator

**Stornierung (Cancellation) (071-090):**
- **BFM071** - Cancellation not allowed
- **BFM075** - Cancellation deadline passed
- **BFM080** - Partial cancellation not supported
- **BFM085** - Cancellation creates orphaned numbers

**Integration & Coordination (091-100+):**
- **BFM091** - External system integration failed
- **BFM095** - Booking coordination timeout
- **BFM100** - Database transaction error

#### 2. Booking History Management (BHM 001-030+)

**History Recording:**
- **BHM001** - History record creation failed
- **BHM005** - Historical data inconsistency
- **BHM010** - Audit trail broken
- **BHM015** - History query failed

**Timeline Reconstruction:**
- **BHM020** - Timeline gap detected
- **BHM025** - Conflicting history entries
- **BHM030** - History archival error

#### 3. Customer Flow Messages (KFM 001-020)

**Customer-Specific Validation:**
- **KFM001** - Customer not found
- **KFM005** - Customer status invalid
- **KFM010** - Customer authorization failed
- **KFM015** - Customer quota exceeded
- **KFM020** - Customer contract violation

**Workflow Coordination:**
- Customer onboarding flows
- Service activation sequences
- Product change validations
- Account management operations

#### 4. Distribution Flow Messages (VFM 001-020)

**Distribution Validation:**
- **VFM001** - Distribution rule violation
- **VFM005** - Distribution capacity exceeded
- **VFM010** - Distribution zone conflict
- **VFM015** - Geographic constraint violation
- **VFM020** - Distribution coordination failed

**Load Balancing:**
- Number pool distribution
- Geographic allocation rules
- Capacity planning validation
- Zone boundary enforcement

#### 5. Fiber Optic Integration (LWL 001-010)

**LWL Network Coordination:**
- **LWL001** - Fiber connection not available
- **LWL005** - LWL capacity exceeded
- **LWL010** - Network segment conflict

**Infrastructure Validation:**
- Fiber infrastructure availability
- Network segment assignment
- Capacity constraint checking
- Physical topology validation

## Understanding Booking & Distribution Workflows

### Core Booking Lifecycle

**Booking Flow Stages:**
1. **Request Validation (BFM001-030)** - Format, availability, authorization, timing
2. **TK-Anlage Validation (BFM031-050)** - PBX rules, MSN group size (typically 10), capacity
3. **Buchungskennzeichen (BFM051-070)** - Booking indicators, state transitions
4. **Booking Execution** - Create record, update status, record history (BHM)
5. **Optional: Stornierung (BFM071-090)** - Cancellation rules and deadlines

**Number State Model:**
```
Available → Requested → Reserved → Booked → Active
                            ↓           ↓
                      Cancelled ← Cancelled
                            ↓           ↓
                        Available   Available
```

### Key Concepts

**Buchungskennzeichen (Booking Indicators):**
- Track booking status and type (STANDARD, EXPRESS, TRIAL, MIGRATION, VIP)
- Control workflow progression and conditional processing
- Validation: Required indicators (BFM065), valid transitions (BFM060), no conflicts (BFM055)

**Stornierung (Cancellation) Rules:**
- **BFM071** - Not allowed when: activated, deadline passed, dependent bookings exist
- **BFM075** - Deadline passed (Express: 24h, Standard: 5 days, Migration: 10 days before activation)
- **BFM080** - Partial cancellation not supported for Kontingent/MSN groups

**Booking History (BHM):**
- **BHM001** - Every change creates history record (audit trail requirement)
- **BHM005** - History must match current state (consistency validation)
- **BHM010** - No gaps in audit trail (sequential tracking)

**Customer Flow (KFM):**
- Validates customer existence, status, authorization, quotas, and contract compliance
- Coordinates onboarding and service activation workflows

**Distribution Flow (VFM):**
- Geographic allocation, capacity-based distribution, zone boundaries
- Load balancing and multi-zone coordination

**Fiber Optic Integration (LWL):**
- **LWL001** - Physical fiber availability check
- **LWL005** - Network segment capacity validation
- **LWL010** - Topology compatibility verification

### Detailed Code Information

For complete error code tables with RNVS implementation locations and business reasons, consult the reference files:

- **[BFM_BHM_Codes_Reference.md](references/BFM_BHM_Codes_Reference.md)** - 285 booking flow & history codes with pack_crm.sql locations
- **[KFM_Codes_Reference.md](references/KFM_Codes_Reference.md)** - Customer flow validation codes
- **[VFM_Codes_Reference.md](references/VFM_Codes_Reference.md)** - Distribution flow codes
- **[LWL_Codes_Reference.md](references/LWL_Codes_Reference.md)** - Fiber optic integration codes

## Implementation Mapping

### Primary PL/SQL Packages

| Package | Lines | Purpose | Modules |
|---------|-------|---------|---------|
| **pack_crm.sql** | 5,000+ | Booking operations | BFM, BHM |
| **pack_body_val.sql** | 3,500+ | Booking validation | All modules |
| **pack_body_rfnr.sql** | 4,500+ | Number operations | BFM support |

### Constant Naming Patterns

| Module | Constant Prefix | Example | Description |
|--------|----------------|---------|-------------|
| BFM | `FC_BFM_` | FC_BFM_INVALID | Booking flow prefix |
| BHM | `FC_BHM_` | FC_BHM_FAILED | History prefix |
| KFM | `FC_KFM_` | FC_KFM_NOT_FOUND | Customer flow prefix |
| VFM | `FC_VFM_` | FC_VFM_VIOLATION | Distribution prefix |
| LWL | `FC_LWL_` | FC_LWL_NO_FIBER | Fiber optic prefix |

## Integration with Other VNRM Skills

- **crm-integration-error-specialist** - ECRM codes for CRM portal booking validation
- **number-assignment-error-specialist** - AFM codes for assignment coordination with bookings
- **german-glossary** - Translate German terms (Stornierung, Buchungskennzeichen, TK-Anlage, Kontingent, Lichtwellenleiter)
- **vnrm-num-architecture** - Map booking operations to VNRM NUM microservices
- **vnrm-cor-architecture** - Map distribution logic to VNRM COR microservices

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, workflows, usage instructions
- **[BFM_BHM_Codes_Reference.md](references/BFM_BHM_Codes_Reference.md)** - Booking flow & history codes (100+)
- **[KFM_Codes_Reference.md](references/KFM_Codes_Reference.md)** - Customer flow codes (15-20)
- **[VFM_Codes_Reference.md](references/VFM_Codes_Reference.md)** - Distribution flow codes (15-20)
- **[LWL_Codes_Reference.md](references/LWL_Codes_Reference.md)** - Fiber optic codes (5-10)

## Best Practices

1. **Booking Lifecycle** - Follow request → validation → execution → history sequence
2. **TK-Anlage Rules** - Validate MSN group sizes and PBX capacity (BFM031-050)
3. **Buchungskennzeichen** - Set required indicators, validate state transitions (BFM051-070)
4. **Stornierung Deadlines** - Check cancellation allowed before attempting (BFM071-090)
5. **History Recording** - Always create BHM records for audit trail (BHM001-030)
6. **Customer Validation** - Verify customer status and authorization (KFM001-020)
7. **Distribution Rules** - Apply geographic and capacity constraints (VFM001-020)
8. **LWL Coordination** - Validate fiber infrastructure availability (LWL001-010)
9. **Concurrent Bookings** - Handle duplicate detection and race conditions (BFM025)
10. **Error Cascade** - Fix validation errors in order (format → availability → authorization)

## Common Debugging Scenarios

**Scenario 1: Booking Not Allowed (BFM005)**
- **Error**: BFM005 - Number not available for booking
- **Root Cause**: Number status not "frei" or already reserved
- **Resolution**:
  1. Check number status in database
  2. Verify no active bookings exist
  3. Check for expired reservations (can be reclaimed)
  4. Investigate porting conflicts

**Scenario 2: TK-Anlage Violation (BFM035)**
- **Error**: BFM035 - PBX MSN group size invalid
- **Root Cause**: Requested MSN group != configured size (typically 10)
- **Resolution**:
  1. Query PBX configuration for required group size
  2. Adjust booking request to match (usually 10 numbers)
  3. OR configure PBX to accept different size (if allowed)

**Scenario 3: Cancellation Deadline Passed (BFM075)**
- **Error**: BFM075 - Cancellation deadline passed
- **Root Cause**: Too late to cancel before activation
- **Resolution**:
  1. Check booking activation date
  2. Calculate cancellation deadline
  3. If truly past deadline: cannot cancel, must deactivate after activation
  4. If calculation error: correct deadline configuration

**Scenario 4: History Recording Failed (BHM001)**
- **Error**: BHM001 - History record creation failed
- **Root Cause**: Database error or constraint violation
- **Resolution**:
  1. Check database connection and space
  2. Verify history table schema
  3. Validate foreign key constraints
  4. CRITICAL: Fix immediately (audit trail broken)

**Scenario 5: Customer Quota Exceeded (KFM015)**
- **Error**: KFM015 - Customer quota exceeded
- **Root Cause**: Customer reached maximum allowed bookings/numbers
- **Resolution**:
  1. Query customer quota configuration
  2. Check current utilization
  3. Request quota increase (if justified)
  4. OR customer must release existing numbers

**Scenario 6: LWL Not Available (LWL001)**
- **Error**: LWL001 - Fiber connection not available
- **Root Cause**: No fiber infrastructure at customer location
- **Resolution**:
  1. Verify customer address against LWL coverage map
  2. Check for planned fiber rollout
  3. Investigate alternative connection technologies
  4. OR customer must choose location with fiber

## Key External References

- **Booking Workflow Specification** - RNVS booking process documentation
- **TK-Anlage Integration Standards** - PBX system compatibility requirements
- **Stornierung Policy** - Cancellation rules and deadlines
- **LWL Infrastructure Database** - Fiber optic network coverage and capacity
- **Customer Quota Management** - Quota assignment and enforcement policies

---

**For detailed code tables with RNVS implementation locations, see individual reference files above**
