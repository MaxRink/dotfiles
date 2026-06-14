---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-rnvs-expert-porting-data-exchange-specialist
description: This skill should be used when the user asks to "analyze PDA processing", "debug porting workflows", "implement correction message generation", "understand PDA correction codes", "validate PDA timing rules", "explain U-Teil/K-Teil structure", or mentions specific PDA codes (e.g., "what is code 2510", "code 0300", "6000-6200"). Provides expert knowledge of PDA (Portierungsdaten Austausch) protocol covering all 72 correction codes, timing rules (AT/KT), pairing validations, and RNVS implementation patterns.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/rnvs-expert/skills/porting-data-exchange-specialist by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# PDA (Porting Data Exchange) Specialist Skill

## Purpose

Provides **comprehensive expert-level knowledge** of the **PDA (Portierungsdaten Austausch / Porting Data Exchange)** protocol used for telecommunications number portability in Germany. This skill covers:

- **72 PDA correction codes** from ITEX-PDA Specification v20.0.0
- **Business semantics** and regulatory compliance (BNetzA, §59 TKG)
- **Timing constraints** (AT working days, KT calendar days)
- **RNVS implementation patterns** across PL/SQL, Java, C++, TCL
- **U-Teil/K-Teil message structure** (original vs correction parts)
- **Validation and pairing rules**

The Reference.md file provides detailed correction code reference tables and is **one component** of this skill's broader PDA protocol expertise.

## When to Use

Use this skill when you need to:
- **Understand PDA protocol** - Learn how porting data exchange works
- **Identify correction codes** - Understand what a specific PDA code means (e.g., "What is code 2510?")
- **Debug porting workflows** - Trace correction message generation and validation logic
- **Implement correction logic** - Generate K-Teil (correction part) messages with proper U-Teil structure
- **Validate timing rules** - Apply AT (working days) and KT (calendar days) deadline calculations
- **Code pairing validation** - Ensure objection codes (25XX) match their operations (41XX-45XX)
- **Understand U-Teil/K-Teil semantics** - Original vs correction message part structure
- **Analyze RNVS implementation** - Map correction codes to PL/SQL packages and business logic
- **Version differences** - Understand PDA specification evolution (PDA19, PDA21.200)
- **Regulatory compliance** - Apply BNetzA rules and §59 TKG requirements
- **Message structure design** - Design PDA message formats for VNRM implementation

## Quick Reference

### Correction Code Categories (72 Total)

| Category | Code Range | Count | Purpose |
|----------|------------|-------|---------|
| **Portierungs-Korrekturcodes** | 0000-6200 | 58 | Phone number porting corrections |
| **RNB-Korrekturcodes** | 20-61 | 6 | Number block corrections |
| **PK-Aktionscodes** | 00, 25, 26 | 3 | Porting number shutdown actions |
| **Info-Kennungen** | 01-05 | 5 | Informational messages |

### Most Critical Correction Codes

| Code | Category | Business Reason | Critical Rule |
|------|----------|-----------------|---------------|
| **0300** | Format Correction | Porting date change | **2AT publication delay** |
| **2547** | Objection | Query station objection | **10AT delivery rule** |
| **4100** | Range Op | Consolidation (2-10 ranges) | Must pair with 2510 for objection |
| **6000/6100/6101** | Single Message | Missing L/P records | Different Owner-Neu handling per status |
| **60/61** | RNB Single | Missing RNB records | **10AT + 20AT dual validation** |
| **05** | Info | Deadline reduction | **10AT → 3AT** reduction period |

### Timing Rules Summary

| Rule Type | Codes | Deadline | Business Context |
|-----------|-------|----------|------------------|
| **2AT** | 0300, 20, 21, 25 | 2 working days | Date change delay, RNB withdrawals/objections |
| **10AT** | 2547, 60, 61 | 10 working days | Query station objection, single message waiting |
| **20AT** | 60, 61 | 20 working days | Minimum time before setup date |
| **6 Months** | 22, 26 | 6 calendar months | R/E message withdrawal deadline |
| **30 KT** | 00 | 30 calendar days | PK shutdown notice |
| **5 KT** | 25, 26 | 5 calendar days | PK objection/withdrawal |

### Pairing Validations (pack_body_pm.sql)

```
2510 ↔ 4100  (Objection to range consolidation)
2520 ↔ 4200  (Objection to range division)
2530 ↔ 4300  (Objection to range-to-10MSN)
2540 ↔ 4400  (Objection to 10MSN-to-range)
2550 ↔ 4500  (Objection to old stock expansion)
```

