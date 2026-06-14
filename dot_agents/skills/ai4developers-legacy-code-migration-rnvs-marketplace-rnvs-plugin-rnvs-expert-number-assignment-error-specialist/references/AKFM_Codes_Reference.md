# KONTES_Validation Error Codes - Complete Reference Table

**Module**: KONTES_Validation
**Prefix**: AKFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 31 codes

---

## AKFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **AKFM0001** | BI-Grenzen entsprechen nicht der Nutzungsart | pack_body_bereichsinfo.sql:48 | Constant: FC_NUTZUNGSART |
| **AKFM0002** | RfNr in KONTES nicht gefunden | pack_body_bereichsinfo.sql:49 | Constant: FC_CF9904 |
| **AKFM0003** | Kollisionsmeldung von KONTES | pack_body_bereichsinfo.sql:50 | Constant: FC_CF9905 |
| **AKFM0004** | abweichende Nummernart | pack_body_bereichsinfo.sql:51 | Constant: FC_ABW_NUMMERNART |
| **AKFM0005** | DuWa hat abweichende Dekaden | pack_body_bereichsinfo.sql:52 | Constant: FC_ABW_DEKADE |
| **AKFM0006** | abweichender Eigentümer | pack_body_bereichsinfo.sql:53 | Constant: FC_ABW_EIGENTUEMER |
| **AKFM0007** | DuWa hat abweichende Grenzen | pack_body_bereichsinfo.sql:54 | Constant: FC_ABW_GRENZE |
| **AKFM0008** | DuWa hat abweichende NBL | pack_body_bereichsinfo.sql:55 | Constant: FC_ABW_NBL |
| **AKFM0009** | RfNr ist in KONTES belegt | pack_body_bereichsinfo.sql:56 | Constant: FC_BELEGT |
| **AKFM0010** | RfNr ist in KONTES exportiert | pack_body_bereichsinfo.sql:57 | Constant: FC_EXPORTIERT |
| **AKFM0014** | MVSt abweichend | unknown | Code definition not found in PL/SQL source |
| **AKFM0015** | abweichender Verwender | pack_body_bereichsinfo.sql:58 | Constant: FC_ABW_VERWENDER |
| **AKFM0020** | BI hat FCode und keine Auftragsnr | pack_body_bereichsinfo.sql:74 | Constant: FC_FCODE |
| **AKFM9999** | 'Timeout von KONTES' | pack_body_bereichsinfo.sql:47 | Constant: FC_TIMEOUT |
| **AKFMB011** | WBD in KONTES groesser als WBD in RNVS | pack_body_bereichsinfo.sql:59 | Constant: FC_B_WBD_GR |
| **AKFMB012** | WBD in KONTES kleiner als WBD in RNVS | pack_body_bereichsinfo.sql:62 | Constant: FC_B_WBD_KL |
| **AKFMB013** | Falscher BE-Zustand bei Freigabe fuer Buchung | pack_body_bereichsinfo.sql:65 | Constant: FC_B_BE_ZUSTAND |
| **AKFMB014** | abweichende MVSt bei Freigabe fuer Buchung | pack_body_bereichsinfo.sql:68 | Constant: FC_B_MVST |
| **AKFMB015** | beschaltbar groesser als Tagesdatum bei Freigabe fuer Buchung | unknown | Code definition not found in PL/SQL source |
| **AKFMB016** | Beschaltbar > Tagesdatum | pack_body_bereichsinfo.sql:71 | Constant: FC_B_BESCHALTBAR |
| **AKFMK011** | WBD in KONTES groesser als WBD in RNVS | pack_body_bereichsinfo.sql:60 | Constant: FC_K_WBD_GR |
| **AKFMK012** | WBD in KONTES kleiner als WBD in RNVS | pack_body_bereichsinfo.sql:63 | Constant: FC_K_WBD_KL |
| **AKFMK013** | BE-Zustand <> 1 (belegbar) falscher BE-Zustand bei Freigabe fuer KONTES | pack_body_bereichsinfo.sql:66 | Constant: FC_K_BE_ZUSTAND |
| **AKFMK014** | abweichende MVSt bei Freigabe fuer KONTES | pack_body_bereichsinfo.sql:69 | Constant: FC_K_MVST |
| **AKFMK015** | beschaltbar groesser als Tagesdatum bei Freigabe fuer KONTES | unknown | Code definition not found in PL/SQL source |
| **AKFMK016** | Beschaltbar > Tagesdatum | pack_body_bereichsinfo.sql:72 | Constant: FC_K_BESCHALTBAR |
| **AKFMT011** | WBD in KONTES groesser bei Freigabe fuer T-Mobile | pack_body_bereichsinfo.sql:61 | Constant: FC_T_WBD_GR |
| **AKFMT012** | WBD in KONTES kleiner bei Freigabe fuer T-Mobile | pack_body_bereichsinfo.sql:64 | Constant: FC_T_WBD_KL |
| **AKFMT013** | falscher BE-Zustand bei Freigabe fuer T-Mobile | pack_body_bereichsinfo.sql:67 | Constant: FC_T_BE_ZUSTAND |
| **AKFMT014** | abweichende MVSt bei Freigabe fuer T-Mobile | pack_body_bereichsinfo.sql:70 | Constant: FC_T_MVST |
| **AKFMT015** | beschaltbar groesser als Tagesdatum bei Freigabe fuer T-Mobile | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 31
- **Found in Source**: 27 (87%)
- **Not in Source**: 4

---

*Document generated: 2025-11-27 09:54:38*
