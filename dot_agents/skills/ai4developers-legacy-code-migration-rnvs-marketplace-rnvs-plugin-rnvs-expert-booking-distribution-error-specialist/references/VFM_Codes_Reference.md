# Validation_Messages Error Codes - Complete Reference Table

**Module**: Validation_Messages
**Prefix**: VFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 33 codes

---

## VFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **VFM0001** | Export: Portdatum abweichend, aber innerhalb der Toleranzgrenze | pack_val.sql:14 | Constant: FC_PORTDAT_TOLERANZ |
| **VFM0002** | abweichende Portierung; unbestaetigter Import ist vorhanden | pack_val.sql:15 | Constant: FC_IMPORT_DTAG_U |
| **VFM0003** | abweichende Portierung; unbestaetigter Export von ISP ist vorhanden | pack_val.sql:16 | Constant: FC_EXPORT_ISP_U |
| **VFM0004** | abweichende Portierung; unbestaetigter Export mit aktuellerem PDat ist vorhanden | pack_val.sql:17 | Constant: FC_EXPORT_U_PDAT |
| **VFM0005** | Besitzer in DB ungleich Besitzer_alt | pack_val.sql:18 | Constant: FC_BALT_ABW |
| **VFM0006** | Logbucheintrag zum Puffer kann nicht ermittelt werden | pack_val.sql:19 | Constant: FC_LBW_NV |
| **VFM0007** | Unterschiedliche Besitzer neu bei Export | pack_val.sql:20 | Constant: FC_ABW_BNEU |
| **VFM0008** | 'Import: Portdatum abweichend, aber innerhalb Toleranzgrenze' | pack_val.sql:21 | Constant: FC_PORTDAT_TOLERANZ8 |
| **VFM0026** | ONKz nicht in DB vorhanden | pack_val.sql:22 | Constant: FC_ON_NV |
| **VFM0027** | RfNr einer Anlage nicht komplett oder fehlerhaft | pack_val.sql:29 | Constant: FC_DUWA_ABW |
| **VFM0031** | Aehnliche RfNr mit anderer Stelligkeit in DB vorhanden | pack_val.sql:24 | Constant: FC_RANGE_EAS |
| **VFM0034** | Die Rufnummer ist nicht in der Datenbank vorhanden (trotz Eigentuemer DTAG) | pack_val.sql:25 | Constant: FC_RFNR_NV |
| **VFM0037** | Portierung auf eine freie DTAG-Rufnummer | pack_val.sql:26 | Constant: FC_FREI_P_L |
| **VFM0088** | gemeldete Portierung ist aelter als aktuelle Portierung | pack_val.sql:30 | Constant: FC_PORTDAT_AELTER |
| **VFM0130** | Portierung mit Level = u3 vorhanden | pack_val.sql:31 | Constant: FC_PL_U3 |
| **VFM0133** | Rueckfall auf eine freie DTAG-Rufnummer | pack_val.sql:28 | Constant: FC_FREI_Z |
| **VFM0155** | Originalmeldung zum Puffer kann nicht ermittelt werden | pack_val.sql:32 | Constant: FC_ORIG_NV |
| **VFM0156** | Im NTR-Bereich ist eine RfNr mit falscher Laenge vorhanden | pack_val.sql:33 | Constant: FC_LAENGE |
| **VFM0157** | Kontingent hat unterschiedliche Besitzer | pack_val.sql:34 | Constant: FC_EXP_KONT |
| **VFM0160** | Der Rufnummerbereich des U-Teils ist in der DB abweichend | unknown | Code definition not found in PL/SQL source |
| **VFM0161** | Der Rufnummerbereich des K-Teils ist in der DB abweichend | unknown | Code definition not found in PL/SQL source |
| **VFM0162** | Der gemeldete Bereich ist in der DB nicht lueckenlos belegt | unknown | Code definition not found in PL/SQL source |
| **VFM0163** | Rufnummern im Bereich ist unbestaetigt portiert | unknown | Code definition not found in PL/SQL source |
| **VFM0164** | Rufnummern im Bereich haben unterschiedliche Besitzer | unknown | Code definition not found in PL/SQL source |
| **VFM0165** | gemeldeter Rufnummernbereich hat mehrere Eigentuemer | unknown | Code definition not found in PL/SQL source |
| **VFM0166** | RfNr hat abweichenden Besitzer bei KCode 4xxx | unknown | Code definition not found in PL/SQL source |
| **VFM0167** | gemeldeter Rufnummernbereich hat in RNVS nicht die gleichen Grenzen | unknown | Code definition not found in PL/SQL source |
| **VFM0169** | Rufnummernbereich enthaelt nicht 10 MSN bei KCode 4300 | unknown | Code definition not found in PL/SQL source |
| **VFM0172** | RfNR zu KCode 4xxx nicht vorhanden | pack_val.sql:35 | Constant: FC_AWK_4 |
| **VFM0173** | Rueckportierung trifft auf Meldung eines TNBs | pack_body_generator.sql:101 | Constant: FC_LBW_VORH |
| **VFM0200** | Veröffentlichung nicht möglich - Regeldatensatz liegt nicht im Meldungskorb | unknown | Code definition not found in PL/SQL source |
| **VFM7043** | Fehler beim Ermitteln des/der RNB(s) zur Rufnummer | unknown | Code definition not found in PL/SQL source |
| **VFM9037** | Weiterportierung auf eine freie DTAG-Rufnummer | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 33
- **Found in Source**: 21 (63%)
- **Not in Source**: 12

---

*Document generated: 2025-11-27 09:54:38*
