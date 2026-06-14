# Wettbewerber_Competitor_File Error Codes - Complete Reference Table

**Module**: Wettbewerber_Competitor_File
**Prefix**: WFC
**Analysis Date**: 2025-11-27
**Total Error Codes**: 123 codes

---

## WFC Error Codes

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **WFC0001** | Fehler in Protokoll gefunden | unknown | Code definition not found in PL/SQL source |
| **WFC0025** | schwerer Fehler bei Verarbeitung der Wettbewerbermeldung | pack_body_rfnr.sql:281 | Constant: FC_DEFAULT |
| **WFC0051** | Originalmeldung konnte nicht gefunden werden | pack_body_rfnr.sql:282 | Constant: FC_ORIG_NV |
| **WFC0055** | Singlemeldung mit DTAG-Beteiligung | unknown | Code definition not found in PL/SQL source |
| **WFC0140** | Originalsatz nicht mehr gueltig | pack_body_rfnr.sql:283 | Constant: FC_BUF_SON |
| **WFC0141** | Meldung ist nicht mehr gueltig bei KCode 2200 | pack_body_rfnr.sql:284 | Constant: FC_BUF_SON_2200 |
| **WFC0143** | RfNr_Von aus U- und K-Teil stimmen nicht ueberein (bei KCode 4xxx) | pack_body_rfnr.sql:285 | Constant: FC_RUFNR_VON_UK |
| **WFC0144** | RfNr_Bis in U- groesser als RfNr_Bis in K-Teil (bei KCode 4100, 4200, 4400) | pack_body_rfnr.sql:286 | Constant: FC_RUFNR_BIS_UK |
| **WFC0145** | RfNr_Von ist nicht dekadig (bei KCode 4xxx) | pack_body_rfnr.sql:287 | Constant: FC_RUFNR_VON_DEK |
| **WFC0146** | RfNr_Bis ist nicht dekadig (bei KCode 4xxx) | pack_body_rfnr.sql:288 | Constant: FC_RUFNR_BIS_DEK |
| **WFC0147** | bereits Korrekturmeldung mit KCode 4xxx im Puffer vorhanden | pack_body_rfnr.sql:289 | Constant: FC_BUFFER3 |
| **WFC0148** | falscher Korrekturcode 24xx | pack_body_rfnr.sql:290 | Constant: FC_KCODE_UEB |
| **WFC0149** | falscher Portierungsstatus bei KCode 6xxx | pack_body_rfnr.sql:291 | Constant: FC_SINGLE_BUF |
| **WFC0150** | Zwischen Einstellen der Single-Meldung und entspr. Portierungsmeldung muessen mind. 10AT liegen | pack_body_rfnr.sql:292 | Constant: FC_FRIST_BUF |
| **WFC0152** | Keine Originalmeldung zur Singlemeldung vorhanden | pack_body_rfnr.sql:293 | Constant: FC_SINGLE_BUF_NV |
| **WFC0154** | Korrekturmeldung mit 4500 erhalten | unknown | Code definition not found in PL/SQL source |
| **WFC0160** | Der Rufnummerbereich des U-Teils ist in der DB abweichend | unknown | Code definition not found in PL/SQL source |
| **WFC0161** | Der Rufnummerbereich des K-Teils ist in der DB abweichend | unknown | Code definition not found in PL/SQL source |
| **WFC0162** | Der gemeldete Bereich ist in der DB nicht lueckenlos belegt | unknown | Code definition not found in PL/SQL source |
| **WFC0163** | Rufnummern im Bereich ist unbestaetigt portiert | unknown | Code definition not found in PL/SQL source |
| **WFC0164** | Rufnummern im Bereich haben unterschiedliche Besitzer | unknown | Code definition not found in PL/SQL source |
| **WFC0165** | gemeldeter Rufnummernbereich hat mehrere Eigentuemer | unknown | Code definition not found in PL/SQL source |
| **WFC0166** | RfNr hat abweichenden Besitzer bei KCode 4xxx | unknown | Code definition not found in PL/SQL source |
| **WFC0167** | gemeldeter Rufnummernbereich hat in RNVS nicht die gleichen Grenzen | unknown | Code definition not found in PL/SQL source |
| **WFC0170** | Im gemeldeten Rufnummernbereich sind belegte RfNr vorhanden bei KCode 4500 | unknown | Code definition not found in PL/SQL source |
| **WFC0171** | Der Eigentuemer ist nicht Altbestand bei KCode 4500 | unknown | Code definition not found in PL/SQL source |
| **WFC0180** | Sperre der Rufnummer aufgrund einer Abschalteverfuegung | pack_body_rfnr.sql:311 | Constant: FC_ABSCHALTEVERF |
| **WFC0181** | Sperre der Rufnummer aufgrund einer Quarantaene | pack_body_rfnr.sql:312 | Constant: FC_QUARANTAENE |
| **WFC0182** | PortStat Z und Besitzer-Alt ungleich Besitzer in der DB | pack_body_rfnr.sql:313 | Constant: FC_Z_BES_UNGL |
| **WFC0183** | Meldung ist nicht mehr im Meldungskorb vorhanden | pack_body_rfnr.sql:314 | Constant: FC_PUF_NV |
| **WFC0184** | Widerspruch nach Zurückziehung, bzw. Zurückziehung nach Widerspruch | pack_body_rfnr.sql:315 | Constant: FC_WFC0184 |
| **WFC0190** | 'Korrekturcode 3000 darf nur auf eine selbst veröffentlichte P-Meldung angewendet werden' | pack_body_rfnr.sql:317 | Constant: FC_WFC0190 |
| **WFC0191** | Der Korrekturcode 2046/2146 wurde für Weiterversorgung nach 10 AT angewendet | pack_body_rfnr.sql:318 | Constant: FC_WFC0191 |
| **WFC0192** | Korrekturcode 3000 darf nur max. 1 Jahr nach Veröffentlichung angewendet werden' | pack_body_rfnr.sql:319 | Constant: FC_WFC0192 |
| **WFC0193** | Unzulässige Umwandlung Rufnummern mit Block in EAS in ON mit 2-stelligen ONKZ | pack_body_rfnr.sql:320 | Constant: FC_WFC0193 |
| **WFC0194** | Das Zusammenfuehrungsdatum muss mind. 1 KT groesser als das Portdatum der einz. Teilbereiche sein | unknown | Code definition not found in PL/SQL source |
| **WFC0195** | Erreichbarkeit von verkuerzten Abfragestellen bei Rufnummernbereichen die mehrere RNB umfassen | pack_body_rfnr.sql:321 | Constant: FC_WFC0195 |
| **WFC0196** | Zuruecknahme / Aufhebung eines Code 4700 | pack_body_rfnr.sql:322 | Constant: FC_WFC0196 |
| **WFC0197** | Erreichbarkeit von Abfragestellen bei 2- und mehrstelligen Durchwahlbloecken | pack_body_rfnr.sql:323 | Constant: FC_WFC0197 |
| **WFC0198** | Zuruecknahme / Aufhebung eines Code 4720 | pack_body_rfnr.sql:324 | Constant: FC_WFC0198 |
| **WFC0199** | Portierungskennungsabschaltemeldung nicht gueltig | unknown | Code definition not found in PL/SQL source |
| **WFC0200** | gueltige Portierungskennungsabschaltemeldung | unknown | Code definition not found in PL/SQL source |
| **WFC0201** | Besitzer Alt/Neu hat eine Portierungskennungsabschaltemeldung | unknown | Code definition not found in PL/SQL source |
| **WFC0202** | Die Veroeffentlichung der Ruecknahme muss mind. 5 KT vor dem Abschaltedatum erfolgt sein | unknown | Code definition not found in PL/SQL source |
| **WFC0203** | Die Ruecknahme darf nur vom Eigentümer der Portierungskennung selber veroeffentlicht werden | unknown | Code definition not found in PL/SQL source |
| **WFC0204** | Gueltige Ruecknahme einer Portierungskennungsabschaltemeldung | unknown | Code definition not found in PL/SQL source |
| **WFC0205** | Die Veroeffentlichung des Widerspruchs muss mind. 5 KT vor dem Abschaltedatum erfolgt sein | unknown | Code definition not found in PL/SQL source |
| **WFC0206** | Gueltiger Widerspruch einer Portierungskennungsabschaltemeldung | unknown | Code definition not found in PL/SQL source |
| **WFC0207** | Die Portierungskennungsabschaltemeldung ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **WFC0208** | Die Rufnummer ist von einer Portierungskennungsabschaltemeldung betroffen | unknown | Code definition not found in PL/SQL source |
| **WFC0216** | Doppelmeldung | pack_body_rfnr.sql:333 | Constant: FC_WFC0216 |
| **WFC6001** | PFM003 - Fehlermeldung von KONTES | pack_body_pm.sql:89 | Constant: FC_WFC6001 |
| **WFC6002** | PFM004 Fehlermeldung von RNPS | unknown | Code definition not found in PL/SQL source |
| **WFC6003** | PFM004 kein Exportauftrag in KONTES vorh. | unknown | Code definition not found in PL/SQL source |
| **WFC6004** | PFM003 Auftrag mit Zukunftsdatum in KONTES | pack_body_pm.sql:90 | Constant: FC_WFC6004 |
| **WFC6005** | PFM003 Rufnummer hat u2-Status | pack_body_pm.sql:91 | Constant: FC_WFC6005 |
| **WFC6006** | PFM003, zum Import liegt ein WMA014 vor, Weiterbearbeitung bei NUM-E | pack_body_pm.sql:92 | Constant: FC_WFC6006 |
| **WFC6007** | PFM003, zum Import liegt ein unklarer Status an der Rufnummer oder weitere Meldungen vor | pack_body_pm.sql:93 | Constant: FC_WFC6007 |
| **WFC6008** | PFM003, zum Import gibt es eine offene PM | pack_body_pm.sql:94 | Constant: FC_WFC6008 |
| **WFC6009** | PFM003 -??? | pack_body_pm.sql:95 | Constant: FC_WFC6009 |
| **WFC6101** | PFM004 - Fehlermeldung von KONTES | pack_body_pm.sql:96 | Constant: FC_WFC6101 |
| **WFC6102** | PFM004 - Fehlermeldung von RNPS | pack_body_pm.sql:97 | Constant: FC_WFC6102 |
| **WFC6103** | PFM004 kein Exportauftrag in KONTES vorh. | pack_body_pm.sql:98 | Constant: FC_WFC6103 |
| **WFC6106** | PFM004 Auftrag mit Zukunftsdatum in KONTES | pack_body_pm.sql:99 | Constant: FC_WFC6106 |
| **WFC7027** | RfNr einer Anlage nicht komplett oder fehlerhaft | pack_body_rfnr.sql:338 | Constant: FC_RANGE_DUWA |
| **WFC7028** | Neue RfNr in einem RNB, der dem Regulierer gehoert | pack_body_rfnr.sql:339 | Constant: FC_RNB_REG |
| **WFC7029** | Gelieferte Rufnummernart stimmt nicht mit der Rufnummernart der vorhandenen Rufnummer ueberein | pack_body_rfnr.sql:340 | Constant: FC_RFNRART |
| **WFC7031** | Aehnliche RfNr mit anderer Stelligkeit in DB vorhanden | pack_body_rfnr.sql:341 | Constant: FC_RANGE_EAS |
| **WFC7036** | Besitzer-Neu ist gleich Besitzer in der DB | pack_body_rfnr.sql:342 | Constant: FC_BES_NEU_AKT2 |
| **WFC7043** | Fehler beim Ermitteln des/der RNB(s) zur Rufnummer | pack_body_rfnr.sql:343 | Constant: FC_RNB_ERM |
| **WFC7134** | identischer Datensatz im Puffer vorhanden | pack_body_rfnr.sql:344 | Constant: FC_BUFFER |
| **WFC7135** | 'Rufnummer ist nicht bestätigt portiert zum Lieferanten des KorrCodes 3000' | pack_body_rfnr.sql:345 | Constant: FC_WFC7135 |
| **WFC7220** | Portierungsdatum ist kleiner oder gleich dem Datum des letzten validierten Portierungsvorgangs | pack_body_rfnr.sql:346 | Constant: FC_WFC7220 |
| **WFC7227** | Originalsatz ist nicht gueltig, da er mit WFC7220 verarbeitet wurde | unknown | Code definition not found in PL/SQL source |
| **WFC9027** | RfNr einer Anlage nicht komplett oder fehlerhaft | pack_body_rfnr.sql:349 | Constant: FC_RANGE_DUWA2 |
| **WFC9028** | Neue RfNr in einem RNB, der dem Regulierer gehoert | pack_body_rfnr.sql:350 | Constant: FC_RNB_REG2 |
| **WFC9029** | Gelieferte Rufnummernart stimmt nicht mit der Rufnummernart der vorhandenen Rufnummer ueberein | pack_body_rfnr.sql:351 | Constant: FC_RFNRART2 |
| **WFC9031** | Aehnliche RfNr mit anderer Stelligkeit in DB vorhanden | pack_body_rfnr.sql:352 | Constant: FC_RANGE_EAS2 |
| **WFC9032** | Besitzer-alt ist ungleich dem Besitzer in DB | pack_body_rfnr.sql:353 | Constant: FC_BES_UNGLEICH |
| **WFC9034** | Die Rufnummer ist nicht in der Datenbank vorhanden (trotz Besitzer DTAG) | pack_body_rfnr.sql:354 | Constant: FC_NICHT_VORH_DTAG |
| **WFC9036** | Besitzer_Neu ist gleich Besitzer in der DB | pack_body_rfnr.sql:355 | Constant: FC_BES_NEU_AKT |
| **WFC9037** | Rufnummer in RNVS frei Weiterportierung , DTAG ist Eigentümer | pack_body_rfnr.sql:356 | Constant: FC_RFNR_FREI_LP |
| **WFC9038** | Z-Meldung auf Import; Eigenuemer = DTAG | pack_body_rfnr.sql:335 | Constant: FC_WFC9038 |
| **WFC9039** | Z-Meldung auf Import; Eigenuemer = Fremd | pack_body_rfnr.sql:336 | Constant: FC_WFC9039 |
| **WFC9043** | Fehler beim Ermitteln des/der RNB(s) zur Rufnummer | pack_body_rfnr.sql:357 | Constant: FC_RNB_ERM2 |
| **WFC9055** | Singlemeldung mit DTAG-Beteiligung | pack_body_rfnr.sql:358 | Constant: FC_DTAG_SINGLE |
| **WFC9092** | Bei ISP Beteiligung ist Besitzer_Alt nicht Besitzer der Rufnummer | pack_body_rfnr.sql:359 | Constant: FC_BES_ISP |
| **WFC9130** | Portierung mit Level = u3 vorhanden | pack_body_rfnr.sql:360 | Constant: FC_RFNR_U3 |
| **WFC9133** | Rufnummer in RNVS frei bei Z-Meldung | pack_body_rfnr.sql:361 | Constant: FC_RFNR_FREI_Z |
| **WFC9134** | identischer Datensatz im Puffer vorhanden | pack_body_rfnr.sql:362 | Constant: FC_BUFFER2 |
| **WFC9151** | Korrekturcode 25 erhalten, Rückfall | pack_body_rfnr.sql:363 | Constant: FC_BUF_DTAG |
| **WFC9155** | RfNr einer Anlage nicht komplett oder fehlerhaft bei Export | pack_body_rfnr.sql:364 | Constant: FC_WFC9155 |
| **WFC9156** | RfNr einer Anlage nicht komplett oder fehlerhaft bei Import | pack_body_rfnr.sql:365 | Constant: FC_WFC9156 |
| **WFC9157** | Besitzer_Alt ist nicht Besitzer der Rufnummer Export | pack_body_rfnr.sql:366 | Constant: FC_WFC9157 |
| **WFC9158** | Besitzer_Alt ist nicht Besitzer der Rufnummer Import | pack_body_rfnr.sql:367 | Constant: FC_WFC9158 |
| **WFC9159** | Rückfall: Besitzer_Alt ist nicht Besitzer der Rufnummer | pack_body_rfnr.sql:368 | Constant: FC_WFC9159 |
| **WFC9180** | Rufnummer in RNVS frei P-Meldung von TNB wurde geliefert | pack_body_rfnr.sql:369 | Constant: FC_WFC9180 |
| **WFC9181** | Rufnummer in RNVS frei L oder Z -Meldung von TNB wurde geliefert | pack_body_rfnr.sql:370 | Constant: FC_WFC9181 |
| **WFC9200** | Korrekturcode 2500 erhalten Import | pack_body_rfnr.sql:371 | Constant: FC_WFC9200 |
| **WFC9201** | Korrekturcode 2500 erhalten Export | pack_body_rfnr.sql:372 | Constant: FC_WFC9201 |
| **WFC9202** | Korrekturcode 2501 erhalten Im- und Export | pack_body_rfnr.sql:373 | Constant: FC_WFC9202 |
| **WFC9203** | Korrekturcode 2502 erhalten Nur Export | pack_body_rfnr.sql:374 | Constant: FC_WFC9203 |
| **WFC9204** | Korrekturcode 2503 erhalten Import und Export | pack_body_rfnr.sql:375 | Constant: FC_WFC9204 |
| **WFC9205** | Korrekturcode 2504 erhalten Import und Export | pack_body_rfnr.sql:376 | Constant: FC_WFC9205 |
| **WFC9206** | Korrekturcode 2505 erhalten Import | pack_body_rfnr.sql:377 | Constant: FC_WFC9206 |
| **WFC9207** | Korrekturcode 2505 erhalten Export | pack_body_rfnr.sql:378 | Constant: FC_WFC9207 |
| **WFC9208** | Korrekturcode 2506 erhalten Export | pack_body_rfnr.sql:379 | Constant: FC_WFC9208 |
| **WFC9209** | Korrekturcode 2506 erhalten Import | pack_body_rfnr.sql:380 | Constant: FC_WFC9209 |
| **WFC9210** | Korrekturcode 2507 erhalten Import und Export | pack_body_rfnr.sql:381 | Constant: FC_WFC9210 |
| **WFC9211** | Korrekturcode 2508 erhalten Import und Export | pack_body_rfnr.sql:382 | Constant: FC_WFC9211 |
| **WFC9212** | Korrekturcode 2510 erhalten Import und Export | pack_body_rfnr.sql:383 | Constant: FC_WFC9212 |
| **WFC9213** | Korrekturcode 2520 erhalten Import und Export | pack_body_rfnr.sql:384 | Constant: FC_WFC9213 |
| **WFC9214** | Korrekturcode 2530 erhalten Import und Export | pack_body_rfnr.sql:385 | Constant: FC_WFC9214 |
| **WFC9215** | Korrekturcode 2540 erhalten Import und Export | pack_body_rfnr.sql:386 | Constant: FC_WFC9215 |
| **WFC9216** | Korrekturcode 2550 erhalten Import und Export | pack_body_rfnr.sql:387 | Constant: FC_WFC9216 |
| **WFC9217** | 'Korrekturcode 2546 auf P-Meldung erhalten' | pack_body_rfnr.sql:388 | Constant: FC_WFC9217 |
| **WFC9218** | 'Korrekturcode 2546 auf L/Z-Meldung erhalten' | pack_body_rfnr.sql:389 | Constant: FC_WFC9218 |
| **WFC9219** | 'Korrekturcode 3000: DTAG beteiligt' | pack_body_rfnr.sql:390 | Constant: FC_WFC9219 |
| **WFC9220** | Portierungsdatum liegt vor dem Datum des letzten validierten Portierungsvorgangs | pack_body_rfnr.sql:391 | Constant: FC_WFC9220 |
| **WFC9221** | Korrekturcode 2599 erhalten | pack_body_rfnr.sql:392 | Constant: FC_WFC9221 |
| **WFC9222** | Korrekturcode 2547 auf 4700 erhalten | pack_body_rfnr.sql:393 | Constant: FC_WFC9222 |
| **WFC9223** | Korrekturcode 2547 auf 4720 erhalten | pack_body_rfnr.sql:394 | Constant: FC_WFC9223 |
| **WFC9227** | 'Originalsatz ist nicht gueltig, da er mit WFC9220 verarbeitet wurde | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **Total Codes**: 123
- **Found in Source**: 95 (77%)
- **Not in Source**: 28

---

*Document generated: 2025-11-27 09:54:38*
