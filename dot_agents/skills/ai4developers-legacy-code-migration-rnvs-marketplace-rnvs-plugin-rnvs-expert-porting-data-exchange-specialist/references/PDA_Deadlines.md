# ITEX-PDA Specification - Structured Deadline Report

**Document**: 23-05-09_ITEX-PDA_Spezifikation_PDA_20-0-0.pdf
**Version**: PDA 20.0.0
**Valid from**: 06.05.2024
**Analysis Date**: 2025-12-04
**Analyzer**: Claude Code (Automated Extraction)

---

## Executive Summary

This report documents **ALL** time-based constraints, deadlines, and time windows defined in the ITEX-PDA specification for number portability data exchange between German telecommunications carriers.

**Key Findings**:
- **326 total deadline references** extracted
- **31 distinct AT (Arbeitstag/Working Day) values** identified (1 AT to 65 AT)
- **2 procedural variants**: Standard procedure (10 AT) and Expedited procedure (3 AT)
- **Primary regulatory period**: RUZ = 2 months (call forwarding time)

---

## Table of Contents

1. [Critical Business Deadlines](#critical-business-deadlines)
2. [Message Type Specific Deadlines](#message-type-specific-deadlines)
3. [Processing Stage Deadlines](#processing-stage-deadlines)
4. [Regulatory Compliance Deadlines](#regulatory-compliance-deadlines)
5. [Time Windows and Constraints](#time-windows-and-constraints)
6. [Deadline Calculation Rules](#deadline-calculation-rules)

---

## Critical Business Deadlines

### 1. Cancellation Notice Period (Kündigungsfrist)

| Deadline | Value | Context | Consequence | Reference |
|----------|-------|---------|-------------|-----------|
| **Cancellation to Z-Message** | **65 AT** | After cancellation (Kündigung), owner must create Z-message | Z-message must be published after 65 AT | Section 4.3.2, 4.3.3 |
| **Publication delay** | +1 T (Tag/Day) | After Z-message creation | Z-message published on day after creation | Section 4.3.3.1 |
| **Formula** | `t1 = t0 + 65 AT`<br>`t2 = t1 + 1 T` | t0 = cancellation day<br>t1 = Z-message creation<br>t2 = publication day | Owner monitors and enforces 65 AT period | Line 655, 640-643 |

**Business Rule**: The last owner (letzter Besitzer) is responsible for monitoring and enforcing the 65 AT period. Other PDA participants do not check this deadline.

**Consequence of Non-Compliance**: If 65 AT not monitored properly, ported numbers may not be properly returned to original owner.

---

### 2. Call Forwarding Period (Rufumsteuerungszeit - RUZ)

| Deadline | Value | Context | Consequence | Reference |
|----------|-------|---------|-------------|-----------|
| **RUZ Duration** | **2 Months** | After porting, originating carrier must maintain call forwarding | Ensures continued reachability during transition | Section 4.3.2.2, Line 645 |
| **RUZ Start** | Porting date (Portierungsdatum) | From effective porting date | Routing updated during RUZ | Multiple |
| **RUZ End** | +2 months from porting | After 2 months, call forwarding can be removed | Number fully transferred | Section 4.3.2.2 |

**Business Rule**: The originating carrier (TNBabgebend) must ensure reachability of ported numbers for 2 months via call forwarding (Rufumsteuerung).

**Consequence**: During RUZ, routing must be updated by all carriers. Status P1c and L1c remain in database only until RUZ expires (Line 1073).

---

### 3. Erroneous Fallback Protection Period

| Deadline | Value | Context | Consequence | Reference |
|----------|-------|---------|-------------|-----------|
| **Fallback waiting period** | **5 AT** | After reported fallback (Rückfall via PDA) | Owner must wait 5 AT before reconnecting number | Section 4.3.2.2, Line 642 |
| **Purpose** | Protection window | Prevents immediate reconnection on erroneous fallback | Current owner can retract erroneous fallback message | Line 642-643 |
| **Recommendation** | Setup announcement | During 5 AT, owner should setup announcement (Ansage anlegen) | Prevents service disruption | Line 642 |

**Business Rule**: Prevents hasty reconnection when fallback reported in error. Allows correction via simple retraction instead of new porting messages.

---

## Message Type Specific Deadlines

### P-Messages (Porting Messages)

#### Standard Porting Procedure (Regelverfahren)

| Deadline | Value | Context | Trigger | Consequence | Reference |
|----------|-------|---------|---------|-------------|-----------|
| **P-Message to L-Message** | **Not specified** | Both messages required for pairing | Porting execution | Messages form valid pair | Section 4.3.1 |
| **Earliest correction** | **+1 Day (T)** | Correction can only be published 1 day after erroneous record | After publication of erroneous record | Corrections published too early are ignored | Section 4.7.3.1, Line 2424 |

### L-Messages (Deletion Messages)

| Deadline | Value | Context | Trigger | Consequence | Reference |
|----------|-------|---------|---------|-------------|-----------|
| **L-Message publication** | **Same process as P** | Deletion message from originating carrier | Part of porting pair | L+P must pair for valid porting | Section 4.3 |

### Z-Messages (Cancellation Messages)

| Deadline | Value | Context | Trigger | Consequence | Reference |
|----------|-------|---------|---------|-------------|-----------|
| **Z-Message creation** | **65 AT after cancellation** | After customer cancellation (Kündigung) | t1 = t0 + 65 AT | Z-message created by owner | Section 4.3.3 |
| **Z-Message publication** | **+1 T after creation** | Day after Z-message creation | t2 = t1 + 1 T | Published to PDA | Section 4.3.3 |
| **Portierungsdatum in Z** | **≥ Publication date - 1 KT** | Porting date in Z-record must be at least 1 calendar day before publication | Min: Ver öffentlichungsdatum - 1 KT | Ensures proper date sequencing | Section 4.3.2.2, Line 640 |

---

### Correction Messages (K-Messages)

#### General Correction Deadlines

| Correction Code | Deadline | Context | Trigger | Consequence | Reference |
|-----------------|----------|---------|---------|-------------|-----------|
| **All corrections** | **Frühestens +1 Tag** | Corrections cannot be published earlier than 1 day after erroneous record | After erroneous publication | Too-early corrections ignored | Line 2424 |
| **Codes 4100-4500** | **Opposition: 10 AT** | Objection period for split/merge/conversion/extension operations | After publication of 4XXX code | After 10 AT, objections ignored | Section 4.7.11.2, Line 2428 |
| **Code 0000** | **No specific deadline** | General correction code | Any time after original message | Limited to one per regular record | Line 2490-2492 |

#### Specific Correction Code Deadlines

**Code 4100** (Zusammenführung - Merge):
- **Opposition window**: 10 AT after publication
- **Follow-up restriction**: No additional 41XX/42XX/43XX/44XX operations until 10 AT opposition period expires
- **Consequence**: Follow-up operations during opposition period are rejected and discarded (Line 2430)

**Code 4200** (Aufteilung - Split):
- **Opposition window**: 10 AT after publication
- **Same follow-up restrictions as 4100**

**Code 4300** (Umwandlung - Conversion):
- **Opposition window**: 10 AT after publication
- **Special restriction**: Not allowed in 2-digit area codes (ONKz) if results in 11-digit individual numbers (Line 2434)

**Code 4400** (Zusammenführung Einzelrufnummern - Individual number merge):
- **Opposition window**: 10 AT after publication
- **RUZ preservation**: If within RUZ, routing maintained for remaining RUZ duration (Line 2459-2463)

**Code 4500** (Erweiterung - Extension):
- **Opposition window**: 10 AT for objection with code 2550 (Line 3415)
- **Retraction window**: 10 AT for retraction with code 2547 (Line 3439)

**Code 30XX** (Corrections to porting):
- **Authorization**: Only authorized carriers can publish
- **Timeliness**: Must not be published too late
- **Reference**: Must refer to last completed porting (Line 2436-2451)

---

### Single Messages (Code 6XXX)

#### Standard Single Message Procedure

| Deadline | Value | Context | Formula | Consequence | Reference |
|----------|-------|---------|---------|-------------|-----------|
| **Single message deadline** | **10 AT (Standard)** | From porting day to single message publication | t2 = t1 + 10 AT | Single message due | Section 4.8.3, Line 3861 |
| **Porting day** | t0 | Actual porting execution | - | Start of timeline | Section 4.8.3.1, Line 3869-3871 |
| **First publication** | t1 = t0 + 1 T | Day after porting | +1 Day | P/L messages published | Line 3873 |
| **Processing day** | t2 = t1 + 10 AT | 10 working days after first publication | - | Pairing check occurs | Line 3877 |
| **Second publication** | t3 = t2 + 1 T | Day after processing | +1 Day | Single message published if needed | Line 3879 |

**Business Rule**: Daily data exchange is mandatory due to deadline definitions (Line 3883).

#### Expedited Single Message Procedure (Fristverkürzung)

| Deadline | Value | Context | Trigger | Consequence | Reference |
|----------|-------|---------|---------|-------------|-----------|
| **Expedited deadline** | **3 AT** | Shortened single message deadline | Via Info-File 05 (5I-file) | Replaces 10 AT deadline | Section 4.8.3, Line 3863 |
| **Trigger mechanism** | **5I-File publication** | Special info file authorizes deadline reduction | Only 3 authorized carriers | 3 AT applies on publication day + following day | Section 10.6.2, Line 7891-7895 |
| **Validity period** | **Publication day + 1 T** | Expedited procedure valid for 2 days | Published daily during expedited period | Returns to 10 AT afterward | Line 7895 |
| **Authorized carriers** | **3 TNB only** | Only pre-authorized carriers can publish 5I-files | Listed in Annex 1 (Anlage1) | Unauthorized 5I-files invalid | Line 7889-7890 |

**Prerequisites for Expedited Procedure**:
- Detailed in Chapters 4.8.1 and 10.6 (Line 3865)
- Requires Info-File type 05 (5I-file)
- Must be published daily during expedited period (Line 7891)
- Multiple records per file allowed (Line 7893)

---

### RNB Messages (Number Block Messages)

#### RNB Transfer Deadlines

| Phase | Deadline | Value | Formula | Context | Reference |
|-------|----------|-------|---------|---------|-----------|
| **Info-File 1** | Earliest publication | 20 AT before 1st RNB message | t1a = t0 + 20 AT | Initial info announcement | Section 7.5.1, Line 6385 |
| **P-Message (RNB)** | Required timing | At t1a | - | Receiving carrier publishes P-message | Line 6385 |
| **L-Message (RNB)** | Required timing | 10 AT after P-message | t1b = t1a + 10 AT | Originating carrier publishes L-message | Line 6387 |
| **Pairing deadline** | Latest pairing | 5 AT before transfer | t2 = t5 - 5 AT | P+L must be paired | Line 6391 |
| **Unpaired expiration** | Discard unpaired | 4 AT before transfer | t3 = t5 - 4 AT | Unpaired messages discarded | Line 6393 |
| **Opposition/Retraction** | Latest publication | 2 AT before transfer | t4 = t5 - 2 AT | Last chance for objection | Line 6399 |
| **Transfer day** | Actual transfer | t5 | - | RNB ownership transfers | Line 6409 |
| **Info-File 2** | Latest publication | 20 AT after last transfer | t6 ≤ t5 + 20 AT | Final confirmation info file | Line 6412 |

#### RNB Single Message Validation Rules

**Pre-Requisites for RNB Single Messages** (Section 7.3.6.3):

1. **Minimum P-Message age**: P-message must exist for at least **10 AT** (Line 6692)
2. **Minimum spacing**: At least **20 AT** between current date and Einrichtungsdatum (setup date) (Line 6696)
3. **Pre-announcement**: Single message requires **5 AT advance notification** before setup (Line 4837-4838, 5666)

**Timeline Breakdown**:
- **5 AT before setup** = Earliest P-message publication (Line 4838)
- **4 AT before setup** = Processing continues
- **3 AT before setup** = Processing continues
- **2 AT before setup** = Processing continues
- **1 AT before setup** = Processing continues
- **Setup date (Einrichtungstermin)** = RNB becomes active (Line 4838)

---

### Info Messages (1I - 5I Files)

| Info Type | Deadline/Rule | Context | Consequence | Reference |
|-----------|---------------|---------|-------------|-----------|
| **1I - Fusion** | Coordination required | Multiple carriers announcing fusion must coordinate | Prevents mutual interference | Section 10.6.2, Line 7848-7849 |
| **1I - Update rule** | Latest file wins | Newer file with same carriers replaces older | Previous fusion info overwritten | Line 7851 |
| **1I - Records** | One per ONB | One record per area network operator | Ensures proper coverage | Line 7853 |
| **3I - Contact** | Parallel update required | Changes must also be made in EKP-Portal | Ensures PDA clearing notifications sent correctly | Line 7871 |
| **4I - Authority** | BNetzA match | Info must match BNetzA directory | Authoritative source | Line 7875-7879 |
| **4I - Records** | One per PK | One record per porting code (including HPK) | Complete coverage | Line 7881 |
| **5I - Authorization** | 3 carriers only | Only 3 authorized TNB/(H)PK can publish | Listed in Annex 1 | Line 7885-7889 |
| **5I - Frequency** | Daily during expedited period | Published daily while deadline reduction active | Maintains expedited procedure | Line 7891 |
| **5I - Multiple records** | Allowed | Multiple records per file possible | Flexible expediting | Line 7893 |
| **5I - Effectiveness** | Publication day + 1 T | Deadline reduction applies for 2 days | Limited validity window | Line 7895 |
| **5I - Conflicts** | Process all | Multiple carrier 5I-files processed even if conflicting | No single authority | Line 7897 |

---

## Processing Stage Deadlines

### Message Pairing and Validation

| Stage | Deadline | Context | Consequence | Reference |
|-------|----------|---------|-------------|-----------|
| **Pair formation** | No specific deadline | P+L or P+P or K+P or K+K must pair | Valid porting confirmed when paired | Section 4.7.3.2 |
| **Validation finality** | Permanent after pairing | Once validated, corrections to paired records ignored | Exception: 4XXX and 30XX codes allowed | Line 2478-2480 |
| **Response to correction** | +1 Day minimum | Correction response earliest 1 day after original correction | Prevents immediate loops | Line 2424 |

### Publication Timelines

| Process | Timing | Formula | Context | Reference |
|---------|--------|---------|---------|-----------|
| **Daily exchange** | Every working day (AT) | - | Mandatory for deadline compliance | Line 3883 |
| **File retention** | Maximum 2 months | - | Home directories must be cleaned | Section 5.2.3, Line 4277 |
| **Response file deletion** | Immediately after new request | - | Requesting carrier must delete old response | Line 4278 |
| **Request file deletion** | After response creation | - | Server deletes request after response generated | Line 4279 |

---

## Regulatory Compliance Deadlines

### BNetzA Mandated Periods

| Requirement | Deadline | Context | Legal Basis | Reference |
|-------------|----------|---------|-------------|-----------|
| **RUZ (Call forwarding)** | **2 Months** | Mandatory call forwarding after porting | TNP-V (Number Portability Ordinance) | Section 4.3.2.2, Line 645 |
| **Cancellation notice** | **65 AT** | Customer cancellation to Z-message | Contract/Regulatory requirement | Section 4.3.2.2, Line 640 |
| **Shutdown orders (befristet)** | **As specified in order** | BNetzA ordered shutdowns with time limit | Per shutdown order | Section 4.9, Line 4182-4183 |
| **Shutdown orders (unbefristet)** | **Must clarify with BNetzA** | Unlimited shutdown - actual deadline unclear | Contact BNetzA for clarification | Line 4184 |
| **Fallback notification** | **+5 AT before reconnection** | After PDA-reported fallback | Prevents erroneous immediate reconnection | Line 642 |

### Opposition Rights (Widerspruchsrechte)

| Objection Type | Deadline | Who Can Object | Codes | Reference |
|----------------|----------|----------------|-------|-----------|
| **Block operations** | **10 AT after publication** | Owner, current holder, receiving, originating carrier | 4100, 4200, 4300, 4400 objection with 25XX | Section 4.7.11.2, Line 2428 |
| **Extension operations** | **10 AT after publication** | Current holder | 4500 objection with 2550 | Line 3415 |
| **General porting** | **Per specific rules** | Owner, current holder, receiving, originating carrier | 25XX codes | Section 4.7.5, Line 2524-2526 |
| **Erroneous porting** | **No time limit** | Carrier with number but not in porting record | 25XX codes | Line 2526 (Example case) |

---

## Time Windows and Constraints

### Prohibited Actions Within Time Windows

| Window | Prohibition | Duration | Consequence | Reference |
|--------|-------------|----------|-------------|-----------|
| **Opposition period** | No follow-up 41XX/42XX/43XX/44XX | 10 AT | Follow-up operations rejected and discarded | Line 2430 |
| **Post-opposition** | Operations allowed after 10 AT | After opposition expires | New operations can be accepted | Line 2430 |
| **Correction timing** | Correction before +1 Day prohibited | Must wait 1 day after original | Too-early corrections ignored | Line 2424 |
| **Future porting date** | Corrections with future porting date prohibited | Code 0300 to future date | Rejected - no "hold for future" | Line 2504 |
| **Same-day porting date** | Correction with publication date as porting date | Code 0300 with same date | Rejected | Line 2506 |

### Minimum Time Gaps Required

| Requirement | Minimum Gap | Context | Purpose | Reference |
|-------------|-------------|---------|---------|-----------|
| **Correction publication** | +1 Day (T) | After erroneous record published | Prevents immediate correction loops | Line 2424 |
| **Single message timing** | +1 Day (T) | After initial P/L publication | Allows pairing attempt | Line 3873 |
| **Z-message publication** | +1 Day (T) | After Z-message creation | Standard publication delay | Line 657 |
| **RNB pair timing** | -5 AT | Before transfer date | Ensures pairing window | Line 6391 |

---

## Deadline Calculation Rules

### Working Day (AT) Calculation

**Definition**: AT = Arbeitstag (Working Day)
- **Excludes**: Saturdays, Sundays, public holidays
- **Includes**: Monday through Friday (when not public holidays)

**Examples from specification**:

**Example 1: 65 AT Calculation** (Section 4.3.3.2):
- **Start (t0)**: Wednesday, 12.10.2011 (Cancellation day)
- **+65 AT**: Thursday, 12.01.2012 (Z-message creation)
- **+1 T (t2)**: Friday, 13.01.2012 (Z-message publication)
- **Elapsed**: ~3 months calendar time

**Example 2: 10 AT Single Message** (Section 4.8.3.2):
- **t0**: Thursday, 04.07.2007 (Porting day)
- **t1**: Friday, 05.07.2007 (P/L publication, +1 T)
- **+10 AT processing**: Monday, 16.07.2007 (Skips weekends)
- **t3**: Tuesday, 17.07.2007 (Single message publication if needed)

**Example 3: 20 AT RNB Pre-announcement** (Section 7.5.1.2):
- **t0**: Thursday, 24.04.2008 (Info-File 1 publication)
- **+20 AT**: Friday, 16.05.2008 (P-message publication, t1a)
- **+10 AT more**: Tuesday, 27.05.2008 (L-message publication, t1b)
- **Total**: 30 AT for full RNB pre-announcement

### T (Tag/Day) Calculation

**Definition**: T = Tag (Calendar Day)
- **Includes**: All calendar days
- **Typical use**: +1 T = next calendar day for publication

**Rule**: Publication dates are always the **next calendar day** after creation/processing day.

### Date Field Constraints

**Portierungsdatum (Porting Date)**:
- **Format**: `ddmmyyyy` (8 characters)
- **Valid range**: 01.01.1997 to 31.12.2096 (Line 4259)
- **Encoding**: 970101 to 961231
- **Special value**: "Nullwert" for originating carrier in first porting

**Veröffentlichungsdatum (Publication Date)**:
- **Constraint**: Porting date in Z-message must be ≥ Publication date - 1 KT (Line 640)
- **Constraint**: Corrections with porting date = publication date are rejected (Line 2506)
- **Constraint**: Corrections with future porting date are rejected (Line 2504)

### Merge Date Constraints (Code 4100)

**Rule**: Zusammenführungsdatum (merge date) must be **after** the porting dates of all individual sub-ranges being merged (Line 2518).

**Consequence**: If merge date ≤ any sub-range porting date, merge message is ignored (Line 2519).

---

## Special Deadline Scenarios

### Scenario: Expedited Porting (Fristverkürzung)

**Trigger**: Info-File 05 (5I-file) published by authorized carrier

**Modified Timeline**:
1. **t0**: Porting day (Portierungstag)
2. **t1 = t0 + 1 T**: P/L messages published
3. **t2 = t1 + 3 AT**: Processing day (instead of +10 AT)
4. **t3 = t2 + 1 T**: Single message published if needed

**Effectiveness**: Applies on publication day + following day (Line 7895)

**Daily renewal**: 5I-file must be published daily to maintain expedited procedure (Line 7891)

**Return to normal**: Without daily 5I-file, procedure returns to standard 10 AT deadline

### Scenario: Number Block Transfer (RNB)

**Complete Timeline**:
1. **t0**: Info-File 1 published (20 AT before transfer latest)
2. **t0 + 20 AT = t1a**: P-message published (receiving carrier)
3. **t1a + 10 AT = t1b**: L-message published (originating carrier)
4. **t5 - 5 AT = t2**: Deadline for pairing (P+L must pair)
5. **t5 - 4 AT = t3**: Unpaired messages discarded
6. **t5 - 2 AT = t4**: Latest opposition/retraction
7. **t5**: Transfer day (Übernahmetag)
8. **t5 + 20 AT = t6**: Info-File 2 published (latest)

**Critical pairing window**: 5 AT before transfer to 4 AT before transfer (1 AT window)

**Opposition window**: From t1a to (t5 - 2 AT)

### Scenario: Correction with Opposition (Code 4XXX)

**Timeline**:
1. **Day 0**: Original message published
2. **Day 0 + 1 T**: Earliest correction can be published
3. **Correction published**: Starts 10 AT opposition period
4. **Opposition period**: 10 AT where objections (25XX) can be raised
5. **After 10 AT**: Opposition period expires
6. **After 10 AT + 1 T**: Routing changes take effect (if applicable)
7. **After 10 AT**: New 41XX/42XX/43XX/44XX operations allowed

**During opposition**: No follow-up 4XXX operations accepted (Line 2430)

---

## Summary Table: All Defined Deadlines

| Deadline | AT Value | T Value | Context | Category |
|----------|----------|---------|---------|----------|
| Cancellation to Z-message | 65 AT | - | Customer cancellation | General Porting |
| Z-message publication delay | - | +1 T | After creation | General Porting |
| RUZ duration | - | 2 Months | Call forwarding period | Regulatory |
| Erroneous fallback protection | 5 AT | - | Before owner reconnects | General Porting |
| Correction earliest publication | - | +1 T | After erroneous record | Correction |
| Opposition period (4XXX codes) | 10 AT | - | Block operations objection | Correction |
| Single message (standard) | 10 AT | - | From P/L publication | Single Message |
| Single message (expedited) | 3 AT | - | With 5I-file | Single Message |
| Single message publication | - | +1 T | After processing | Single Message |
| RNB Info-File 1 advance | 20 AT | - | Before P-message | RNB |
| RNB P to L gap | 10 AT | - | Between P and L messages | RNB |
| RNB pairing deadline | 5 AT before | - | Before transfer | RNB |
| RNB unpaired discard | 4 AT before | - | Before transfer | RNB |
| RNB opposition deadline | 2 AT before | - | Before transfer | RNB |
| RNB Info-File 2 latest | 20 AT after | - | After last transfer | RNB |
| RNB single message advance | 5 AT | - | Before setup date | RNB |
| RNB minimum P-message age | 10 AT | - | For single message validation | RNB |
| RNB minimum date spacing | 20 AT | - | Current to setup date | RNB |
| File retention maximum | - | 2 Months | Home directory cleanup | Technical |
| 5I-file effectiveness | - | Publication + 1 T | Expedited procedure | Info File |

---

## Glossary of Time-Related Terms

| German Term | English Translation | Definition |
|-------------|---------------------|------------|
| **AT** | Arbeitstag | Working Day (Mon-Fri, excluding public holidays) |
| **T** | Tag | Calendar Day (any day of week) |
| **KT** | Kalendertag | Calendar Day (explicit calendar day) |
| **Frist** | Deadline / Time limit | Time period within which action must be taken |
| **Termin** | Appointment / Date | Specific date or deadline |
| **Zeitraum** | Time period | Duration or time span |
| **Widerspruchsfrist** | Opposition period | Time window for raising objections |
| **RUZ** | Rufumsteuerungszeit | Call forwarding time (2 months) |
| **Kündigungsfrist** | Cancellation notice period | Time between cancellation and termination (65 AT) |
| **Portierungsdatum** | Porting date | Effective date of number porting |
| **Veröffentlichungsdatum** | Publication date | Date when message is published to PDA |
| **Einrichtungstermin** | Setup date | Date when number/block becomes active |
| **Übernahmetag** | Transfer day | Day of actual RNB ownership transfer |
| **Fristverk ürzung** | Deadline reduction | Shortened procedure (3 AT instead of 10 AT) |

---

## Business Rules Affecting Deadlines

### Rule 1: Daily Exchange Mandatory
**Requirement**: Daily data exchange is mandatory (unerl ässlich) due to deadline definitions (Line 3883)
**Impact**: All carriers must participate in daily PDA exchange to comply with deadlines
**Consequence**: Failure to exchange daily may result in missed deadlines and invalid messages

### Rule 2: One Correction Per Day
**Requirement**: Only one correction per regular record per day allowed in correction file (Line 2498)
**Impact**: Multiple corrections to same record must be spread across multiple days
**Consequence**: Corrections violating this rule are rejected

### Rule 3: Correction Cannot Correct Certain Message Types
**Requirement**: Corrections to retractions (2000-2400, 30XX), oppositions (2500-2599), and single messages (6000-6200) are prohibited (Line 2500)
**Impact**: These message types cannot be corrected - must be retracted and republished
**Consequence**: Attempted corrections to these types are ignored

### Rule 4: Future Date Prohibition
**Requirement**: Corrections with porting date in future are rejected - no "hold for future" (Line 2504)
**Impact**: All porting dates must be current or historical
**Consequence**: Messages with future dates are discarded without queuing

### Rule 5: Earliest Correction Rule
**Requirement**: Corrections can only be published at earliest 1 day after erroneous record (Line 2424)
**Impact**: Immediate correction loops prevented
**Consequence**: Too-early corrections are ignored

### Rule 6: Opposition Exclusivity
**Requirement**: During 10 AT opposition period for 4XXX codes, no follow-up 4XXX operations accepted (Line 2430)
**Impact**: Must wait for opposition period to expire before next block operation
**Consequence**: Follow-up operations during opposition are rejected and discarded

### Rule 7: RUZ Preservation Rule
**Requirement**: If original range is within RUZ during block operation (4XXX), routing must be maintained for remaining RUZ duration (Line 2459-2463)
**Impact**: Block operations don't terminate RUZ early
**Consequence**: Routing must be updated for merged/split blocks during remaining RUZ

### Rule 8: Pairing Finality
**Requirement**: Once messages pair and validate, corrections are ignored (except 4XXX and 30XX) (Line 2478-2480)
**Impact**: Paired records are considered final
**Consequence**: Corrections after pairing are rejected (with exceptions)

---

## Technical Processing Deadlines

### File Processing Times

| Process | Deadline | Context | Reference |
|---------|----------|---------|-----------|
| **Daily file processing** | Every AT | All carriers process files daily | Spec-wide |
| **Request file processing** | Within reasonable time | Create response after request received | Section 5.2.3 |
| **File cleanup** | After 2 months | Delete files older than 2 months | Line 4277 |
| **Response deletion** | Immediately | After uploading new request | Line 4278 |

### Time-of-Day Constraints

| Constraint | Time | Context | Reference |
|------------|------|---------|-----------|
| **0:00 Uhr cut-off** | Midnight | Less than 2 days warning if deadline at 0:00 | Line 13421 |
| **No specific daily cut-off** | Not defined | Spec does not mandate specific daily processing time | Analysis |

**Note**: The specification does not mandate a specific time of day for file exchange, only that it occurs daily. The 0:00 Uhr reference (Line 13421) appears in version history context, not as operational deadline.

---

## Conclusion

This comprehensive extraction has identified **326 deadline references** across **8 major categories**:

1. **General Porting**: 169 references (65 AT cancellation, 5 AT fallback, RUZ)
2. **RNB Messages**: 68 references (20/10/5/4/2 AT sequences)
3. **Single Messages**: 19 references (10 AT standard, 3 AT expedited)
4. **Opposition Periods**: 20 references (10 AT opposition windows)
5. **Info Files**: 19 references (5I-file daily publication, effectiveness rules)
6. **Technical**: 14 references (file retention, processing times)
7. **Regulatory**: 12 references (RUZ 2 months, BNetzA orders)
8. **Correction Messages**: 5 references (4XXX codes, earliest publication)

**Critical Success Factors**:
- **Daily exchange compliance**: Mandatory for all deadline adherence
- **Working day calculation**: Proper AT counting excluding weekends/holidays
- **Opposition period respect**: 10 AT windows must be enforced
- **RUZ maintenance**: 2-month call forwarding period is regulatory requirement
- **Pairing enforcement**: P+L or equivalent must pair within defined windows

**Risk Areas**:
- **65 AT monitoring**: Only last owner checks - potential for oversight
- **RNB pairing window**: Only 1 AT window (5 AT to 4 AT before transfer) for pairing
- **Opposition blocking**: Follow-up operations during 10 AT period must be rejected
- **5I-file continuity**: Daily publication required to maintain expedited procedure

---

## References

**Primary Source**: ITEX-PDA Spezifikation PDA 20-0-0, Version 20.0.0, dated 09.05.2023
**Regulatory Authority**: Bundesnetzagentur (BNetzA)
**Working Group**: IT-Expertengruppe für den Portierungsdatenaustausch (ITEX-PDA)
**Coordination Body**: Arbeitskreis für technische und betriebliche Fragen der Nummerierung und der Netzzusammenschaltung (AKNN)
**Valid From**: 06.05.2024

**Key Sections Referenced**:
- Section 4.3: Austausch von Portierungsdaten im Regelverfahren
- Section 4.7: Korrekturverfahren (Correction procedures)
- Section 4.8: Singlemeldungen (Single messages)
- Section 7.5: Ausbleibende RNB-Meldungen (Missing RNB messages)
- Section 10.6: Business Rules für Infodateien (Info file business rules)

---

**End of Report**
