---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-number-assignment-error-specialist
description: This skill should be used when the user asks to "debug KONTES workflows", "resolve assignment errors", "fix allocation conflicts", "understand Kontingent management", or mentions assignment codes (AFM, A1P, A2R, A3R, AHM, AKFM). Provides expert knowledge of 230+ RNVS number assignment error codes covering KONTES integration, assignment lifecycle (allocation/reservation/release), Kontingent management, portability validation, ownership conflicts, number state transitions, and assignment history tracking.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/number-assignment-error-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Number Assignment Error Code Specialist Skill

## Purpose

Provides **expert-level knowledge** of **230+ RNVS number assignment error codes** that govern the complete assignment lifecycle from initial allocation through reservation to final release. These codes manage KONTES (T-Com internal system) integration, Kontingent (allocation block) operations, and number ownership transitions.

### Error Code Modules (230+ Total)

| Module | Prefix | Code Count | Purpose |
|--------|--------|------------|---------|
| **AFM** | AFM | 129 | KONTES assignment flow messages |
| **A1P** | A1P | 50+ | Assignment Phase 1 (initial allocation) |
| **A2R** | A2R | 15-20 | Assignment Phase 2 (reservation) |
| **A3R** | A3R | 5-10 | Assignment Phase 3 (release) |
| **AHM** | AHM | 15-20 | Assignment history management |
| **AKFM** | AKFM | 15-20 | Assignment correction flow messages |

## When to Use

Use this skill when you need to:
- **Debug KONTES integration** - Resolve AFM message processing failures
- **Assignment lifecycle issues** - Trace allocation, reservation, and release errors
- **Kontingent management** - Debug allocation block operations and conflicts
- **Portability validation** - Resolve porting conflicts during assignment (AFM130)
- **Ownership conflicts** - Debug Eigentümer/Besitzer validation (AFM261-268)
- **Number state transitions** - Understand status changes (frei/belegt/reserviert)
- **Assignment history** - Track and audit assignment changes over time
- **Correction workflows** - Debug assignment error correction (AKFM)
- **Product change validation** - Resolve conflicts during service migrations
- **Migration planning** - Map assignment logic to VNRM microservices

## Quick Reference

### Critical Error Categories

#### 1. KONTES Assignment Flow (AFM 007-294)

**Number State Conflicts (007-024):**
- **AFM007** - Product change in progress
- **AFM008** - Number already occupied
- **AFM009** - Number already reserved
- **AFM010** - Number locked by another process

**Portability Validation (130-134):**
- **AFM130** - **CRITICAL** - Porting with Level = U3 exists
- **AFM131** - Porting date tolerance exceeded
- **AFM133/134** - EAS/DUWA collision from KONTES

**Kontingent Management (242-289):**
- **AFM242** - Numbers not in same Kontingent
- **AFM243** - Kontingent validation failed
- **AFM289** - **CRITICAL** - Kontingent incompletely ported

**Ownership & Boundaries (261-294):**
- **AFM261a/b** - Number has Besitzer Telekom
- **AFM267** - Number block has multiple Eigentümer
- **AFM268** - Eigentümer is BNetzA
- **AFM270** - Blockgrenzen (block boundary) violation

**Loader & Integration (200-241):**
- **AFM200** - Error/message from porting loader
- **AFM210** - KONTES message parsing failed
- **AFM220** - Database transaction error
- **AFM230** - Validation rule violation

#### 2. Assignment Phase 1 - Initial Allocation (A1P 001-050+)

**Allocation Validation:**
- Number availability checks
- RNB boundary validation
- Eigentümer verification
- Capacity constraints
- Product compatibility

**Critical Errors:**
- **A1P001** - No free numbers available in requested range
- **A1P010** - RNB not found or invalid
- **A1P020** - Allocation exceeds RNB capacity
- **A1P030** - Product not compatible with number type
- **A1P040** - Eigentümer mismatch

#### 3. Assignment Phase 2 - Reservation (A2R 001-020)

**Reservation Validation:**
- Reservation duration limits
- Customer authorization
- Concurrent reservation conflicts
- Expiration handling

**Critical Errors:**
- **A2R001** - Number not available for reservation
- **A2R005** - Reservation period invalid
- **A2R010** - Customer not authorized
- **A2R015** - Reservation already exists

#### 4. Assignment Phase 3 - Release (A3R 001-010)

**Release Validation:**
- Active service checks
- Cleanup operations
- Status transition rules
- History recording

**Critical Errors:**
- **A3R001** - Number has active services
- **A3R005** - Release not authorized
- **A3R010** - Cleanup operation failed

