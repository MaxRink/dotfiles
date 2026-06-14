---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-crm-integration-error-specialist
description: This skill should be used when the user asks to "debug CRM portal failures", "understand ECRM codes", "resolve number booking issues", "fix ownership conflicts", "resolve process locking", or mentions specific ECRM codes (ECRMP, ERESP). Provides expert knowledge of 226 ECRM error codes covering CRM Portal integration including callnumber booking validation, availability checks, ownership conflicts, reservation management, porting collisions, TK-Anlage (PBX) booking rules, Kontingent allocation, and process locking (ECRMP080).
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/crm-integration-error-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CRM Integration Error Code Specialist Skill

## Purpose

Provides **expert-level knowledge** of **226 ECRM error codes** that govern CRM Portal integration with RNVS. These codes validate callnumber booking operations, ownership rules, availability checks, and customer-facing number management operations.

### Error Code Modules (226 Total)

| Module | Prefix | Code Count | Purpose |
|--------|--------|------------|---------|
| **ECRMP** | ECRMP | 183 | CRM Portal request validation errors |
| **ERESP** | ERESP | 43 | CRM Portal response messages |

## When to Use

Use this skill when you need to:
- **Debug CRM portal failures** - Understand why number booking requests fail
- **Identify ECRM error codes** - Understand what a specific code means (e.g., "What is ECRMP045?")
- **Validate callnumber availability** - Trace free number search failures and conflicts
- **Resolve ownership conflicts** - Debug Eigentümer (owner) vs Besitzer (possessor) issues
- **Understand booking rules** - Apply TK-Anlage, Kontingent, and reservation logic
- **Porting collision detection** - Identify when porting operations block bookings
- **Process locking issues** - Debug ECRMP080 and concurrent operation conflicts
- **Analyze legacy CRM logic** - Map error constants to PL/SQL implementation
- **Migration planning** - Map ECRM validation to VNRM microservices

## Quick Reference

### Critical Error Categories

#### 1. Callnumber Availability (ECRMP 001-020)
**Common Errors:**
- **ECRMP001** - No free callnumber available for connection type
- **ECRMP002** - Callnumber not free (status: belegt, reserviert, gesperrt)
- **ECRMP005** - Callnumber already occupied
- **ECRMP006** - Callnumber reserved by another process
- **ECRMP007** - Callnumber blocked (gesperrt)
- **ECRMP014** - Free number search failed (no matches)

#### 2. Number Format & Rules (ECRMP 021-040)
**Common Errors:**
- **ECRMP021** - MSN digit count validation failed
- **ECRMP022** - Invalid number format (must be 10 or 11 digits)
- **ECRMP023** - RNB format validation error
- **ECRMP024** - Blockgrenzen (block boundary) violation
- **ECRMP025** - ONKZ (area code) validation failed

#### 3. Ownership & Control (ECRMP 041-080)
**Common Errors:**
- **ECRMP041** - Eigentümer (owner) validation failed
- **ECRMP042** - Besitzer (possessor) mismatch
- **ECRMP043/044** - Porting message already exists (P-message/L-message)
- **ECRMP045** - Number in active porting workflow
- **ECRMP047** - Callnumber not in RNVS database
- **ECRMP016** - Callnumber exported (Besitzer: Dxxx)
- **ECRMP050** - BNetzA Altbestand (legacy stock) rule violation
- **ECRMP080** - **CRITICAL** - Callnumber locked by another process

#### 4. Booking Operations (ECRMP 081-150)
**Common Errors:**
- **ECRMP081** - Kontingent (allocation block) validation failed
- **ECRMP082** - Kontingent already assigned
- **ECRMP090** - TK-Anlage (PBX) booking rule violation
- **ECRMP091** - PBX system capacity exceeded
- **ECRMP095** - Buchungskennzeichen (booking indicator) invalid
- **ECRMP100** - Booking history validation failed
- **ECRMP110** - Stornierung (cancellation) not allowed
- **ECRMP120** - Reservation period expired

#### 5. Special Cases (ECRMP 151-183)
**Common Errors:**
- **ECRMP151** - ISP-specific rule violation
- **ECRMP160** - Porting date constraint violation
- **ECRMP170** - Cross-system validation failed
- **ECRMP180** - Database consistency check failed

### Response Codes (ERESP 001-043)
**Purpose:** Error codes returned to CRM portal in response messages

**Common Response Codes:**
- **ERESP001** - Request accepted successfully
- **ERESP005** - Request rejected (validation failed)
- **ERESP010** - Partial success (some numbers processed)
- **ERESP020** - System busy (retry later)
- **ERESP030** - Authorization failed
- **ERESP040** - Database error occurred

## Instructions

