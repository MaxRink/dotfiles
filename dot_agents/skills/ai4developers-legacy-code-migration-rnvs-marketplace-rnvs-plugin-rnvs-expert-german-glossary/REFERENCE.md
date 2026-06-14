# German Telecommunications Glossary Reference

Complete database of 200+ German telecommunications terms for RNVS/VNRM migration.

---

## Table of Contents

1. [Variable Glossary](#variable-glossary)
2. [Core Telecommunications Terms](#core-telecommunications-terms)
3. [System Components](#system-components)
4. [Porting & Import/Export](#porting--importexport)
5. [Organizational Abbreviations](#organizational-abbreviations)
6. [Technical Abbreviations](#technical-abbreviations)
7. [Status & Process Terms](#status--process-terms)
8. [Network & Technology](#network--technology)
9. [Product & Service Abbreviations](#product--service-abbreviations)
10. [Partner Systems & Interfaces](#partner-systems--interfaces)
11. [Cloud & Infrastructure](#cloud--infrastructure)
12. [Special Cases](#special-cases)
13. [Compound Words](#compound-words)

---

## Variable Glossary

Common German variable names found in RNVS code:

| Variable | English Translation | German Full Form | Type |
|----------|---------------------|------------------|------|
| rfnr | callNumber | Rufnummer | String |
| rnb | numberBlock | Rufnummernblock | Object |
| rnbId | numberBlockId | Rufnummernblock-ID | Long |
| onkz | areaCode | Ortsnetzkennzahl | String |
| tnb | fno | Teilnehmernetzbetreiber | String |
| tnbKennung | fnoIdentifier | Teilnehmernetzbetreiber-Kennung | String |
| pdaExport | portingDataExport | Portierungsdaten Austausch Export | Object |
| pdaImport | portingDataImport | Portierungsdaten Austausch Import | Object |
| bsa | provisioningOrder | Bereitstellungsauftrag | Object |
| bereichsInfo | areaInformation | Bereichsinformation | Object |
| besitzer | possessor | Besitzer | String |
| eigentuemer | owner | Eigentümer | String |
| auftrag | order | Auftrag | Object |
| verwaltung | management | Verwaltung | Object |
| portierung | porting | Portierung | Object |
| rufumsteuerzeit | callForwardingTime | Rufumsteuerzeit | Duration |
| schalttag | setupDate | Schalttag | Date |
| vermittlungseinheit | switchingUnit | Vermittlungseinheit | String |
| netzzugang | networkAccess | Netzzugang | String |
| endeinrichtungsnummer | extensionNumber | Endeinrichtungsnummer | String |
| muttervermittlungsstelle | parentExchange | Muttervermittlungsstelle | String |
| datendrehscheibe | dataHub | Datendrehscheibe | System |
| buchungsauftrag | bookingOrder | Buchungsauftrag | Object |
| buchungskontingent | bookingContingent | Buchungskontingent | Object |
| schwellwert | thresholdValue | Schwellwert | Integer |
| portierungslevel | portingLevel | Portierungslevel | String |
| portierungsstatus | portingStatus | Portierungsstatus | String |

---

## Core Telecommunications Terms

| German | English | Abbreviation | Context |
|--------|---------|--------------|---------|
| Rufnummer | Call Number / Phone Number | RN | Individual telephone number |
| Rufnummernblock | Number Block | RNB | Block of telephone numbers |
| Rufnummernverwaltungssystem | Phone Number Management System | RNVS | Legacy system name (keep as-is) |
| Teilnehmernetzbetreiber | Fixed-line Network Operator | TNB, FNO | Telecom service provider |
| Portierungsdaten Austausch | Porting Data Exchange | PDA | Number portability process |
| Ortsnetzkennzahl | Area Code | ONKZ | Geographic area identifier |
| Ortsnetzbereich | Local Calling Area | ONB | Local exchange area |
| Durchwahlrufnummer | Direct Dialing Number | DuWa, DDI | Extension dialing |
| Einzelrufnummer | Single Call Number | ERN | Individual phone number |
| Bundesnetzagentur | Federal Network Agency | BNetzA, FNA | German telecom regulator |
| Portierungskennung | Porting Identifier | PK, D-Kennung | Provider identifier for porting |
| Besitzer | Possessor / Holder | - | Current number user (not legal owner) |
| Eigentümer | Owner / Originator | - | Legal owner of number |
| Vermittlungseinheit | Switching Unit | VE | Technical routing unit |
| Netzzugang | Network Access | NZ | Connection to telephone network |
| Endeinrichtungsnummer | Extension Number | EENr | Internal extension digit |
| Buchungsauftrag | Booking Order | - | Number allocation order |
| Bereitstellungsauftrag | Provisioning Order | BSA | Setup order |
| Bereichsinformation | Area Information | BI | Number range metadata |
| Muttervermittlungsstelle | Parent Exchange | MVSt | Central switching station |
| Datendrehscheibe | Data Hub | DDS | File exchange platform |
| Weiterversorgung | Continued Service | - | Service continuation |
| Wiederanschaltung | Reconnection | - | Service reactivation |
| Rückfall | Fallback | - | Number returns to original owner |
| Rückportierung | Reverse Porting | - | Porting back to original provider |
| Kündigung | Termination / Cancellation | - | Contract termination |
| Auftrag | Order | - | Business order/task |
| Verwaltung | Management | Vwltg | Administration |
| Rechnung | Invoice | Rech | Billing |
| Telefonanlage | PBX / Telephone System | TK-Anlage | Private branch exchange |
| Notruf | Emergency Services | - | 110, 112 calls |

---

## System Components

| German | English | Context |
|--------|---------|---------|
| Voice Number & Routing Management | VNRM | New system name (keep as-is) |
| Leitweglenkung | Routing | LWL - Call routing management |
| Nummernmanager | Number Manager | NM - Number management role |
| Strukturierer | Allocator | Number allocation system |
| Buchungskennzeichen | Booking Identifier | Bkz - Allocation marker |
| Buchungssystem | Booking System | BSys - Allocation system |
| Buchungskontingent | Booking Contingent | BUK - Number quota |
| Schwellwerte | Threshold Values | Allocation limits |
| Festwert | Fixed Value | Minimum threshold |
| Statistikzähler | Statistical Counter | Usage metrics |
| Betriebstagebuch | Operational Diary | System log |

---

## Porting & Import/Export

| German | English | Abbreviation | Description |
|--------|---------|--------------|-------------|
| Export | Export | - | Porting number out of DTAG network |
| Import | Import | - | Porting number into DTAG network |
| ReImport | Re-Import | - | Porting D001-owned number back to DTAG |
| Portierungslevel | Porting Level | - | Porting status (u1, u2, u3, u4) |
| Portierungsstatus | Porting Status | PStatus | P=ported in, L=ported out, Z=fallback |
| Drittportierung | Third-party Porting | - | Porting between non-DTAG providers |
| Vorabstimmung | Pre-coordination | VA | Porting pre-agreement |

---

## Organizational Abbreviations

| Abbreviation | German | English | Description |
|--------------|--------|---------|-------------|
| BNetzA | Bundesnetzagentur | Federal Network Agency | German telecom regulator |
| DTAG | Deutsche Telekom AG | - | Company name |
| DTIT | Deutsche Telekom IT GmbH | - | IT subsidiary |
| TSI | T-Systems International GmbH | - | IT company |
| TNB | Teilnehmernetzbetreiber | Fixed-line Network Operator | Service provider |
| ISP | Internet Service Provider | - | Provider without own network |
| AKNN | Arbeitskreis Nummerierung | Working Group Numbering | Technical committee |
| ITEX-PDA | IT-Expertengruppe PDA | IT Expert Group PDA | PDA technical group |

---

## Technical Abbreviations

| Abbreviation | Full Form | English | Description |
|--------------|-----------|---------|-------------|
| RNVS | Rufnummernverwaltungssystem | Phone Number Management System | Legacy system |
| VNRM | Voice Number & Routing Management | - | New system |
| DDS | Datendrehscheibe | Data Hub | File exchange platform |
| ComServ | Communication Server | - | Integration server |
| PDA | Portierungsdaten Austausch | Porting Data Exchange | Portability process |
| RNB | Rufnummernblock | Number Block | Block of numbers |
| ERN | Einzelrufnummer | Single Call Number | Individual number |
| DuWa | Durchwahlrufnummer | Direct Dial Number | Extension number |
| EAS | EinzelAnSchluss | Single Line | Analog single connection |
| BAAS | Basisanschluss | ISDN Basic Access | 2B+D ISDN |
| NZ-E | Netzzugang Einzelrufnummern | Network Access Single Numbers | Individual number access |
| NZ-Z | Netzzugang Zusammenhängend | Network Access Contiguous | Block number access |
| ONKZ | Ortsnetzkennzahl | Area Code | Geographic prefix |
| ONB | Ortsnetzbereich | Local Calling Area | Local exchange area |
| MVSt | Muttervermittlungsstelle | Parent Exchange | Central switch |
| VE | Vermittlungseinheit | Switching Unit | Routing unit |
| EENr | Endeinrichtungsnummer | Extension Number | Internal extension |
| BI | Bereichsinformation | Area Information | Range metadata |
| BSA | Bereitstellungsauftrag | Provisioning Order | Setup order |
| BUK | Buchungskontingent | Booking Contingent | Number quota |
| NGN | Next Generation Network | - | Modern network |
| NGN-PK | NGN-Portierungskennung | NGN Porting Identifier | NGN provider ID |
| IP-NPK | IP-Netzportierungskennung | IP Network Porting Identifier | IP provider ID (199C07) |
| NGNP | Next Generation Number Porting | - | Nokia routing system |
| RNPS | Resource Number Provisioning Service | - | Provisioning service |
| ZMRDB | Zentrale Master Routing Datenbank | Central Master Routing Database | National routing DB |
| MNP | Mobilrufnummernportabilität | Mobile Number Portability | Mobile porting |
| MRDB | Master Routing Datenbank | Master Routing Database | Routing database |
| HBK | Hauptportierungskennung | Main Porting Identifier | Primary provider ID (D001) |
| CPI | Callnumber Porting Info | - | Porting information service |
| CCI | Callnumber Contingent Information | - | VNRM quota function |

---

## Status & Process Terms

| German | English | Values/Description |
|--------|---------|-------------------|
| Status = frei | Status = free | Available for allocation |
| Status = erledigt | Status = completed | Order completed |
| Status = gestoppt | Status = stopped | Order stopped |
| Wiederbelegungsdatum | Reallocation Date | Date when number becomes available |
| Schalttag | Setup Date | Date when access is activated |
| Einrichtungsdatum | Provisioning Date | Date when block becomes active |
| Freigabedatum | Release Date | Date when available for booking |
| Arbeitstage | Working Days | AT - Mon-Fri excluding federal holidays |
| Toleranzgrenze | Tolerance Limit | ±days for porting |
| Rufumsteuerzeit | Call Forwarding Time | RUZ - 2 months |

---

## Network & Technology

| Abbreviation | Full Form | Description |
|--------------|-----------|-------------|
| PSTN | Public Switched Telephone Network | Analog telephone network |
| IMS | IP Multimedia Subsystem | VoIP telephone network |
| SIP | Session Initiation Protocol | VoIP protocol |
| VoIP | Voice over IP | Internet telephony |
| ISDN | Integrated Services Digital Network | Digital telephone |
| CPE | Customer Premises Equipment | Customer device |
| IAD | Integrated Access Device | Speedport, Fritz!Box |
| BNG | Border Network Gateway | IP aggregation point |
| HLR/HSS | Home Location Register / Home Subscriber Server | Mobile network DB |
| CORBA | Common Object Request Broker Architecture | Legacy integration |
| REST | Representational State Transfer | Modern API |
| SOAP | Simple Object Access Protocol | Web service protocol |

---

## Product & Service Abbreviations

| Abbreviation | German | English | Description |
|--------------|--------|---------|-------------|
| CFS | Customer Facing Service | - | Customer-visible service |
| RFS | Resource-facing Service | - | Internal resource service |
| TKG | Telekommunikationsgesetz | Telecommunications Act | German telecom law |
| GEO | German Eyes Only | - | German security level |
| VS-NfD | Verschlusssachen - nur für den Dienstgebrauch | Classified - Official Use Only | Security classification |

---

## Partner Systems & Interfaces

| Abbreviation | Full Name | Type | Description |
|--------------|-----------|------|-------------|
| CRM-C | Customer Relationship Management Classic | System | Customer management |
| CRM-T | Customer Relationship Management Telekom | System | DTAG CRM |
| KONTES | - | System | Wholesaler system |
| TSAM | - | System | T-Systems order system |
| EKI | Eingangs Kanal Internet | System | Telekom.de platform |
| RAM | - | Interface | T-Online booking interface |
| BLW | Business Logic Wholesale | Interface | Wholesale interface |
| POINT | - | System | Legacy system (now BISS-KDM) |
| BISS-KDM | - | System | POINT successor |
| KLS | Key Location Service | Interface | Location data service |
| ECC | - | Portal | Magenta Business portal |
| MH | Magenta Haus | System | Magenta Business |
| PBP | Product Business Platform | System | Magenta Business platform |
| RMK | Ressourcen Management Komponente | System | Resource management |
| SMK | Service Management Komponente | System | Service management |
| AMK | Auftragsmanagementkomponente | System | Order management |
| AL-PS | Auftragslenkung Produkt und Service | System | Order routing |
| SDI-DB | SIP-Trunk Database | Database | VoIP GK customer data |
| SIP-DB | SIP Database | Database | VoIP PK customer data |

---

## Cloud & Infrastructure

| Abbreviation | Full Name | Description |
|--------------|-----------|-------------|
| OTC | Open Telekom Cloud | TSI cloud based on Huawei/OpenStack |
| TPC | Telekom Private Cloud | DTIT private cloud (IaaS) |
| FCI | Future Cloud Infrastructure | TSI cloud based on Lenovo/VCF |
| DCP | Dynamic Cloud Platform | TSI virtualized infrastructure (Cisco) |
| ITSF | IT Serverfarm | DTIT compute infrastructure |
| CaaS | Container as a Service | DTIT K8S namespace service |
| TAP | Telekom Application Platform | DTIT PaaS (successor of ASF) |
| ASF | API & Service Factory | DTIT PaaS (predecessor of TAP) |
| AWS | Amazon Web Services | Public cloud |
| GCP | Google Cloud Platform | Public cloud |
| OCI | Oracle Cloud Infrastructure | Oracle cloud |
| K8S | Kubernetes | Container orchestration |
| VCF | VMware Cloud Foundation | Multi-cloud platform |

---

## Special Cases

### TNB vs FNO vs ISP

- **TNB** (Teilnehmernetzbetreiber): Generic German term
  - English: "Fixed-line Network Operator (FNO)"
- **FNO** with own network: "Fixed-line Network Operator"
- **ISP** without network: "Internet Service Provider"

**When to use**:
- Use TNB in German documentation
- Use FNO in English technical documentation
- Use ISP only for providers without their own network infrastructure

### Besitzer vs Eigentümer

- **Besitzer**: Current possessor/holder (NOT legal owner)
  - In porting context → "possessor"
  - In legal context → "holder"
  - Meaning: The person/company currently using the number

- **Eigentümer**: Legal owner (originator)
  - Always → "owner"
  - Meaning: The legal entity that owns the number
  - Note: D001 (DTAG) is always **Eigentümer** for DTAG-allocated numbers

**When to use**:
- Porting documentation: Use "possessor" vs "owner" to distinguish
- Legal documentation: Use "holder" vs "owner"
- Code variables: `besitzer` → `possessor`, `eigentuemer` → `owner`

### Porting Terminology

- **Export**: Porting number OUT of DTAG network (to another provider)
- **Import**: Porting number INTO DTAG network (from another provider)
- **ReImport**: Porting D001-owned number back to DTAG (was ported out, now coming back)
- **Drittportierung**: Third-party porting (neither source nor target is DTAG)

**Context**:
- From DTAG perspective: Export = losing customer, Import = gaining customer
- D001 = DTAG's main porting identifier (Hauptportierungskennung/HBK)

### Status Values

Porting levels (Portierungslevel):
- **u1**: Unconfirmed stage 1
- **u2**: Unconfirmed stage 2
- **u3**: Fallback (Rückfall) - porting canceled, number returns
- **u4**: Porting notification exists

Porting status (Portierungsstatus):
- **P**: Ported in (to own network)
- **L**: Ported out (left to other provider - "L" for "Lief")
- **Z**: Returned to owner or terminated ("Z" for "Zurück")

Booking status:
- **frei**: Free/available for allocation
- **erledigt**: Completed/done
- **gestoppt**: Stopped/halted

### Auftrag Context

The word **Auftrag** has different translations based on context:

1. **Booking context** → "order"
   - Example: `Buchungsauftrag` → "booking order"
   - Meaning: Order to allocate numbers

2. **Task context** → "task"
   - Example: `Arbeitsauftrag` → "work task"
   - Meaning: Work assignment or job

3. **Contract context** → "contract" or "order"
   - Example: `Kundenauftrag` → "customer order"
   - Meaning: Service order from customer

**Rule**: Look at the prefix or context to determine meaning.

---

## Compound Words

German compound words can be broken down into component parts:

| Compound Word | Parts | Translations | Combined English | Abbreviation |
|---------------|-------|--------------|------------------|--------------|
| Rufnummernverwaltungssystem | Rufnummer + Verwaltung + System | Call Number + Management + System | Phone Number Management System | RNVS |
| Teilnehmernetzbetreiber | Teilnehmer + Netz + Betreiber | Subscriber + Network + Operator | Fixed-line Network Operator | TNB |
| Ortsnetzkennzahl | Orts + Netz + Kennzahl | Local + Network + Code | Area Code | ONKZ |
| Portierungsdaten | Portierung + Daten | Porting + Data | Porting Data | - |
| Muttervermittlungsstelle | Mutter + Vermittlung + Stelle | Parent + Switching + Station | Parent Exchange | MVSt |
| Datendrehscheibe | Daten + Dreh + Scheibe | Data + Rotating + Disk | Data Hub | DDS |
| Bereitstellungsauftrag | Bereitstellung + Auftrag | Provisioning + Order | Provisioning Order | BSA |
| Buchungskontingent | Buchung + Kontingent | Booking + Contingent | Booking Contingent | BUK |
| Bundesne tzagentur | Bundes + Netz + Agentur | Federal + Network + Agency | Federal Network Agency | BNetzA |

**Translation Strategy**:
1. Identify word boundaries (often with connecting "s" or "n")
2. Translate each component
3. Combine in English order (may be reversed from German)
4. Check if there's a standard abbreviation

---

## Output Formats

### For Variable Translation Tables

```markdown
| German Original | English Translation | German Full Form | Type | File Location |
|----------------|---------------------|------------------|------|---------------|
| rfnr | callNumber | Rufnummer | String | PortingService.java:45 |
| rnbId | numberBlockId | Rufnummernblock-ID | Long | AllocationService.java:23 |
```

### For Abbreviation Expansion in Diagrams

```plantuml
note right
  RNB = Rufnummernblock (Number Block)
  TNB = Teilnehmernetzbetreiber (Fixed-line Network Operator)
  PDA = Portierungsdaten Austausch (Porting Data Exchange)
end note
```

### For Business Logic Documentation (German)

```markdown
Regel R001: Rufnummernvalidierung

Business-Ziel: Sicherstellen, dass nur gültige Rufnummern (RN) im System
gebucht werden, die den BNetzA-Vergaberegeln entsprechen.

Glossar:
- RN = Rufnummer (Call Number)
- BNetzA = Bundesnetzagentur (Federal Network Agency)
```

---

**Last Updated**: 2025-10-21
**Total Terms**: 200+
**Categories**: 12
