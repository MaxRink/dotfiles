# Porting_Messages Error Codes - Complete Reference Table

**Module**: Porting_Messages
**Prefix**: PFM
**Analysis Date**: 2025-11-27
**Total Error Codes**: 37 codes

---

## PFM Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **PFM001** | WSST fehlt zur Meldung von T-Com | pack_val.sql:38 | Constant: FC_NVAL_KONTES_P |
| **PFM002** | nicht validierte Portierung von WSSt | pack_val.sql:39 | Constant: FC_NVAL_WSST |
| **PFM003** | Import von T-Com/T-Mobile/TSBS fehlt zur L-Meldung der WSST | pack_val.sql:40 | Constant: FC_NVAL_L_SATZ |
| **PFM004** | Export von DTAG fehlt zur P-Meldung der Wettbewerber SSt | pack_val.sql:41 | Constant: FC_NVAL_P_SATZ |
| **PFM005** | WSST fehlt zur L-Meldung von DTAG | pack_val.sql:42 | Constant: FC_NVAL_KONTES_L |
| **PFM006** | WSST fehlt zur Z-Meldung von DTAG | pack_val.sql:43 | Constant: FC_NVAL_KONTES_Z |
| **PFM007** | Nicht validierte Portierung von WSSt - L-Meldung liegt vor, P-Meldung fehlt | pack_val.sql:44 | Constant: FC_NVAL_WSST_007 |
| **PFM008** | Nicht validierte Portierung von WSSt - Z-Meldung liegt vor, P-Meldung fehlt | pack_val.sql:45 | Constant: FC_NVAL_WSST_008 |
| **PFM009** | Nicht validierte Portierung von WSSt - P-Meldung liegt vor, L-Meldung fehlt | pack_val.sql:46 | Constant: FC_NVAL_WSST_009 |
| **PFM011** | Meldung von T-Mobile fehlt zur WSST | pack_val.sql:47 | Constant: FC_WSST_TMD_FEHLT |
| **PFM012** | WSST fehlt zur Meldung von T-Mobile | pack_val.sql:48 | Constant: FC_TMD_WSST_FEHLT |
| **PFM014** | Meldung von T-Mobile fehlt zur Meldung von T-Com | pack_val.sql:49 | Constant: FC_KONT_TMD_FEHLT |
| **PFM015** | Meldung von T-Com fehlt zur Meldung von T-Mobile | pack_val.sql:50 | Constant: FC_TMD_KONT_FEHLT |
| **PFM016** | Meldung von T-Mobile fehlt zur Meldung von ISP | pack_val.sql:51 | Constant: FC_ISP_TMD_FEHLT |
| **PFM017** | Meldung von DTAG fehlt zur Meldung von ISP | pack_val.sql:52 | Constant: FC_ISP_KONT_FEHLT |
| **PFM018** | Meldung von ISP fehlt zur WSST | pack_val.sql:53 | Constant: FC_WSST_ISP_FEHLT |
| **PFM019** | Meldung von ISP fehlt zur Meldung von DTAG | pack_val.sql:54 | Constant: FC_KONT_ISP_FEHLT |
| **PFM020** | Meldung von ISP fehlt zur Meldung von T-Mobile | pack_val.sql:55 | Constant: FC_TMD_ISP_FEHLT |
| **PFM021** | WSST fehlt zur Meldung von ISP | pack_val.sql:56 | Constant: FC_ISP_WSST_FEHLT |
| **PFM022** | Import: WSST/ISP fehlt zur Meldung von IP-Produkt | pack_val.sql:57 | Constant: FC_TOI_WSST_L_FEHLT |
| **PFM023** | Meldung von anderem ISP fehlt zur Meldung von ISP | pack_val.sql:58 | Constant: FC_ISP_ISP_FEHLT |
| **PFM024** | 'Export/Rückfall: WSST/ISP fehlt zur Meldung von IP-Produkt' | pack_val.sql:59 | Constant: FC_TOI_WSST_P_FEHLT |
| **PFM025** | Realisierung des Imports von KONTES/CRM-T fehlt | pack_val.sql:60 | Constant: FC_KONT_VIMP |
| **PFM026** | Frist fuer KCode 4500 von D001 erreicht | pack_val.sql:61 | Constant: FC_KCODE_4500_AWK |
| **PFM027** | BI prüfen / ändern, Altbestand oder Frist fuer KCode 4100 erreicht | pack_bereichsinfo.sql:11 | Constant: FC_RFNR_VORH |
| **PFM028** | Frist fuer Buchung im Altbestand erreicht | pack_bereichsinfo.sql:12 | Constant: FC_FRIST_UEBERSCHR |
| **PFM029** | Frist fuer KCode 4500 von fremdem TNB erreicht | pack_val.sql:62 | Constant: FC_KCODE_4500_EWK |
| **PFM030** | PFM004 Rufnummer ist frei | pack_body_pm.sql:88 | Constant: FC_PFM030 |
| **PFM031** | Import von MH fehlt zur L-Meldung der WSST | pack_val.sql:63 | Constant: FC_NVAL_P_VON_MH |
| **PFM032** | Export von MH fehlt zur P-Meldung der WSST | pack_val.sql:64 | Constant: FC_NVAL_L_VON_MH |
| **PFM033** | Export: WSST/ISP fehlt zur Meldung von MH | pack_val.sql:65 | Constant: FC_NVAL_P_VON_WETTB1 |
| **PFM034** | Rueckfall: WSST/ISP fehlt zur Meldung von MH | pack_val.sql:66 | Constant: FC_NVAL_P_VON_WETTB2 |
| **PFM035** | Import: WSST/ISP fehlt zur Meldung von MH | pack_val.sql:67 | Constant: FC_NVAL_L_VON_WETTB |
| **PFM036** | Import von Congstar fehlt zur L-Meldung der WSST | pack_val.sql:68 | Constant: FC_NVAL_P_VON_CS |
| **PFM037** | Export von Congstar fehlt zur P-Meldung der WSST | pack_val.sql:69 | Constant: FC_NVAL_L_VON_CS |
| **PFM038** | Import: WSST/ISP fehlt zur Meldung von Congstar | pack_val.sql:70 | Constant: FC_NVAL_PFM038 |
| **PFM039** | Rueckfall: WSST/ISP fehlt zur Z-Meldung von IP-Produkt | pack_val.sql:71 | Constant: FC_TOI_WSST_P_FEHLT2 |

---

## Coverage Analysis

- **Total Codes**: 37
- **Found in Source**: 37 (100%)
- **Not in Source**: 0

---

*Document generated: 2025-11-27 09:54:38*
