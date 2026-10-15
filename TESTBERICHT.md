# Testbericht vom 13.10.2026

## Bestanden

- 6 Python-Tests: Beispieldatei einschließlich Firmenname mit senkrechtem Strich, mehrere Empfänger, fehlende Empfänger, CSV mit Anführungszeichen und Windows-1252, Native-Messaging-Protokoll, Pfadbegrenzung, Duplikatsperre, wiederholter Abschluss ohne doppelte Zeile, Sicherung der Fertig-Liste und abweichende CSV-Spaltenreihenfolge.
- 4 JavaScript-Tests mit nachgebildeter Thunderbird-Schnittstelle: vollständiger Entwurfsablauf in richtiger Reihenfolge, Speicherfehler ohne Fertig-Markierung, PDF-Fehler ohne Verfassen-Fenster und Fehler beim Abschlussprotokoll mit erhaltenem Entwurf.
- DOCX und ODT der gelieferten Bewerbung wurden mit dem installierten LibreOffice personalisiert und als PDF exportiert. Beide Ergebnisse haben 4 Seiten. Alle 8 gerenderten Seiten wurden visuell geprüft; Adresse, Anschreiben, Lebenslauf, Foto und Unterschrift sind erhalten. Es erfolgte keine redaktionelle Überarbeitung.
- Echte XLS-, XLSX- und ODS-Testdateien wurden mit LibreOffice erzeugt und wieder eingelesen. Firmenname, aufgeteilte Anschrift und beide E-Mail-Adressen stimmen überein.
- Der installierte Starter liefert korrekt gerahmte Native-Messaging-Antworten.
- Das XPI enthält das Manifest und alle benötigten Add-on-Dateien im Archivwurzelverzeichnis.
- Lokales Hilfsprogramm für das aktuelle Windows-Benutzerkonto registriert.

## Noch offen

Installation des XPI und vollständiger Praxistest in Thunderbird 157.0.1 mit einem konfigurierten Absenderkonto: echte Entwurfsspeicherung, PDF-Anhang, Fertig-Liste sowie Systemton und Ergebnisfenster zusammen prüfen. Der Zugriff auf die native Thunderbird-Oberfläche steht in dieser Sitzung nicht zur Verfügung. Es wurden deshalb keine echten Bewerbungsentwürfe erzeugt und keine E-Mails versandt.

Legacy-DOC wird vom Konverter unterstützt, wurde mangels DOC-Beispieldatei nicht separat geprüft.

Die ursprünglichen Daten unter `Data/` wurden in den Tests nicht verändert. Testausgaben liegen ausschließlich unter `tests/output/`; Ablauftests arbeiten mit Kopien.

## Update 1.1.0

- Absender werden unabhängig vom lokalen Hilfsprogramm geladen; eine leere Auswahl zeigt einen Einrichtungshinweis. Ein Knopf lädt Absender erneut.
- Insgesamt 10 Python-Tests und 7 JavaScript-Tests bestanden, einschließlich englischer Tabellenüberschriften, internationaler Anschriften, ausgewähltem Suchimport ohne Duplikate, Ablehnung von KI-Antworten ohne Webquellen und Sprachumschaltung.
- Die englischen Vorlagenplatzhalter wurden zusätzlich mit einer DOCX-Testkopie durch LibreOffice geprüft: Firmenname, Straße und Ort sind korrekt ersetzt; die PDF umfasst weiterhin 4 Seiten. Die deutschen DOCX-/ODT-Konvertierungen bestehen ebenfalls.
- Gemini-Zugang mit echter Modellabfrage erfolgreich geprüft. Kein Schlüsselwert wurde ausgegeben oder ins Add-on-Paket aufgenommen.
- Live-Suchtest: `gemini-2.5-flash` wurde mit HTTP 404 abgewiesen, obwohl es in der Modellliste auftaucht. Das aktuell dokumentierte und gelistete Standardmodell wurde deshalb auf `gemini-3.8-flash` geändert. Dessen Suchaufruf wurde mit HTTP 429 (Kontingent/Ratenlimit) abgewiesen. Keine erfolgreiche Live-Stellensuche; Google-Kontingent muss geprüft werden. Keine weiteren Suchaufrufe durchgeführt.
- Die Suchverarbeitung ist mit simulierten Antworten getestet. Thunderbird-Oberfläche und vollständiger Suchablauf nach Freischaltung des Kontingents bleiben offen.

## Update 1.2.0

