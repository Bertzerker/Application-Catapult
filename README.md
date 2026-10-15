# Bewerbungskatapult

Thunderbird-Add-on für Windows: Firmenliste einlesen, eine Bewerbungsvorlage mit Firmenname und Anschrift personalisieren, mit LibreOffice als PDF exportieren und die dazugehörige E-Mail als Entwurf speichern.

## Einrichtung

1. LibreOffice und Thunderbird müssen installiert sein. Entwickelt für Thunderbird 157, Mindestversion 140. Die Einrichtung erwartet LibreOffice unter `C:\Program Files\LibreOffice\program`; ein anderer Pfad kann über den Parameter `-LibreOffice` angegeben werden.
2. `Installieren.ps1` mit PowerShell ausführen. Das registriert nur das lokale Hilfsprogramm für das aktuelle Windows-Benutzerkonto; Administratorrechte sind nicht nötig. Den Projektordner danach nicht verschieben, ohne die Einrichtung erneut auszuführen.
3. In Thunderbird **Add-ons und Themes → Zahnrad → Add-on aus Datei installieren** öffnen und `dist/Bewerbungskatapult.xpi` auswählen. Berechtigungen bestätigen.
4. Über die Schaltfläche **Bewerbungskatapult** in der Thunderbird-Werkzeugleiste das Add-on öffnen.

Falls Windows die Skriptausführung für diese lokale Datei blockiert, lässt sich die Einrichtung einmalig über `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Installieren.ps1` starten. Eine dauerhafte Änderung der Ausführungsrichtlinie ist nicht erforderlich.

## Bedienung

Den Datenordner laden und Firmenliste, Fertig-Liste, Bewerbungsvorlage, Mailtext sowie Absender auswählen. Die mitgelieferten Dateinamen werden vorausgewählt; ODT ist die bevorzugte Vorlage. **Vorschau prüfen** zeigt Empfänger und Ausschlussgründe. Anschließend **Entwürfe mit PDF erstellen** starten.

Pro Firma entsteht ein Entwurf mit allen erkannten E-Mail-Adressen im An-Feld und genau einer PDF. Währenddessen erscheinen kurz Verfassen-Fenster. Diese schließen sich nach erfolgreicher Speicherung. Thunderbird speichert im Entwurfsordner des gewählten Absenders; bei IMAP kann dieser auf dem Mailserver liegen. Das Add-on selbst hat keine Sendeberechtigung und verwendet keine externen Konvertierungsdienste.

Zum Abschluss ertönt der Windows-Systemton und ein Ergebnisfenster öffnet sich. Fehler und abgebrochene Läufe werden ebenfalls eindeutig im Ergebnis angezeigt. **Nach aktueller Firma stoppen** beendet den Lauf nach dem laufenden Arbeitsschritt; bereits gespeicherte Entwürfe bleiben bestehen.

## Dateiformate

- Firmenliste und „Bereits bearbeitet“: ausschließlich `.json`, UTF-8. Jede Datei enthält ein JSON-Array. Pro Firma sind `name` (Firmenname), `address` (Anschrift) und `emails` (Liste einzelner E-Mail-Adressen) erforderlich. Eine leere Liste ist `[]`.
- Nach bestätigter Entwurfsspeicherung wird die Firma zur Fertig-Liste hinzugefügt. Vor Änderungen entsteht eine `.bak`-Sicherung. „Fertig“ bedeutet **Entwurf gespeichert**, nicht versendet.
- Bewerbungsvorlage: DOC, DOCX oder ODT.
- Mailtext: TXT oder MD. Erste Zeile = Betreff, zweite Zeile leer, danach der Mailtext.

```json
[
  {
    "name": "Beispiel GmbH",
    "address": "Musterstraße 1, 12345 Musterstadt",
    "emails": ["bewerbung@example.org", "personal@example.org"]
  }
]
```

Fehlende E-Mail-Adressen werden als `[]`, fehlende Anschriften als `""` gespeichert; solche Firmen werden bei der Entwurfserstellung übersprungen. Das optionale Feld `emailText` bewahrt Hinweise aus konvertierten E-Mail-Spalten. Für Empfänger ist ausschließlich `emails` maßgeblich. Zusätzliche Felder bleiben beim Speichern erhalten.