### 1. Understanding ECRM Code Structure

**Code Format:**
```
ECRMP[NUMBER] - Portal request errors (001-183)
ERESP[NUMBER] - Portal response codes (001-043)
```

**Examples:**
- `ECRMP045` - Porting message exists
- `ECRMP080` - Process lock conflict
- `ERESP005` - Request rejected

### 2. Callnumber Availability Validation (ECRMP 001-020)

**Validation Flow:**
1. **Check number status** - Must be "frei" (free)
2. **Verify no reservations** - Check reservation table
3. **Validate no locks** - Ensure no process locks exist
4. **Check porting conflicts** - Verify no active porting messages
5. **Confirm ownership** - Validate Eigentümer/Besitzer rules

**Critical Rules:**
- Status must be exactly "frei" (not "belegt", "reserviert", "gesperrt")
- Reservation expiration checked before assignment
- Process locks prevent concurrent modifications (ECRMP080)

### 3. Ownership Validation (ECRMP 041-080)

**Eigentümer vs Besitzer:**
- **Eigentümer (Owner)** - Legal number block owner (BNetzA assignment)
- **Besitzer (Possessor)** - Current operational possessor (can differ during porting)

**Validation Rules:**
- **ECRMP041** - Eigentümer must be valid TNB participant
- **ECRMP042** - Besitzer must match expected carrier
- **ECRMP016** - Exported numbers (Dxxx) cannot be booked
- **ECRMP050** - BNetzA Altbestand rules enforced

**Export/Import Logic:**
- **D001-D999** - Deutsche Telekom internal codes
- **Export** - Number assigned to external carrier
- **Import** - Number received from external carrier

### 4. Porting Collision Detection (ECRMP 043-047)

**Collision Scenarios:**
- **ECRMP043** - P-message (porting request) already exists
- **ECRMP044** - L-message (porting notification) already exists
- **ECRMP045** - Active porting workflow in progress
- **ECRMP046** - Porting date conflicts with booking date

**Resolution:**
1. Check porting message status (P/L/Z)
2. Verify porting date vs booking date
3. Determine if porting can be cancelled
4. If not, reject booking request

### 5. Kontingent & TK-Anlage Booking (ECRMP 081-110)

**Kontingent (Allocation Block):**
- Group of numbers assigned as single unit
- **ECRMP081** - Kontingent validation failed
- **ECRMP082** - Kontingent already assigned to customer
- **ECRMP083** - Kontingent partially allocated (incomplete)

**TK-Anlage (PBX System):**
- **ECRMP090** - PBX booking rule violation
- **ECRMP091** - PBX capacity limit exceeded
- **ECRMP092** - MSN group assignment conflict

**Rules:**
- Kontingent must be booked atomically (all or nothing)
- TK-Anlage MSN groups have size constraints (typically 10 numbers)
- Cannot split Kontingent across multiple customers

### 6. Process Locking (ECRMP080)

**Critical Concurrency Control:**
- **ECRMP080** - Callnumber locked by another process

**Lock Scenarios:**
1. Concurrent booking attempts (CRM portal)
2. Active porting workflow (PDA processing)
3. Batch operations (nightly cleanup)
4. Manual admin operations

**Resolution:**
- Wait for lock release (typically seconds)
- Retry request after short delay
- Check for stuck locks (orphaned processes)

### 7. Validation Sequence

**Order of Validation (pack_crm.sql):**
```
1. Syntax validation (number format, length)
2. Database lookup (number exists?)
3. Status check (frei/belegt/reserviert/gesperrt)
4. Ownership validation (Eigentümer/Besitzer)
5. Process lock check (ECRMP080)
6. Porting conflict detection (ECRMP043-047)
7. Kontingent/TK-Anlage rules (ECRMP081-110)
8. Business rule validation (Altbestand, export, etc.)
9. Final authorization check
```

**Error Cascade:**
- Errors reported in validation order
- Fix syntax errors first, then business logic
- Process locks block all subsequent validation

## Implementation Mapping

### Primary PL/SQL Package

| Package | Lines | Purpose |
|---------|-------|---------|
| **pack_crm.sql** | 5,000+ | CRM integration, error constant definitions |

### Constant Naming Pattern

**ECRMP Codes:**
```sql
-- Pattern: FC_ + descriptive German name
FC_KEINE_FREIE_RFNR    -- ECRMP001
FC_RFNR_VORH           -- ECRMP005
FC_RFNR_EXPORTIERT     -- ECRMP016
FC_PM_VORHANDEN        -- ECRMP043/044
FC_RFNR_NICHT_RNVS     -- ECRMP047
FC_RFNR_GESPERRT       -- ECRMP080
```

**Location:** pack_crm.sql:236-400+

