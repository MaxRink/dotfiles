---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-porting-workflow-error-specialist
description: This skill should be used when the user asks to "debug porting workflows", "resolve carrier coordination issues", "validate RNB file messages", "fix U-Teil/K-Teil structure", "calculate AT deadlines", or mentions porting codes (PFM, WFA, WFB, WFC, RNBFM, RNPS). Provides expert knowledge of 170+ RNVS porting workflow error codes covering TNB carrier coordination, PDA message pairing validation, RNB file message syntax/timing rules, U-Teil/K-Teil structure validation, AT (working days) deadline calculations, and porting status tracking.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/porting-workflow-error-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Porting Workflow Error Code Specialist Skill

## Purpose

Provides **expert-level knowledge** of **170+ RNVS porting workflow error codes** that govern number portability operations, carrier coordination, RNB (number block) file processing, and inter-carrier message validation. These codes ensure correct TNB communication, PDA message pairing, timing constraint enforcement, and regulatory compliance.

### Error Code Modules (170+ Total)

| Module | Prefix | Code Count | Purpose |
|--------|--------|------------|---------|
| **WFC** | WFC | 50+ | Workflow C (advanced carrier coordination) |
| **RNBFM** | RNBFM | 39 | RNB file message validation (number blocks) |
| **PFM** | PFM | 37 | Porting flow message validation |
| **WFA** | WFA | 20 | Workflow A (carrier action validation) |
| **RNPS** | RNPS | 10-15 | RNB process status tracking |
| **WFB** | WFB | 10-20 | Workflow B (intermediate carrier coordination) |

## When to Use

Use this skill when you need to:
- **Debug porting workflows** - Trace P/L/Z message validation failures
- **Carrier coordination issues** - Resolve WFA/WFB/WFC workflow errors
- **RNB file validation** - Debug RNBFM syntax, timing, or ownership errors
- **PDA message pairing** - Validate KONTES/WSSt/ISP/T-Mobile coordination
- **AT timing calculations** - Apply working day deadline rules (20 AT, 10 AT, 2 AT)
- **U-Teil/K-Teil validation** - Debug original vs correction message structure
- **TNB coordination** - Resolve carrier-to-carrier communication errors
- **Correction code validation** - Ensure proper PDA correction code usage
- **RNB process tracking** - Monitor number block operation status
- **Migration planning** - Map porting validation to VNRM PRT microservices

## Quick Reference

### Critical Error Categories

#### 1. Porting Flow Messages (PFM 001-037)

**Missing Message Detection (001-024):**
- **PFM001** - Competitor missing for T-Com message
- **PFM003** - T-Com/T-Mobile/TSBS import missing for WSSt L-message
- **PFM004** - DTAG export missing for competitor P-message
- **PFM018** - ISP message missing for WSSt

**Validation States (007-009):**
- **PFM007** - L exists, P missing
- **PFM008** - Z exists, P missing
- **PFM009** - P exists, L missing

**Special Product Integration (022-039):**
- **PFM022/024** - IP product WSSt/ISP coordination
- **PFM031-037** - Mobile Home (MH) integration
- **PFM036-038** - Congstar integration

**Deadline & Realization (025-030):**
- **PFM025** - KONTES/CRM-T import realization missing
- **PFM030** - PFM004 callnumber is free

#### 2. RNB File Messages (RNBFM 001-055)

**Syntax & Format (001-010):**
- **RNBFM001** - Callnumber empty
- **RNBFM002** - Callnumbers different lengths
- **RNBFM003/004** - ONKZ invalid/different
- **RNBFM006** - RNB syntactically incorrect
- **RNBFM008** - Wrong date format

**Database & TNB Validation (007-016):**
- **RNBFM007** - RNB not in database
- **RNBFM010** - TNB not in database
- **RNBFM015** - Occupied numbers with Besitzer ≠ Eigentümer
- **RNBFM016** - Occupied callnumbers exist

**Correction Code Logic (017-020):**
- **RNBFM017** - Correction code invalid
- **RNBFM018** - Original message not present
- **RNBFM019** - Original message invalid
- **RNBFM020** - Original message faulty

**Timing Constraints - AT Rules (021-023):**
- **RNBFM021** - Less than **20 AT** between file date and setup date
- **RNBFM022** - Setup date must be ≥ file date + **2 AT**
- **RNBFM023** - Original message setup date must be ≥ file date - **6 months**

**BSA Integration (050-055):**
- **RNBFM050** - Bereitstellungsauftrag (provisioning order) not present
- **RNBFM053** - Provisioning order already completed
- **RNBFM055** - RNB affected by PK shutdown message

#### 3. Workflow A - Carrier Actions (WFA 0001-0141)

**Structure & Format (0001-0010):**
- **WFA0001** - Error reading record (structure)
- **WFA0003/0004** - Besitzer_Alt/Neu faulty or missing
- **WFA0008** - Error reading file origin (Dateiherkunft)
- **WFA0010** - Porting status length > 1

