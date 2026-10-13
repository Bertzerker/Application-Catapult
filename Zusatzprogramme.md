# Zusatzprogramme und Modelle (Version 1.4.0)

Codex (ChatGPT), Antigravity (Google-Konto), Gemini API und OpenAI API können
unabhängig ausgewählt und kombiniert werden. Alle vier Verbindungen haben ein
eigenes Modell-Dropdown. Der API-Bereich bleibt auf- und zuklappbar; eine
angekreuzte API-Verbindung bleibt auch zugeklappt aktiv.

## Anmeldung

Codex: `codex login` mit ChatGPT. Antigravity: `agy` starten und mit Google
anmelden. Beide Programme werden automatisch gesucht, Antigravity auch unter
`%LOCALAPPDATA%/agy/bin/agy.exe`. Die frühere Gemini CLI wird nicht mehr verwendet.
Die installierte Antigravity-Version muss den Headless-Modus mit Streaming-JSON
unterstützen (hier 1.3.4). Der Prüfknopf für Antigravity ruft die Modellliste ab;
er prüft damit Anmeldung und Erreichbarkeit, führt aber keine Stellensuche aus.

## Modelle bearbeiten

Die Datei **models.json** im Projektordner enthält vier Listen:

- `codex`: Codex mit ChatGPT-Anmeldung; `""` bedeutet Programmstandard.
- `antigravity`: Modelle für Antigravity mit Google-Anmeldung.
- `gemini`: Modelle der Gemini API.
- `openai`: Modelle der OpenAI API.

Zum Ergänzen einen Modellnamen in Anführungszeichen in die entsprechende Liste
setzen, durch Komma von den anderen Einträgen getrennt. Zum Entfernen den
Eintrag samt überflüssigem Komma löschen. Jede Liste muss mindestens einen
Eintrag enthalten. Beispiel: `["gemini-3.8-flash-high", "gemini-3.8-flash-medium"]`.
Anschließend speichern und in Thunderbird **Modelllisten neu laden** wählen.
Ein Neubau oder eine Neuinstallation der Erweiterung ist dafür nicht nötig.
Die vorhandene Auswahl bleibt erhalten, solange sie noch in der Liste steht;
sonst wird der erste Eintrag ausgewählt. Fehlerhafte Dateien werden gemeldet.

Antigravity-Namen wurden am 14.10.2026 mit `agy models` für dieses Konto ausgelesen.
Der Katalog ist eine bearbeitbare Momentaufnahme, keine Garantie für Kontingent,
Modellfreigabe oder Websuchunterstützung. Die API-Listen sind eine Vorauswahl;
insbesondere wurde der ausdrücklich gewünschte Eintrag `gemini-2.5-pro` erhalten.
Antigravity-Modellnamen sind nicht automatisch gültige Gemini-API-Modellnamen.

## Ergebnisse

Nur die ausgewählten Verbindungen werden aufgerufen. Zusatzprogramme erhalten
keine gespeicherten API-Schlüssel; es gibt keinen automatischen API-Ersatz bei
Fehlern. Kontogrenzen gelten weiterhin. Eine Suche läuft in einem eigenen
Arbeitsordner; Bewerbungsdateien werden nicht als Suchkontext übergeben.
Ergebnisse benötigen eine abgeschlossene Websuche mit Quellen. Nach Prüfung
können Firmen wie bisher ausgewählt und ohne Dubletten angehängt werden.

Dokumentation: https://antigravity.google/docs/cli/headless/

Die Antigravity-Suche verwendet `search_web`. Direkte Webseitenabrufe benötigen
in Antigravity zusätzliche Freigaben und werden nicht angefordert. Firmen, deren
Kontaktdaten nicht ausreichend durch Suchergebnisse belegt sind, sollen ausgelassen
werden. Die Anwendung ändert keine globalen Antigravity-Berechtigungen und verwendet
keinen Schalter zum pauschalen Überspringen von Freigaben.
