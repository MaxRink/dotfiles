# ITEX-PDA Process Overview and Dependencies

**Version:** Based on ITEX-PDA Specification 20.0.0 (Valid from 06.05.2024)
**Document Date:** 2025-12-12
**Purpose:** Comprehensive overview of all Portierungsdatenaustausch (PDA) processes and their interdependencies

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Message Types Overview](#message-types-overview)
3. [Main Process Categories](#main-process-categories)
4. [Process Dependencies](#process-dependencies)
5. [Critical Timelines and Deadlines](#critical-timelines-and-deadlines)
6. [Business Rules Summary](#business-rules-summary)
7. [Diagram Guide](#diagram-guide)
8. [Quick Reference Tables](#quick-reference-tables)

---

## Executive Summary

The ITEX-PDA (IT Expert Group for Porting Data Exchange) specification defines the **Portierungsdatenaustausch** (porting data exchange) process between German telecommunications network operators (TNB - Telekommunikationsnetzbetreiber).

### Key Objectives

- **Data Exchange:** Automated exchange of porting information between carriers
- **Routing Updates:** Enable correct call routing after number portability
- **Regulatory Compliance:** Meet BNetzA (Federal Network Agency) requirements
- **Data Consistency:** Ensure all carriers have synchronized porting information

### Process Categories

The PDA system consists of **4 main process categories** with **8 message types**:

1. **REGELVERFAHREN** (Standard Procedures) - Messages: P, L, Z
2. **KORREKTURVERFAHREN** (Correction Procedures) - Message: K
3. **RNB-VERFAHREN** (Number Block Procedures) - Messages: E, C
4. **SUPPORT-PROZESSE** (Support Processes) - Messages: I, DR

---

## Message Types Overview

### 1. P-Meldung (Porting Message)

**Purpose:** Notification that a number has been ported **to** a carrier
**Sender:** TNB aufnehmend (receiving carrier)
**File:** 1Dyymmdd.txt (Daily Default file)
**Status Code:** P (portiert - ported)

**Content:**
- Ported phone number(s)
- Porting date
- PK aufnehmend (receiving carrier code)
- PK abgebend (donating carrier code)

**Key Rules:**
- Must be published day after porting (Tag+1)
- Requires pairing with L-Meldung
- Porting date must match L-Meldung exactly
- Cannot be published before E-Meldung + 1 KT for numbers in RNB

### 2. L-Meldung (Leaving Message)

**Purpose:** Notification that a number has **left** a carrier
**Sender:** TNB abgebend (donating carrier)
**File:** 1Dyymmdd.txt (Daily Default file)
**Status Code:** L (löschen - delete/leaving)

**Content:**
- Same as P-Meldung
- Must have identical porting date as P-Meldung

**Key Rules:**
- Published by donating carrier on same day as P
- Forms validated pair with P-Meldung
- After pairing, initiates RUZ (Rufumsteuerungszeit - call forwarding period of 2 months)

### 3. Z-Meldung (Zurück/Return Message)

**Purpose:** Notification of number return/fallback to owner
**Sender:** Last owner (letzter Besitzer)
**File:** 1Dyymmdd.txt (Daily Default file)
**Status Code:** Z (zurück - return)

**Content:**
- Returned phone number(s)
- Return date
- Owner PK (receives back)
- Last holder PK (returns)

**Key Rules:**
- Published after 65 AT (Arbeitstage - working days) from deactivation
- Porting date must be: Publication date - minimum 1 KT (Kalendertag - calendar day)
- Forms validated pair with P-Meldung from owner
- Triggers RUZ of 2 months
- Owner waits 5 AT before removing call forwarding (safety period)

### 4. E-Meldung (Einrichtung/Setup Message)

**Purpose:** Notification of new RNB (Rufnummernblock - number block) setup
**Sender:** RNB owner
**File:** 1Eyymmdd.txt (RNB setup file)

**Content:**
- Number block range
- Setup date (Einrichtungsdatum)
- Owner PK (to D000 from BNetzA)
- Block size
- Status: E (Standalone)

**Key Rules:**
- Must be published minimum **5 AT (working days) before Einrichtungstermin** (AKNN 7.1.3.2)
- Required before any P/L-Meldungen for numbers in this block
- P-Meldung allowed only after E-Datum + 1 KT
- Enables automatic routing setup in all TNB networks
- Only one record needed (not paired)

**Triggers:**
- New allocation from BNetzA
- Migration scenarios

### 4.1 R-Meldung (Rückgabe/Return Message)

**Purpose:** Return of free RNB to BNetzA
**Sender:** Original allocation holder (originärer Zuteilungsnehmer)
**File:** 1Ryymmdd.txt (RNB return file)
**To:** D000 (BNetzA)

**Content:**
- Number block range
- Return date (Rückgabedatum in field "Einrichtungsdatum")
- From: Owner PK
- To: D000 (BNetzA)
- Status: R (Standalone)

**Key Rules:**
- Must be published minimum **20 AT before return date** (AKNN 7.1.3.3)
- **Standalone message - NOT paired** (only one record needed, AKNN 7.2.4)
- RNB must be free (no assigned phone numbers)
- Return-TNB must release calls with proper signaling
- Different from RNB transfer (which uses P+L)

**Process:**
1. Publication 20 AT before return date
2. All TNB prepare routing as "not connected"
3. Return-TNB releases calls with signaling
4. BNetzA receives RNB back
5. If re-allocated later: new E-Meldung required

### 4.2 P/L-Meldung for RNB Transfer

**Purpose:** Transfer RNB ownership between TNBs
**Procedure:** Same as regular porting (AKNN 7.4.2)

**Key Rules:**
- RNB transfer (Übernahme) requires **P + L pairing** (not standalone)
- P-Meldung from new owner (taking TNB)
- L-Meldung from old owner (giving TNB)
- BNetzA approval required for transfer
- Different from R-Meldung (which is return to BNetzA)

**Important Distinction:**
- **E-Meldung**: Setup new RNB (BNetzA → TNB) - Standalone
- **R-Meldung**: Return RNB (TNB → BNetzA) - Standalone
- **P+L-Meldung**: Transfer RNB (TNB → TNB) - Paired

### 5. C-Meldung (RNB Correction Message)

**Purpose:** Correction of E-Meldungen
**Sender:** RNB owner
**File:** 1Cyymmdd.txt (RNB correction file)

**Content:**
- Original E-Meldung (U: prefix)
- Corrected E-Meldung (C: prefix)
- Correction code

**Key Rules:**
- Similar structure to K-Meldungen but for RNB
- Correction codes specific to RNB processes
- Published minimum 1 day after erroneous E-Meldung

### 6. K-Meldung (Korrektur/Correction Message)

**Purpose:** Correction, withdrawal, or objection to P/L/Z messages
**Sender:** Error-causing TNB or affected TNB
**File:** 1Kyymmdd.txt (Correction file)

**Content:**
- Original message (U: prefix - Ursprung)
- Correction message (K: prefix - Korrektur)
- Correction code (see below)

**Correction Code Categories:**

#### 2XXX - Withdrawal/Objection (No confirmation needed)
- **2000-2400:** Withdraw own message
  - 2000: Withdraw P-Meldung
  - 2100: Withdraw L-Meldung
  - 2200: Withdraw Z-Meldung
  - 2300: Withdraw K-Meldung
  - 2400: Withdraw E-Meldung
- **2500-2599:** Object to foreign message
  - 2500: Object to P-Meldung
  - 2501: Object to L-Meldung
  - 2502: Object to Z-Meldung
  - 2503: Wrong block size
  - 2504-2599: Various errors

#### 0XXX - Data Corrections (Confirmation required)
- **0100:** Change PK aufnehmend
- **0200:** Change PK abgebend
- **0300:** Change porting date
- **0400:** Multiple changes

#### 4XXX - Structural Changes (10 AT objection period)
- **4100:** Merge number ranges (Zusammenführung)
- **4200:** Extend number range (Erweiterung)
- **4300:** Split number range (Aufteilung)
- **4400:** Combine individual + range
- **4500:** Extend legacy numbers (Altbestand)
- **4600-4730:** Blocking codes
  - 4600: Block individual number
  - 4610: Block number range
  - 4700: Legal block
  - 4710: Technical block
  - 4720: BNetzA order
  - 4730: Remove block

#### 3XXX - Retrospective Corrections
- **30XX:** Correct already validated pairs
- **3025:** Wrong allocation detected

#### 6XXX - Single Messages (After 61 AT)
- **6000:** Single P-Meldung (if no L received)
- **6100:** Single L-Meldung (if no P received)
- **6200:** Single Z-Meldung (if no P received)

**Key Rules:**
- Published minimum 1 day after erroneous message
- Most codes require confirmation by second TNB
- Codes 2XXX and 4XXX do not require confirmation
- After 61 AT without pair, single message validation possible
- 10 AT objection period for 4XXX codes

### 7. I-Meldung (Info Message)

**Purpose:** Provide contact and organizational information
**Sender:** All TNBs
**File:** 1Iyymmdd.txt (Info file)
**Update Frequency:** Daily

**Info Kennungen (Info Types):**

#### 01 - Fachlicher Ansprechpartner (Technical Contact)
- Primary business contact
- PDA procedure questions
- Clearing coordination

#### 02 - Fachlich Detaillierter Ansprechpartner (Detailed Technical Contact)
- Detailed technical issues
- Complex porting scenarios
- Escalation contact

#### 03 - Technischer Ansprechpartner (IT Contact)
- SSH/SFTP connection issues
- File transfer problems
- System outages

#### 04 - PK-Beziehungen (4i-Datei)
- HPK (Hauptportierungskennung) to PK mapping
- Multiple PK relationships
- Merger/fusion information
- PK hierarchy

#### 05 - Migrations-Ankündigung
- Announce mass migrations
- Large RNB transfers
- Schedule coordination

**Key Rules:**
- Must be kept up-to-date daily
- Contact information must be valid and reachable
- Critical for clearing process
- Required for PDA participation

### 8. DR-Meldung (Data Request)

**Purpose:** Request or provide porting data inventory
**Types:** Request, Response, Default
**Files:**
- Request: Custom filename
- Response: 1Ryymmdd.txt
- Default: 1Dyymmdd.txt

**Request File:**
- One TNB requests data from another
- Specifies date range or "current"

**Response File:**
- Contains all P/L/Z pairs
- Last 2 months of K-Dateien
- All E-Dateien (RNB)
- Response to specific request

**Default File:**
- Complete inventory
- Provided daily without request
- For database synchronization
- New TNB initialization

---

## Main Process Categories

### 1. REGELVERFAHREN (Standard Porting Procedures)

#### 1.1 Portierung (Porting Process)

**Scenarios:**

##### Szenario 1a: Erstportierung (First-time Porting)
**Flow:** TNB A (owner + donating) → TNB B (receiving)

**Process:**
1. Number is ported from A to B
2. TNB B publishes P-Meldung (Tag+1)
3. TNB A publishes L-Meldung (Tag+1)
4. P + L form validated pair
5. All other TNBs update routing
6. RUZ begins (2 months call forwarding by A)

**Actors:**
- TNB A: Eigentümer (owner) + Abgebend (donating)
- TNB B: Aufnehmend (receiving)
- TNB C/D: Other carriers (update routing)

##### Szenario 1b: Zweitportierung (Second Porting)
**Flow:** TNB A (owner) ← TNB B (donating) → TNB C (receiving)

**Process:**
1. Previously ported number moves from B to C
2. TNB C publishes P-Meldung
3. TNB B publishes L-Meldung
4. P + L form validated pair
5. Old P1a + L1a deleted after RUZ
6. TNB A updates routing (maintains forwarding)

**Key Difference:**
- TNB A maintains call forwarding chain
- Previous pair (P1a + L1a) deleted after new pair validated
- RUZ renewed for 2 months

##### Szenario 1c: Rückportierung (Return Porting - after first port)
**Flow:** TNB A (owner) ← TNB B (returns)

**Process:**
1. Number returns to original owner A
2. TNB A publishes P-Meldung (now receiving back)
3. TNB B publishes L-Meldung (returning)
4. P + L validated
5. Call forwarding no longer needed after RUZ

##### Szenario 1d: Rückportierung (Return Porting - after multiple ports)
**Flow:** After multiple portings, return from any TNB

**Process:**
- Similar to 1c but with complex history
- All intermediate pairs deleted after RUZ
- Routing simplified after return

##### Szenario 1e: Spezialfälle (Special Cases)
- **Interne Portierung:** Same HPK, different PK
- **Mehrere PK:** Using multiple porting codes
- **Fusionen:** Carrier mergers/acquisitions

#### 1.2 Rückgabe (Return/Fallback Process)

**Trigger:** Number deactivated by customer

##### Szenario 2a: Standard-Rückfall (Standard Fallback)
**Flow:** After 65 AT → automatic return to owner

**Process:**
1. Customer terminates service (day 0)
2. Number deactivated
3. Last owner waits 65 AT (working days)
4. Last owner publishes Z-Meldung (Tag+66)
   - Z-Datum = Publication date - minimum 1 KT
5. Owner publishes P-Meldung (accepts return)
6. P + Z validated
7. RUZ begins (2 months)
8. Owner waits 5 AT before removing forwarding (safety period)
9. Owner activates number or sets announcement

**Critical Timelines:**
- **t0:** Termination day
- **t0 + 65 AT:** Z-Meldung creation
- **t0 + 65 AT + 1 T:** Z-Meldung publication
- **RUZ:** 2 months from validation
- **Safety:** 5 AT before owner removes forwarding

##### Szenario 2b: Spezielle Rückgaben (Special Returns)
- Early returns (with agreement)
- Multiple PK scenarios
- Fusion-related returns

#### 1.3 Business Rules - Regelverfahren

**General Rules:**
1. Daily publication (Tag+1 after porting)
2. No future-dated messages accepted
3. Same-day publication and porting not allowed
4. Backdated messages accepted (with original porting date)
5. Messages before last validated porting ignored
6. Same-date re-porting not allowed (minimum Tag+1)
7. Porting only after E-Datum + 1 KT for RNB numbers
8. Wrong sender TNB messages rejected
9. Invalid number formats rejected

**Pairing Rules:**
1. P + L must have identical porting date
2. P + Z must have identical porting date
3. Routing updated only after validated pair
4. Unpaired messages remain open
5. New pair overwrites old unpaired messages (same or older date)
6. Wrong sequence accepted if dates valid
7. Historical pairs deleted after RUZ

**Deadline Rules:**
1. **Portierung:** Publish Tag+1, RUZ 2 months
2. **Rückgabe:** 65 AT + Z-Meldung, RUZ 2 months, 5 AT safety
3. **Validation:** Immediate upon pair match
4. **Deletion:** After RUZ expiry

---

### 2. KORREKTURVERFAHREN (Correction Procedures)

#### 2.1 Purpose

The correction procedure serves to:
1. Correct erroneous porting messages
2. Withdraw incorrect messages
3. Object to false messages from other TNBs
4. Adjust number structures (splits, mergers)
5. Block numbers (legal, technical, regulatory)
6. Handle missing pair messages (single messages)

#### 2.2 Principle

**Confirmation Requirement:**
- Most K-Meldungen require confirmation by second TNB
- Confirmation via:
  - Second K-Meldung (if both TNB made errors)
  - New correct P/L/Z message
  - Acceptance of correction

**Exceptions (No confirmation needed):**
- Codes 2000-2450 (withdrawals/objections)
- Codes 4000-4730 (structural changes/blocks)

**Structure:**
```
U: Original (incorrect) message
K: Correction message
```

#### 2.3 Correction Code Details

##### 2XXX: Rücknahme & Widerspruch (Withdrawal & Objection)

**2000-2400: Eigene Meldung zurücknehmen**
- Withdraw own erroneous message
- No confirmation needed
- Immediate effect
- Can be done within RUZ period

**2500-2599: Widerspruch fremde Meldung**
- Object to incorrect message from other TNB
- No confirmation needed
- Prevents validation of incorrect pair
- Common codes:
  - 2500: Wrong P-Meldung
  - 2501: Wrong L-Meldung
  - 2502: Wrong Z-Meldung
  - 2503: Wrong block size
  - 2504-2599: Various errors

##### 0XXX-1XXX: Einfache Korrekturen (Simple Corrections)

**0100: PK aufnehmend ändern**
- Change receiving carrier code
- Requires confirmation
- Must reference original message (U:)

**0200: PK abgebend ändern**
- Change donating carrier code
- Requires confirmation

**0300: Portierungsdatum ändern**
- Change porting date
- New date must be after original
- Cannot change to date before last validated porting
- Requires confirmation

**0400: Mehrfachänderung**
- Multiple field changes simultaneously
- Requires confirmation

##### 4XXX: Strukturänderungen (Structural Changes)

**4100: Zusammenführung (Merge)**
- Combine multiple number ranges into one
- Zusammenführungsdatum > all individual porting dates
- 10 AT objection period
- Routing updated after objection period
- No confirmation needed

**Example:**
```
Original:
- 030-1234-000 to 030-1234-099
- 030-1234-100 to 030-1234-199

After 4100:
- 030-1234-000 to 030-1234-199
```

**4200: Erweiterung (Extension)**
- Extend existing number range
- Add more numbers to existing block
- 10 AT objection period
- No confirmation needed

**4300: Aufteilung (Split)**
- Split number range into multiple parts
- Requires cooperation of owner TNB
- 10 AT objection period
- Creates multiple new ranges
- No confirmation needed

**4400: Kombination (Combination)**
- Combine individual numbers with ranges
- Complex scenarios
- 10 AT objection period

**4500: Altbestand Erweiterung (Legacy Extension)**
- Extend legacy numbers without base message
- Special case for old data
- No confirmation needed

**4600-4730: Sperrungen (Blocks)**
- **4600:** Block individual number
- **4610:** Block number range
- **4700:** Legal block (court order, law enforcement)
- **4710:** Technical block (spam, abuse)
- **4720:** BNetzA regulatory order
- **4730:** Remove block
- 10 AT objection period for 4700, 4710, 4720
- No confirmation needed

##### 3XXX: Nachträgliche Korrekturen (Retrospective Corrections)

**30XX: Korrektur validierter Paare**
- Correct already validated (paired) messages
- Exception to "no correction after validation" rule
- Special cases only
- **3025:** Wrong allocation detected

##### 6XXX: Singlemeldungen (Single Messages)

**Purpose:** Handle situations where pair partner never arrives

**Automatic Validation After 61 AT:**
- **6000:** Single P-Meldung (L never received)
- **6100:** Single L-Meldung (P never received)
- **6200:** Single Z-Meldung (P never received)

**Process:**
1. Message published (P, L, or Z)
2. Wait 61 AT (working days)
3. If no pair partner received, automatic single validation
4. 10 AT objection period
5. If no objection, message considered validated

**Use Cases:**
- TNB no longer participates in PDA
- TNB returned PK to BNetzA
- Data initialization of new systems
- Historical data imports

#### 2.4 Fristen (Deadlines) - Korrekturverfahren

**Publication:**
- Minimum Tag+1 after erroneous message
- Cannot be published same day as error

**Objection Period:**
- 10 AT for codes 4XXX (structural changes)
- 10 AT for codes 6XXX (single messages)
- 10 AT for codes 4700, 4710, 4720 (blocks)

**Single Message:**
- 61 AT waiting period before automatic validation
- Then 10 AT objection period

**Correction on Correction:**
- Can correct a correction
- Must use same correction code
- U: part always refers to original (first) message
- Can use code 0000 for general reset

---

### 3. RNB-VERFAHREN (Number Block Procedures)

#### 3.1 Purpose

RNB (Rufnummernblock - number block) procedures ensure:
- All TNBs know which blocks are allocated to which carriers
- Routing is established before numbers are used
- Block ownership changes are transparent
- Coordination for mass migrations

#### 3.2 E-Meldung: Einrichtung (Setup)

**Triggers:**
1. **Neue Zuteilung:** New allocation from BNetzA
2. **Übernahme:** Takeover from another TNB
3. **Migration:** Mass migration scenario

**Process:**
1. TNB receives RNB from BNetzA or another TNB
2. TNB publishes E-Meldung
   - Minimum 10 KT before intended usage
3. E-Meldung contains:
   - Number block range
   - Setup date (Einrichtungsdatum)
   - Owner PK
   - Block size
4. All TNBs receive E-Meldung
5. All TNBs set up routing to owner
6. After E-Datum + 1 KT minimum, P/L-Meldungen allowed

**Critical Rule:**
- **No portings before E-Datum + 1 KT**
- P/L-Meldungen for numbers in RNB only after this date
- Earlier messages are rejected

**File Format:**
- File: 1Eyymmdd.txt
- Contains RNB data records
- Published via SFTP

#### 3.3 RNB-Übernahme (Takeover)

**Scenarios:**
1. **Fusion:** Two carriers merge
2. **Acquisition:** One carrier buys another
3. **Business Transfer:** Contract transfer
4. **PK Return:** TNB returns PK to BNetzA, blocks must transfer

**Process:**

##### Step 1: BNetzA Approval
- BNetzA decides on RNB transfer
- Publishes RNB-Übernahme file
- Lists blocks to transfer
- Specifies old and new owner

##### Step 2: Coordination
- Old owner and new owner coordinate
- Technical preparation
- Network routing setup
- Timeline agreement

##### Step 3: Old Owner Actions
- Continue service until transfer date
- Ensure reachability
- Prepare for routing changes
- Return empty blocks if required

##### Step 4: New Owner Actions
- Publish E-Meldung for taken-over blocks
- Minimum 10 KT before usage
- Set up routing
- Prepare network infrastructure

##### Step 5: Completion
- Transfer executed on agreed date
- Routing updated in all networks
- Old owner removes blocks from system
- New owner assumes full responsibility

**BNetzA File:**
- Lists all RNB transfers
- Source TNB (PK alt)
- Target TNB (PK neu)
- Block ranges
- Effective dates

**Rules:**
- Old owner must cooperate (Mitwirkungspflicht)
- New owner ensures technical readiness
- Minimum 10 KT preparation time
- Ported numbers within blocks remain ported

#### 3.4 Massenmigration (Mass Migration)

**Limits:**
- **Standard:** Maximum 20,000 numbers per day (all TNBs combined)
- **With Agreement:** Maximum 100,000 numbers per day
  - Requires approval from all active PDA participants
  - Approval requested from:
    - 3i-Datei contacts (01 + 02)
    - BNetzA active participant list

**I-Datei Announcement:**
- Migrations must be announced via I-Datei (Info-Kennung 05)
- Details:
  - Planned date
  - Volume estimate
  - Affected number ranges
  - Contact information

**Coordination:**
- All TNBs must be informed
- Technical capacity confirmed
- Processing windows agreed
- Monitoring intensified

#### 3.5 C-Meldung: RNB-Korrektur (RNB Correction)

**Purpose:** Correct E-Meldungen

**Similar to K-Meldung but for RNB:**

**Structure:**
```
U: Original E-Meldung
C: Corrected E-Meldung
```

**Correction Types:**
- Change setup date (Einrichtungsdatum)
- Change block size
- Change owner PK
- Withdraw E-Meldung (Rücknahme)

**Rules:**
- Published minimum Tag+1 after erroneous E-Meldung
- Similar confirmation rules as K-Meldungen
- Affects routing setup

**File Format:**
- File: 1Cyymmdd.txt
- Contains corrected RNB records

---

### 4. SUPPORT-PROZESSE (Support Processes)

#### 4.1 I-Meldung (Information Messages)

##### 3i-Datei: Ansprechpartner (Contact Information)

**Purpose:** Provide current contact information for PDA operations

**Info-Kennung 01: Fachlicher Ansprechpartner**
- Primary business contact
- PDA procedure questions
- General porting issues
- Clearing coordination
- **Must be reachable during business hours**

**Info-Kennung 02: Fachlich Detaillierter Ansprechpartner**
- Detailed technical contact
- Complex porting scenarios
- Escalation point
- In-depth analysis
- **For complex cases**

**Info-Kennung 03: Technischer Ansprechpartner**
- IT/technical contact
- SSH/SFTP issues
- File transfer problems
- System outages
- Connection problems
- **For infrastructure issues**

**Content per Contact:**
- Contact type (01, 02, 03)
- Company name
- Contact person name
- Phone number
- Email address
- Availability hours

**Update Frequency:**
- Daily publication via 1Iyymmdd.txt
- Must be kept current
- Changes effective next day

**Critical Requirement:**
- Contacts must be reachable
- Valid contact details mandatory
- Required for PDA participation
- Used for clearing escalation

##### 4i-Datei: PK-Beziehungen (PK Relationships)

**Purpose:** Document relationships between PK and HPK

**Info-Kennung 04:**

**Content:**
- **HPK:** Hauptportierungskennung (Main porting code)
- **PK:** Portierungskennung (Porting code)
- **Relationship:** Which PKs belong to which HPK

**Use Cases:**
1. **Multiple PK:** One carrier uses multiple porting codes
2. **Merger/Fusion:** Company mergers, combined operations
3. **Organizational:** Different divisions, brands
4. **Historical:** Legacy relationships

**Example:**
```
HPK: D001
PKs: D001, D002, D003
(All three PKs represent same carrier group)
```

**Impact on Processes:**
- Z-Meldungen accepted from any PK in same HPK group
- Internal portings between PKs of same HPK
- Routing decisions
- Clearing coordination

**Rules:**
- Must be kept current
- Changes announced in advance
- Affects porting validation logic
- Critical for multi-PK scenarios

##### Info-Kennung 05: Migrations-Ankündigung (Migration Announcement)

**Purpose:** Announce large-scale migrations or RNB transfers

**Content:**
- Planned date
- Number volume estimate
- Affected ranges/blocks
- Expected impact
- Contact for coordination

**Required For:**
- Mass migrations >20,000 numbers
- Large RNB transfers
- System cutovers
- Data center migrations

#### 4.2 DR-Meldung (Data Request/Response)

##### Request-File

**Purpose:** Request porting data from another TNB

**Process:**
1. TNB A wants data from TNB B
2. TNB A creates request file
3. Places in TNB B's directory
4. TNB B processes request
5. TNB B provides response file

**Request Content:**
- Requesting PK
- Date range (or "current")
- Specific number ranges (optional)

##### Response-File

**Purpose:** Provide requested porting data

**File:** 1Ryymmdd.txt

**Content:**
- All current P/L/Z pairs (as of request date)
- Last 2 months of K-Dateien (within RUZ)
- All E-Dateien (current RNB setup)
- All C-Dateien (RNB corrections)

**Rules:**
- Response within reasonable time (typically 1-2 days)
- Complete and accurate data
- Includes corrections for proper interpretation

**Example:**
If request date = 2024-01-15:
- P/L/Z pairs valid on 2024-01-15
- K-Dateien from 2023-11-15 to 2024-01-15 (2 months RUZ)
- All active E-Dateien

##### Default-File

**Purpose:** Provide complete porting inventory without request

**File:** 1Dyymmdd.txt (daily)

**Content:**
- All current P/L/Z pairs
- Typically not full K-Datei history (only current day)
- Current day's E-Dateien

**Use Cases:**
1. **Daily Synchronization:** Regular updates
2. **New TNB Initialization:** Complete data for new participant
3. **Database Rebuild:** Full inventory for recovery

**Frequency:**
- Published daily
- Available in each TNB's home directory
- Other TNBs fetch daily

#### 4.3 Ausbleibende Meldungen (Missing Messages)

**Problem:** Pair partner message never arrives

**Causes:**
1. TNB no longer participates in PDA
2. TNB returned PK to BNetzA
3. Technical failure
4. Human error (forgot to send)
5. TNB dispute (intentional withholding)

**Solution: Singlemeldungen (Single Messages)**

##### Process: Automatic Validation After 61 AT

**Step 1: Initial Message**
- TNB A publishes P-Meldung (day 1)
- Waiting for L-Meldung from TNB B

**Step 2: Waiting Period**
- Wait 61 AT (working days)
- No L-Meldung received

**Step 3: Automatic Single Validation**
- After 61 AT, system automatically validates
- P-Meldung treated as "Single P" (Code 6000)
- Considered validated without L-Meldung

**Step 4: Objection Period**
- 10 AT objection period starts
- Other TNBs can object if incorrect

**Step 5: Final Validation**
- If no objection after 10 AT, final validation
- Routing updated based on single message

**Special Case: Initialisierung (Initialization)**
- New TNB database initialization
- Historical portings where partner TNB no longer exists
- Example: TNB returned PK to BNetzA years ago
- Automatic acceptance without waiting 61 AT
- Based on BNetzA verified data

##### Single Message Codes

**6000: Single P-Meldung**
- P-Meldung validated without L-Meldung
- Receiving TNB confirms porting alone
- Used when donating TNB doesn't participate

**6100: Single L-Meldung**
- L-Meldung validated without P-Meldung
- Donating TNB confirms release alone
- Used when receiving TNB doesn't participate

**6200: Single Z-Meldung**
- Z-Meldung validated without P-Meldung
- Return confirmed by last owner alone
- Owner may not participate anymore

#### 4.4 PK-Abschaltung (PK Deactivation)

**Scenario:** TNB ceases PDA operations

**Reasons:**
1. Business closure
2. License revoked
3. Merger (PK consolidated)
4. Voluntary PDA exit

**Process:**

##### Step 1: Announcement
- TNB publishes PK-Abschaltemeldung
- Announces intention to deactivate PK
- Provides timeline
- Lists all affected PKs

**File:** PK-Abschalte-Datei

##### Step 2: Objection Period
- Other TNBs can object
- Valid reasons:
  - Open portings
  - Unresolved disputes
  - Outstanding RNB transfers

##### Step 3: RNB Transfer
- All RNB must be transferred
- Either:
  - Returned to BNetzA
  - Transferred to other TNB (with BNetzA approval)
- Via RNB-Übernahme process

##### Step 4: Porting Resolution
- All open portings must be resolved
- Options:
  - Return numbers to owners (Z-Meldungen)
  - Transfer to another TNB (agreement required)
  - Complete outstanding pairs

##### Step 5: Final Deactivation
- After all transfers and resolutions complete
- PK officially deactivated
- Removed from active participant list
- No longer receives/sends PDA messages

**Aktionscodes:**
- **Announce:** Intent to deactivate
- **Object:** Objection to deactivation
- **Confirm:** Deactivation executed

**Impact:**
- Future portings to/from this PK not possible
- Historical data remains for reference
- Routing updated to reflect closure
- RNB ownership transferred

#### 4.5 Clearing & Kommunikation (Clearing & Communication)

##### Email Communication

**Standardized Subject Line:**
```
[PDA-Clearing] [PK-From] [PK-To] [Topic-Code] [Reference]
```

**Example:**
```
[PDA-Clearing] [D001] [D002] [2503] [030-1234-5678]
```

**Topic Codes:**
- Message type (P, L, Z, E, K, C)
- Correction code (0100, 2503, 4100, etc.)
- Issue type

**Clearing Process:**
1. TNB identifies issue with message from other TNB
2. Sends clearing email using standard format
3. Email goes to contacts from 3i-Datei (01 or 02)
4. Resolution discussion
5. Agreement on correction
6. Publication of correction (K/C-Meldung) or new message

**Eskalation:**
1. Initial contact (3i-01 or 3i-02)
2. If no response: Escalate to 3i-02 (if not already)
3. Still no response: Industry working group (AKNN/ITEX-PDA)
4. Ultimate: BNetzA involvement

**Documentation:**
- Arbeitshandbuch Clearing (Clearing Handbook)
- Published by AK-SPRI (Arbeitskreis Schnittstellen und Prozesse)
- Available: https://ak-spri.de/prozesse/clearing/
- Contains:
  - Standard scenarios
  - Resolution procedures
  - Email templates
  - Escalation paths

---

## Process Dependencies

### Key Dependency Rules

#### 1. E-Meldung → P/L-Meldungen
**Rule:** Portings for numbers in RNB only allowed after E-Datum + 1 KT

**Dependency Chain:**
```
BNetzA allocation
  → E-Meldung publication (-10 KT)
  → E-Datum reached
  → +1 KT minimum
  → P/L-Meldungen allowed
```

**Impact:**
- Cannot port numbers before block is officially set up
- Ensures routing is ready
- Prevents unreachable numbers

#### 2. P/L Pairing Requirement
**Rule:** P and L must form validated pair

**Dependency:**
```
P-Meldung published
  AND
L-Meldung published
  AND
Identical porting date
  AND
Matching number/range
  →
Validated porting
  →
Routing update by all TNBs
```

**Impact:**
- Routing not updated until pair validated
- Single-sided messages remain in limbo
- After 61 AT, single validation possible

#### 3. P/Z Pairing Requirement (Return)
**Rule:** P and Z must form validated pair for return

**Dependency:**
```
Number deactivated (t0)
  → 65 AT waiting period
  → Z-Meldung published (t0 + 65 AT + 1 T)
  → P-Meldung from owner
  → P + Z validated
  → Return executed
  → RUZ begins (2 months)
  → Owner waits 5 AT
  → Owner removes forwarding
```

**Impact:**
- Automatic return after 65 AT
- Safety period prevents premature number reactivation
- Allows correction of erroneous returns

#### 4. K-Meldung → P/L/Z Basis
**Rule:** Correction requires original message

**Dependency:**
```
P/L/Z message published (erroneous)
  → Tag+1 minimum
  → K-Meldung published
  → References original (U: part)
  → Proposes correction (K: part)
  → [Confirmation required for most codes]
  → Correction applied
```

**Exceptions:**
- Code 4500: Can exist without base message (legacy extension)
- Sequential 4XXX codes: Can build on each other

#### 5. C-Meldung → E-Meldung Basis
**Rule:** RNB correction requires original E-Meldung

**Dependency:**
```
E-Meldung published (erroneous)
  → Tag+1 minimum
  → C-Meldung published
  → References original E (U: part)
  → Proposes correction (C: part)
  → Correction applied
```

#### 6. RNB-Übernahme Dependencies

**Dependency Chain:**
```
BNetzA decision
  → RNB-Übernahme file published
  → Old owner notified
  → New owner prepares
  → Old owner continues service
  → Old owner publishes L-Meldung (like porting)
  → New owner publishes P-Meldung (like porting)
  → Transfer date reached
  → New owner assumes responsibility
  → Old owner deactivates
  → Routing updated everywhere
```

**Critical:** Both TNB must cooperate (Mitwirkungspflicht)

#### 7. Single Message Dependencies

**Dependency Chain:**
```
P/L/Z message published
  → Wait for pair partner
  → 61 AT elapsed
  → No pair partner received
  → Automatic single validation
  → 10 AT objection period
  → If no objection: Final validation
  → Routing updated
```

**Alternative Path:**
```
Initialization scenario
  → Partner TNB no longer exists
  → Verified by BNetzA data
  → Immediate single validation
  → No 61 AT waiting
```

#### 8. Mass Migration Dependencies

**Dependency Chain:**
```
Migration planned
  → Check volume limits (20,000 or 100,000)
  → If >20,000: Get agreements from all active TNBs
  → Publish I-Datei announcement (05)
  → Coordinate timeline
  → Execute migration
  → Monitor processing
  → Confirm completion
```

### Dependency Matrix

| Message | Requires | Timing | Forms Pair With | Enables |
|---------|----------|--------|-----------------|---------|
| **E** | BNetzA allocation | **-5 AT before Einrichtungstermin** | - (Standalone) | P/L after +1 KT |
| **R** | Free RNB | **-20 AT before return** | - (Standalone) | RNB return to BNetzA |
| **P** (Phone) | E-Datum + 1 KT | Tag+1 after port | L (porting) or Z (return) | K, Routing update |
| **P** (RNB) | BNetzA approval | Like porting | L (RNB transfer) | RNB transfer |
| **L** (Phone) | E-Datum + 1 KT | Tag+1 after port | P | K, Routing update |
| **L** (RNB) | BNetzA approval | Like porting | P (RNB transfer) | RNB transfer |
| **Z** | 65 AT after deact | Tag+66 (Z-Datum = Pub-1 KT) | P | K, Routing update |
| **K** | P/L/Z exists | Tag+1 after error | P/L/Z or K | Correction |
| **C** | E/R exists | Tag+1 after error | E/R or C | E/R correction |
| **I** | - | Daily | - | Clearing, Info |
| **DR** | - | On demand | - | Response |

**Note:** Phone numbers use P, L, Z messages. RNBs use E, P, L, R messages (no Z for RNBs).

---

## Critical Timelines and Deadlines

### Timeline Summary Table

| Process | Trigger | Publication | Validation | Routing Update | Expiry |
|---------|---------|-------------|------------|----------------|--------|
| **Portierung** | Porting executed | Tag+1 | P+L pair | After validation | After RUZ (2M) |
| **Rückgabe** | Deactivation | 65 AT + 1 T | P+Z pair | After validation + 5 AT | After RUZ (2M) |
| **RNB Setup (E)** | BNetzA allocation | **-5 AT before Einrichtungstermin** | Immediate (Standalone) | Immediate | Never (until return) |
| **RNB Return (R)** | Return decision | **-20 AT before return** | Immediate (Standalone) | As "not connected" | Returned to BNetzA |
| **RNB Transfer (P+L)** | BNetzA approval | Like porting | P+L pair required | After validation | Never |
| **Korrektur** | Error detected | Tag+1 after error | Most: confirmation | After validation | After RUZ |
| **Single** | Missing pair | 61 AT after message | Auto after 61 AT | After objection (10 AT) | Never |
| **4XXX Codes** | Structure change | Tag+1 | No confirm needed | After objection (10 AT) | After RUZ |

### Detailed Timelines

#### Portierung Timeline (Porting)

```
t0: Porting executed in networks
t0+1: P-Meldung published by TNB receiving
t0+1: L-Meldung published by TNB donating
t0+1: Validation (if P and L match)
t0+1: Other TNBs update routing
t0 to t0+2M: RUZ (call forwarding by donating TNB)
t0+2M: RUZ expires, forwarding can be removed
t0+2M: Old P/L pair can be deleted from databases
```

**Working Days vs. Calendar Days:**
- Publication: Next calendar day (T) after porting
- RUZ: 2 calendar months (M)

#### Rückgabe Timeline (Return)

```
t0: Customer termination (number deactivated)
t0 to t0+65 AT: Reactivation possible at any TNB
t0+65 AT: Last owner must create Z-Meldung
t0+65 AT +1 T: Z-Meldung publication
            Z-Datum = Publication date - 1 KT minimum
t0+65 AT +1 T: Owner publishes P-Meldung
t0+65 AT +1 T: Validation (P+Z pair)
t0+65 AT +1 T: Routing updated
t0+65 AT +1 T to +5 AT: Safety period (no number reactivation by owner)
t0+65 AT +6 AT: Owner can remove forwarding and activate number
t0+65 AT +1 T to +2M: RUZ period
t0+65 AT +2M: RUZ expires, old pair can be deleted
```

**Key Points:**
- 65 AT = 65 Arbeitstage (working days)
- Z-Datum must be < Publication date (minimum 1 KT difference)
- 5 AT safety period prevents premature reactivation
- Allows correction of erroneous returns

#### RNB Timeline (Number Block)

```
t0: BNetzA allocates RNB to TNB
t0: TNB prepares E-Meldung
t0+X: E-Meldung published (minimum -10 KT before E-Datum)
t0+X: All TNBs receive E-Meldung
t0+X to E-Datum: Routing preparation (minimum 10 KT)
E-Datum: Official setup date
E-Datum +1 KT: Earliest P/L-Meldungen allowed for numbers in block
```

**Migration Variant:**
```
t0: Migration planning
t0+1: I-Datei announcement (if >20,000 numbers)
t0+2: Coordination with other TNBs
t0+X: E-Meldungen published (-10 KT)
E-Datum +1 KT: Mass P/L-Meldungen
      (max 20,000/day or 100,000/day with agreement)
```

#### Korrektur Timeline (Correction)

```
t0: Erroneous message published
t0+1: Earliest K-Meldung publication
t0+1 to t0+RUZ: Correction period
t0+1+conf: Validation (if confirmation required)
t0+1+conf: Routing updated (if applicable)
```

**4XXX Structural Changes:**
```
t0: Original messages published
t0+1: 4XXX K-Meldung published
t0+1 to t0+10 AT: Objection period
t0+10 AT: If no objection, change accepted
t0+10 AT: Routing updated
```

**Single Message:**
```
t0: P/L/Z message published
t0 to t0+61 AT: Waiting for pair partner
t0+61 AT: Automatic single validation
t0+61 AT to t0+71 AT: Objection period (10 AT)
t0+71 AT: If no objection, final validation
t0+71 AT: Routing updated
```

#### PK-Abschaltung Timeline (PK Deactivation)

```
t0: Decision to deactivate PK
t0+1: PK-Abschaltemeldung published (announcement)
t0+1 to t0+X: Objection period (variable, typically 30-60 days)
t0+1 to t0+X: RNB transfer preparation
t0+1 to t0+X: Open porting resolution
t0+X: RNB transfers executed (E-Meldungen by new owners)
t0+X: All portings resolved (Z-Meldungen or transfers)
t0+X: Final PK-Abschaltemeldung (confirmation)
t0+X: PK officially deactivated
```

### Frist Types (Deadline Types)

| Term | Type | Description | Calculation |
|------|------|-------------|-------------|
| **AT** | Arbeitstage | Working days | Monday-Friday, excluding public holidays |
| **KT** | Kalendertage | Calendar days | Every day including weekends and holidays |
| **T** | Tag | Day | Next calendar day |
| **M** | Monate | Months | Calendar months |
| **RUZ** | Rufumsteuerungszeit | Call forwarding period | 2 calendar months |

**Important Distinctions:**
- **65 AT:** 65 working days (approximately 3 calendar months)
- **2 M:** 2 calendar months (approximately 60 days)
- **Tag+1:** Next calendar day (not working day)
- **10 KT:** 10 calendar days (not working days)

### Automatic Processes

| Process | Trigger | Automatic Action | Timing |
|---------|---------|------------------|--------|
| **Single Validation** | No pair after 61 AT | Validate single message | 61 AT after publication |
| **Objection Deadline** | 4XXX or 6XXX code | Accept if no objection | 10 AT after publication |
| **Return Trigger** | 65 AT after deact | Create Z-Meldung | 65 AT after deactivation |
| **Routing Update** | Pair validated | Update routing tables | Immediately after validation |
| **RUZ Expiry** | 2 months passed | Allow deletion of old pairs | 2 M after porting/return |

---

## Business Rules Summary

### General Rules

1. **Daily Publication:** All messages published daily (Tag+1 after event)
2. **No Future Messages:** Future-dated messages rejected
3. **Exact Date Matching:** Pairs must have identical porting date
4. **No Same-Day Re-porting:** Minimum Tag+1 between portings of same number
5. **Historical Precedence:** Messages before last validated porting ignored
6. **Sender Validation:** Message sender must match role (aufnehmend/abgebend)
7. **Format Compliance:** Invalid number formats rejected
8. **RNB Prerequisite:** Portings only after E-Datum + 1 KT for RNB numbers

### Pairing Rules

1. **Mandatory Pairing:** P+L or P+Z required for validation
2. **Date Identity:** Paired messages must have identical dates
3. **Routing Trigger:** Routing updated only after validated pair
4. **Single Exception:** After 61 AT, single validation possible
5. **New Pair Precedence:** New validated pair overwrites old unpaired messages
6. **Historical Cleanup:** Old pairs deleted after RUZ expiry

### Correction Rules

1. **Minimum Delay:** Tag+1 after erroneous message
2. **Reference Requirement:** K/C must reference original message (U: part)
3. **Confirmation:** Most codes require confirmation by second TNB
4. **Exceptions:** Codes 2XXX, 4XXX no confirmation needed
5. **Validated Pair Protection:** Cannot correct validated pairs (except 30XX, 4XXX)
6. **Objection Period:** 10 AT for 4XXX and 6XXX codes
7. **Single Validation:** After 61 AT without pair

### RNB Rules

1. **Pre-announcement:** E-Meldung minimum 10 KT before usage
2. **Porting Delay:** P/L only after E-Datum + 1 KT
3. **Migration Limits:** 20,000/day standard, 100,000/day with agreement
4. **I-Datei Announcement:** Required for mass migrations
5. **Takeover Cooperation:** Both old and new owner must cooperate
6. **BNetzA Approval:** Required for RNB transfers

### Timeline Rules

1. **Portierung:** Publication Tag+1, RUZ 2 months
2. **Rückgabe:** 65 AT waiting, Z-Datum = Pub - 1 KT, RUZ 2 months, 5 AT safety
3. **Korrektur:** Publication Tag+1, objection 10 AT (if applicable)
4. **Single:** 61 AT waiting, 10 AT objection
5. **RNB:** Publication -10 KT, usage after E-Datum + 1 KT

### Information Rules

1. **3i-Datei:** Daily update, valid contacts mandatory
2. **4i-Datei:** HPK/PK relationships, merger information
3. **Contact Reachability:** Contacts must be available during business hours
4. **Clearing:** Standard email format, escalation path defined
5. **Migration Announcement:** Via I-Datei for large volumes

### Validation Rules

1. **Accept:** Backdated messages with original porting date
2. **Reject:** Future-dated messages
3. **Reject:** Same publication and porting date
4. **Reject:** Before E-Datum + 1 KT (for RNB numbers)
5. **Reject:** Wrong sender TNB
6. **Reject:** Before last validated porting date
7. **Reject:** Invalid number formats (e.g., 11-digit in 2-digit area code zones)

### Deletion Rules

1. **After RUZ:** Old validated pairs can be deleted (2 months)
2. **After Validation:** Unpaired messages deleted when new pair validated
3. **Historization:** Deleted = not current, but can be archived
4. **Reference Retention:** K-Dateien kept for RUZ period (2 months)
5. **E-Datei Retention:** Until RNB returned to BNetzA

---

## Diagram Guide

### Available Diagrams

This documentation includes two PlantUML diagrams:

#### 1. PDA-Process-Mindmap.puml
**Type:** Mindmap
**Purpose:** High-level overview of all PDA processes
**View:** Organized by process category

**Structure:**
- **Left Side:**
  - REGELVERFAHREN (Standard Procedures)
    - Portierung scenarios (1a-1e)
    - Rückgabe scenarios (2a-2b)
    - Fristen & Business Rules
  - KORREKTURVERFAHREN (Corrections)
    - Rücknahme codes (2XXX)
    - Korrektur codes (0XXX-1XXX)
    - Struktur codes (4XXX)
    - Nachträglich codes (3XXX, 6XXX)

- **Right Side:**
  - RNB-VERFAHREN (Number Blocks)
    - Einrichtung (E-Messages)
    - Übernahme (Takeover)
    - RNB-Korrektur (C-Messages)
    - Business Rules
  - SUPPORT-PROZESSE (Support)
    - Info-Dateien (I-Messages)
    - Datenabfragen (DR-Messages)
    - Ausbleibende Meldungen (Missing messages)
    - PK-Abschaltung (PK deactivation)
    - Technische Infrastruktur (Technical infrastructure)

**Color Coding:**
- **Blue:** Main processes
- **Green:** Standard porting messages (P, L, Z)
- **Red:** Correction procedures (K)
- **Purple:** RNB processes (E, C)
- **Cyan:** Support processes (I, DR)

**Best For:**
- Understanding overall PDA structure
- Learning process categories
- Quick reference to find specific procedures

#### 2. PDA-Process-Dependencies.puml
**Type:** Component/Package Diagram
**Purpose:** Show dependencies and relationships between message types
**View:** Organized by dependency chains

**Structure:**
- **REGELVERFAHREN Package:**
  - Portierung (P + L pairing)
  - Rückgabe (P + Z pairing)

- **KORREKTURVERFAHREN Package:**
  - K-Meldung (corrections for P/L/Z)
  - Single-Meldungen (6XXX codes)

- **RNB-VERFAHREN Package:**
  - E-Meldung (RNB setup)
  - C-Meldung (RNB corrections)
  - RNB-Übernahme (takeover process)

- **SUPPORT-PROZESSE Package:**
  - I-Meldung (information)
  - DR-Meldung (data requests)
  - PK-Abschaltung (deactivation)

- **ZEITLICHE ABLÄUFE Package:**
  - Fristen (deadlines)
  - Validierung (validation rules)

**Arrow Types:**
- **Solid:** Required pairing / Direct dependency
- **Dashed:** Correction / Withdrawal relationship
- **Dotted:** Information / Request relationship
- **Bold:** Enables / Prerequisites

**Best For:**
- Understanding message dependencies
- Planning implementation sequences
- Troubleshooting validation issues
- Understanding when messages can/cannot be published

### How to Use the Diagrams

#### For New PDA Participants:
1. Start with **Mindmap** to understand overall structure
2. Focus on REGELVERFAHREN section (standard processes)
3. Review **Dependencies** diagram to understand pairing requirements
4. Study timeline rules

#### For Implementers:
1. Use **Dependencies** diagram to understand technical requirements
2. Identify mandatory dependencies (solid arrows)
3. Implement validation logic based on dependency rules
4. Refer to **Mindmap** for complete code lists

#### For Operations:
1. **Mindmap** for daily reference (code lookups, process steps)
2. **Dependencies** for troubleshooting (why message rejected?)
3. Timeline section for deadline calculations

#### For Troubleshooting:
1. **Dependencies** diagram: Check if prerequisite met
2. **Mindmap**: Find correct procedure and code
3. This document: Verify business rule compliance
4. Timeline section: Calculate if within deadline

### Generating Diagrams

**Requirements:**
- PlantUML (https://plantuml.com/)
- Java Runtime Environment
- Or: Online PlantUML editor (https://www.plantuml.com/plantuml/)

**Command Line:**
```bash
java -jar plantuml.jar PDA-Process-Mindmap.puml
java -jar plantuml.jar PDA-Process-Dependencies.puml
```

**Output:**
- PNG, SVG, or PDF format
- Scalable for presentations
- Printable for reference

**Integration:**
- Can be embedded in Confluence
- Can be included in technical documentation
- Can be used in training materials

---

## Quick Reference Tables

### Message Type Quick Reference

| Code | Name | German | Sender | Pair With | Purpose | Applies To |
|------|------|--------|--------|-----------|---------|------------|
| **P** | Porting | Portierung | TNB aufnehmend | L or Z | Number ported TO carrier | Rufnummern + RNB |
| **L** | Leaving | Löschen | TNB abgebend | P | Number LEFT carrier | Rufnummern + RNB |
| **Z** | Return | Zurück | Last owner | P | Number RETURNED to owner | **Rufnummern only** |
| **E** | Setup | Einrichtung | RNB owner | - (Standalone) | New RNB SET UP (BNetzA→TNB) | **RNB only** |
| **R** | Return | Rückgabe | Original holder | - (Standalone) | RNB RETURNED to BNetzA (TNB→D000) | **RNB only** |
| **C** | RNB Correction | RNB Korrektur | RNB owner | E or R | Correct E/R-Message | **RNB only** |
| **K** | Correction | Korrektur | Error source | P/L/Z or K | Correct P/L/Z message | Rufnummern |
| **I** | Information | Info | Any TNB | - | Provide contact/org info | All |
| **DR** | Data Request | Datenabfrage | Requesting TNB | - | Request/provide data | All |

**Important:**
- **Rufnummern** (phone numbers) use: P, L, Z messages
- **RNBs** (number blocks) use: E, P, L, R messages (**no Z for RNBs**)
- **E and R are standalone** (not paired) per AKNN 7.2.4
- **P+L for RNB transfer** requires pairing per AKNN 7.4.2

### Correction Code Quick Reference

| Code Range | Category | Confirmation | Purpose | Objection Period |
|------------|----------|--------------|---------|------------------|
| **2000-2400** | Own withdrawal | No | Withdraw own message | None |
| **2500-2599** | Foreign objection | No | Object to foreign message | None |
| **0100-0400** | Data correction | Yes | Correct field data | None |
| **4100** | Merge | No | Combine ranges | 10 AT |
| **4200** | Extend | No | Extend range | 10 AT |
| **4300** | Split | No | Split range | 10 AT |
| **4400-4500** | Combination | No | Complex structures | 10 AT |
| **4600-4730** | Blocking | No | Block/unblock numbers | 10 AT (4700-4720) |
| **30XX** | Retrospective | Yes | Correct validated pairs | None |
| **6000-6200** | Single | No | Validate without pair | 10 AT |

### File Name Quick Reference

| Prefix | Type | German | Content | Frequency |
|--------|------|--------|---------|-----------|
| **1D** | Default | Standard | Daily P/L/Z inventory | Daily |
| **1R** | Response | Antwort | Response to request | On demand |
| **1K** | Correction | Korrektur | K-Messages (corrections) | As needed |
| **1E** | RNB Setup | Einrichtung | E-Messages (RNB setup) | As needed |
| **1C** | RNB Correction | RNB Korrektur | C-Messages (RNB corr) | As needed |
| **1I** | Information | Info | I-Messages (contacts) | Daily |

**Format:** `[Prefix][YYMMDD].txt`
**Example:** `1D251212.txt` (Default file from December 12, 2025)

### Deadline Type Quick Reference

| Term | Full Name | Type | Example | Typical Duration |
|------|-----------|------|---------|------------------|
| **AT** | Arbeitstage | Working days | 65 AT | ~13 weeks |
| **KT** | Kalendertage | Calendar days | 10 KT | ~1.5 weeks |
| **T** | Tag | Day | Tag+1 | Next day |
| **M** | Monate | Months | 2 M | 2 months |
| **RUZ** | Rufumsteuerungszeit | Call forwarding | 2 M | 2 months |

### Timeline Quick Reference

| Process | When to Publish | When Validated | When Routing Updated | When Expired |
|---------|----------------|----------------|---------------------|--------------|
| **Portierung** | Tag+1 | P+L pair | After validation | After RUZ (2M) |
| **Rückgabe** | 65 AT + 1 T | P+Z pair | After valid + 5 AT | After RUZ (2M) |
| **RNB Setup** | -10 KT before E-Datum | Immediate | Immediate | Until RNB returned |
| **Korrektur** | Tag+1 after error | On confirmation | After validation | After RUZ |
| **Single** | After 61 AT | Auto after 61 AT | After 10 AT | Never |
| **4XXX** | Tag+1 | No confirm | After 10 AT | After RUZ |

### Contact Type Quick Reference (3i-Datei)

| Code | Type | German | Purpose | When to Contact |
|------|------|--------|---------|-----------------|
| **01** | Business | Fachlich | General PDA questions | Standard issues |
| **02** | Detailed Business | Fachlich detailliert | Complex scenarios | Escalation, complex cases |
| **03** | Technical | Technisch | IT/system issues | Connection, file transfer |

### Process Flow Quick Reference

#### Standard Porting (1a):
```
1. Port executed → 2. Publish P+L (Tag+1) → 3. Validated → 4. Routing updated → 5. RUZ (2M)
```

#### Return (2a):
```
1. Deactivate → 2. Wait 65 AT → 3. Publish Z+P (Tag+66) → 4. Validated → 5. Wait 5 AT → 6. Remove forwarding → 7. RUZ (2M)
```

#### RNB Setup:
```
1. BNetzA allocates → 2. Publish E (-10 KT) → 3. E-Datum → 4. Wait 1 KT → 5. Allow P/L
```

#### Correction:
```
1. Error detected → 2. Wait 1 day → 3. Publish K → 4. Confirmation (if required) → 5. Applied
```

#### Single Message:
```
1. Publish P/L/Z → 2. Wait 61 AT → 3. Auto-validate → 4. Objection period 10 AT → 5. Final
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-12 | Documentation Team | Initial creation based on ITEX-PDA 20.0.0 |

---

## References

1. **ITEX-PDA Specification 20.0.0** (Valid from 06.05.2024)
   - Primary source document
   - File: `23-05-09_ITEX-PDA_Spezifikation_PDA_20-0-0.pdf`

2. **Arbeitshandbuch Clearing** (Clearing Handbook)
   - Published by AK-SPRI
   - URL: https://ak-spri.de/prozesse/clearing/
   - Contains clearing scenarios and procedures

3. **BNetzA Regulations**
   - Rufnummernportierung regulations
   - RNB allocation procedures
   - Compliance requirements

4. **AKNN** (Arbeitskreis für technische und betriebliche Fragen der Nummerierung und der Netzzusammenschaltung)
   - Working group for numbering and interconnection
   - Approves PDA specification versions

---

## Contact & Support

For questions about this documentation:
- Contact your organization's PDA team
- Refer to 3i-Datei contacts for operational issues
- Consult ITEX-PDA working group for specification questions

For technical issues with diagrams:
- PlantUML documentation: https://plantuml.com/
- PlantUML forum: https://forum.plantuml.net/

---

**Document End**