#### 5. Assignment History (AHM 001-020)

**History Tracking:**
- Assignment change auditing
- Timeline reconstruction
- Ownership transitions
- Compliance reporting

**Critical Errors:**
- **AHM001** - History record creation failed
- **AHM005** - Historical data inconsistency
- **AHM010** - Audit trail broken

#### 6. Assignment Correction (AKFM 001-020)

**Correction Workflows:**
- Assignment error detection
- Correction message generation
- Rollback operations
- Data reconciliation

**Critical Errors:**
- **AKFM001** - Correction not allowed
- **AKFM005** - Original assignment not found
- **AKFM010** - Correction creates conflict

## Understanding Number Assignment Workflows

### Assignment Lifecycle

**Three-Phase Model:**
1. **Phase 1 (A1P): Allocation** - Identify free numbers, validate ownership, check capacity, reserve block
2. **Phase 2 (A2R): Reservation** - Create customer reservation, set expiration timer, lock for exclusive use
3. **Phase 3 (A3R): Release** - Verify no active services, return to free pool, record in history

**Number State Transitions:**
```
frei (free) → reserviert (reserved) → belegt (occupied)
                    ↓                        ↓
                 expired                  release
                    ↓                        ↓
                  frei ← ← ← ← ← ← ← ← ← ← frei
```

### Key Concepts

**KONTES Integration (AFM):**
- External system for number assignment coordination
- AFM validation sequence: Structure → Availability → Portability → Ownership → Kontingent → Boundaries
- Implementation: pack_crm.sql (FC_KONT_* constants, lines 450-650)

**Critical Portability Conflict (AFM130):**
- **Error:** "Porting with Level = U3 exists"
- **Level U3** = Active porting workflow in progress
- **Resolution:** Wait for porting completion, cancel if authorized, or choose different number

**Kontingent Management (AFM242-289):**
- **Kontingent** = Allocation block (group of numbers assigned as single unit)
- Must be allocated/ported atomically, cannot split across customers
- **AFM242** - Numbers not in same Kontingent
- **AFM289** - Kontingent incompletely ported (blocks migration)

**Ownership Validation (AFM261-268):**
- **AFM261a/b** - Number has Besitzer Telekom (ownership conflict)
- **AFM267** - Number block has multiple Eigentümer (split required)
- **AFM268** - Eigentümer is BNetzA (awaiting Federal Network Agency assignment)

**Assignment History (AHM):**
- Audit trail for compliance and dispute resolution
- Tracks: Status transitions, ownership changes, reservation lifecycle, errors/corrections

### Detailed Code Information

For complete error code tables with RNVS implementation locations and business reasons, consult the reference files:

- **AFM Codes** - KONTES assignment flow validation (129 codes with pack_crm.sql locations)
- **A1P Codes** - Phase 1 allocation errors (50+ codes)
- **A2R Codes** - Phase 2 reservation errors (15-20 codes)
- **A3R Codes** - Phase 3 release errors (5-10 codes)
- **AHM Codes** - Assignment history management (15-20 codes)
- **AKFM Codes** - Assignment coordination flows (15-20 codes)

## Implementation Mapping

### Primary PL/SQL Packages

| Package | Lines | Purpose | Modules |
|---------|-------|---------|---------|
| **pack_crm.sql** | 5,000+ | Assignment operations | AFM, A1P-A3R |
| **pack_body_val.sql** | 3,500+ | Assignment validation | AFM support |
| **pack_body_rfnr.sql** | 4,500+ | Callnumber operations | All modules |
| **pack_body_pm.sql** | 3,500+ | Porting conflict detection | AFM130 |

### Constant Naming Patterns

| Module | Constant Prefix | Example | Description |
|--------|----------------|---------|-------------|
| AFM | `FC_KONT_` | FC_KONT_U3_PM | KONTES prefix |
| A1P | `FC_A1P_` | FC_A1P_NO_FREE | Phase 1 prefix |
| A2R | `FC_A2R_` | FC_A2R_EXISTS | Phase 2 prefix |
| A3R | `FC_A3R_` | FC_A3R_ACTIVE | Phase 3 prefix |
| AHM | `FC_AHM_` | FC_AHM_FAILED | History prefix |
| AKFM | `FC_AK_` | FC_AK_FORBIDDEN | Correction prefix |

## Integration with Other VNRM Skills

