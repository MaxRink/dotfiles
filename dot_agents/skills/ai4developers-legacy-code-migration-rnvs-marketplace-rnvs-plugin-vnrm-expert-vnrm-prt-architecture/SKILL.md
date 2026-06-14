---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-prt-architecture
description: VNRM PRT (Porting Management) submodule architecture reference covering number portability operations, PDA (Portierungsdaten Austausch) message processing, carrier integration, and BNetzA regulatory compliance. This skill should be used when designing or implementing PRT microservices in phases 6-12 of the RNVS→VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-prt-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM PRT Architecture Expert Skill

## Purpose

Provides comprehensive architecture knowledge for the **VNRM PRT (PORTING MANAGEMENT)** submodule, which handles all aspects of telephone number portability including PDA message processing, carrier coordination, and regulatory compliance with BNetzA requirements.

## When to Use

Use this skill when you need to:
- **Design PRT microservices** during Phase 6 (microservice architecture design)
- **Understand PDA workflows** - porting data exchange between TNB carriers
- **Number portability operations** - callnumber and block porting management
- **State models** - porting order states and callnumber porting lifecycle
- **Integration patterns** - How PRT integrates with NUM, COM, and external TNB systems
- **Regulatory compliance** - BNetzA requirements and correction management
- **Message bus architecture** - Integration with Message Bus-based Tardis Horizon
- **Service level requirements** - HA vs OT service classification for porting operations

## Quick Reference

### Three Core Services

1. **FCPM (Fixednet Callnumber Porting Management)** - Individual callnumber porting workflows (HA level)
2. **FBPM (Fixednet Block Porting Management)** - Number block porting operations (HA level)
3. **FCCM (Fixed Callnumber Clearing Management)** - Correction and error management (OT level)

### Message Bus Integration

- **Tardis Horizon** - Central Message Bus-based message bus for porting notifications
- **No dedicated PBUS microservice** - Uses existing Tardis Horizon infrastructure
- **Event-driven architecture** - PDA messages flow through Message Bus topics

### Critical HA Services (24/7 Support)

- **fixednet-callnumber-porting-management-api** - Core callnumber porting
- **fixednet-block-porting-management-api** - Block porting operations

### Key PDA Message Types

| Type | German | Purpose | Sender |
|------|--------|---------|---------|
| L | Liefermeldung | Number export notification | Delivering TNB (abgebender TNB) |
| P | Portierungsmeldung | Number import confirmation | Receiving TNB (aufnehmender TNB) |
| Z | Zurückfall | Number return to owner | Current owner |
| 1K | Korrektur | Correction notification | Error-causing TNB |
| 7K | Information correction | Callnumber active info | Any involved TNB |

## Instructions

### 1. Understanding PRT's Critical Role

PRT coordinates number portability between all German TNB carriers (approximately 160 TSPs):
- **NUM services** → PRT validates and reserves callnumbers for porting operations
- **COM services** → PRT depends on RDM for TNB/PK validation and config server
- **External TNB** → PDA file exchange for L/P/Z message coordination
- **BNetzA** → Regulatory compliance and porting number (PK) management
- **COR services** → Error correction workflows and problem resolution
- **Tardis Horizon** → Central Message Bus message bus for event distribution

### 2. PDA Process Flow

**Standard Porting Workflow:**
1. **Porting Request** → Customer initiates number transfer between TNB carriers
2. **L-Message** → Delivering TNB sends export notification (status "L")
3. **P-Message** → Receiving TNB confirms import (status "P")
4. **State Validation** → Both messages must match: same date, complementary PKs
5. **Completion** → Porting order transitions to "PORTED" state

**Parallel Processing (PROVISIONAL_IMPORT):**
- Phone number import and booking occur in parallel
- CRM-T books numbers not in DTAG inventory as "vi" (provisional import)
- LWL implementation message (ModOSS) triggers PDA_MESSAGE_OUT with status "P"

**Error Scenarios:**
- **Mismatched dates** → PROBLEM state, correction required
- **Unknown PK** → Validation failure, rejection
- **Missing P-message** → WAITING state until timeout
- **Invalid data** → REJECTED state, correction workflow

### 3. Porting Order State Model

| State | German | Definition | Business Logic |
|-------|--------|------------|----------------|
| CHECKED | Integrität geprüft | PDA record syntactically validated | Internal order created, no syntax errors |
| PROVISIONAL_IMPORT | Vorläufiger Import | Parallel import/booking in progress | CRM-T books numbers, awaits LWL confirmation |
| WAITING | Wartend | Waiting for second notification from TSP | Order waits for matching L/P pair |
| PORTED | Portierung abgeschlossen | Both L and P messages received and validated | Matching date, complementary PKs (PK_auf ≠ PK_ab) |
| PROBLEM | Ungültig | Data validation failed | Unknown PK, same PK values, past date, mismatched pairs |
| REJECTED | Abgelehnt | Porting rejected due to errors | Manual intervention required |
| CORRECTION | Korrekturmeldung | Correction message triggered | Send to causing TNB via PDA |

### 4. Database Schema Overview

