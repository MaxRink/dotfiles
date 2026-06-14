# Wettbewerber_Actions Error Codes - Complete Reference Table

**Module**: Wettbewerber_Actions
**Prefix**: WFA
**Analysis Date**: 2025-11-27
**Total Error Codes**: 20 codes

---

## WFA Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **WFA0001** | Fehler beim Lesen eines Datensatzes | pack_body_rfnr.sql:228 | Constant: FC_STRUKTUR |
| **WFA0003** | Besitzer_Alt fehlerhaft oder fehlt | pack_body_rfnr.sql:229 | Constant: FC_BESITZER_ALT |
| **WFA0004** | Besitzer_Neu fehlerhaft oder fehlt | pack_body_rfnr.sql:230 | Constant: FC_BESITZER_NEU |
| **WFA0008** | Fehler beim Lesen der Dateiherkunft | pack_body_rfnr.sql:231 | Constant: FC_LIEFERANT |
| **WFA0010** | Laenge des Portierungsstatus ist groesser als 1 | pack_body_rfnr.sql:232 | Constant: FC_PORTSTAT_L |
| **WFA0014** | RufNr_Von fehlerhaft oder fehlt | pack_body_rfnr.sql:233 | Constant: FC_RFNRVON |
| **WFA0015** | RufNr_bis fehlerhaft oder fehlt | pack_body_rfnr.sql:234 | Constant: FC_RFNRBIS |
| **WFA0020** | unterschiedliche Laengen bei RfNrVon und RfNrBis | pack_body_rfnr.sql:235 | Constant: FC_RFNR_LAENGE |
| **WFA0021** | unterschiedliche ONKz ermittelt bei RfNrVon und RfNrBis | pack_body_rfnr.sql:236 | Constant: FC_UNTERSCH_ONKZ |
| **WFA0023** | Fehlerhaftes Portierungsdatum | pack_body_rfnr.sql:237 | Constant: FC_PORTDAT |
| **WFA0026** | ONKz nicht in DB vorhanden | pack_body_rfnr.sql:238 | Constant: FC_ON_RFNR |
| **WFA0035** | RufnummerVon ist groesser als RufnummerBis. | pack_body_rfnr.sql:239 | Constant: FC_VON_GR_BIS |
| **WFA0050** | unbekannter Korekturcodes | pack_body_rfnr.sql:240 | Constant: FC_KCODE_FALSCH |
| **WFA0132** | Dateidatum hat falsches Format | pack_body_rfnr.sql:241 | Constant: FC_DATEIDAT |
| **WFA0136** | Korrekturcode hat falsche Laenge | pack_body_rfnr.sql:242 | Constant: FC_KORRCODE |
| **WFA0137** | U-Teil ist nicht komplett gefuellt | pack_body_rfnr.sql:243 | Constant: FC_U_STRUKT |
| **WFA0138** | K-Teil ist nicht komplett gefuellt | pack_body_rfnr.sql:244 | Constant: FC_K_STRUKT |
| **WFA0139** | Aufteilungsdatum im K-Teil nicht spezifiziert' | pack_body_rfnr.sql:245 | Constant: FC_WFA0139 |
| **WFA0140** | Datei mit gleichem Namen und gleicher Zeilenanzahl bereits verarbeitet' | pack_body_rfnr.sql:246 | Constant: FC_WFA0140 |
| **WFA0141** | Datei mit gleichem Namen und geringerer Zeilenanzahl bereits verarbeitet | pack_body_rfnr.sql:247 | Constant: FC_WFA0141 |

---

## Coverage Analysis

- **Total Codes**: 20
- **Found in Source**: 20 (100%)
- **Not in Source**: 0

---

*Document generated: 2025-11-27 09:54:38*
