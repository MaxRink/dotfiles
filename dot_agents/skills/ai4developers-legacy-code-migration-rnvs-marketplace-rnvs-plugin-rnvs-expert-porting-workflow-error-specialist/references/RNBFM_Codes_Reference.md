# RNB_File_Messages Error Codes - Complete Reference Table

**Module**: RNB_File_Messages
**Prefix**: RNBFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 39 codes

---

## RNBFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **RNBFM001** | Rufnummer ist leer | pack_body_rnb.sql:80 | Constant: FC_RFNR_LEER |
| **RNBFM002** | Rufnummern haben unterschiedliche Laenge | pack_body_rnb.sql:81 | Constant: FC_RFNR_LAENGE |
| **RNBFM003** | ONKZ ist ungueltig | pack_body_rnb.sql:82 | Constant: FC_ONKZ_UNGUELTIG |
| **RNBFM004** | ONKZ sind unterschiedlich | pack_body_rnb.sql:83 | Constant: FC_ONKZ_UNTERSCH |
| **RNBFM005** | ON-Stelligkeit und Laenge der Rufnummer passen nicht zusammen | pack_body_rnb.sql:84 | Constant: FC_ON_STELLIGK |
| **RNBFM006** | RNB ist syntaktisch falsch | pack_body_rnb.sql:85 | Constant: FC_RNB_SYNTAX |
| **RNBFM007** | RNB ist in der DB nicht vorhanden | pack_body_rnb.sql:86 | Constant: FC_RNB_NICHT_GEF |
| **RNBFM008** | Falsches Datumsformat | pack_body_rnb.sql:87 | Constant: FC_DATUM_FALSCH |
| **RNBFM009** | Falscher Portierungsstatus | pack_body_rnb.sql:88 | Constant: FC_PORTSTAT_FALSCH |
| **RNBFM010** | TNB ist in der DB nicht vorhanden | pack_body_rnb.sql:89 | Constant: FC_TNB_NICHT_GEF |
| **RNBFM011** | Falscher Besitzer-Alt | pack_body_rnb.sql:90 | Constant: FC_BESITZER_ALT_FALSCH |
| **RNBFM012** | Falscher Besitzer-Neu | pack_body_rnb.sql:91 | Constant: FC_BESITZER_NEU_FALSCH |
| **RNBFM013** | Falscher Eigentuemer | pack_body_rnb.sql:92 | Constant: FC_EIGENTUEMER_FALSCH |
| **RNBFM014** | Falscher Eigentuemer - muesste D001 sein | pack_body_rnb.sql:93 | Constant: FC_EIGENTUEMER_D001 |
| **RNBFM015** | Belegte Rufnummern mit Besitzer <> Eigentuemer vorhanden | pack_body_rnb.sql:94 | Constant: FC_BESITZER_EIGENT |
| **RNBFM016** | Belegte Rufnummern sind vorhanden | pack_body_rnb.sql:95 | Constant: FC_BELEGTE_RUFNR |
| **RNBFM017** | Korrekturcode ist ungueltig | pack_body_rnb.sql:96 | Constant: FC_KCODE_UNGUELTIG |
| **RNBFM018** | Originalmeldung ist nicht vorhanden | pack_body_rnb.sql:97 | Constant: FC_ORIG_NICHT_VORH |
| **RNBFM019** | Originalmeldung ist ungueltig | pack_body_rnb.sql:98 | Constant: FC_ORIG_UNGUELTIG |
| **RNBFM020** | Originalmeldung ist fehlerhaft | pack_body_rnb.sql:99 | Constant: FC_ORIG_FEHLERHAFT |
| **RNBFM021** | Zwischen Dateidatum und Einrichtungsdatum liegen weniger als 20 AT | pack_body_rnb.sql:100 | Constant: FC_AELTER_20AT |
| **RNBFM022** | Einrichtungsdatum muss >= Dateidatum + 2 AT sein | pack_body_rnb.sql:101 | Constant: FC_AELTER_2AT |
| **RNBFM023** | Einrichtungsdatum der OrigMeldung muss >= Dateidatum - 6 Monate sein | pack_body_rnb.sql:102 | Constant: FC_AELTER_6MON |
| **RNBFM024** | Historisierter RNB ist nicht vorhanden | pack_body_rnb.sql:103 | Constant: FC_HRNB_FEHLT |
| **RNBFM025** | Widerspruch zu einer Einrichtung mit Eigentuemer-Neu D001 | pack_body_rnb.sql:104 | Constant: FC_WID_EINR_D001 |
| **RNBFM026** | Widerspruch zu einer Rueckgabe mit Eigentuemer-Alt D001 | pack_body_rnb.sql:105 | Constant: FC_WID_RUECK_D001 |
| **RNBFM027** | Falscher Portierungsstatus | pack_body_rnb.sql:106 | Constant: FC_FALSCHER_PORTSTAT |
| **RNBFM028** | Dateidatum liegt in der Zukunft | pack_body_rnb.sql:107 | Constant: FC_DATEIDAT_ZUKUNFT |
| **RNBFM029** | SYNTAXFEHLER | pack_body_rnb.sql:108 | Constant: FC_SYNTAX |
| **RNBFM030** | Unterschiedliche Rufnummern | pack_body_rnb.sql:109 | Constant: FC_RFNR_UNTERSCH |
| **RNBFM031** | RNBID ist nicht in der URNB-Datei von BNetzA eingetragen | pack_body_rnb.sql:110 | Constant: FC_URNB |
| **RNBFM032** | Fusionsmeldung ist nicht vorhanden | pack_body_rnb.sql:111 | Constant: FC_FUS_FEHLT |
| **RNBFM033** | Zwischen Dateidatum und Fusionsdatum liegen nicht 20 AT | pack_body_rnb.sql:112 | Constant: FC_AELTER_20AT_INFO |
| **RNBFM050** | Bereitstellungsauftrag nicht vorhanden | pack_body_strukt.sql:184 | Constant: FC_BSA_NICHT_VORH |
| **RNBFM051** | RNB zur MNK-Meldung nicht vorhanden | pack_body_strukt.sql:185 | Constant: FC_RNB_NICHT_VORH |
| **RNBFM052** | Eigentuemer wurde inzwischen geaendert | pack_body_strukt.sql:186 | Constant: FC_BESITZER_UNGL |
| **RNBFM053** | Bereitstellungsauftrag wurde bereits erledigt | pack_body_strukt.sql:187 | Constant: FC_ERLEDIGT |
| **RNBFM054** | Von MNK gemeldete MVSt ist nicht vorhanden | pack_body_strukt.sql:188 | Constant: FC_MVST_NICHT_VORH |
| **RNBFM055** | Der RNB ist von einer Portierungskennungsabschaltemeldung betroffen | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 39
- **Found in Source**: 38 (97%)
- **Not in Source**: 1

---

*Document generated: 2025-11-27 09:54:38*