- 18 Python-Tests und 8 JavaScript-Tests bestanden. Neu geprüft: Speichern beider Schlüssel ohne Verlust des jeweils anderen, leere Felder, keine Rückgabe gespeicherter Schlüssel, Leeren der Passwortfelder, Gemini-Anzeigenamen, Anbieter einzeln/gemeinsam, Teilergebnisse bei Fehlern, Zusammenführen von Kontakten, Erhalt verschiedener Firmen, Sicherung und wiederholbare Bereinigung der Markdown-Liste sowie OpenAI-Quellen und Fehlerklassifikation.
- Der neue OpenAI-Schlüssel wurde lokal gespeichert und durch eine Modellabfrage bestätigt; `gpt-5-mini` ist für den Schlüssel gelistet. Ablaufzeit wurde unverändert aus der bestätigten Auswahl übernommen (60 Tage).
- Beim ersten Einrichtungslauf ging die temporäre Entschlüsselungsdatei durch die Sandbox verloren. Ein Ersatzschlüssel mit denselben bestätigten Einstellungen wurde erstellt und erfolgreich gespeichert. Der ältere, nicht verwendete Schlüssel mit dem Namen Bewerbungskatapult bleibt in OpenAI Platform zur Löschung; diese Sitzung bietet kein Werkzeug zum Widerruf an. Lokale Entschlüsselungs-Zwischendateien wurden entfernt.
- Gemeinsamer Live-Suchtest mit `Gemini 2.5 Pro` und `gpt-5-mini`: Gemini HTTP 404, OpenAI HTTP 429. Keine Suchergebnisse wurden importiert. Provider-Konfiguration/Kontingente müssen vor einem erfolgreichen Live-Suchtest geprüft werden. Eine erfolgreiche Modellabfrage allein bestätigt keinen erfolgreichen Suchaufruf.
- Bestehende `Data/ApplicationList.MD`: acht Datensätze, keine Dubletten nach den dokumentierten Regeln. Daher keine Änderung an der Nutzerdatei.
- Native Hilfsdateien aktualisiert; Add-on-Version 1.2.0. Praxistest der neuen Oberfläche im echten Thunderbird bleibt offen.

## Erweiterung 1.3.0 – 13.10.2026

23 Python-Tests und 9 JavaScript-Tests bestanden. Neu geprüft: vier unabhängige
Anbieter, alte gespeicherte API-Auswahl, aktive Auswahl bei zugeklapptem Bereich,
CLI ohne API-Aufruf, Entfernung von API-Schlüsseln aus dem CLI-Prozessumfeld,
Ergebnisannahme nur nach abgeschlossener Websuche mit Quellen, Fehlerfälle und
anbieterübergreifendes Zusammenführen von Dubletten. Ältere Tests auf die
vorhandenen MD-Beispieldateinamen angepasst.

Echter Codex-Liveaufruf über ChatGPT-Anmeldung erfolgreich: öffentliche Suche
nach Arbeitgebern für Softwareentwicklung im Raum Essen, 8 Firmenzeilen und
14 Quellenlinks. Kein automatischer Import und keine Änderung der Firmenliste.
Quelleninhalte wurden nicht einzeln nachgeprüft. Gemini CLI ist auf diesem
Rechner noch nicht eingerichtet; Gemini-Streamingparser und gemeinsame
Verarbeitung wurden mit Testantworten geprüft. Thunderbird-Oberflächentest
bleibt offen. XPI 1.3.0 neu gebaut.

## Version 1.4.0 – 14.10.2026

26 Python-Tests und 9 JavaScript-Tests bestanden. Geprüft wurden insbesondere:
Antigravity-Streamingformat (event/step_update/result), Fehler bei verweigertem
Quellenabruf, unabhängige Modellparameter für beide Zusatzprogramme, Katalog-
Validierung, Hinzufügen und Entfernen von Modellen, Neuladen der Dropdowns sowie
Erhaltung der bestehenden Anbieterwahl und API-Anbindung.

Antigravity 1.3.4: Anmeldung und tatsächliche Modellliste über agy models geprüft.
Live-Stellensuche über Gemini 3.8 Flash High erfolgreich: zehn Firmenzeilen und
zehn Quellenlinks. Die ersten Versuche endeten ohne gültige Antwort, weil direkte
Seitenabrufe eine Freigabe verlangten. Der abschließende Test beschränkte sich
auf das erlaubte search_web-Werkzeug und lieferte ein gültiges Ergebnis.
Keine globalen Berechtigungen geändert, keine pauschale Freigabe verwendet.
Quellen und Kontaktdaten wurden nicht einzeln manuell verifiziert; keine
Suchergebnisse in ApplicationList.MD importiert. Thunderbird-Oberflächentest offen.

## 1.5.0 · 14.10.2026
Geprüft: Import veralteter Suchtreffer, erneuter Import ohne Änderungen, bestehende Empfänger bleiben erhalten, Fertig-Liste und gespeicherte/unklare Entwürfe sperren Import, ausgewählte Zieldatei, bearbeiteter Mailtext und Formatvalidierung, Mehrfachauswahl ohne unvollständige Firmen. Provider- und Entwurfsablauf-Regressionstests bestanden. Tests verwenden simulierte Anbieter; keine Live-Suche oder E-Mail-Versand. Fertig-Tabelle vor/nach Formatierung auf identische Firmeninhalte geprüft; XPI-Version und Flaggen geprüft.

## 1.6.0 · 15.10.2026
Firmenliste und Fertig-Liste ausschließlich JSON. 29 Python-Tests und 11 JavaScript-Tests bestanden: JSON-Lesen/Schreiben, Pflichtfelder, Ablehnung alter Formate, idempotente Entwurfsspeicherung, Sicherung, Importfilter, Dateiauswahl-Migration und bestehende UI-/Entwurfsprüfungen. Migration der lokalen Listen separat auf gleiche Anzahl und identische Namen, Anschriften, Empfänger sowie abgeleitete Adressfelder geprüft. Keine Live-Suche und kein E-Mail-Versand.