## Understanding PDA Correction Codes

### Core Concepts

**U-Teil vs K-Teil (Original vs Correction):**
- **U-Teil (Ursprungsteil)** - Original message data being corrected
- **K-Teil (Korrekturteil)** - Correction data with new values
- **Empty K-Teil** - Indicates withdrawal (codes 2000-2450)
- **Special K-Teil** - Codes 4300/4710/4730 store porting date only in K-Teil

**Code Formats:**
- **Portierungs-Korrekturcodes**: 4-digit (e.g., 0300, 2510, 4100)
- **RNB-Korrekturcodes**: 2-digit (e.g., 20, 60)
- **PK-Aktionscodes**: 2-digit (e.g., 00, 25)
- **Info-Kennungen**: 2-digit (e.g., 01, 05)

### Detailed Code Information

For complete implementation details, business rules, and RNVS code locations, consult **[PDA_Correction_Codes.md](references/PDA_Correction_Codes.md)**:

**Porting Corrections (Sections 1.1-1.9):**
- Format Corrections (0000-0600) → Section 1.1
- Withdrawal Codes (2000-2450) → Sections 1.2-1.4
- Objection Codes (25XX) → Section 1.5
- Special Codes (3000, 3025) → Section 1.6
- Range Operations (4100-4500) → Section 1.7
- Query Station Codes (4700-4730) → Section 1.8
- Single Messages (6000-6200) → Section 1.9

**Other Message Types:**
- RNB Correction Codes (20-61) → Section 2
- PK Action Codes (00, 25, 26) → Section 3
- Info Codes (01-05) → Section 4

Each code entry includes:
- Business reason (from ITEX-PDA specification)
- RNVS implementation file locations with line numbers
- Complete description covering all processing stages
- Critical timing rules (AT/KT) and validation logic

## Implementation Mapping

### Primary PL/SQL Packages (95% of logic)

| Package | Lines | Purpose |
|---------|-------|---------|
| **pack_body_rfnr.sql** | 4,500+ | Porting corrections (0000-6200) |
| **pack_body_rnb.sql** | 4,000+ | Number block corrections (20-61) |
| **pack_body_tnb.sql** | 5,200+ | TNB operations (Info 01-05, PK 00/25/26) |
| **pack_body_pm.sql** | 3,500+ | Porting message processing, pairing validation |
| **pack_body_generator.sql** | 9,000+ | PDA file generation, U-Teil/K-Teil logic |
| **pack_body_pdba.sql** | 4,200+ | PDA export/import operations |
| **pack_body_bea.sql** | 6,000+ | Processing orchestration |
| **pack_body_val.sql** | 4,800+ | Validation and generation |

### Supporting Technologies (5% of logic)

- **Java** - GUI display, user selection (~5 files)
- **C++** - Use case orchestration via CORBA (~3 files)
- **TCL** - Batch automation (e.g., start.kc_4700_4720_flag_loeschen.tcl)

## Integration with Other VNRM Skills

- **vnrm-prt-architecture** - PRT implements PDA message processing using these correction codes
- **german-glossary** - Translate German terms (AT, KT, TNB, PK, BNetzA, §59 TKG)
- **vnrm-num-architecture** - Number validation for porting operations
- **vnrm-cor-architecture** - Correction workflow management

## Progressive Disclosure

### Core Documentation
- **SKILL.md** (this file) - Overview, quick reference, critical correction codes, usage instructions

### Detailed References

Consult these references for comprehensive information:

- **[PDA_Correction_Codes.md](references/PDA_Correction_Codes.md)** - Complete 72-code reference table with RNVS implementation locations
- **[PDA_Deadlines.md](references/PDA_Deadlines.md)** - Comprehensive PDA timing rules and deadline calculations
- **[PDA-Process-Overview-Documentation.md](references/PDA-Process-Overview-Documentation.md)** - Complete process documentation covering:
  - All 9 message types with detailed scenarios:
    - **Rufnummern (phone numbers)**: P, L, Z
    - **RNBs (number blocks)**: E, P, L, R (no Z for RNBs)
    - **Corrections**: K (for P/L/Z), C (for E/R)
    - **Info**: I, DR
  - Process dependencies and validation rules
  - Timeline calculations and business rules
  - Quick reference tables and troubleshooting guides

### Visual Diagrams

Two PlantUML diagrams for visual understanding:

- **[PDA-Process-Mindmap.puml](references/PDA-Process-Mindmap.puml)** - Mindmap overview of all PDA procedures organized by category (best for learning structure and finding specific procedures)
- **[PDA-Process-Dependencies.puml](references/PDA-Process-Dependencies.puml)** - Component diagram showing message dependencies and relationships (best for understanding validation rules and implementation sequences)

## Using the References

### When to Use Which Resource

**For Code Lookup:**
- Check SKILL.md Quick Reference tables first
- Use PDA_Correction_Codes.md for complete 72-code details with RNVS file locations

**For Deadline Calculations:**
- Use PDA_Deadlines.md for AT/KT calculations and timing rules
- Reference PDA-Process-Overview-Documentation.md for complete timeline examples

**For Process Understanding:**
- Start with PDA-Process-Mindmap.puml diagram for visual overview
- Read PDA-Process-Overview-Documentation.md sections for detailed process flows
- Use PDA-Process-Dependencies.puml to understand message relationships

**For Implementation:**
- Review PDA-Process-Dependencies.puml for mandatory dependencies
- Check PDA_Correction_Codes.md for RNVS package locations (pack_body_*.sql files)
- Reference PDA-Process-Overview-Documentation.md for business rules and validation logic

**For Troubleshooting:**
- Use PDA-Process-Dependencies.puml to identify missing prerequisites
- Check PDA_Deadlines.md to verify timing compliance
- Review Common Debugging Scenarios in SKILL.md below
- Consult PDA-Process-Overview-Documentation.md for detailed validation rules

## Best Practices

1. **Always validate pairing** - Check 25XX ↔ 41XX-45XX objection-operation pairs
2. **Apply timing rules strictly** - AT vs KT, publication delays, deadline calculations
3. **U-Teil/K-Teil semantics** - Understand empty vs filled correction parts
4. **Version awareness** - Check PDA specification version (PDA19, PDA21.200)
5. **Regulatory compliance** - Apply BNetzA rules and §59 TKG requirements
6. **Code coverage** - 97% implementation rate (70/72 codes found)
7. **Owner validation** - Verify Owner-Neu, Owner-Alt, Dateiherkunft relationships
8. **Query station flags** - Use cleanup scripts for 4700/4720 flag maintenance
9. **Single message timing** - Apply 10AT/20AT dual validation for codes 60/61
10. **Deadline reduction** - Only apply Info 05 during authorized reduction period

## Common Debugging Scenarios

**Scenario 1: Code 2510 Validation Failure**
- **Issue**: 2510 used without matching 4100
- **Check**: pack_body_pm.sql:2613 pairing validation
- **Fix**: Ensure K-Teil code is 2510 AND original message code is 4100

**Scenario 2: Code 0300 Not Delayed**
- **Issue**: Date change published immediately
- **Check**: pack_body_pm.sql:1752-1763 delay logic
- **Fix**: Apply 2AT (2 working days) publication delay

**Scenario 3: Code 60/61 Timing Violation**
- **Issue**: Single message rejected despite existing P/L record
- **Check**: pack_body_rnb.sql:3875-3986 dual validation
- **Fix**: Verify both 10AT message age AND 20AT setup distance

**Scenario 4: Code 6101 Owner-Neu Not Empty**
- **Issue**: Z-status single message has filled Owner-Neu
- **Check**: pack_body_generator.sql:7429 - must be empty for 6101
- **Fix**: Use 6100 for L-status, 6101 for Z-status (PDA 21.200 split)

## Key External References

- **PDA Specification v20.0.0** - ITEX-PDA Spezifikation (09.05.2023)
- **BNetzA Regulations** - Federal Network Agency compliance rules
- **§59 TKG** - Telecommunications Act §59 (Weiterversorgung - continued service)
- **PDA Version Evolution** - Track PDA19, PDA21.200 specification changes

---

## Reference Files

**For detailed information, consult these references:**

- **[PDA_Correction_Codes.md](references/PDA_Correction_Codes.md)** - Complete 72-code reference table with RNVS implementation locations
- **[PDA_Deadlines.md](references/PDA_Deadlines.md)** - Comprehensive PDA timing rules and deadline calculations
- **[PDA-Process-Overview-Documentation.md](references/PDA-Process-Overview-Documentation.md)** - Complete process documentation with scenarios, dependencies, and quick reference tables
- **[PDA-Process-Mindmap.puml](references/PDA-Process-Mindmap.puml)** - Visual mindmap of all PDA procedures
- **[PDA-Process-Dependencies.puml](references/PDA-Process-Dependencies.puml)** - Visual diagram of message dependencies
