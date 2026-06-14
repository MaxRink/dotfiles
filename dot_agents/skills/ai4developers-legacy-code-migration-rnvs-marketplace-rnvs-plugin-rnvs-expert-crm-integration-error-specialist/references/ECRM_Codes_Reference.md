# ECRM Portal Error Codes - Complete Reference Table
## ECRMP (CRM Portal Request) and ERESP (CRM Portal Response) Implementation

**Module**: CRM Integration (ECRM Portal Interface)
**Analysis Date**: 2025-11-27
**Total Error Codes**: 226 codes
**Coverage**: ECRMP: 183 codes, ERESP: 43 codes

---

## 1. ECRMP CODES (CRM Portal Request Validation Errors)

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **ECRMP001** | Es konnte keine freie Rufnummer zu dieser Anschlussart ermittelt werden. | pack_crm.sql:236 | Constant: FC_KEINE_FREIE_RFNR |
| **ECRMP002** | Ungültiger Wert in Feld ONKz | pack_crm.sql:237 | Constant: FC_FALSCHES_ONKZ |
| **ECRMP003** | MVSt fehlt. | pack_crm.sql:238 | Constant: FC_MVST_NV |
| **ECRMP004** | Die Mobilfunknummer ist nicht vorhanden. | pack_crm.sql:239 | Constant: FC_MRFNR_NV |
| **ECRMP005** | Die Rufnummer {0} ist bereits belegt. | pack_crm.sql:240 | Constant: FC_RFNR_VORH |
| **ECRMP006** | Die Rufnummer {0} ist reserviert. | pack_crm.sql:241 | Constant: FC_RFNR_RES |
| **ECRMP007** | Zur Rufnummer {0} laeuft zur Zeit eine Produktaenderung. | pack_crm.sql:242 | Constant: FC_RFNR_VU |
| **ECRMP008** | Die Rufnummer {0} ist vorlaeufig belegt | pack_crm.sql:243 | Constant: FC_RFNR_VB |
| **ECRMP009** | Zur Rufnummer {0} ist eine Belegung in der Zukunft vorgesehen. | pack_crm.sql:244 | Constant: FC_RFNR_ZO |
| **ECRMP010** | Die Rufnummer {0} hat falsche Laenge. | pack_crm.sql:245 | Constant: FC_RFNR_LAENGE |
| **ECRMP011** | Die Laenge der Rufnummer {0} entspricht nicht den Vorgaben des NM (Bereichsinfo). | pack_crm.sql:246 | Constant: FC_BI_LAENGE |
| **ECRMP012** | Die Rufnummer {0} ist nicht zur Buchung freigegeben. | pack_crm.sql:247 | Constant: FC_BI_FREIGABE |
| **ECRMP013** | Rufnummer {0} liegt im gesperrten Bereich (Gasse 19) | pack_crm.sql:248 | Constant: FC_GASSE_10 |
| **ECRMP014** | Rufnummer hat falschen Eigentümer | pack_crm.sql:249 | Constant: FC_EIG_FREMD |
| **ECRMP015** | Die Rufnummer {0} ist Altbestand d.h. Eigentuemer ist BNetzA. | pack_crm.sql:250 | Constant: FC_EIG_ALTBESTAND |
| **ECRMP016** | (B) Rufnummer xxxxxxx ist exportiert - Besitzer: Dxxx | pack_crm.sql:251 | Constant: FC_RFNR_EXP |
| **ECRMP017** | Rufnummer {0} ist nicht fuer diese Nutzungsart freigegeben. | pack_crm.sql:252 | Constant: FC_BI_NUTZUNG |
| **ECRMP018** | Rufnummer {0} hat Wiederbelegungssperre bis {1}. | pack_crm.sql:253 | Constant: FC_RFNR_SPERRE |
| **ECRMP019** | Ungueltiger Wert in Feld MVSt. | pack_crm.sql:254 | Constant: FC_MVST_FALSCH |
| **ECRMP020** | Zu dieser Anschlußart sind max. 10 MSN erlaubt. | pack_crm.sql:255 | Constant: FC_ANZ_MSN |
| **ECRMP021** | Falsche Stelligkeit der MSN (3 Rufnummer 10-stellig, 7 Rufnummern 11-stellig) | pack_crm.sql:256 | Constant: FC_MSN_10_11 |
| **ECRMP022** | Zu diesem Ortsnetz muessen die MSN 10-stellig zugeteilt werden. | pack_crm.sql:257 | Constant: FC_MSN_10 |
| **ECRMP023** | Zu diesem Ortsnetz muessen die MSN 11-stellig zugeteilt werden. | pack_crm.sql:258 | Constant: FC_MSN_11 |
| **ECRMP024** | Falsches Format der RufNr. Es konnte kein RNB ermittelt werden | pack_crm.sql:259 | Constant: FC_RNB_NV |
| **ECRMP025** | Die Rufnummer {0} ist fuer Buchung durch KONTES freigegeben | pack_crm.sql:260 | Constant: FC_BI_FREI_KONTES |
| **ECRMP026** | Die Rufnummer {0} liegt in einem fuer MASSUM reservierten Bereich | pack_crm.sql:261 | Constant: FC_BI_RES_MASSUM |
| **ECRMP027** | Ungültiger Wert in Feld NBL. | pack_crm.sql:262 | Constant: FC_NBL_FALSCH |
| **ECRMP028** | Ungültiger Wert in Feld ATM (Bandbreite) | pack_crm.sql:263 | Constant: FC_ATM_FALSCH |
| **ECRMP029** | RufNr_bis ist kleiner als RufNr_von | pack_crm.sql:264 | Constant: FC_BIS_KL_VON |
| **ECRMP030** | Wiederbelegungssperre darf nicht kleiner als Tagesdatum sein. | pack_crm.sql:265 | Constant: FC_WBL_FALSCH |
| **ECRMP031** | Es konnte kein Rufnummernbereich in der entsprechenden Größe ermittelt werden. | pack_crm.sql:266 | Constant: FC_RFNRB_NV |
| **ECRMP032** | Der Rufnummernbereich ist (teilweise) bereits belegt. | pack_crm.sql:267 | Constant: FC_RFNRB_BELEGT |
| **ECRMP033** | Der Rufnummernbereich ist (teilweise) gesperrt. | pack_crm.sql:268 | Constant: FC_RFNRB_SPERRE |
| **ECRMP034** | Der Rufnummernbereich ist Altbestand, d.h. Eigentümer ist BNetzA | pack_crm.sql:269 | Constant: FC_RFNRB_EIG_ALTBESTAND |
| **ECRMP035** | Der Rufnummernbereich ist nicht für Buchung freigegeben. | pack_crm.sql:270 | Constant: FC_RFNRB_BI_FREIGABE |
| **ECRMP036** | Der Rufnummernbereich ist nur für Buchung durch KONTES freigegeben. | pack_crm.sql:271 | Constant: FC_RFNRB_BI_KONTES |
| **ECRMP038** | Der Rufnummernbereich hat falschen Eigentümer | pack_crm.sql:273 | Constant: FC_RFNRB_EIG_FREMD |
| **ECRMP039** | Die TK-Anlage hat mehr als 1000 Nutzkanäle, d.h. Buchungsfall "Buchung TK-Anlage Methode 2" | pack_crm.sql:274 | Constant: FC_MAX_ANZ_EENR |
| **ECRMP040** | Die gewünschte Rufnummernanzahl ist größer als die max. Anzahl lt. Vergaberichtlinien. | pack_crm.sql:275 | Constant: FC_MAX_ANZ_RFNR |
| **ECRMP041** | Die angegebene Blocklänge entspricht nicht dem mitgelieferten Rufnummernbereich. | pack_crm.sql:276 | Constant: FC_RFNRB_NBL_ |
| **ECRMP042** | Die gelieferten Rufnummern gehoeren nicht zum gleichen Kontingent. | pack_crm.sql:277 | Constant: FC_KONTINGENT_FALSCH |
| **ECRMP043** | Zur Rufnummer liegt bereits eine Portierungsmeldung vor. | pack_crm.sql:278 | Constant: FC_PORT_KONTES |
| **ECRMP044** | Zur Rufnummer liegt eine Portierungsmeldung vor. | pack_crm.sql:279 | Constant: FC_PORT_WSST |
| **ECRMP045** | Die Blockgrenzen der Rufnummer stimmen nicht mit den RNVS-Daten überein. | pack_crm.sql:280 | Constant: FC_BLOCKGRENZEN_FALSCH |
| **ECRMP046** | Die Rufnummer {0} befindet sich im BNetzA-Kontingent (Altbestand) im Bereich der INDI-Rufnummern (ONKz+19xxx). | pack_crm.sql:281 | Constant: FC_INDI_NR |
| **ECRMP047** | Die Rufnummer {0} ist in RNVS nicht vorhanden. | pack_crm.sql:282 | Constant: FC_RFNR_NV |
| **ECRMP048** | Die Buchungsnr der Rufnr {0} stimmt nicht ueberein. | pack_crm.sql:283 | Constant: FC_FALSCHE_BUCHNR |
| **ECRMP049** | Die Stornierung kann nicht durchgefuehrt werden. Der urspruengliche Stand der Rufnr konnte nicht ermittelt werden. | pack_crm.sql:284 | Constant: FC_HISTORIE_NV |
| **ECRMP050** | Ungültiger Wert in Feld Besitzer. | pack_crm.sql:285 | Constant: FC_FALSCHE_REGID |
| **ECRMP051** | Das gelieferte Kontingent ist unvollstaendig. Folgende Rufnummern fehlen {0}. | pack_crm.sql:286 | Constant: FC_KONT_UNVOLLSTAENDIG |
| **ECRMP052** | Die Rufnr {0} kann nicht gebucht werden, da der Rufnummernbereich durch eine Rufnr mit anderen Grenzen belegt ist. | pack_crm.sql:287 | Constant: FC_RFNR_BEL_GRENZEN |
| **ECRMP053** | Eine freie Rufnummer mit Eigentümer DTAG kann nicht importiert werden. | pack_crm.sql:288 | Constant: FC_IMP_FREI_DTAG |
| **ECRMP054** | Zur Rufnr {0} liegt eine noch nicht abgeschlossene Buchungsmeldung vor. | pack_crm.sql:289 | Constant: FC_BKZ_VB_VU |
| **ECRMP055** | Die RufNr ist bereits bestätigt. | pack_crm.sql:290 | Constant: FC_BESTAET_VORH |
| **ECRMP056** | Die Rufnr {0} hat den Status 'frei'. | pack_crm.sql:291 | Constant: FC_STAT_FREI |
| **ECRMP057** | Der gelieferte Buchungsauftrag ist unvollstaendig | pack_crm.sql:292 | Constant: FC_BUCH_UNVOLLSTAENDIG |
| **ECRMP058** | Falsches Buchungskennzeichen zur Rufnummer. | pack_crm.sql:293 | Constant: FC_BKZ_FALSCH |
| **ECRMP059** | Anzahl Rufnr-Soll >= Anzahl Rufnr-Ist (bei Reduzierung). | pack_crm.sql:294 | Constant: FC_ANZ_RFNR_SOLL_FALSCH |
| **ECRMP060** | Die Buchungsnummer ist nicht eindeutig. | pack_crm.sql:295 | Constant: FC_BUCHNR_N_EINDEUTIG |
| **ECRMP061** | Die Rufnummer hat Besitzer DTAG | pack_crm.sql:296 | Constant: FC_BESITZER_TELEKOM |
| **ECRMP062** | Die zu reduzierende BlockRufNr ist nicht vorhanden bzw. nicht Teil der vorhandenen Rufnummer. | pack_crm.sql:297 | Constant: FC_RFNRB_SOLL_FALSCH |
| **ECRMP063** | RufNr_von und RufNr_bis haben unterschiedliche Länge. | pack_crm.sql:298 | Constant: FC_RFNRB_LAENGE_FALSCH |
| **ECRMP064** | RufNr_von ist größer als RufNr_bis. | pack_crm.sql:299 | Constant: FC_RFNRB_ENDE_FALSCH |
| **ECRMP065** | Der Buchungsauftrag ist nicht vorhanden. | pack_crm.sql:300 | Constant: FC_BUCHAUFTRAG_NV |
| **ECRMP066** | Der Buchungsauftrag enthält ein falsches Produkt | pack_crm.sql:301 | Constant: FC_FALSCHES_PRODUKT |
| **ECRMP067** | Der gewünschte Rufnummernbereich hat mehrere Eigentümer | pack_crm.sql:302 | Constant: FC_MEHRERE_EIG |
| **ECRMP068** | Eigentuemer der Rufnummer ist BNetzA. | pack_crm.sql:303 | Constant: FC_EIGENT_REGTP |
| **ECRMP069** | Zur Rufnummer gibt es eine unbestätigte Portierungsmeldung | pack_crm.sql:304 | Constant: FC_PORT_U |
| **ECRMP070** | Anzahl der Sammelanschlüsse wurde nicht angegeben. | pack_crm.sql:305 | Constant: FC_SAS_NV |
| **ECRMP071** | Es dürfen maximal 30 Sammelanschlüsse angegeben werden. | pack_crm.sql:306 | Constant: FC_MAX_SAS |
| **ECRMP072** | Die Anzahl Sammelanschlüsse ist nicht gleich der Anzahl der gewünschten Rufnummern. | pack_crm.sql:307 | Constant: FC_SAS_UNGLEICH_RFNR |
| **ECRMP073** | Rufnummern aus zwei verschieden Ortsnetzen können nicht gebucht werden. | pack_crm.sql:308 | Constant: FC_MANNH_LUDW |
| **ECRMP074** | Anzahl RufNr_soll darf nicht kleiner als die Anzahl der benannten Rufnummern sein. | pack_crm.sql:309 | Constant: FC_ANZ_SOLL_KL_RFNR |
| **ECRMP075** | max. Anzahl der Treffer: 100 | pack_crm.sql:310 | Constant: FC_MAX_TREFFER |
| **ECRMP076** | Der Buchungsfall ist unzulaessig | pack_crm.sql:312 | Constant: FC_BFALL_UNZULAESSIG |
| **ECRMP077** | Die Rufnr ist Teil eines Kontingents | pack_crm.sql:313 | Constant: FC_KONT_VORH |
| **ECRMP078** | Die Importmeldung zu dieser Rufnr ist bereits vorhanden | pack_crm.sql:314 | Constant: FC_BEREITS_IMPORT |
| **ECRMP079** | Die Exportmeldung zu dieser Rufnr ist bereits vorhanden | pack_crm.sql:315 | Constant: FC_BEREITS_EXPORT |
| **ECRMP080** | Die ausgewählte Rufnummer ist durch einen anderen Prozess gesperrt und kann nicht bearbeitet werden. | pack_crm.sql:316 | Constant: FC_RFNR_GESPERRT |
| **ECRMP081** | Importmeldung auf eine Z-Meldung des Wettbewerbers | pack_crm.sql:317 | Constant: FC_IMPORT_AUF_Z |
| **ECRMP083** | Bei zweistelliger ONKz werden keine sonderstelligen Rufnummern zugeteilt | pack_crm.sql:319 | Constant: FC_SONDERSTELLIG |
| **ECRMP086** | Ansprechpartner/ eMail-Adresse des Ansprechpartners fehlt | pack_crm.sql:322 | Constant: FC_ASP_FEHLT |
| **ECRMP087** | Die Rufnummernanzahl entspricht keiner ganzen Dekade | pack_crm.sql:323 | Constant: FC_NICHT_DEKADIG |
| **ECRMP088** | Es können maximal 10 Rufnummern beauftragt werden | pack_crm.sql:324 | Constant: FC_MAX_RUFNR |
| **ECRMP089** | Das Portierungsdatum muss <= Tagesdatum + 1 sein | pack_crm.sql:325 | Constant: FC_PORTDAT |
| **ECRMP090** | Der meldende ISP ist in RNVS nicht bekannt | pack_crm.sql:326 | Constant: FC_ISP_UNBEK |
| **ECRMP091** | Abweichendes Portierungsdatum und TNB an der Portierung beteiligt | pack_crm.sql:327 | Constant: FC_ABW_PORTDAT |
| **ECRMP092** | Buchungsnummer zu lang | pack_crm.sql:328 | Constant: FC_BUCHUNGSNR_ZU_LANG |
| **ECRMP093** | Stornierung nicht zulässig - Rufnummer wurde verändert | pack_crm.sql:329 | Constant: FC_STO_NICHT_ZULAESSIG |
| **ECRMP094** | Stornierung einer Portierung ist nicht möglich | pack_crm.sql:330 | Constant: FC_STO_PORT |
| **ECRMP095** | Aktueller Besitzer entspricht nicht dem anfragenden ISP | pack_crm.sql:331 | Constant: FC_BESITZER_ISP |
| **ECRMP096** | Im Moment läuft gerade eine Reaktivierung | pack_crm.sql:332 | Constant: FC_REAKT_LAEUFT |
| **ECRMP097** | Falscher Servicetyp | pack_crm.sql:333 | Constant: FC_FALSCHER_SERVTYPE |
| **ECRMP098** | Eine Blockrufnummer ist bei diesem Servicetyp nicht möglich | pack_crm.sql:334 | Constant: FC_RAM_RUFNR_BLOCK |
| **ECRMP099** | Die eingegebene Rufnummer ist zu kurz | pack_crm.sql:335 | Constant: FC_RFNR_ZU_KURZ |
| **ECRMP100** | Eine Reaktivierung durch diesen TNB ist unzulässig | pack_crm.sql:336 | Constant: FC_REAKT_UNZULAESSIG |
| **ECRMP101** | Reaktivierungsfrist der Rufnummer ist noch nicht abgelaufen | pack_crm.sql:337 | Constant: FC_U3 |
| **ECRMP102** | In diesem Rufnummernbereich sind mehrere Rufnummern vorhanden | pack_crm.sql:338 | Constant: FC_MEHR_RFNR |
| **ECRMP103** | Status der Rufnummer ist nicht eindeutig, bitte mit dem NM in Verbindung setzen | pack_crm.sql:339 | Constant: FC_MEHR_BI |
| **ECRMP104** | Die Rufnummer ist durch eine kürzere oder längere Rufnummer belegt | pack_crm.sql:340 | Constant: FC_RFNR_KURZ_LANG |
| **ECRMP105** | Timeout | pack_crm.sql:341 | Constant: FC_ABBRUCH |
| **ECRMP106** | Rufnummer ist bereits exportiert | pack_crm.sql:342 | Constant: FC_RFNRIMPORT |
| **ECRMP107** | Import auf eine DTAG-Rufnummer | pack_crm.sql:343 | Constant: FC_IMPORT_DTAGRFNR |
| **ECRMP108** | RfNr kann nicht gebucht werden; Altbestand | pack_crm.sql:344 | Constant: FC_SPERRE_ALTBESTAND |
| **ECRMP109** | RfNr kann nicht gebucht werden, falsche Laenge | pack_crm.sql:345 | Constant: FC_SPERRE_RFNRLAENGE |
| **ECRMP110** | Nicht genuegend freie Rechnungsnummern gefunden | pack_crm.sql:347 | Constant: FC_KEINE_FREIE_RECHNR |
| **ECRMP111** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP112** | DUWA-Grenzen stimmen nicht ueberein | pack_crm.sql:348 | Constant: FC_KONTINGENT_PROBL |
| **ECRMP113** | Die Buchung kann nur mit einem von der BNetzA genehmigten Antrag erfolgen | pack_crm.sql:349 | Constant: FC_SOLL_GR_MAX |
| **ECRMP114** | Die Buchung kann nur mit einem genehmigten Antrag auf Mehrbedarf erfolgen | pack_crm.sql:350 | Constant: FC_SOLL_GR_STD |
| **ECRMP115** | Keine Anzahl abhaengiger Anschluesse uebergeben - Buchung | pack_crm.sql:351 | Constant: FC_KEINE_ABH_ANSCHL |
| **ECRMP116** | Mischung von unbenannter und benannter Buchung | pack_crm.sql:352 | Constant: FC_MISCHUNG |
| **ECRMP117** | Der Rufnummern-Teil darf nicht mit einem Stern beginnen | pack_crm.sql:353 | Constant: FC_RUFNR_TEIL |
| **ECRMP118** | Keine Anzahl abhaengiger Anschluesse uebergeben - Recherche | pack_crm.sql:354 | Constant: FC_KEINE_ANZ_ABH_ANS |
| **ECRMP119** | Kein Bestand gefunden - Erweiterung nicht moeglich | pack_crm.sql:355 | Constant: FC_KEIN_BEST |
| **ECRMP120** | Kein freier Bereich gefunden - Erweiterung nicht moeglich | pack_crm.sql:356 | Constant: FC_KEIN_FREI |
| **ECRMP121** | Keine Kontingent-SID eingetragen | pack_crm.sql:357 | Constant: FC_KEINE_KONTSID |
| **ECRMP122** | Belegte EAS gefunden - Erweiterung nicht moeglich | pack_crm.sql:358 | Constant: FC_BELEGTE_EAS |
| **ECRMP123** | Gemeldeter Bereich unplausibel | pack_crm.sql:359 | Constant: FC_BEREICH_UNPLAUSIBEL |
| **ECRMP124** | Die angegebene Rufnummer ist unvollstaendig | pack_crm.sql:360 | Constant: FC_DUWA_UNVOLLSTAENDIG |
| **ECRMP125** | ONKZ der Rechnungsnummern sind unterschiedlich | pack_crm.sql:361 | Constant: FC_RECHNR_ONKZ_UNT |
| **ECRMP126** | Das Anlage-Erweiterungs-KZ darf bei unbenannter Buchung nicht gesetzt sein | pack_crm.sql:362 | Constant: FC_ANLERW_UNBENANNT |
| **ECRMP127** | Alle angegebenen EENr-Bereiche muessen die gleiche Stelligkeit haben | pack_crm.sql:363 | Constant: FC_EENR_STELLIGKEIT |
| **ECRMP128** | EENr-Bis muss goesser oder gleich EENr-Von sein | pack_crm.sql:364 | Constant: FC_EENR_VON_GR_BIS |
| **ECRMP129** | EENr-Bereiche duerfen nicht ueberlappend sein | pack_crm.sql:365 | Constant: FC_EENR_UEBERLAPPEND |
| **ECRMP130** | Kuendigung/Export einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | pack_crm.sql:367 | Constant: FC_ABSCHALTEVERF_K |
| **ECRMP131** | Kuendigung/Export einer Rufnummer - Sperre aufgrund einer Quarantaene | pack_crm.sql:368 | Constant: FC_QUARANTAENE_K |
| **ECRMP132** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Abschalteverfuegung | pack_crm.sql:369 | Constant: FC_ABSCHALTEVERF |
| **ECRMP133** | Buchung/Import einer Rufnummer - Sperre aufgrund einer Quarantaene | pack_crm.sql:370 | Constant: FC_QUARANTAENE |
| **ECRMP134** | Falsche Serviveart | pack_crm.sql:372 | Constant: FC_SERVICEART |
| **ECRMP135** | Die Serial-Nr. muss den Wert 00001 haben | pack_crm.sql:373 | Constant: FC_FALSCHE_SERIALNR |
| **ECRMP136** | Die Buchungsnr. muss gefuellt sein | pack_crm.sql:374 | Constant: FC_LEERE_BUCHNR |
| **ECRMP137** | Die Rufnummer muss gefuellt sein | pack_crm.sql:375 | Constant: FC_LEERE_RUFNR |
| **ECRMP138** | Das Ausführungs- datum muss gefuellt sein | pack_crm.sql:376 | Constant: FC_LEERES_AUSFDAT |
| **ECRMP139** | Der Produktsubtyp muss gefuellt sein | pack_crm.sql:377 | Constant: FC_LEERER_PRODTYP |
| **ECRMP140** | Der Technikkenner muss gefuellt sein | pack_crm.sql:378 | Constant: FC_LEERE_TECHNIK |
| **ECRMP141** | Eine Netzbuchungsinfo zur Rufnummer ist bereits vorhanden | pack_crm.sql:379 | Constant: FC_NI_VORH |
| **ECRMP142** | Das Vertriebssystem stimmt nicht ueberein | pack_crm.sql:380 | Constant: FC_FALSCHES_VERTRSYSTEM |
| **ECRMP143** | Falscher TNB | pack_crm.sql:381 | Constant: FC_FALSCHER_TNB |
| **ECRMP144** | Das Ausführungsdatum muss in der Zukunft liegen | pack_crm.sql:382 | Constant: FC_AUSFDAT |
| **ECRMP145** | Der TNB muss gefuellt sein | pack_crm.sql:383 | Constant: FC_LEERER_TNB |
| **ECRMP146** | Rufnummern mit unterschiedlicher Technik | pack_crm.sql:384 | Constant: FC_WECHSEL |
| **ECRMP147** | Netzbuchung - Kontingentfehler | pack_crm.sql:385 | Constant: FC_BNET_KONT |
| **ECRMP148** | Stornierung nicht moeglich, da zur RfNr ist keine Netzbuchungsinfo vorhanden ist | pack_crm.sql:386 | Constant: FC_NI_NICHT_VORH |
| **ECRMP149** | Stornierung nicht moeglich, da Buchungsnummer abweichend | pack_crm.sql:387 | Constant: FC_NI_ABW_BUCHNR |
| **ECRMP150** | Ungueltiger TNB | pack_crm.sql:388 | Constant: FC_TNB_UNGUELTIG |
| **ECRMP151** | Auftrag mit gleicher Buchungsnummer bereits vorhanden | pack_crm.sql:389 | Constant: FC_BUA_VORH |
| **ECRMP152** | Rufnummer ohne Bindestrich und Netzausscheidungsziffer liefern | pack_crm.sql:390 | Constant: FC_BINDESTRICH |
| **ECRMP153** | Es existiert bereits eine Netzbuchung | pack_crm.sql:393 | Constant: FC_NI_VORH_EX |
| **ECRMP154** | Das Portierungsziel darf nicht D001 oder 199C07 sein | pack_crm.sql:394 | Constant: FC_PORT_ZIEL_EX |
| **ECRMP155** | Der Besitzer der Rufnummer ist weder D001 noch 199C07 | pack_crm.sql:395 | Constant: FC_BESITZER_EX |
| **ECRMP156** | Die Rufnummer ist Bestandteil einer TK-Anlage | pack_crm.sql:396 | Constant: FC_TKANL_EX |
| **ECRMP157** | Zur Rufnummer exisitiert eine nicht erledigte Problemmeldung | pack_crm.sql:397 | Constant: FC_NICHT_ERL_PM |
| **ECRMP158** | BuchNetz EX bereits vorhanden und RNPS bereits informiert | pack_crm.sql:398 | Constant: FC_RNPS_INFORM |
| **ECRMP159** | Stornierung nicht mehr möglich, da RNPS bereits informiert wurde | pack_crm.sql:399 | Constant: FC_RNPS_INFORM_STO |
| **ECRMP160** | Übernahme nicht möglich da Rufnummer fehlt | pack_crm.sql:402 | Constant: FC_UFRM_RFNR_FEHLT |
| **ECRMP161** | Übernahme nicht in Verbindung mit Import möglich | pack_crm.sql:403 | Constant: FC_UFRM_IMPORT |
| **ECRMP162** | Übernahme nicht in Kombination mit noch nicht abgeschlossenen Aufträgen möglich | pack_crm.sql:404 | Constant: FC_UFRM_VORG |
| **ECRMP163** | Übernahme nicht möglich in Verbindung mit Erweiterung einer Anlage | pack_crm.sql:405 | Constant: FC_UFRM_ERWEITERUNG |
| **ECRMP164** | Auftrag nicht möglich, da eine Übernahme vorliegt | pack_crm.sql:406 | Constant: FC_UFRM_UEBERNAHME |
| **ECRMP165** | Übernahme nur bei schon belegten Rufnummern möglich | pack_crm.sql:407 | Constant: FC_UFRM_BELEGT |
| **ECRMP166** | Übernahme nicht möglich, da Kollision mit TIVU Portierungauftrag | pack_crm.sql:408 | Constant: FC_UFRM_TIVU |
| **ECRMP167** | Übernahme von Rechnungsnummern nicht zulässig | pack_crm.sql:409 | Constant: FC_UFRM_RECHNR |
| **ECRMP168** | Übernahme: Verarbeitung in RNVS nicht möglich | pack_crm.sql:410 | Constant: FC_UFRM_VERARB |
| **ECRMP169** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP170** | Verarbeitung nicht möglich da Nummer nur für Leitung (NG-Dummy) | pack_crm.sql:413 | Constant: FC_NGDUMMY_VERARB |
| **ECRMP171** | NG-Buchung: Verarbeitung nicht möglich | pack_crm.sql:414 | Constant: FC_BNG |
| **ECRMP172** | NGDummy nur für BLW gebuchte Rufummern zulässig | pack_crm.sql:415 | Constant: FC_NGDUMMY_BLW |
| **ECRMP173** | Rufnummer bereits in Verwendung | pack_crm.sql:416 | Constant: FC_NGDUMMY_VERW |
| **ECRMP174** | Sperre aufgrund von NGDummy | pack_crm.sql:417 | Constant: FC_NGDUMMY_SPERRE |
| **ECRMP175** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP176** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP177** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP178** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP179** | Fehlernummer noch nicht vergeben | unknown | Code definition not found in PL/SQL source |
| **ECRMP180** | Buchung/Import einer Rufnummer - Sperre aufgrund von Quali-Frei | pack_crm.sql:420 | Constant: FC_QUALI_FREI |
| **ECRMP181** | Kuendigung/Export einer Rufnummer - Sperre aufgrund von Quali-Frei | pack_crm.sql:421 | Constant: FC_QUALI_FREI_K |
| **ECRMP190** | Der Besitzer der Rufnummer ist keine IP-Netzportierungskennung | pack_crm.sql:424 | Constant: FC_BES_IP_NPK |
| **ECRMP200** | 'Rufnummer hat kein oder falsches Buchungskennzeichen | pack_crm.sql:427 | Constant: FC_FALSCHES_BUCHKZ |
| **ECRMP201** | Fehlende PreOrder Buchung bei UFRM-KONTES | pack_crm.sql:430 | Constant: FC_UFRMK_FEHL_BUCH |
| **ECRMP202** | 'Portierungskennung ungleich bei UFRM-KONTES | pack_crm.sql:431 | Constant: FC_UFRMK_PK_UNGL |
| **ECRMP203** | 'Unzulässiges BKZ bei UFRM-KONTES' | pack_crm.sql:432 | Constant: FC_UFRMK_UNZUL_BKZ |
| **ECRMP204** | 'CRM-Real. nach Storno bei UFRM-KONTES' | pack_crm.sql:433 | Constant: FC_UFRMK_REAL_STO |

