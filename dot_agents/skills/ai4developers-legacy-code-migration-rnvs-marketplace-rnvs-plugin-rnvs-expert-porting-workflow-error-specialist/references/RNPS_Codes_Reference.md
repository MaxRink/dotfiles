# RNPS_File_Messages Error Codes - Complete Reference Table

**Module**: RNPS_File_Messages
**Prefix**: RFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 19 codes

---

## RFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **RFM001** | Rufnummer wurde nicht gefunden | pack_rnps.sql:18 | Constant: FC_RFNR_NV |
| **RFM002** | Beide Saetze sind aktiv | pack_rnps.sql:19 | Constant: FC_BEIDE_AKTIV |
| **RFM003** | Rufnummerntypen sind verschieden | pack_rnps.sql:20 | Constant: FC_RFNR_TYP |
| **RFM004** | Rufnummerngrenzen stimmen nicht ueberein | pack_rnps.sql:21 | Constant: FC_RFNR_GRENZEN |
| **RFM005** | Portierungsinformationen stimmen nicht ueberein | pack_rnps.sql:22 | Constant: FC_PI_UNGLEICH |
| **RFM006** | Anfrageergebnis stimmt nicht mit Vormerkung ueberein | unknown | Code definition not found in PL/SQL source |
| **RFM007** | Rufnummernlaengen stimmen nicht ueberein | pack_rnps.sql:23 | Constant: FC_RFNR_LAENGE |
| **RFM008** | Blockrufnummer von RNPS hat nicht alle oder zu viele Dekaden | pack_rnps.sql:24 | Constant: FC_DEKADEN_UNGL |
| **RFM009** | Verschiedene Portierungsinformationen der Dekaden von RNPS | pack_rnps.sql:25 | Constant: FC_PI_DEKADEN_UNGL |
| **RFM010** | RNPS lieferte einen Fehler | pack_rnps.sql:26 | Constant: FC_FEHLER_RNPS |
| **RFM011** | Rufnummer im RNPS nicht vorhanden | pack_rnps.sql:27 | Constant: FC_RNPS_NV |
| **RFM012** | RNPS meldet beide Datensatzteile als inaktiv' | pack_rnps.sql:28 | Constant: FC_BEIDE_INAKTIV |
| **RFM013** | RNPS meldet fehlerhaften Returncode | pack_strukt.sql:26 | Constant: FC_RET_CODE_NOK |
| **RFM014** | RNPS/RNVS Rufnummer stimmt nicht überein | pack_strukt.sql:27 | Constant: FC_RFNR_UNGL |
| **RFM015** | RNPS/RNVS Besitzer stimmt nicht überein | pack_strukt.sql:28 | Constant: FC_BESITZ_UNGL |
| **RFM016** | Rufnummer in RNPS nicht ermittelbar | pack_strukt.sql:29 | Constant: FC_RFNR_NV |
| **RFM017** | Abfrage mit voller Rufnummer - Daten ident | pack_strukt.sql:30 | Constant: FC_VOLL_IDENT |
| **RFM018** | 'Abfrage mit Stamm - Daten ident | pack_strukt.sql:31 | Constant: FC_STAMM_IDENT |
| **RFM999** | 'Unerwarteter Fehler' | pack_strukt.sql:32 | Constant: FC_SOAP_FEHLER |

---

## Coverage Analysis

- **Total Codes**: 19
- **Found in Source**: 18 (94%)
- **Not in Source**: 1

---

*Document generated: 2025-11-27 09:54:38*
