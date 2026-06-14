# Wettbewerber_Booking Error Codes - Complete Reference Table

**Module**: Wettbewerber_Booking
**Prefix**: WFB
**Analysis Date**: 2025-11-27
**Total Error Codes**: 28 codes

---

## WFB Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **WFB0007** | Besitzer_Alt und Besitzer_Neu stimmen ueberein | pack_body_rfnr.sql:251 | Constant: FC_BESITZER |
| **WFB0011** | Besitzer_Neu und liefernder TNB nicht identisch oder Portierungsstatus falsch. | pack_body_rfnr.sql:252 | Constant: FC_LIEF_BES_NEU |
| **WFB0012** | Besitzer_Alt und liefernder TNB nicht identisch oder Portierungsstatus falsch. | pack_body_rfnr.sql:253 | Constant: FC_LIEF_BES_ALT |
| **WFB0013** | unbekannter Portierungsstatus | pack_body_rfnr.sql:254 | Constant: FC_PORTSTAT |
| **WFB0016** | RfNrvon besteht nicht nur aus Ziffern | pack_body_rfnr.sql:255 | Constant: FC_RFNR_VON_NUM |
| **WFB0017** | RfNrbis besteht nicht nur aus Ziffern | pack_body_rfnr.sql:256 | Constant: FC_RFNR_BIS_NUM |
| **WFB0030** | Besitzer_Neu ist nicht leer bei Portierungsstatus Z | pack_body_rfnr.sql:257 | Constant: FC_Z_BES_NEU |
| **WFB0045** | Besitzer_Neu ist leer bei Portierungsstatus ungleich Z | pack_body_rfnr.sql:258 | Constant: FC_BES_NEU_LEER |
| **WFB0046** | Besitzer_Neu nicht in DB vorhanden | pack_body_rfnr.sql:259 | Constant: FC_BES_NEU_DB |
| **WFB0047** | Besitzer_Alt nicht in DB vorhanden | pack_body_rfnr.sql:260 | Constant: FC_BES_ALT_DB |
| **WFB0049** | Portierungsdatum liegt in der Zukunft | pack_body_rfnr.sql:261 | Constant: FC_PORT_DAT |
| **WFB0068** | Keinen Unterschied zwischen U- und K-Teil gefunden | pack_body_rfnr.sql:262 | Constant: FC_U_K_GLEICH |
| **WFB0071** | U-Teil und K-Teil passen nicht zum Korrekturcode | pack_body_rfnr.sql:263 | Constant: FC_K_TEIL_GEF |
| **WFB0085** | Unplausible Rufnummer, Stelligkeit <= 6 | pack_body_rfnr.sql:264 | Constant: FC_RFNR_KURZ |
| **WFB0086** | DuWa-Meldung mit NBL=1 und einer Dekade nicht erlaubt | pack_body_rfnr.sql:265 | Constant: FC_DUWA_NBL1 |
| **WFB0087** | Unzulaessige Portierung von/zu ISP | pack_body_rfnr.sql:266 | Constant: FC_ISP |
| **WFB0088** | PortStat Z Frist für Rückfall nicht eingehalten | pack_body_rfnr.sql:267 | Constant: FC_Z_PORT_LIEF |
| **WFB0090** | RufNr.-Laenge in 2stelligen ON groesser 10 | pack_body_rfnr.sql:268 | Constant: FC_RFNR_LAENGE1 |
| **WFB0091** | RufNr.-Laenge groesser 11 Stellen | pack_body_rfnr.sql:269 | Constant: FC_RFNR_LAENGE2 |
| **WFB0092** | K-Teil nicht komplett leer, obwohl lt. KCode erforderlich | pack_body_rfnr.sql:270 | Constant: FC_K_NICHT_LEER |
| **WFB0093** | U-Teil nicht komplett leer, obwohl lt. KCode erforderlich | pack_body_rfnr.sql:271 | Constant: FC_U_NICHT_LEER |
| **WFB0094** | Korrmeldg. 4X00 die nicht aelter als 10AT ist | pack_body_rfnr.sql:272 | Constant: FC_4X00_10AT |
| **WFB0131** | RufNr.-Laenge ungleich 11 Stellen bei NTR | pack_body_rfnr.sql:273 | Constant: FC_NTR |
| **WFB0132** | Dateidatum hat falsches Format | unknown | Code definition not found in PL/SQL source |
| **WFB0135** | Portierungsdatum ist gleich Lieferdatum | pack_body_rfnr.sql:274 | Constant: FC_PORT_DATEI_DAT |
| **WFB0142** | Besitzer_Alt, Besitzer_neu und Lieferant stimmen nicht ueberein bei KCode 4xxx | pack_body_rfnr.sql:275 | Constant: FC_BESITZER_LIEF |
| **WFB0153** | Korrekturcode passt nicht zu Portierungsstatus | pack_body_rfnr.sql:276 | Constant: FC_KORRC_STAT |
| **WFB0169** | Rufnummernbereich enthaelt nicht 10 MSN bei KCode 4300 | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 28
- **Found in Source**: 26 (92%)
- **Not in Source**: 2

---

*Document generated: 2025-11-27 09:54:38*
