# KONTES_Interface Error Codes - Complete Reference Table

**Module**: KONTES_Interface
**Prefix**: KFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 29 codes

---

## KFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **KFM0001** | Fehler bei Freigabe KONTES | pack_kba.sql:55 | Constant: FC_FREIGABE_KONT |
| **KFM0002** | Fehler bei Freigabe CRM | pack_kba.sql:56 | Constant: FC_FREIGABE_CRM |
| **KFM0003** | Fehler bei Freigabe T-Mobile | pack_kba.sql:57 | Constant: FC_FREIGABE_TMD |
| **KFM0004** | Fehler bei Löschen der Freigabe in KONTES | pack_kba.sql:58 | Constant: FC_KONTES_LOESCHEN |
| **KFM0005** | Fehler bei Auskunft KONTES | pack_kba.sql:59 | Constant: FC_KONT_PRUEFEN |
| **KFM0006** | Fehler bei Reaktivierung | pack_kba.sql:60 | Constant: FC_KONT_NPORT |
| **KFM0007** | Fehler bei Löschen Wiederbelegungssperre | pack_kba.sql:61 | Constant: FC_KONT_LOESCHEN_WBEL |
| **KFM0008** | Fehler bei Portierungsmeldung ISP (Buchung) | pack_kba.sql:62 | Constant: FC_KONT_BUCH |
| **KFM0009** | Fehler bei Portierungsmeldung ISP | pack_kba.sql:63 | Constant: FC_KONT_PORT |
| **KFM0010** | Fehler bei Meldung eines Rückfalls | pack_kba.sql:64 | Constant: FC_KONT_ZUR |
| **KFM0011** | Fehler bei Einrichtung eines RNB | pack_kba.sql:65 | Constant: FC_KONT_RNB_EINR |
| **KFM0012** | Fehler bei Rückgabe eines RNB | pack_kba.sql:66 | Constant: FC_KONT_RNB_LOE |
| **KFM0013** | Fehler bei Reaktivierung - Systemnachricht | pack_kba.sql:67 | Constant: FC_REAKT_BELEGT |
| **KFM0014** | MVST nicht gefunden | pack_body_strukt.sql:190 | Constant: FC_MVSTK_NV |
| **KFM0015** | KONTES meldet eine EAS-Kollisionsmeldung und die Rufnummer aus KONTES ist länger als die CRM-T Rufnr | pack_body_strukt.sql:191 | Constant: FC_KOLL_RFNRLAENGE |
| **KFM0016** | KONTES meldet einen Fehler bei der erneuten Info-Anfrage | pack_body_strukt.sql:192 | Constant: FC_INFOAUFTRAG_NOK |
| **KFM0017** | KONTES meldet einen unbekannten Fehler | pack_body_strukt.sql:193 | Constant: FC_FCODE_FREMD |
| **KFM0018** | KONTES meldet eine belegte Rufnummer | pack_body_strukt.sql:194 | Constant: FC_RFNR_BELEGT |
| **KFM0019** | KONTES meldet eine freie Rufnummer mit Besitzer = 199C07 | pack_body_strukt.sql:195 | Constant: FC_KONTES_BES_199C07 |
| **KFM0020** | KONTES meldet eine gesperrte Rufnummer | pack_body_strukt.sql:196 | Constant: FC_KONTES_GESPERRT |
| **KFM0021** | Rufnummernlänge in KONTES ist länger als in CRM-T | pack_body_strukt.sql:197 | Constant: FC_KONTES_RUFNR_GR |
| **KFM0022** | KONTES meldet eine kürzere Rufnummer mit Eigentümer = D001 | pack_body_strukt.sql:198 | Constant: FC_KONTES_RUFNR_KL |
| **KFM0023** | KONTES meldet einen Fehler beim Einrichtungsauftrag | pack_body_strukt.sql:199 | Constant: FC_EINRAUFTRAG_NOK |
| **KFM0024** | KONTES meldet einen Fehler beim Löschauftrag | pack_body_strukt.sql:200 | Constant: FC_LOESCHAUFTRAG_NOK |
| **KFM0025** | KONTES meldet einen eine DUWA-Rufnr in einem falschen Format | pack_body_strukt.sql:201 | Constant: FC_DUWA_FORMAT |
| **KFM0026** | Nicht alle Dekaden der DUWA sind frei | pack_body_strukt.sql:202 | Constant: FC_DUWA_DEK |
| **KFM0027** | KONTES meldet eine EAS im Bereich der DUWA | pack_body_strukt.sql:203 | Constant: FC_DUWA_EAS |
| **KFM0028** | Fehler bei Portierungsmeldung ISP (Buchung) - UFRM-KONTES | pack_kba.sql:69 | Constant: FC_KONT_UFRMK |
| **KFM0030** | Technischer Fehler beim Löschen der Rufnummer in KONTES | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 29
- **Found in Source**: 28 (96%)
- **Not in Source**: 1

---

*Document generated: 2025-11-27 09:54:38*