**PORTING_ORDER Table (Core Entity):**
- `order_id` - Unique internal porting order identifier (Numeric, PK)
- `file_type` - PDA file type (1D=default, 1Q=request, 1R=response, 1K=correction, 7K=info correction, 1P=closing, 1I=info)
- `ndc` - National destination code (ONKz) from RDM validation
- `sn_from/sn_to` - Subscriber number range (without ONKz)
- `porting_date` - Planned porting execution date
- `PK_old/PK_new` - Delivering/receiving TNB porting identifiers (Format: Dxxx)
- `notification_published` - Boolean: published via PDA or received from TSP
- `porting_state` - completed/published/unpublished
- `order_state` - Current workflow state
- `order_open_date` - Order creation timestamp
- `porting_activation_date` - Actual porting execution date

**PORTING_ENTRY Table (PDA Records):**
- Raw PDA file records after formal validation
- Links to parent porting order via `order_id`
- Contains original notification data (L/P/Z messages)
- File metadata (file_name, file_type, notification_date)

**FCN_PORTING_INVENTORY Table:**
- Current porting state per callnumber
- Historical porting chain tracking
- External porting ID references (HPK, PK)
- Links to `last_porting_order_id`

**CORRECTION_MESSAGE Table:**
- PDA correction workflow management
- Links to problematic porting orders
- Correction codes per BNetzA specification Chapter 4.7.10

### 5. Integration Patterns

**With NUM Submodule:**
```
PRT → NUM: Validate callnumber availability
PRT → NUM: Reserve numbers for porting
PRT ← NUM: Confirm reservation success
PRT → NUM: Update porting status
```

**With Tardis Horizon (Message Bus):**
```
PRT → Tardis: Publish porting events
PRT ← Tardis: Consume PDA notifications
PRT ↔ Tardis: Event-driven coordination
External TNB ↔ Tardis: PDA file distribution
```

**With External TNB:**
```
TNB → PRT: Send PDA files (L/P/Z messages)
PRT → TNB: Distribute porting notifications
PRT ↔ TNB: Exchange correction messages (K-files)
```

**With BNetzA:**
```
PRT → BNetzA: Validate porting numbers (PK)
PRT ← BNetzA: Receive regulatory updates
PRT → BNetzA: Report compliance status
```

### 6. Central Porting Service Decision

**Deutsche Telekom Decision:**
- **No central porting service** - Telekom maintains own porting database
- **Direct PDA participation** - Full control over data correctness
- **Independent validation** - Own porting number management

**Alternative (Not Used):**
- TSPs can use central porting services to disclaim own databases
- Central service handles data correctness and PDA exchange
- Telekom chose direct participation for control and compliance

## Integration with Other VNRM Skills

- **vnrm-num-architecture** - PRT depends on NUM for callnumber validation and reservation
- **vnrm-com-architecture** - PRT uses COM's RDM for TNB validation and config server
- **vnrm-cor-architecture** - COR handles PRT error correction workflows
- **vnrm-spe-architecture** - SPE synchronizes legacy porting data with PRT
- **german-glossary** - For translating German terms (PDA, TNB, ONKz, PK, BNetzA)

## Progressive Disclosure

- **SKILL.md** (this file) - Overview, when to use, quick reference
- **[REFERENCE.md](REFERENCE.md)** - Complete architecture specifications (services, schemas, APIs)
- **[examples.md](examples.md)** - Practical usage patterns and integration examples

## Best Practices

1. **PDA compliance** - Follow official BNetzA PDA specification v20.0.3 strictly
2. **State model adherence** - Implement all porting order states with proper transitions
3. **TNB coordination** - Handle asynchronous L/P message pairs with timeout logic
4. **Error handling** - Generate appropriate correction codes per PDA specification
5. **Database-per-service** - FCPM, FBPM, FCCM each have separate PostgreSQL schemas
6. **Audit trail** - Log all PDA message processing with timestamps and sources
7. **Regulatory compliance** - Maintain BNetzA-compliant porting records and reporting
8. **Idempotency** - Handle duplicate PDA messages gracefully
9. **Performance** - Process high-volume PDA files efficiently (daily exchanges)
10. **Event-driven design** - Leverage Tardis Horizon for loose coupling
11. **Provisional import handling** - Support parallel CRM-T booking workflows
12. **ONKz validation** - Use COM RDM for National Destination Code validation

## Key External References

- **PDA Specification** - [BNetzA Official Documentation](https://www.aknn.de/oeffentliche-dokumente/uak-tnbvnb-wechsel/)
- **Current PDA Version** - [PDA Specification v20.0.3](https://www.aknn.de/fileadmin/uploads/oeffentlich/24-06-26_ITEX-PDA_Spezifikation_PDA_20-0-3.pdf)
- **TNB Directory** - [BNetzA Porting Numbers Registry](https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Nummerierung/Portierungskennungen/Verzeichnis.html)
- **Error Codes** - PDA specification Chapter 4.7.10 correction codes

---

**For complete PRT architecture details, see [REFERENCE.md](REFERENCE.md)**