- **crm-integration-error-specialist** - ECRM codes for booking validation (complements AFM)
- **porting-workflow-error-specialist** - PFM codes for porting coordination with AFM130
- **german-glossary** - Translate German terms (Kontingent, Eigentümer, Besitzer, KONTES)
- **vnrm-num-architecture** - Map assignment operations to VNRM NUM microservices
- **vnrm-prt-architecture** - Map AFM130 porting conflicts to VNRM PRT microservices

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, lifecycle, usage instructions
- **[AFM_Codes_Reference.md](references/AFM_Codes_Reference.md)** - KONTES assignment codes (129)
- **[A1P_Codes_Reference.md](references/A1P_Codes_Reference.md)** - Phase 1 allocation codes (50+)
- **[A2R_Codes_Reference.md](references/A2R_Codes_Reference.md)** - Phase 2 reservation codes (15-20)
- **[A3R_Codes_Reference.md](references/A3R_Codes_Reference.md)** - Phase 3 release codes (5-10)
- **[AHM_Codes_Reference.md](references/AHM_Codes_Reference.md)** - History management codes (15-20)
- **[AKFM_Codes_Reference.md](references/AKFM_Codes_Reference.md)** - Correction flow codes (15-20)

## Best Practices

1. **Portability First** - Always check AFM130 before assignment (porting blocks allocation)
2. **Kontingent Atomicity** - Never split allocation blocks (AFM242, AFM289)
3. **Ownership Verification** - Validate Eigentümer before allocation (AFM261-268)
4. **Phase Sequence** - Follow A1P → A2R → A3R lifecycle strictly
5. **History Recording** - Always log assignment changes for audit trail (AHM)
6. **Boundary Checks** - Validate block boundaries before range operations (AFM270)
7. **KONTES Integration** - Parse messages carefully, validate before processing (AFM210)
8. **State Transitions** - Follow frei → reserviert → belegt → frei state model
9. **Expiration Handling** - Monitor and process reservation expirations (A2R)
10. **Correction Workflow** - Use AKFM codes for proper error correction (not manual fixes)

## Common Debugging Scenarios

**Scenario 1: Porting Conflict (AFM130)**
- **Error**: AFM130 - Porting with Level = U3 exists
- **Check**: pack_crm.sql:590 (FC_KONT_U3_PM)
- **Root Cause**: Active porting workflow blocks assignment
- **Resolution**:
  1. Query porting table: `SELECT * FROM porting WHERE level = 'U3'`
  2. Check porting date (completion time)
  3. Wait for porting OR cancel if authorized
  4. Retry assignment after porting complete

**Scenario 2: Kontingent Incomplete Porting (AFM289)**
- **Error**: AFM289 - Kontingent incompletely ported
- **Check**: pack_crm.sql:650 (FC_KONT_UNVOLL_PORT)
- **Root Cause**: Allocation block partially migrated
- **Resolution**:
  1. Identify Kontingent ID
  2. List all numbers in Kontingent
  3. Complete porting of remaining numbers
  4. OR split Kontingent (requires authorization)

**Scenario 3: Multiple Eigentümer (AFM267)**
- **Error**: AFM267 - Number block has multiple Eigentümer
- **Check**: pack_crm.sql:630 (FC_KONT_MULTI_EIG)
- **Root Cause**: Requested range spans ownership boundaries
- **Resolution**:
  1. Query RNB table for Eigentümer per range
  2. Split request into separate blocks per owner
  3. OR choose range within single ownership
  4. Resubmit assignment with corrected ranges

**Scenario 4: No Free Numbers (A1P001)**
- **Error**: A1P001 - No free numbers available in requested range
- **Check**: pack_crm.sql:500 (FC_A1P_NO_FREE)
- **Root Cause**: All numbers in range are belegt or reserviert
- **Resolution**:
  1. Search broader range for free numbers
  2. Check for expired reservations (can be reclaimed)
  3. Consider different RNB or area code
  4. Investigate unusual occupancy (data integrity?)

**Scenario 5: Reservation Conflict (A2R015)**
- **Error**: A2R015 - Reservation already exists
- **Check**: pack_crm.sql:550 (FC_A2R_EXISTS)
- **Root Cause**: Number already reserved by another customer
- **Resolution**:
  1. Check reservation expiration time
  2. If expired, trigger cleanup and retry
  3. If active, choose different number
  4. Investigate if duplicate reservation request

## Key External References

- **KONTES Integration Specification** - T-Com internal system interface
- **Kontingent Management Policy** - Allocation block rules
- **Number Assignment Lifecycle** - Phase 1/2/3 process documentation
- **BNetzA URNB File** - Federal Network Agency ownership registry
- **Reservation Expiration Rules** - Timeout and cleanup policies

---

**For detailed code tables with RNVS implementation locations, see individual reference files above**