**Number Validation (0014-0026):**
- **WFA0014/0015** - RufNr_Von/Bis faulty or missing
- **WFA0020/0021** - Different lengths/ONKZ for Von/Bis
- **WFA0023** - Faulty porting date
- **WFA0026** - ONKZ not in database

**Correction & Duplicates (0050, 0137-0141):**
- **WFA0050** - Unknown correction code
- **WFA0137/0138** - U-Teil/K-Teil not completely filled
- **WFA0140/0141** - Duplicate file detection

#### 4. Workflow B & C - Advanced Coordination

**WFB (10-20 codes):** Intermediate carrier coordination workflows

**WFC (50+ codes):** Advanced carrier coordination, complex message pairing

#### 5. RNB Process Status (RNPS 001-015)

**Purpose:** Track RNB operation states through lifecycle
- Process initiation validation
- State transition errors
- Completion verification
- Cleanup operation tracking

## Understanding Porting Workflows

### Porting Architecture

**Message Types:**
- **P-Message (Portierungsanzeige)** - Request to port number
- **L-Message (Lieferanzeige)** - Notification of number delivery
- **Z-Message (Zulieferanzeige)** - Additional delivery notification

**Carrier Types:**
- KONTES (T-Com internal), WSSt (Competitor carriers), ISP, T-Mobile, TSBS

**Validation Chain:**
File structure (WFA) → Syntax (RNBFM) → Database lookup → Message pairing (PFM) → Correction codes → Timing (AT rules) → Orchestration (WFB/WFC) → Status tracking (RNPS)

### Key Concepts

**PFM - Message Pairing Rules:**
- **PFM001** - Competitor missing for T-Com message
- **PFM003** - Internal import missing for WSSt L-message
- **PFM004** - DTAG export missing for competitor P-message
- **PFM018** - ISP message missing for coordination
- Implementation: pack_val.sql (FC_NVAL_* constants, lines 40-75)

**RNBFM - RNB File Message Validation:**
- **Syntax (001-010)** - Callnumber format, Von/Bis length, ONKZ, RNB format, date format
- **Database (007-016)** - Message lookup and reference validation
- **Correction Codes (017-020)** - PDA specification existence, original message presence/structure/logic
- **Timing (021-023)** - AT (working days) deadline enforcement

**Critical AT (Arbeitstage) Rules:**
- **RNBFM021** - 20 AT minimum advance notice for RNB operations (regulatory requirement)
- **RNBFM022** - 2 AT minimum processing time before setup
- **RNBFM023** - 6 month maximum age for historical message correction
- **AT calculation** - Monday-Friday excluding German public holidays (national + state-specific)

**WFA - Carrier Action Validation:**
- **U-Teil/K-Teil Structure** - U-Teil (Ursprungsteil/original) vs K-Teil (Korrekturteil/correction)
- **WFA0137** - U-Teil must be completely filled for corrections
- **WFA0138** - K-Teil must be completely filled (or empty for withdrawals)
- **Besitzer Validation** - Besitzer_Alt (previous) and Besitzer_Neu (new) must be valid TNB participants
- Implementation: pack_body_rfnr.sql:228-247

**Workflow Orchestration:**
- **WFA** - Basic file validation
- **WFB** - Multi-message coordination, state transitions
- **WFC** - Complex orchestration, 3+ carrier pairing, cross-product integration

**RNPS - Process Status Tracking:**
- Lifecycle: Initiation → Progress → Completion → Cleanup
- Validates state consistency, transition authorization, completion criteria

## Implementation Mapping

### Primary PL/SQL Packages

| Package | Lines | Purpose | Modules |
|---------|-------|---------|---------|
| **pack_body_rnb.sql** | 4,000+ | RNB operations | RNBFM, RNPS |
| **pack_val.sql** | 3,500+ | Porting validation | PFM |
| **pack_body_rfnr.sql** | 4,500+ | Callnumber operations | WFA |
| **pack_body_pm.sql** | 3,500+ | Porting messages | PFM support |
| **pack_bereichsinfo.sql** | 2,000+ | Range info validation | PFM support |
| **pack_body_strukt.sql** | 1,500+ | Structural validation | RNBFM BSA |

### Constant Naming Patterns

| Module | Constant Prefix | Example | Description |
|--------|----------------|---------|-------------|
| PFM | `FC_NVAL_` | FC_NVAL_KONTES_P | Not-validated prefix |
| RNBFM | `FC_` | FC_RFNR_LEER | Descriptive name |
| WFA | `FC_` | FC_STRUKTUR | Descriptive name |
| RNPS | `FC_RNB_` | FC_RNB_PROCESS | RNB process prefix |

## Integration with Other VNRM Skills

