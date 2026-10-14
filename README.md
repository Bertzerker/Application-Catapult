# Application Catapult

Thunderbird-Erweiterung für Windows: Firmenlisten lesen, Bewerbungen mit LibreOffice
personalisieren, als PDF exportieren und E-Mails als **Entwürfe** speichern.
Deutsch/Englisch, Dublettenprüfung und optionale KI-Firmensuche über Codex,
Antigravity, Gemini API oder OpenAI API. Version 1.5.1.

## Einrichtung

1. Thunderbird (mindestens 140) und LibreOffice mit Python installieren.
2. `Installieren.ps1` ausführen. Es registriert den lokalen Helfer für das aktuelle
   Windows-Konto. Der LibreOffice-Pfad lässt sich mit `-LibreOffice` ändern.
3. `dist/Bewerbungskatapult.xpi` in Thunderbird über Add-ons und Themes → Zahnrad →
   Add-on aus Datei installieren auswählen. Bei Bedarf mit `Bauen.ps1` neu bauen.
4. Einen eigenen Datenordner wählen. Persönliche Bewerbungsdateien sind nicht enthalten.

## Eingabedateien

- Firmenliste: Markdown, TXT, CSV, XLS, XLSX oder ODS. Spalten: Firmenname, Adresse, E-Mail.
- Fertig-Liste: dieselben Spalten, Markdown oder CSV empfohlen. Bereits bearbeitete Firmen werden übersprungen.
- Vorlage: DOC, DOCX oder ODT mit `{{Firmenname}}`, `{{Adresse}}` und optional `{{Adresszusatz}}`.
- Mailtext: erste Zeile Betreff, danach Leerzeile und Anschreiben.

Mehrere Empfänger können durch Semikolon getrennt sein. Vor dem Erstellen Vorschau
prüfen. Es werden ausschließlich Entwürfe gespeichert; die Erweiterung hat keine
Sendeberechtigung. Nach dem Speichern wird die Fertig-Liste mit Sicherung ergänzt.
Bei einem unklaren Abbruch schützt das lokale Journal vor doppelten Entwürfen.

## KI-Suche und Modelle

Jede Verbindung ist einzeln auswählbar und besitzt ein eigenes Modell-Dropdown.
Die API-Einstellungen sind aufklappbar. Schlüssel optional in der Oberfläche lokal
speichern oder `.env.example` nach `.env.local` kopieren und dort ergänzen.
Diese Schlüsseldatei wird ignoriert und darf nicht hochgeladen werden.
Kontoanmeldung, Modelllisten und Voraussetzungen: [Zusatzprogramme.md](Zusatzprogramme.md).
Die Datei [models.json](models.json) kann manuell ergänzt oder gekürzt werden;
anschließend in Thunderbird „Modelllisten neu laden“ klicken.
API-Kosten und Kontolimits hängen vom Anbieter ab. Ergebnisse und Quellen vor dem
Import prüfen. Die Modellliste ist eine Momentaufnahme, keine Zugriffsgewähr.

## Tests

```powershell
& 'C:\Program Files\LibreOffice\program\python.exe' -m unittest discover -s tests -v
node --test tests/*.test.cjs
```

Die automatisierten Tests verwenden erfundene Daten. Ein Thunderbird-Praxistest und
Tests mit eigenen Dokumentvorlagen sind weiterhin erforderlich. Der optionale
Tabellen-Konvertierungstest ist `tests/spreadsheet_smoke.py`.

## Datenschutz dieser Kopie

Diese Kopie enthält keine persönlichen Bewerbungen, Firmen-/Empfängerlisten,
API-Schlüssel, Passwörter, Anmeldesitzungen, Logs oder lokal erzeugten PDFs.
Das XPI wird ausschließlich aus dem geprüften Ordner `addon` neu gebaut.
Die Erweiterungs-ID dieser Kopie ist eigenständig, damit lokale Installationen
nicht unbeabsichtigt überschrieben werden.

## Neu in 1.5.1

- Suchtreffer werden bei Anzeige und Import gegen bestehende Firmenlisten, Fertig-Listen und das Entwurfsjournal geprüft. Auch veraltete Suchergebnisse können diese Sperre nicht umgehen.
- Betreff und Anschreiben direkt bearbeiten und dauerhaft in die ausgewählte Maildatei speichern. Die vorherige Fassung wird als .bak gesichert; zwischenzeitliche externe Änderungen werden erkannt.
- Eigene Scrollbereiche für Vorschau, Entwurfsfortschritt und KI-Protokoll.
- Alle vollständigen Treffer gemeinsam auswählen; Sprachwahl mit Flaggen.

Nach dem Aktualisieren die Add-on-Seite schließen und neu öffnen.
