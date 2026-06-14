# CID Label Convention Reference

The CID group uses a structured label system with letter prefixes indicating category.

## A - Squad Assignment (Team Ownership)

| Label | Description |
|-------|-------------|
| `A - CDM_squad` | Cloud Delivery Management squad |
| `A - CaaS_squad` | CaaS squad |
| `A - DC_squad` | DC Infrastructure squad |
| `A - DCIM_squad` | DCIM development squad |
| `A - Networks_squad` | Networks squad |
| `A - Magellan_squad` | Magellan squad |
| `A - Monitoring_squad` | Monitoring squad |
| `A - Onboarding_squad` | Onboarding squad |
| `A - OBSERVABILITY_squad` | Observability squad |
| `A - JeePain_squad` | JeePain squad |
| `A - DEVELOPMENTS_squad` | Developments squad |

## B - Epic Status & Ownership

**Epic Lifecycle (`B - epic::`):**
| Label | Description |
|-------|-------------|
| `B - epic::Backlog` | Epic in backlog |
| `B - epic::Refinement` | Epic in design and sizing |
| `B - epic::Prepared` | Epic prioritized and ready for scheduling |
| `B - epic::ToDo` | Epic in scope of Sprint planning |
| `B - epic::Doing` | Epic in implementation |
| `B - epic::Done` | Epic closed |

**Epic Owners (`B - epic_owner::`):**
`B - epic_owner::Balazs`, `B - epic_owner::Gyuri`, `B - epic_owner::Igor`, `B - epic_owner::Kostas`, `B - epic_owner::Levi`, `B - epic_owner::Pavel`, `B - epic_owner::PeterB`, `B - epic_owner::Sanyi`, `B - epic_owner::Sebastian`, `B - epic_owner::Tamas`

## C - Issue Status

| Label | Description |
|-------|-------------|
| `C - issue::Backlog` | Issue in backlog |
| `C - issue::Refinement` | Issue is topic for refinement session |
| `C - issue::Prepared` | Prioritized, weighted with clear definition |
| `C - issue::ToDo` | In scope of sprint but not started |
| `C - issue::Doing` | Issue is in implementation |
| `C - issue::Blocked` | Issue is blocked |
| `C - issue::Pending merge` | Waiting for code merge |
| `C - issue::Done` | Issue ready to close |
| `C - issue::Closed` | Solution accepted by PO/customer |

## D - Priority

| Label | Priority Level |
|-------|----------------|
| `D - 1 - critical` | Critical (1) |
| `D - 2 - high` | High (2) |
| `D - 3 - medium` | Medium (3) |
| `D - 4 - low` | Low (4) |

## E - Environment/Datacenter Location

Format: `E - {IC|SC|HC}-{COUNTRY}{CITY}{TYPE}{NUMBER}`

**Country codes:** AT (Austria), CZ (Czechia), DE (Germany), GR (Greece), HR (Croatia), HU (Hungary), ME (Montenegro), MK (North Macedonia), PL (Poland), RO (Romania), SK (Slovakia)

**Type codes:** IC (Infrastructure Cloud), SC (Support Cloud), HC (Housekeeper Cloud), B (BDC), F (FDC), T (Test)

Examples:
- `E - IC-HUBUDF1` - Budapest Fehervari (Li)
- `E - IC-DEBAMF1` - Bamberg F1
- `E - IC-HRZAGF1` - Zagreb FDC production
- `E - SC-HUBUDB1` - Budapest SC v1

## Country Reference (for --country filter)

The `--country` filter accepts country codes or full names (case-insensitive):

| Code | Country | Known City Patterns in Titles |
|------|---------|------------------------------|
| AT | Austria | atwie, atvie, vienna, wien |
| CZ | Czechia | czthp, czbrn, czpra, prague, praha, brno, tmcz |
| DE | Germany | debam, defra, bamberg, frankfurt |
| GR | Greece | grthe, grsal, thessaloniki, salonica |
| HR | Croatia | hrzag, zagreb |
| HU | Hungary | hubud, budapest |
| ME | Montenegro | mepod, podgorica |
| MK | North Macedonia | mksko, skopje |
| PL | Poland | plwar, plkra, warsaw, warszawa, krakow |
| RO | Romania | robuc, bucharest, bucuresti |
| SK | Slovakia | skbra, skvar, skkos, skjak, bratislava, varin, kosice, jarovce |

**Note:** City patterns are matched in epic titles (case-insensitive). Extend the patterns in `utils/config.py` as new naming conventions emerge.

## I - DC Squad Work Categories

| Label | Description |
|-------|-------------|
| `I - DESIGN` | BOM preparation, site design and LLD |
| `I - ORDER & PROCURE` | Equipment ordering, procurement and delivery |
| `I - SITE READINESS` | HW installation and DCIM update |
| `I - HW MGMT` | Hardware management |
| `I - ASSET TRANSFER` | Asset transfer or transport of equipment |
| `I - GENERAL` | Contract prolongation, one time activities |

## Numbered Workflow Labels (Procurement Process)

Sequential labels tracking the procurement/ordering workflow:

| Stage | Label | Description |
|-------|-------|-------------|
| 1 | `01. BOM CREATION` | BOM created and saved |
| 2 | `02. RFQ SENT` | Quotation sent to vendor |
| 2b | `02b. ITEMS X-CHECKED` | RFQ response received, items checked |
| 3 | `03. CSO CREATED` | CSO issued based on design approval |
| 3b | `03b. CSO WAITING` | PR created, waiting for approval |
| 4 | `04. PR CREATED` | Procurement created PR |
| 4b | `04b. PR WAITING` | Waiting for controlling/finance approval |
| 5 | `05. PO CREATED` | PO created, waiting for approval |
| 5b | `05b. PO WAITING` | Waiting for CFO/controlling approval |
| 6 | `06. ORDERED` | All approvals done, vendor selected |
| 6b | `06b. VENDOR WAITING` | PO sent, waiting for delivery date |
| 7 | `07. LLD DONE` | Rack layout, cable maps in NetBox |
| 8 | `08. DELIVERY TIME` | Delivery date known |
| 9 | `09. SHS SENT` | Smart Hand Request sent/accepted |
| 11 | `11. HW INSTALLED` | HW installation based on LLD ready |
| 12 | `12. HW REVIEWED` | Handover accepted, design reviewed |
| 14 | `14. SITE VISIT PLANNED` | Site visit planned, adjustments done |