- **porting-data-exchange-specialist** - External PDA correction codes (0000-6200, 20-61)
- **crm-integration-error-specialist** - ECRM codes for porting collision detection (ECRMP043-047)
- **number-assignment-error-specialist** - AFM codes for KONTES porting coordination
- **german-glossary** - Translate German terms (AT, TNB, Besitzer, Eigentümer, U-Teil, K-Teil)
- **vnrm-prt-architecture** - Map RNVS porting errors to VNRM PRT microservices
- **vnrm-num-architecture** - Map RNB validation to VNRM NUM microservices

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, categories, usage instructions
- **[PFM_Codes_Reference.md](references/PFM_Codes_Reference.md)** - Porting flow message codes (37)
- **[RNBFM_Codes_Reference.md](references/RNBFM_Codes_Reference.md)** - RNB file message codes (39)
- **[WFA_Codes_Reference.md](references/WFA_Codes_Reference.md)** - Workflow A codes (20)
- **[WFB_Codes_Reference.md](references/WFB_Codes_Reference.md)** - Workflow B codes (10-20)
- **[WFC_Codes_Reference.md](references/WFC_Codes_Reference.md)** - Workflow C codes (50+)
- **[RNPS_Codes_Reference.md](references/RNPS_Codes_Reference.md)** - RNB process status codes (10-15)

## Best Practices

1. **Message Pairing** - Always validate P/L/Z message coordination (PFM)
2. **AT Calculations** - Use working day calendars, exclude holidays (RNBFM021-023)
3. **U-Teil/K-Teil** - Understand original vs correction semantics (WFA0137/0138)
4. **Syntax First** - Fix RNBFM syntax errors before business logic validation
5. **Correction Codes** - Validate correction code exists and matches original (RNBFM017-020)
6. **TNB Validation** - Verify Besitzer_Alt/Neu are valid carriers (WFA0003/0004)
7. **Timing Rules** - Apply 20 AT, 10 AT, 2 AT deadlines correctly
8. **German Translation** - Use german-glossary for error message translation
9. **Process Status** - Track RNB operation lifecycle with RNPS codes
10. **Workflow Complexity** - Choose WFA/WFB/WFC based on coordination needs

## Common Debugging Scenarios

**Scenario 1: Missing Porting Message (PFM004)**
- **Error**: PFM004 - DTAG export missing for competitor P-message
- **Check**: pack_val.sql:41 (FC_NVAL_P_SATZ)
- **Root Cause**: Competitor P-message exists, but DTAG L-message not generated
- **Resolution**:
  1. Query P/L message tables for carrier pair
  2. Check if L-message generation was triggered
  3. Verify no validation blocking L-message
  4. Generate missing L-message or investigate workflow

**Scenario 2: RNB Timing Violation (RNBFM021)**
- **Error**: RNBFM021 - Less than 20 AT between file date and setup date
- **Check**: pack_body_rnb.sql:100 (FC_AELTER_20AT)
- **Root Cause**: Regulatory 20 working day advance notice not met
- **Resolution**:
  1. Calculate working days (exclude weekends + holidays)
  2. Verify file_date and setup_date are correct
  3. Adjust setup_date forward to meet 20 AT requirement
  4. Or use correction code to update dates

**Scenario 3: U-Teil Structure Error (WFA0137)**
- **Error**: WFA0137 - U-Teil not completely filled
- **Check**: pack_body_rfnr.sql:243 (FC_U_STRUKT)
- **Root Cause**: Original message part missing required fields
- **Resolution**:
  1. Validate PDA file structure (all U-Teil fields present)
  2. Check if correction code requires filled U-Teil
  3. Verify original message exists and is complete
  4. Regenerate file with complete U-Teil structure

**Scenario 4: Invalid Correction Code (RNBFM017)**
- **Error**: RNBFM017 - Correction code invalid
- **Check**: pack_body_rnb.sql:95 (FC_KCODE_UNGUELTIG)
- **Root Cause**: Correction code not in PDA specification
- **Resolution**:
  1. Verify code exists in PDA spec (20, 21, 22, 25, 26, 60, 61)
  2. Check for typos (e.g., "62" instead of "61")
  3. Validate code is applicable to message type (P/L/R/E)
  4. Use correct PDA specification version (PDA19, PDA21.200)

**Scenario 5: Besitzer Validation Failed (WFA0003/0004)**
- **Error**: WFA0003 - Besitzer_Alt faulty or missing
- **Check**: pack_body_rfnr.sql:230 (FC_BESITZER_ALT)
- **Root Cause**: Previous possessor code invalid or not found in TNB table
- **Resolution**:
  1. Query TNB participant table for Besitzer_Alt code
  2. Verify carrier code format (e.g., D001-D999, T001, etc.)
  3. Check if carrier is active TNB participant
  4. Update Besitzer_Alt to valid carrier code

## Key External References

- **PDA Specification** - ITEX-PDA Spezifikation v20.0.0 (correction codes)
- **BNetzA Regulations** - Federal Network Agency porting rules
- **AT Calculation Logic** - German working day calendar
- **TNB Participant Database** - Valid carrier codes
- **BSA Specification** - Bereitstellungsauftrag (provisioning order) integration

---

**For detailed code tables with RNVS implementation locations, see individual reference files above**