Die vorhandenen `ApplicationList.MD` und `ApplicationFinished.MD` wurden nach `ApplicationList.json` und `ApplicationFinished.json` konvertiert. Die Originaldateien bleiben als Sicherung erhalten und werden nicht mehr als Firmenlisten eingelesen oder beschrieben. Nach dem Update die Add-on-Seite neu öffnen und den Ordner laden. Bisher gespeicherte Dateiauswahlen werden auf die gleichnamige JSON-Datei umgestellt; alte Vorschauen müssen neu erstellt werden.

## Platzhalter

Die gelieferten Vorlagen funktionieren unverändert: Die jeweils allein stehenden Absätze `Firmenname`, `Adresse,` und `Adresszusatz` werden ersetzt. `Personalabteilung` bleibt stehen. Die Anschrift wird bei `Straße, 12345 Ort` in Straße und PLZ/Ort aufgeteilt.

Für eigene Vorlagen stehen `{{Firmenname}}` oder `{{Name}}`, `{{Adresse}}`, `{{Adresszusatz}}`, `{{Email}}` oder `{{E-Mail}}` zur Verfügung. Firmenname und Adresse müssen als Platzhalter vorhanden sein, sonst stoppt die PDF-Erstellung. Andere Inhalte, insbesondere Datumsangaben, werden nicht redaktionell geändert; dynamische LibreOffice-Felder können sich beim Öffnen aktualisieren. Bei ungewöhnlichen oder ausländischen Adressformaten die PDF besonders prüfen.

## Ablage und Wiederaufnahme

Unter dem gewählten Datenordner entsteht `Bewerbungskatapult/`. Dort liegen PDFs, Vorschauaufträge und `journal.json`. Diese Dateien enthalten Bewerbungsdaten und bleiben lokal erhalten. Sie können nach Abschluss archiviert werden; das Journal dient zusätzlich zur Fertig-Liste als Duplikatschutz.

Vor dem Öffnen des Verfassen-Fensters wird die Firma als `pending` reserviert. Nach bestätigter Entwurfsspeicherung wird sie `saved`. Bei einem Absturz zwischen diesen Schritten wird die Firma beim nächsten Lauf gesperrt, damit nicht unbeabsichtigt ein zweiter Entwurf entsteht.

Bei „Unklarer früherer Vorgang“ zuerst den Thunderbird-Entwurfsordner prüfen. Ist ein vollständiger Entwurf vorhanden, die Firma manuell in die Fertig-Liste aufnehmen. Ist keiner vorhanden, bei beendetem Lauf nach einer Sicherung ausschließlich den betroffenen Firmeneintrag aus `journal.json` entfernen und die Vorschau neu laden. Fehlgeschlagene Verfassen-Fenster bleiben zur Prüfung geöffnet. Das gesamte Journal nicht pauschal löschen.

Wenn nach dem Speichern nur das Ergänzen der Fertig-Liste fehlschlägt, enthält das Journal weiterhin `saved`. Der Entwurf bleibt geschützt; die Fertig-Liste dann manuell ergänzen. Für einen bewusst erneuten Entwurf müssen sowohl Fertig-Liste als auch Journal passend bereinigt werden.

## Entwicklung und Tests

`Bauen.ps1` erzeugt das installierbare XPI aus `addon/`. Das Hilfsprogramm in `native/` nutzt die Python-Laufzeit von LibreOffice; zusätzliche Python-Pakete sind nicht nötig. LibreOffice läuft für die Verarbeitung unsichtbar mit einem separaten temporären Profil, deaktivierten Makros und ohne Aktualisierung externer Dokumentverknüpfungen.

Tests:

```powershell
& 'C:\Program Files\LibreOffice\program\python.exe' -m unittest discover -s tests -v
node --test tests/background.test.cjs
& 'C:\Program Files\LibreOffice\program\python.exe' tests/pdf_smoke.py
& 'C:\Program Files\LibreOffice\program\python.exe' tests/spreadsheet_smoke.py
```