### Supporting Packages

- **pack_body_val.sql** - Additional validation logic
- **pack_body_pm.sql** - Porting message collision detection
- **pack_body_rfnr.sql** - Callnumber status management

## Integration with Other VNRM Skills

- **porting-workflow-error-specialist** - PFM codes for porting workflow validation
- **number-assignment-error-specialist** - AFM codes for KONTES assignment flows
- **porting-data-exchange-specialist** - External PDA codes (0000-6200)
- **german-glossary** - Translate German error descriptions (Rufnummer, Besitzer, Eigentümer, Kontingent, TK-Anlage)
- **vnrm-num-architecture** - Map ECRM validation to VNRM NUM microservices
- **vnrm-prt-architecture** - Map porting collision detection to VNRM PRT microservices

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, categories, usage instructions
- **[ECRM_Codes_Reference.md](references/ECRM_Codes_Reference.md)** - Complete 226-code reference table with implementation locations

## Best Practices

1. **Validation Order** - Follow pack_crm.sql validation sequence to avoid cascading errors
2. **Process Locks** - Always check ECRMP080 first when debugging concurrency issues
3. **Porting Conflicts** - Verify no active P/L/Z messages before booking (ECRMP043-047)
4. **Ownership Rules** - Understand Eigentümer vs Besitzer semantics
5. **Kontingent Atomicity** - Book allocation blocks atomically (all or nothing)
6. **German Translation** - Use german-glossary for error message translation
7. **Constant Lookup** - Use FC_* constant names to locate implementation in pack_crm.sql
8. **Status Checks** - Always verify callnumber status before attempting operations
9. **Export Detection** - Check for Dxxx Besitzer codes (ECRMP016)
10. **Error Cascade** - Fix earlier validation errors before debugging later stages

## Common Debugging Scenarios

**Scenario 1: CRM Portal Booking Failure (ECRMP005)**
- **Error**: ECRMP005 - Callnumber already occupied
- **Check**: pack_crm.sql:240 (FC_RFNR_VORH)
- **Root Cause**: Number status = 'belegt' (occupied)
- **Resolution**:
  1. Query callnumber status in database
  2. Check for porting messages (P/L/Z)
  3. Verify no reservation exists
  4. If incorrectly marked occupied, investigate data integrity

**Scenario 2: Process Lock Conflict (ECRMP080)**
- **Error**: ECRMP080 - Callnumber locked by another process
- **Check**: pack_crm.sql:290 (FC_RFNR_GESPERRT)
- **Root Cause**: Concurrent modification attempt
- **Resolution**:
  1. Wait 5-10 seconds and retry
  2. Check for stuck locks (orphaned processes)
  3. Identify locking process (CRM, batch, admin)
  4. If stuck, manually release lock (admin operation)

**Scenario 3: Porting Collision (ECRMP043/044)**
- **Error**: ECRMP043 - P-message already exists
- **Check**: pack_crm.sql:260 (FC_PM_VORHANDEN)
- **Root Cause**: Active porting request conflicts with booking
- **Resolution**:
  1. Query porting message table (P/L/Z status)
  2. Check porting date vs requested booking date
  3. Determine if porting can be cancelled
  4. If not cancellable, reject booking or delay until porting complete

**Scenario 4: Kontingent Validation Failed (ECRMP081)**
- **Error**: ECRMP081 - Kontingent validation failed
- **Check**: pack_crm.sql:350 (FC_KONT_INVALID)
- **Root Cause**: Allocation block rules violated
- **Resolution**:
  1. Verify Kontingent exists and is complete
  2. Check for partial allocations
  3. Ensure atomic booking (all numbers together)
  4. Validate no porting conflicts within Kontingent

**Scenario 5: Exported Number (ECRMP016)**
- **Error**: ECRMP016 - Callnumber exported (Besitzer: Dxxx)
- **Check**: pack_crm.sql:250 (FC_RFNR_EXPORTIERT)
- **Root Cause**: Number assigned to external carrier
- **Resolution**:
  1. Verify Besitzer code (D001-D999 = exported)
  2. Check if export is current or historical
  3. If incorrectly exported, investigate porting workflow
  4. Cannot book exported numbers until import complete

## Key External References

- **CRM-T Integration Specification** - CRM portal to RNVS interface documentation
- **RNVS Architecture** - Legacy system architecture
- **BNetzA Altbestand Rules** - Federal Network Agency legacy stock regulations
- **Kontingent Management** - Number allocation block policies
- **TK-Anlage Standards** - PBX system integration requirements

---

**For complete ECRM code reference table with RNVS implementation locations, see [ECRM_Codes_Reference.md](references/ECRM_Codes_Reference.md)**