---

## 2. ERESP CODES (CRM Portal Response Errors)

| Error Code | Business Reason | Code Reference RNVS | Description of Code Reference |
|------------|-----------------|---------------------|-------------------------------|
| **ERESP001** | Es konnte keine freie Rufnummer zu dieser Anschlussart ermittelt werden. | pack_crm.sql:443 | Constant: FC_MH_KEINE_FREIE_RFNR |
| **ERESP002** | Ungueltige ONKz. Angabe korrigieren und Buchung neu starten. | pack_crm.sql:444 | Constant: FC_MH_FALSCHES_ONKZ |
| **ERESP005** | Die Rufnummer {0} ist bereits belegt. Eine Buchung ist nicht moeglich. | pack_crm.sql:446 | Constant: FC_MH_RFNR_VORH |
| **ERESP011** | Die Rufnummer {0} hat falsche Laenge. | pack_crm.sql:447 | Constant: FC_MH_RFNR_LAENGE |
| **ERESP012** | Die Rufnummer {0} ist nicht zur Buchung freigegeben. | pack_crm.sql:448 | Constant: FC_MH_BI_FREIGABE |
| **ERESP014** | Die Rufnummer ist nicht an die Deutsche Telekom zugeteilt… | pack_crm.sql:449 | Constant: FC_MH_EIG_FREMD |
| **ERESP015** | Rufnr {0} ist Altbestand. Eine Buchung ist nur in durch die Bundesnetzagentur festgelegten Ausnahmen zulaessig.<br />Bei Fortsetzung der Buchung, sind Sie persoenlich fuer die Einhaltung der Vergaberegeln verantwortlich | pack_crm.sql:450 | Constant: FC_MH_EIG_ALTBESTAND |
| **ERESP016** | Rufnummer {0} ist exportiert - Besitzer ist {1}. Eine Bearbeitung ist nicht zulaessig! | pack_crm.sql:451 | Constant: FC_MH_RFNR_EXP |
| **ERESP017** | Rufnummer {0} ist nicht fuer diese Nutzungsart freigegeben. | pack_crm.sql:452 | Constant: FC_MH_BI_NUTZUNG |
| **ERESP018** | Rufnummer {0} hat Wiederbelegungssperre bis {1}. Wollen Sie die Buchung dennoch fortsetzen? | pack_crm.sql:453 | Constant: FC_MH_RFNR_SPERRE |
| **ERESP043** | Zu Rufnummer {0} liegt bereits eine Portierungsmeldung vor. Neuer Besitzer ist {1}. Eine Bearbeitung ist nicht moeglich. | pack_crm.sql:456 | Constant: FC_MH_PORT_KONTES |
| **ERESP047** | Die Rufnummer {0} ist in RNVS nicht vorhanden. Eine Bearbeitung ist nicht moeglich. | pack_crm.sql:457 | Constant: FC_MH_RFNR_NV |
| **ERESP050** | Ungueltiger Wert in Feld Besitzer. | pack_crm.sql:458 | Constant: FC_MH_FALSCHE_REGID |
| **ERESP052** | Die Rufnr {0} kann nicht gebucht werden, da der Rufnummernbereich durch eine Rufnr mit anderen Grenzen belegt ist. | pack_crm.sql:459 | Constant: FC_MH_RFNR_BEL_GRENZEN |
| **ERESP056** | Die Rufnr {0} hat den Status ''frei''. Eine Bearbeitung ist nicht moeglich | pack_crm.sql:460 | Constant: FC_MH_STAT_FREI |
| **ERESP058** | Falsches Buchungskennzeichen zur Rufnr {0} | pack_crm.sql:461 | Constant: FC_MH_BKZ_FALSCH |
| **ERESP069** | Zur Rufnummer {0} gibt es eine unbestaetigte Portierungsmeldung | pack_crm.sql:462 | Constant: FC_MH_PORT_U |
| **ERESP073** | Rufnummern koennen nicht aus unterschiedlichen ON gebucht werden.<br />Mannheim und Ludwigshafen sind zwei unterschiedliche ON. Angabe korrigieren und Buchung neu starten. | pack_crm.sql:463 | Constant: FC_MH_MANNH_LUDW |
| **ERESP089** | Das Portierungsdatum muss kleiner oder gleich Tagesdatum {0} | pack_crm.sql:466 | Constant: FC_MH_PORTDAT |
| **ERESP106** | Die Rufnummer {0} hat Besitzer {1} | pack_crm.sql:467 | Constant: FC_MH_RFNRIMPORT |
| **ERESP107** | Import auf eine DTAG-Rufnummer {0} | pack_crm.sql:468 | Constant: FC_MH_IMPORT_DTAGRFNR |
| **ERESP108** | Die Rufnummer {0} kann gemaess den Vorgaben der Bundesnetzagentur nicht mehr gebucht werden. | pack_crm.sql:469 | Constant: FC_MH_SPERRE_ALTBESTAND |
| **ERESP150** | Ungueltiger TNB | pack_crm.sql:495 | Constant: FC_MH_TNB_UNGUELTIG |
| **ERESP300** | Wenn das Ortsnetz 621 ist, muss das optionlae Feld ltcSubArea gefuellt sein. | pack_crm.sql:497 | Constant: FC_MH_ML_FEHLT |
| **ERESP303** | Das Aktivierungsdatum muss kleiner gleich dem Tagesdatum sein. | pack_crm.sql:500 | Constant: FC_MH_AKTDAT_TD |
| **ERESP304** | Das Aktivierungsdatum darf nicht aelter als 10 Jahre sein. | pack_crm.sql:501 | Constant: FC_MH_AKTDAT_ALT |
| **ERESP305** | Die Rufnummern gehoeren zu unterschiedlichen Ortsnetzen. | pack_crm.sql:502 | Constant: FC_MH_UNTERSCH_ON |
| **ERESP306** | Die Rufnummer hat weder das BSys: MH noch CSTAR | pack_crm.sql:503 | Constant: FC_MH_VERTRSYS |
| **ERESP307** | Die Rufnummer {0} ist belegt und das Buchungs-KZ ist leer oder bestätigt portiert bei DTAG | pack_crm.sql:504 | Constant: FC_MH_BEL_DTAG |
| **ERESP309** | Die Rufnummer {0} ist Teil einer Blockrufnummer | pack_crm.sql:505 | Constant: FC_MH_DUWA |
| **ERESP310** | Doppelmeldung: die Rufnummer {0} ist bereits realisiert | pack_crm.sql:506 | Constant: FC_MH_DOPP_REAL |
| **ERESP311** | Der Wert des Filter-Parameters muss 'allOwner' sein | pack_crm.sql:507 | Constant: FC_MH_FILTER |
| **ERESP312** | Der Eigentümer der Rufnummer {0} ist: BNetzA | pack_crm.sql:508 | Constant: FC_MH_BNETZA |
| **ERESP313** | Das Portierungsdatum liegt mehr als 10 Jahre in der Vergangenheit | pack_crm.sql:509 | Constant: FC_MH_PORTDAT_VG |
| **ERESP314** | Die Rufnummer {0} ist unbestaetigt portiert und hat einen Portierungslevel u3 | pack_crm.sql:510 | Constant: FC_MH_UPORT_U3 |
| **ERESP315** | Die Rufnummer {0} ist unbestaetigt portiert und der Portierungsbesitzer ist ungleich dem gemeldeten Portierungsbesitzer | pack_crm.sql:511 | Constant: FC_MH_UPORT |
| **ERESP316** | Die Rufnummer {0} ist bestaetigt portiert und der Portierungsbesitzer ist ungleich dem gemeldeten Portierungsbesitzer | pack_crm.sql:512 | Constant: FC_MH_BPORT |
| **ERESP317** | Die Rufnummer {0} ist bestaetigt portiert bei D999 (Abschalteverfuegung/Quarantaene/Quali Frei) | pack_crm.sql:513 | Constant: FC_MH_IMP_BNETZA |
| **ERESP318** | Doppelmeldung fuer Rufnummer: Es liegt bereits ein Importauftrag durch MH oder CONGSTAR vor | pack_crm.sql:514 | Constant: FC_MH_DOPP_IMP |
| **ERESP319** | Es liegt ein laufender Portierungsauftrag zur Rufnummer {0} | pack_crm.sql:515 | Constant: FC_MH_IMP |
| **ERESP320** | Die Rufnummern-Laenge inklusive ONKz des Import-Geschaeftsfalls bei Eigentümer Fremd < 10 | pack_crm.sql:516 | Constant: FC_MH_IMP_LAENGE |
| **ERESP321** | Die Rufnummer {0} ist mit anderer Laenge in der DB vorhanden und Besitzer <> Eigentuemer | pack_crm.sql:517 | Constant: FC_MH_IMP_EIG |
| **ERESP322** | Die Rufnummer {0} ist u3 portiert | pack_crm.sql:518 | Constant: FC_MH_REAK |

---

## Coverage Analysis

- **ECRMP Codes**: 183 total
  - Found in source: 176
  - Not in source: 7
- **ERESP Codes**: 43 total
  - Found in source: 43
  - Not in source: 0

**Primary Implementation Files**:
- pack_crm.sql - Constant definitions and business logic
- pack_body_crm.sql - CRM portal request processing
- Additional usage in various pack_body_*.sql files

---

*Document generated: 2025-11-27 09:54:38*