Der PDF-Test liest die Beispieldateien und erzeugt ausschließlich Test-PDFs unter `tests/output/`. Der Entwurfsablauf wird mit nachgebildeten Thunderbird-Schnittstellen getestet. Ein vollständiger Durchlauf im echten Thunderbird-Konto muss nach Installation noch geprüft werden.

Prüfergebnisse und verbleibende Prüfschritte stehen in `TESTBERICHT.md`.

## Deutsch und Englisch

Version 1.1.0 enthält den Umschalter **Sprache / Language**. Die Auswahl wird gespeichert und gilt auch für das Ergebnisfenster. `addon/lang.js` enthält die gemeinsamen Übersetzungen. Die Umschaltung lädt die Oberfläche neu; laufende Entwurfsläufe bleiben im Hintergrund aktiv. Eine noch nicht gestartete Vorschau muss anschließend neu geladen werden.

Englische Tabellenüberschriften wie `Company Name`, `Address` / `Postal Address` und `Email` / `Email Address` werden akzeptiert. Für englische Vorlagen gibt es `{{Company}}`, `{{CompanyName}}`, `{{Address}}`, `{{AddressLine2}}`, `{{Email}}` sowie die alleinstehenden Absätze `Company name`, `Address,` und `Address line 2`. Bei nichtdeutschen Anschriften wird am ersten Komma beziehungsweise Zeilenumbruch getrennt. Texte und Dokumente werden nicht automatisch übersetzt.

## Stellensuche mit Gemini und OpenAI

Im Abschnitt **KI-Stellensuche** Ort, Umkreis (1–200 km), Beruf und Suchart eingeben. Standard ist die Suche nach aktuellen Stellen; Firmen für Initiativbewerbungen können gesondert gewählt werden. Das Modell ist konfigurierbar, voreingestellt ist `gemini-2.5-pro`. **Verbindung prüfen** testet den Schlüssel mit einer Modellabfrage.

Die Suche nutzt nach Auswahl Gemini mit Google Search, OpenAI mit Websuche oder beide gleichzeitig. Nur Suchkriterien und die gewünschte Erklärungssprache werden übermittelt; Bewerbungsvorlagen, Lebenslauf, bestehende Firmenlisten und E-Mail-Konten werden nicht hochgeladen. Für die gewählten APIs und Websuche können Kosten beim jeweiligen Anbieter anfallen. Die Entwurfserstellung selbst arbeitet weiter lokal.

Ergebnisse werden zusammen mit Quellen angezeigt. Stellenverfügbarkeit, ungefähren Umkreis und Kontaktdaten vor dem Import prüfen: KI-Recherche kann Fehler enthalten. Die gewünschten Firmen anhaken und **Ausgewählte Firmen anhängen** wählen. Erst dieser Schritt ergänzt `ApplicationList.json` im gewählten Datenordner; vorhandene Firmen werden anhand ihres Namens nicht erneut angehängt. Die Datei enthält ein JSON-Array mit `name`, `address` und `emails`. Vorhandene Zeilen bleiben erhalten; eine `.bak`-Sicherung wird angelegt. Anschließend wird diese Liste für die Entwurfsvorschau ausgewählt. Die Fertig-Liste wird weiterhin erst nach Entwurfsspeicherung ergänzt.

Die Rohantwort mit Quellen bleibt für die Nachprüfung unter `Bewerbungskatapult/search-<ID>.json` erhalten. Ohne Webquellen oder bei unvollständiger Antwort wird kein Import angeboten. Es werden keine E-Mail-Adressen automatisch ergänzt oder geraten; nur vom Modell gelieferte, ausgewählte Einträge mit Adresse und E-Mail sind importierbar.

Der Gemini-Schlüssel steht in der lokalen `.env.local` im Projektordner als `GEMINI_API_KEY`. Diese Datei ist von Git ausgeschlossen und wird nicht ins XPI aufgenommen. Den Schlüssel ausschließlich lokal ersetzen, nicht im Chat posten. Zum Weitergeben des Projekts `.env.local`, `Data/` und Testausgaben auslassen. OpenAI wird über die Responses API angebunden; eine MCP-Anbindung ist nicht erforderlich.

