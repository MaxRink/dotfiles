# Booking Module Error Codes - Complete Reference Table
## BFM (Booking File Messages) and BHM (Booking Hinweis Messages) Implementation

**Module**: Booking Interface (Number Booking Operations)
**Analysis Date**: 2025-11-27
**Total Error Codes**: 285 codes
**Coverage**: BFM: 235 codes, BHM: 50 codes

---

## 1. BFM CODES (Booking File Messages)

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **BFM001** | „frei für Buchung“ kleiner als Schwellwert | pack_strukt.sql:18 | Constant: FC_SW_IN_VE |
| **BFM002** | „in VE eingerichtet“ kleiner als Freigabegröße | pack_strukt.sql:19 | Constant: FC_FGR_IN_VE |
| **BFM003** | RNB Bestellvorwarnung | pack_strukt.sql:20 | Constant: FC_SW_RNB |
| **BFM005** | belegte Rufnummer in Bereich mit Vergabeinfo "in VE eingerichtet" | pack_strukt.sql:21 | Constant: FC_RFNR_BI |
| **BFM011** | keine nutzbaren BI für Freigabe vorhanden | pack_strukt.sql:22 | Constant: FC_NICHT_NUTZBAR |
| **BFM012** | keine Rufnummern freigegeben | pack_strukt.sql:23 | Constant: FC_SW_FREIGABE |
| **BFM013** | Ein Auftrag kann nicht realisiert werden RNB Bestellung erforderlich | pack_strukt.sql:24 | Constant: FC_BESTElLUNG |
| **BFM050** | RufNr wurde während der Reaktivierung in RNVS geändert | pack_body_strukt.sql:182 | Constant: FC_REAKT_PORTLEVEL |
| **BFM108** | RfNr kann nicht gebucht werden; Altbestand | pack_crm.sql:648 | Constant: PM_SPERRE_ALTBESTAND |
| **BFM150** | Ungültiger TNB | pack_crm.sql:666 | Constant: PM_TNB_UNGUELTIG |
| **BFM169** | Techniktyp passt nicht zum zukünftigen Kontingent | pack_crm.sql:668 | Constant: PM_UFRM_KONT_TECH |
| **BFM170** | Techniktyp oder Besitzer passt nicht zum Stamm der DUWA | pack_crm.sql:670 | Constant: PM_TECH_DUWA |
| **BFM171** | TVS/Storno auf einen validerten Export ohne NBI | pack_crm.sql:672 | Constant: PM_VAL_EXPORT |
| **BFM214** | Die Rufnr hat einen fremden Eigentümer | pack_crm.sql:651 | Constant: PM_EIG_FREMD |
| **BFM251** | Das Kontingent ist unvollständig | pack_crm.sql:653 | Constant: PM_KONT_UNVOLLSTAENDIG |
| **BFM252** | Es ist eine RfNr mit anderen Grenzen vorhanden | pack_crm.sql:649 | Constant: PM_RFNR_BEL_GRENZEN |
| **BFM255** | Belegung wurde nicht verarbeitet | pack_crm.sql:652 | Constant: PM_BESTAET_VORH |
| **BFM268** | Der Eigentümer der Rufnr ist BNetzA | pack_crm.sql:650 | Constant: PM_EIGENT_REGTP |
| **BFM269** | Toleranzgrenze für Datumsabweichung überschritten | pack_crm.sql:654 | Constant: PM_PORTDAT |
| **BFM300** | Kuendigung/Export einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | pack_crm.sql:656 | Constant: PM_ABSCHALTEVERFUEGUNG |
| **BFM301** | Kuendigung/Export einer Rufnummer - Sperre aufgrund einer Quarantaene | pack_crm.sql:657 | Constant: PM_QUARANTAENE |
| **BFM302** | Kuendigung/Export einer Rufnummer - Sperre aufgrund von Quali-Frei | pack_crm.sql:660 | Constant: PM_QUALI_FREI |
| **BFM312** | DUWA-Grenzen stimmen nicht überein | pack_crm.sql:655 | Constant: PM_KONTINGENT_PROBL |
| **BFM316** | Rufnummer ist exportiert | unknown | Code definition not found in PL/SQL source |
| **BFM343** | Zu Rufnummer liegt bereits eine Portierungsmeldung vor. | unknown | Code definition not found in PL/SQL source |
| **BFM344** | Zu Rufnummer liegt eine Portierungsmeldung vor | unknown | Code definition not found in PL/SQL source |
| **BFM355** | Die Rufnr ist bereits bestaetigt. | unknown | Code definition not found in PL/SQL source |
| **BFM356** | Die Rufnr hat den Status "frei". | unknown | Code definition not found in PL/SQL source |
| **BFM365** | Der Buchungsauftrag ist nicht vorhanden. | unknown | Code definition not found in PL/SQL source |
| **BFM402** | Uebergebene Rfnr liegen in untersch. Kontingenten | pack_crm.sql:663 | Constant: PM_KONTINGENT |
| **BFM403** | Schaltdatum der Netzbuchung ueberschritten | pack_crm.sql:664 | Constant: PM_REAL_NI |
| **BFM404** | Kontingentfehler | pack_crm.sql:665 | Constant: PM_KONT_FEHLER |
| **BFM405** | ALPS-Realisierung ohne vorhergehende Netzbuchung | unknown | Code definition not found in PL/SQL source |
| **BFM406** | Reaktivierungsauftrag - Stornierung | pack_crm.sql:679 | Constant: PM_REAKT_STO |
| **BFM407** | Reaktivierungsauftrag - Terminverschiebung | pack_crm.sql:678 | Constant: PM_REAKT_TV |
| **BFM408** | Export zu D150 ohne ECRMPxxx | unknown | Code definition not found in PL/SQL source |
| **BFM409** | Export zu D150 mit ECRMPxxx | unknown | Code definition not found in PL/SQL source |
| **BFM410** | Export zu D150 - Promex 6110 | unknown | Code definition not found in PL/SQL source |
| **BFM5007** | Zur Rufnummer laeuft zur Zeit eine Produktaenderung | unknown | Code definition not found in PL/SQL source |
| **BFM501** | Ursprüngliches Kontingent wurde verändert | unknown | Code definition not found in PL/SQL source |
| **BFM5010** | Die Rufnummer hat falsche Laenge | unknown | Code definition not found in PL/SQL source |
| **BFM5014** | Rufnummer hat falschen Eigentuemer | unknown | Code definition not found in PL/SQL source |
| **BFM5016** | Rufnummer ist exportiert oder Rückfall vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM503** | Rufnummer mit ungültigem Status im Kontingent | unknown | Code definition not found in PL/SQL source |
| **BFM5030** | Wiederbelegungssperre darf nicht kleiner als Tagesdatum sein | unknown | Code definition not found in PL/SQL source |
| **BFM5042** | Die gelieferten Rufnummern gehoeren nicht zum gleichen Kontingent. | unknown | Code definition not found in PL/SQL source |
| **BFM5043** | Zu der Rufnummer liegt bereits eine Portierungsmeldung von Telekom vor | unknown | Code definition not found in PL/SQL source |
| **BFM5044** | Zu der Rufnummer liegt bereits eine Portierungsmeldung von WSST vor' | unknown | Code definition not found in PL/SQL source |
| **BFM5045** | Die Blockgrenzen der Rufnummer stimmen nicht überein | unknown | Code definition not found in PL/SQL source |
| **BFM5047** | Die Rufnummer ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM5048** | Die Buchungsnr der Rufnr stimmt nicht ueberein | unknown | Code definition not found in PL/SQL source |
| **BFM5049** | Die Stornierung kann nicht durchgefuehrt werden.' | unknown | Code definition not found in PL/SQL source |
| **BFM5052** | Die Rufnr kann nicht gebucht werden; Rufnummernbereich ist durch Rfnr mit anderen Grenzen belegt | unknown | Code definition not found in PL/SQL source |
| **BFM5055** | Die Rufnr ist bereits bestaetigt | unknown | Code definition not found in PL/SQL source |
| **BFM5056** | Die Rufnr hat den Status "frei | unknown | Code definition not found in PL/SQL source |
| **BFM5058** | Falsches Buchungskennzeichen zur Rufnr | unknown | Code definition not found in PL/SQL source |
| **BFM5065** | Der Buchungsauftrag ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM5068** | Eigentuemer der Rufnummer ist BNetzA | unknown | Code definition not found in PL/SQL source |
| **BFM5069** | Zur Rufnummer gibt es eine unbestaetigte Portierungsmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM5076** | Der Buchungsfall ist unzulässig | unknown | Code definition not found in PL/SQL source |
| **BFM5093** | Stornierung nicht zulaessig - Rufnummer wurde veraendert | unknown | Code definition not found in PL/SQL source |
| **BFM5107** | Import auf eine DTAG-Rufnummer | unknown | Code definition not found in PL/SQL source |
| **BFM5108** | RfNr kann nicht gebucht werden; Altbestand | unknown | Code definition not found in PL/SQL source |
| **BFM5132** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | unknown | Code definition not found in PL/SQL source |
| **BFM5133** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Quarantaene | unknown | Code definition not found in PL/SQL source |
| **BFM5141** | Eine Netzbuchungsinfo zur Rufnummer ist bereits vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM5142** | Das Vertriebssystem stimmt nicht ueberein | unknown | Code definition not found in PL/SQL source |
| **BFM5143** | Falscher TNB | unknown | Code definition not found in PL/SQL source |
| **BFM5144** | Das Ausführungsdatum muss in der Zukunft liegen | unknown | Code definition not found in PL/SQL source |
| **BFM5146** | Rufnummern mit unterschiedlicher Technik | unknown | Code definition not found in PL/SQL source |
| **BFM5147** | Netzbuchung - Kontingentfehler | unknown | Code definition not found in PL/SQL source |
| **BFM5148** | Eine Netzbuchungsinfo zur Rufnummer ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM5149** | Die Netzbuchungsinfo hat eine abweichende Buchungsnummer | unknown | Code definition not found in PL/SQL source |
| **BFM5153** | Es existiert bereits eine Netzbuchung | unknown | Code definition not found in PL/SQL source |
| **BFM5154** | Das Portierungsziel darf nicht D001 oder 199C07 sein | unknown | Code definition not found in PL/SQL source |
| **BFM5155** | Der Besitzer der Rufnummer ist weder D001 noch 199C07 | unknown | Code definition not found in PL/SQL source |
| **BFM5156** | Die Rufnummer ist Bestandteil einer TK-Anlage | unknown | Code definition not found in PL/SQL source |
| **BFM5157** | Zur Rufnummer exisitiert eine nicht erledigte Problemmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM5158** | BuchNetz EX bereits vorhanden und RNPS bereits informiert | unknown | Code definition not found in PL/SQL source |
| **BFM5159** | Stornierung nicht mehr möglich, da RNPS bereits informiert wurde | unknown | Code definition not found in PL/SQL source |
| **BFM5170** | Verarbeitung nicht möglich da Nummer nur für Leitung (NG-Dummy) | unknown | Code definition not found in PL/SQL source |
| **BFM5171** | NGDummy nur für BLW gebuchte Rufummern zulässig | unknown | Code definition not found in PL/SQL source |
| **BFM5172** | NGDummy nur für BLW gebuchte Rufummern zulässig | unknown | Code definition not found in PL/SQL source |
| **BFM5173** | Rufnummer bereits in Verwendung | unknown | Code definition not found in PL/SQL source |
| **BFM5174** | Sperre aufgrund von NGDummy | unknown | Code definition not found in PL/SQL source |
| **BFM5180** | Buchung/Import einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM5181** | Kuendigung/Export einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM5182** | Export einer Rufnummer - Sperre aufgrund von Abschalteverfügung | unknown | Code definition not found in PL/SQL source |
| **BFM5183** | Export einer Rufnummer - Sperre aufgrund von Quarantäne | unknown | Code definition not found in PL/SQL source |
| **BFM5190** | Der Besitzer der Rufnummer ist keine IP-Netzportierungskennung | unknown | Code definition not found in PL/SQL source |
| **BFM5200** | Rufnummer hat kein oder falsches Buchungskennzeichen | unknown | Code definition not found in PL/SQL source |
| **BFM5201** | Fehlende PreOrder Buchung bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5202** | Portierungskennung ungleich bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5203** | Unzulässiges BKZ bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5204** | CRM-Real. nach Storno bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5205** | CRM-Buchung fehlt bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5206** | CRM-Buchung fehlt nach "FR" von KONTES bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5207** | CRM-Realisierung fehlt nach "FR" bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5208** | CRM-Kündigung fehlt nach "BE" bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM5209** | CRM-Storno fehlt bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6007** | Zur Rufnummer laeuft zur Zeit eine Produktaenderung | unknown | Code definition not found in PL/SQL source |
| **BFM6010** | Die Rufnummer hat falsche Laenge | unknown | Code definition not found in PL/SQL source |
| **BFM6014** | Rufnummer hat falschen Eigentuemer | unknown | Code definition not found in PL/SQL source |
| **BFM6016** | Rufnummer ist exportiert oder Rückfall vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM6030** | Wiederbelegungssperre darf nicht kleiner als Tagesdatum sein | unknown | Code definition not found in PL/SQL source |
| **BFM6042** | Die gelieferten Rufnummern gehoeren nicht zum gleichen Kontingent. | unknown | Code definition not found in PL/SQL source |
| **BFM6043** | Zu der Rufnummer liegt bereits eine Portierungsmeldung von Telekom vor | unknown | Code definition not found in PL/SQL source |
| **BFM6044** | Zu der Rufnummer liegt bereits eine Portierungsmeldung von WSST vor' | unknown | Code definition not found in PL/SQL source |
| **BFM6045** | Die Blockgrenzen der Rufnummer stimmen nicht überein | unknown | Code definition not found in PL/SQL source |
| **BFM6047** | Die Rufnummer ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM6048** | Die Buchungsnr der Rufnr stimmt nicht ueberein | unknown | Code definition not found in PL/SQL source |
| **BFM6049** | Die Stornierung kann nicht durchgefuehrt werden.' | unknown | Code definition not found in PL/SQL source |
| **BFM6052** | Die Rufnr kann nicht gebucht werden; Rufnummernbereich ist durch Rfnr mit anderen Grenzen belegt | unknown | Code definition not found in PL/SQL source |
| **BFM6055** | Die Rufnr ist bereits bestaetigt | unknown | Code definition not found in PL/SQL source |
| **BFM6056** | Die Rufnr hat den Status "frei | unknown | Code definition not found in PL/SQL source |
| **BFM6058** | Falsches Buchungskennzeichen zur Rufnr | unknown | Code definition not found in PL/SQL source |
| **BFM6065** | Der Buchungsauftrag ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM6068** | Eigentuemer der Rufnummer ist BNetzA | unknown | Code definition not found in PL/SQL source |
| **BFM6069** | Zur Rufnummer gibt es eine unbestaetigte Portierungsmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM6076** | Der Buchungsfall ist unzulässig | unknown | Code definition not found in PL/SQL source |
| **BFM6093** | Stornierung nicht zulaessig - Rufnummer wurde veraendert | unknown | Code definition not found in PL/SQL source |
| **BFM6107** | Import auf eine DTAG-Rufnummer | unknown | Code definition not found in PL/SQL source |
| **BFM6108** | RfNr kann nicht gebucht werden; Altbestand | unknown | Code definition not found in PL/SQL source |
| **BFM6132** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | unknown | Code definition not found in PL/SQL source |
| **BFM6133** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Quarantaene | unknown | Code definition not found in PL/SQL source |
| **BFM6141** | Eine Netzbuchungsinfo zur Rufnummer ist bereits vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM6142** | Das Vertriebssystem stimmt nicht ueberein | unknown | Code definition not found in PL/SQL source |
| **BFM6143** | Falscher TNB | unknown | Code definition not found in PL/SQL source |
| **BFM6144** | Das Ausführungsdatum muss in der Zukunft liegen | unknown | Code definition not found in PL/SQL source |
| **BFM6146** | Rufnummern mit unterschiedlicher Technik | unknown | Code definition not found in PL/SQL source |
| **BFM6147** | Netzbuchung - Kontingentfehler | unknown | Code definition not found in PL/SQL source |
| **BFM6148** | Eine Netzbuchungsinfo zur Rufnummer ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM6149** | Die Netzbuchungsinfo hat eine abweichende Buchungsnummer | unknown | Code definition not found in PL/SQL source |
| **BFM6153** | Es existiert bereits eine Netzbuchung | unknown | Code definition not found in PL/SQL source |
| **BFM6154** | Das Portierungsziel darf nicht D001 oder 199C07 sein | unknown | Code definition not found in PL/SQL source |
| **BFM6155** | Der Besitzer der Rufnummer ist weder D001 noch 199C07 | unknown | Code definition not found in PL/SQL source |
| **BFM6156** | Die Rufnummer ist Bestandteil einer TK-Anlage | unknown | Code definition not found in PL/SQL source |
| **BFM6157** | Zur Rufnummer exisitiert eine nicht erledigte Problemmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM6158** | BuchNetz EX bereits vorhanden und RNPS bereits informiert | unknown | Code definition not found in PL/SQL source |
| **BFM6159** | Stornierung nicht mehr möglich, da RNPS bereits informiert wurde | unknown | Code definition not found in PL/SQL source |
| **BFM6170** | Verarbeitung nicht möglich da Nummer nur für Leitung (NG-Dummy) | unknown | Code definition not found in PL/SQL source |
| **BFM6171** | NG-Buchung: Verarbeitung nicht möglich' | unknown | Code definition not found in PL/SQL source |
| **BFM6172** | NGDummy nur für BLW gebuchte Rufummern zulässig | unknown | Code definition not found in PL/SQL source |
| **BFM6173** | Rufnummer bereits in Verwendung | unknown | Code definition not found in PL/SQL source |
| **BFM6174** | Sperre aufgrund von NGDummy | unknown | Code definition not found in PL/SQL source |
| **BFM6180** | Buchung/Import einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM6181** | Kuendigung/Export einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM6182** | Export einer Rufnummer - Sperre aufgrund von Abschalteverfügung | unknown | Code definition not found in PL/SQL source |
| **BFM6183** | Export einer Rufnummer - Sperre aufgrund von Quarantäne | unknown | Code definition not found in PL/SQL source |
| **BFM6190** | Der Besitzer der Rufnummer ist keine IP-Netzportierungskennung | unknown | Code definition not found in PL/SQL source |
| **BFM6200** | Rufnummer hat kein oder falsches Buchungskennzeichen | unknown | Code definition not found in PL/SQL source |
| **BFM6201** | Fehlende PreOrder Buchung bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6202** | Portierungskennung ungleich bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6203** | Unzulässiges BKZ bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6204** | CRM-Real. nach Storno bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6205** | CRM-Buchung fehlt bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6206** | CRM-Buchung fehlt nach "FR" von KONTES bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6207** | CRM-Realisierung fehlt nach "FR" bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6208** | CRM-Kündigung fehlt nach "BE" bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM6209** | CRM-Storno fehlt bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM7005** | Die Rufnummer ist bereits belegt. | unknown | Code definition not found in PL/SQL source |
| **BFM7011** | Die Rufnummer hat falsche Laenge. | unknown | Code definition not found in PL/SQL source |
| **BFM7012** | Die Rufnummer ist nicht zur Buchung freigegeben. | unknown | Code definition not found in PL/SQL source |
| **BFM7014** | Die Rufnummer ist nicht an die Deutsche Telekom zugeteilt. | unknown | Code definition not found in PL/SQL source |
| **BFM7017** | Die Rufnummer ist nicht fuer diese Nutzungsart freigegeben. | unknown | Code definition not found in PL/SQL source |
| **BFM7043** | Zu der Rufnummer liegt bereits eine Portierungsmeldung vor. | unknown | Code definition not found in PL/SQL source |
| **BFM7052** | Die Rufnummer kann nicht gebucht werden. Rufnrbereich ist durch Rufnr mit anderen Grenzen belegt | unknown | Code definition not found in PL/SQL source |
| **BFM7056** | Die Rufnummer hat den Status ''frei' | unknown | Code definition not found in PL/SQL source |
| **BFM7058** | Falsches Buchungskennzeichen zur Rufnummer. | unknown | Code definition not found in PL/SQL source |
| **BFM7069** | Zur Rufnummer gibt es eine unbestaetigte Portierungsmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM7107** | Import auf eine DTAG-Rufnummer. | unknown | Code definition not found in PL/SQL source |
| **BFM7108** | Falschbuchung aus Rufnummernservice | unknown | Code definition not found in PL/SQL source |
| **BFM7305** | Die Rufnummern gehoeren zu unterschiedlichen Ortsnetzen. | unknown | Code definition not found in PL/SQL source |
| **BFM7306** | Die Rufnummer hat nicht das Vertriebssystem MH. | unknown | Code definition not found in PL/SQL source |
| **BFM7307** | Die Rufnummer ist belegt bei D001 oder bestaetigt portiert bei DTAG | unknown | Code definition not found in PL/SQL source |
| **BFM7312** | Der Eigentuemer der Rufnummer ist: BNetzA | unknown | Code definition not found in PL/SQL source |
| **BFM7314** | Die Rufnummer ist unbestaetigt portiert und hat einen Portierungslevel u3 | unknown | Code definition not found in PL/SQL source |
| **BFM7315** | Die Rufnummer ist unbestaetigt portiert und der Portbes ist ungleich dem gemeldeten Portbes | unknown | Code definition not found in PL/SQL source |
| **BFM7316** | Die Rufnummer ist bestaetigt portiert und der Portbes ist ungleich dem gemeldeten Portbes | unknown | Code definition not found in PL/SQL source |
| **BFM7317** | Die Rufnummer ist bestaetigt portiert bei D999 (Abschalteverfuegung/Quarantaene/Quali Frei) | unknown | Code definition not found in PL/SQL source |
| **BFM7319** | Es liegt ein laufender Portierungsauftrag vor | unknown | Code definition not found in PL/SQL source |
| **BFM7321** | Die Rufnummer ist mit anderer Laenge in der DB vorhanden und Besitzer <> Eigentuemer | unknown | Code definition not found in PL/SQL source |
| **BFM7323** | Eine Weiterversorgung ist nicht moeglich | unknown | Code definition not found in PL/SQL source |
| **BFM7324** | Die Weiterversorgungsfrist ist ueberschritten | unknown | Code definition not found in PL/SQL source |
| **BFM9007** | Zur Rufnummer läuft zur Zeit eine Produktänderung | unknown | Code definition not found in PL/SQL source |
| **BFM9016** | Rufnummer ist exportiert oder Rückfall vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM9043** | Zu der Rufnummer liegt bereits eine Portierungsmeldung von Telekom vor | unknown | Code definition not found in PL/SQL source |
| **BFM9044** | Zu der Rufnummer liegt bereits eine Portierungsmeldung der WSSt vor | unknown | Code definition not found in PL/SQL source |
| **BFM9045** | Die Blockgrenzen der Rufnummer stimmen nicht überein | unknown | Code definition not found in PL/SQL source |
| **BFM9047** | Der Netzbuchungsauftrag ist nicht vorhanden. | unknown | Code definition not found in PL/SQL source |
| **BFM9048** | Die Buchungsnr der Rufnr stimmt nicht ueberein. | unknown | Code definition not found in PL/SQL source |
| **BFM9055** | Belegtmeldung aus CRM-T trifft auf valide Portierung im RNVS | unknown | Code definition not found in PL/SQL source |
| **BFM9056** | Die Rufnr hat den Status "frei". | unknown | Code definition not found in PL/SQL source |
| **BFM9065** | Der Buchungsauftrag ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM9069** | Zur Rufnummer gibt es eine unbestaetigte Portierungsmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM9076** | Die Rufnummer hat Technik = NG-Dummy | unknown | Code definition not found in PL/SQL source |
| **BFM9093** | Stornierung nicht zulaessig - Rufnummer wurde veraendert | pack_crm.sql:675 | Constant: PM_STO_NICHT_ZULAESSIG |
| **BFM9132** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | unknown | Code definition not found in PL/SQL source |
| **BFM9133** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Quarantaene | unknown | Code definition not found in PL/SQL source |
| **BFM9138** | Das Ausführungsdatum muss gefüllt sein | unknown | Code definition not found in PL/SQL source |
| **BFM9141** | Eine Netzbuchungsinfo zur Rufnummer ist bereits vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM9142** | Das Vertriebssystem stimmt nicht ueberein | unknown | Code definition not found in PL/SQL source |
| **BFM9144** | Das Ausführungsdatum muss in der Zukunft liegen | unknown | Code definition not found in PL/SQL source |
| **BFM9146** | Rufnummern mit unterschiedlicher Technik | unknown | Code definition not found in PL/SQL source |
| **BFM9147** | Netzbuchung - Kontingentfehler | unknown | Code definition not found in PL/SQL source |
| **BFM9148** | Eine Netzbuchungsinfo zur Rufnummer ist nicht vorhanden | unknown | Code definition not found in PL/SQL source |
| **BFM9149** | Die Netzbuchungsinfo hat eine abweichende Buchungsnummer | unknown | Code definition not found in PL/SQL source |
| **BFM9153** | Es existiert bereits eine Netzbuchung | unknown | Code definition not found in PL/SQL source |
| **BFM9154** | Das Portierungsziel darf nicht D001 oder 199C07 sein | unknown | Code definition not found in PL/SQL source |
| **BFM9155** | Der Besitzer der Rufnummer ist weder D001 noch 199C07 | unknown | Code definition not found in PL/SQL source |
| **BFM9156** | Die Rufnummer ist Bestandteil einer TK-Anlage | unknown | Code definition not found in PL/SQL source |
| **BFM9157** | Zur Rufnummer exisitiert eine nicht erledigte Problemmeldung | unknown | Code definition not found in PL/SQL source |
| **BFM9158** | BuchNetz EX bereits vorhanden und RNPS bereits informiert | unknown | Code definition not found in PL/SQL source |
| **BFM9159** | Stornierung nicht mehr möglich, da RNPS bereits informiert wurde | unknown | Code definition not found in PL/SQL source |
| **BFM9168** | Doppelte Kündigung bei Rufnummernübernahme CRM-T | unknown | Code definition not found in PL/SQL source |
| **BFM9170** | Verarbeitung nicht möglich da Nummer nur für Leitung (NG-Dummy) | unknown | Code definition not found in PL/SQL source |
| **BFM9171** | NG-Buchung: Verarbeitung nicht möglich | unknown | Code definition not found in PL/SQL source |
| **BFM9172** | NG Dummy nur für BLW gebuchte Rufummern zulässig | unknown | Code definition not found in PL/SQL source |
| **BFM9173** | Rufnummer bereits in Verwendung | unknown | Code definition not found in PL/SQL source |
| **BFM9174** | Sperre aufgrund von NGDummy | unknown | Code definition not found in PL/SQL source |
| **BFM9180** | Buchung/Import einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM9181** | Kuendigung/Export einer Rufnummer - Sperre aufgrund von Quali-Frei | unknown | Code definition not found in PL/SQL source |
| **BFM9182** | Export einer Rufnummer - Sperre aufgrund von Abschalteverfügung' | unknown | Code definition not found in PL/SQL source |
| **BFM9183** | 'Export einer Rufnummer - Sperre aufgrund von Quarantäne' | unknown | Code definition not found in PL/SQL source |
| **BFM9190** | Der Besitzer der Rufnummer ist keine IP-Netzportierungskennung' | unknown | Code definition not found in PL/SQL source |
| **BFM9200** | Rufnummer hat kein oder falsches Buchungskennzeichen | unknown | Code definition not found in PL/SQL source |
| **BFM9201** | Fehlende PreOrder Buchung bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM9202** | Portierungskennung ungleich bei UFRM-KONTES | unknown | Code definition not found in PL/SQL source |
| **BFM9203** | Unzulässiges BKZ bei UFRM-KONTES | pack_crm.sql:682 | Constant: PM_UFRMK_UNZUL_BKZ |
| **BFM9204** | CRM-Real. nach Storno bei UFRM-KONTES | pack_crm.sql:683 | Constant: PM_UFRMK_REAL_STO |
| **BFM9205** | CRM-Buchung fehlt bei UFRM-KONTES | pack_crm.sql:684 | Constant: PM_UFRMK_FK |
| **BFM9206** | CRM-Buchung fehlt nach "FR" von KONTES bei UFRM-KONTES | pack_crm.sql:685 | Constant: PM_UFRMK_FR |
| **BFM9207** | CRM-Realisierung fehlt nach "FR" bei UFRM-KONTES | pack_crm.sql:686 | Constant: PM_UFRMK_UR |
| **BFM9208** | CRM-Kündigung fehlt nach "BE" bei UFRM-KONTES | pack_crm.sql:687 | Constant: PM_UFRMK_KR |
| **BFM9209** | CRM-Storno fehlt bei UFRM-KONTES | pack_crm.sql:688 | Constant: PM_UFRMK_ST |

---

## 2. BHM CODES (Booking Hinweis/Notice Messages)

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **BHM101** | Zur RfNr ist eine Buchung eines anderen Systems vorhanden | pack_crm.sql:623 | Constant: HM_WEITERE_BUCHUNG |
| **BHM102** | Die gelieferte Rufnummer ist nicht in einem Kontingent | pack_crm.sql:624 | Constant: HM_KEINE_KONTSID |
| **BHM103** | Die Rufnummer ist nicht im gleichen Kontingent | pack_crm.sql:625 | Constant: HM_KONTINGENT_FALSCH |
| **BHM104** | Das gelieferte Kontingent ist unvollständig | pack_crm.sql:626 | Constant: HM_KONT_UNVOLLSTAENDIG |
| **BHM105** | Kuendigung einer vorläufig belegten RfNr von KONTES | pack_crm.sql:627 | Constant: HM_KUEND_FR_VSYSTEM |
| **BHM106** | Kuendigung einer noch nicht abgeschlossenen Produktaenderung von KONTES | pack_crm.sql:628 | Constant: HM_KUEND_FR_VSYSTEM2 |
| **BHM111** | Erweiterung eines Kontingents durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:629 | Constant: HM_AEND_BUFF |
| **BHM112** | Reduzierung eines Kontingents durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:630 | Constant: HM_RED_BUFF |
| **BHM113** | Kündigung durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:631 | Constant: HM_KUEND_BUFF |
| **BHM114** | Realisierung durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:632 | Constant: HM_REAL_BUFF |
| **BHM115** | Buchung eines Kontingents durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:633 | Constant: HM_BUCH_BUFF_BAAS |
| **BHM116** | Buchung einer Einzelrufnr durch CRM; Portierungsmeldung im Meldungskorb vorhanden | pack_crm.sql:634 | Constant: HM_BUCH_BUFF_EAS |
| **BHM117** | Buchung einer TK-Anlage; Meldungskorb ist vorhanden | pack_crm.sql:635 | Constant: HM_BUCH_BUFF_TKANL |
| **BHM118** | Buchung einer freien RfNr; Meldungskorb ist vorhanden | pack_crm.sql:636 | Constant: HM_BUCH_BUFF_FREI |
| **BHM119** | Eine vorhandene Netzbuchungsinfo wurde überschrieben | pack_crm.sql:637 | Constant: HM_BNETZ_INT |
| **BHM120** | BuchNetz Extern auf eine IP-Rufnummer Cu | pack_crm.sql:638 | Constant: HM_BNETZ_EXT_CU |
| **BHM121** | ALPS Storno: RNPS bereits informiert | pack_crm.sql:639 | Constant: HM_STO_RNPS |
| **BHM122** | MODIFY auf belegte D001-Rufnummer | pack_crm.sql:640 | Constant: HM_MOD_D001 |
| **BHM123** | Rufnummer aus Kontingent rausgelöst | pack_crm.sql:641 | Constant: HM_KONT_RAUS |
| **BHM124** | Das Buchungskennzeichen der Rufnummer wurde gelöscht | pack_crm.sql:642 | Constant: HM_BUCHKZ_DEL |
| **BHM125** | Export zu D150 - HM Promex 6110 - TR_Besitzer = 199CXX | unknown | Code definition not found in PL/SQL source |
| **BHM126** | BHM126','Export zu D150 - Promex 6110 - BFM409 - Export nachgebildet | unknown | Code definition not found in PL/SQL source |
| **BHM127** | Stornierung nicht mehr möglich, da RNPS bereits informiert wurde | unknown | Code definition not found in PL/SQL source |
| **BHM128** | ALPS Meldung fehlt! - Besitzer D001 - kein Verwender 10 | unknown | Code definition not found in PL/SQL source |
| **BHM129** | ALPS Meldung fehlt! - u1 und Besitzer D001 - kein Verwender 10 | unknown | Code definition not found in PL/SQL source |
| **BHM130** | Die Rufnummer hat BSys = MH, CONAN oder CONGSTAR | pack_crm.sql:646 | Constant: HM_REST_API |
| **BHM131** | Import einer Rufnummer; Z-Meldung ist vorhanden | unknown | Code definition not found in PL/SQL source |
| **BHM132** | Rueckfall umgesetzt trotz vorhandenen Import | unknown | Code definition not found in PL/SQL source |
| **BHM133** | CRM-T Export zu D001 auf 199C07/u2/199C09 | unknown | Code definition not found in PL/SQL source |
| **BHM269** | Toleranzgrenze fuer Datumsabweichung ueberschritten | pack_crm.sql:643 | Constant: HM_PORTDAT |
| **BHM7001** | Es konnte keine freie Rufnummer zu dieser Anschlussart ermittelt werden. | unknown | Code definition not found in PL/SQL source |
| **BHM7015** | Die Rufnummer hat Eigentuemer Altbestand. | unknown | Code definition not found in PL/SQL source |
| **BHM7016** | Die Rufnummer ist exportiert. | unknown | Code definition not found in PL/SQL source |
| **BHM7017** |  | unknown | Code definition not found in PL/SQL source |
| **BHM7018** | Die Rufnummer hat eine Wiederbelegungssperre. | unknown | Code definition not found in PL/SQL source |
| **BHM7310** | Doppelmeldung: die Rufnummer ist bereits realisiert | unknown | Code definition not found in PL/SQL source |
| **BHM7318** | Doppelmeldung fuer Rufnummer: Es liegt bereits ein Importauftrag durch MH vor | unknown | Code definition not found in PL/SQL source |
| **BHM7320** | Die Rufnummern-Laenge des Import-Geschaeftsfalls < 10 | unknown | Code definition not found in PL/SQL source |
| **BHM7322** | Die Rufnummer ist u3 portiert | unknown | Code definition not found in PL/SQL source |
| **BHM7901** | Buchungsfall: Storno / Die Rufnummer hat den Status FREI | pack_crm.sql:565 | Constant: HM_STO_FREI |
| **BHM7902** | Buchungsfall: Storno / Die Rufnummer ist bestaetigt portiert bei einem fremden TNB | pack_crm.sql:566 | Constant: HM_STO_PORT |
| **BHM7903** | Buchungsfall: Kuend / Die Rufnummer hat den Status FREI | pack_crm.sql:567 | Constant: HM_KUEND_FREI |
| **BHM7904** | Buchungsfall: Kuend / Die Rufnummer steht auf u3 zum fremden TNB | pack_crm.sql:568 | Constant: HM_KUEND_PORT |
| **BHM7905** | Bei Kuendigung ist ein Buffer vorhanden | pack_crm.sql:569 | Constant: HM_MH_KUEND_BUFF |
| **BHM7906** | Bei Buchung ist ein Buffer vorhanden | pack_crm.sql:570 | Constant: HM_MH_BUCH_BUFF |
| **BHM7907** | Die Rufnummer ist unbestaetigt portiert und der PortBes ist gleich dem gemeldeten PortBes | pack_crm.sql:571 | Constant: HM_MH_UPORT |
| **BHM7908** | Die Rufnummer ist bestaetigt portiert und der PortBes ist gleich dem gemeldeten PortBes | pack_crm.sql:572 | Constant: HM_MH_BPORT |
| **BHM7910** | Das aufrufende System stimmt nicht mit dem BSys der Rufnummer ueberein | pack_crm.sql:573 | Constant: HM_MH_BSYS |
| **BHM9016** | Rufnummer ist exportiert oder Rueckfall vorhanden | pack_crm.sql:645 | Constant: HM_RFNR_EXP |
| **BHM9056** | Die Rufnr hat den Status "frei". | unknown | Code definition not found in PL/SQL source |

---

## Coverage Analysis

- **BFM Codes**: 235 total (36 in source)
- **BHM Codes**: 50 total (32 in source)

---

*Document generated: 2025-11-27 09:54:38*