Quellen für die Integration: [Thunderbird Compose API](https://webextension-api.thunderbird.net/en/mv2/compose.html), [Mozilla Native Messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging) und [Gemini Google Search](https://ai.google.dev/gemini-api/docs/generate-content/google-search).


## Update 1.2.0

**API-Schlüssel verwalten** öffnet Passwortfelder für Gemini und OpenAI. Neue Schlüssel eingeben und **Schlüssel speichern** wählen. Leere Felder behalten den vorhandenen Schlüssel. Gespeicherte Schlüssel werden nicht in die Oberfläche zurückgeladen; diese zeigt nur vorhanden/fehlend. Die Eingaben werden nach erfolgreichem Speichern geleert. Die Schlüssel liegen lokal in der nicht versionierten `.env.local` (nicht verschlüsselt); sie werden weder im Thunderbird-Einstellungsspeicher noch in Suchprotokollen oder im XPI gespeichert. Den Projektordner einschließlich dieser Datei nicht unbereinigt weitergeben.

Die Kontrollkästchen **Gemini** und **ChatGPT / OpenAI** bestimmen, welcher Dienst gesucht wird. Beide dürfen aktiv sein. Es muss mindestens einer aktiv sein. Wenn nur ein Dienst scheitert, bleiben die Treffer des anderen erhalten und der Fehler wird zusätzlich angezeigt. Modellvorgaben sind `gemini-2.5-pro` und `gpt-5-mini`; die Verfügbarkeit richtet sich nach deinem API-Konto. Gemini akzeptiert auch `Gemini 2.5 Pro`, `2.5 Pro` und `models/gemini-2.5-pro`. Die OpenAI-Anbindung verwendet einen API-Schlüssel, nicht die ChatGPT-Webanmeldung.

Die Verbindungsprüfung liest nur die Modellliste. Eine erfolgreiche Prüfung bestätigt weder ausreichendes Suchkontingent noch den Zugriff auf jedes aufgeführte Modell. HTTP 404 stammt vom Anbieter (Modell/Endpunkt nicht verfügbar); HTTP 429 bedeutet ein Kontingent- oder Ratenlimit. Falls OpenAI einen konkreten Fehlercode liefert, unterscheidet die Oberfläche zwischen Guthaben/Ausgabenlimit und einem zeitweiligen Anfragelimit. Es gibt keine automatischen kostenpflichtigen Wiederholungen.

**Dubletten:** Der Abgleich erfolgt ausschließlich lokal, ohne weitere KI-Aufrufe. Namen werden ohne Groß-/Kleinschreibung, Leerzeichen und Satzzeichen verglichen. Abweichende Rechtsform-Endungen werden nur bei gleicher normalisierter Anschrift zusammengeführt. Verschiedene Namen mit einer gemeinsamen Adresse oder Sammel-E-Mail werden nicht pauschal als identisch betrachtet. Der erste Firmenname und die erste Anschrift bleiben erhalten; alle verschiedenen E-Mail-Adressen werden zusammengeführt. Unsichere Namensvarianten bleiben zur manuellen Prüfung getrennt.

Beim Anhängen ausgewählter Suchtreffer wird die vorhandene `ApplicationList.json` ebenfalls auf Dubletten geprüft. **Dubletten in ApplicationList.json bereinigen** führt diesen Schritt separat und ohne API-Aufruf aus. Vor Änderungen entsteht eine `.bak`-Sicherung. Die Liste wird bei einer Bereinigung als JSON gespeichert; es gehen keine zusammengeführten E-Mail-Adressen verloren. Bei einer separaten Prüfung ohne Dubletten bleibt die Datei unverändert.

OpenAI-Referenz: [Websuche mit der Responses API](https://developers.openai.com/api/docs/guides/tools-web-search).

## Suche über Kontoanmeldung (1.3.0)

Codex und Gemini können zusätzlich über ihre lokalen Zusatzprogramme verwendet werden.
Alle vier Verbindungen sind unabhängig auswählbar. Die API-Anbindung bleibt im
aufklappbaren Bereich erhalten. Einrichtung und Kontovoraussetzungen stehen in
[Zusatzprogramme.md](Zusatzprogramme.md). Die neue XPI aus `dist` in Thunderbird
über die Add-on-Verwaltung installieren. Der vorhandene native Helfer verwendet
die aktualisierten Dateien direkt.

## Antigravity und Modell-Dropdowns (1.4.0)

Die frühere Gemini-CLI-Kontoanbindung verwendet jetzt Antigravity (`agy`).
Jede der vier Verbindungen besitzt ein eigenes Modell-Dropdown. Modelle in
[models.json](models.json) ergänzen oder löschen und anschließend in Thunderbird
„Modelllisten neu laden“ wählen. Codex bietet zusätzlich „Programmstandard“ an.
Einrichtung und Dateiformat: [Zusatzprogramme.md](Zusatzprogramme.md).
Die neue XPI aus `dist` in Thunderbird installieren. Änderungen an models.json
benötigen anschließend keinen Neubau der Erweiterung.

## Version 1.5.0
- Suchtreffer werden vor Anzeige und erneut beim Import gegen Firmenliste, Fertig-Liste und Entwurfsjournal geprüft. Auch Application(s)List und Application(s)Finished werden berücksichtigt; vorhandene Einträge werden beim Import nicht überschrieben.
- Betreff und Mailtext können direkt auf der Seite bearbeitet werden (erste Zeile Betreff, Leerzeile, Text). Änderungen gelten für die Sitzung und werden nach erneuter Vorschau für die Entwürfe verwendet. Die Quelldatei bleibt erhalten.
- Vorschau, Entwurfsfortschritt und KI-Protokoll haben eigene Scrollbereiche. „Alle verfügbaren Firmen auswählen“ markiert vollständige Treffer.
- Sprachwahl mit den Flaggen aus Data/lang.
- Nach Installation der neuen dist/Bewerbungskatapult.xpi die geöffnete Add-on-Seite schließen und erneut öffnen.

## Version 1.5.1
Unter dem Mailtext-Editor speichert „Betreff und Anschreiben speichern“ den Text dauerhaft in die ausgewählte Maildatei. Die vorherige Version liegt daneben als .bak. Betreff, Leerzeile und Anschreiben werden geprüft. Zwischenzeitliche externe Änderungen werden nicht überschrieben; in diesem Fall zuerst den eigenen Text sichern und den Ordner neu laden. Ungespeicherte Änderungen werden angezeigt.

## Excel-Export (1.6.1)
Unter „Bereits bearbeitet“ erstellt **Als Excel exportieren** eine Excel-Datei (.xlsx) aus der ausgewählten JSON-Liste. Sie wird mit Zeitstempel und eindeutiger Kennung im Datenordner gespeichert; der vollständige Pfad erscheint nach Abschluss. Vorhandene Exporte und die JSON-Liste bleiben unverändert. Enthalten sind Firmenname, Adresse, E-Mail-Adressen und Hinweise aus emailText. Die Kopfzeile bleibt beim Scrollen sichtbar. LibreOffice wird wie bei der PDF-Erstellung verwendet; eine zusätzliche Installation ist nicht nötig. Die Datei dokumentiert den Listeninhalt, keinen nachträglich ermittelten Versandstatus.

## Version 1.6.2
Erfolgreich gespeicherte Firmen werden nach der Aufnahme in die Fertig-Liste aus der offenen JSON-Firmenliste entfernt. Die Vorschau blendet bestätigte Erfolge während des Laufs automatisch aus. Beim erneuten Prüfen der Vorschau werden auch ältere erledigte Einträge bereinigt. Als gespeichert protokollierte Firmen werden bei Bedarf zunächst in der Fertig-Liste nachgetragen. Unklare Vorgänge bleiben zur Prüfung erhalten. Vor Listenänderungen entsteht eine .bak-Sicherung.
