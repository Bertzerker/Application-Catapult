/* Shared DE/EN strings. Applicant documents and company data are never translated. */
const Lang = (() => {
  let language = 'de';
  const en = {
    'Als Excel exportieren': 'Export to Excel',
    'Excel-Export läuft…': 'Exporting to Excel…',
    'Excel-Datei gespeichert:': 'Excel file saved:',
    'Excel-Export fehlgeschlagen.': 'Excel export failed.',
    'Bitte eine JSON-Firmenliste auswählen.': 'Please select a JSON company list.',
    'Firmenlisten müssen JSON-Dateien sein. Bitte die JSON-Datei auswählen und die Vorschau neu laden.': 'Company lists must be JSON files. Select the JSON file and reload the preview.',
    'Bitte JSON-Dateien auswählen und die Vorschau neu laden.': 'Select JSON files and reload the preview.',
    'Firmenliste: JSON-Array mit Firmen erforderlich.': 'Company list: a JSON array of companies is required.', 
    'Betreff und Anschreiben bearbeiten': 'Edit subject and email body',
    'Betreff und Anschreiben speichern': 'Save subject and email body',
    'Betreff und Anschreiben gespeichert.': 'Subject and email body saved.',
    'Ungespeicherte Änderungen.': 'Unsaved changes.',
    'Die Maildatei wurde inzwischen geändert. Bitte den Ordner neu laden.': 'The email file has changed. Please reload the folder.',
    'Erste Zeile: Betreff. Danach eine Leerzeile und das Anschreiben. Speichern übernimmt den Text dauerhaft in die ausgewählte Maildatei.': 'First line: subject. Then a blank line and the email body. Save writes the text permanently to the selected email file.',
    'bereits bearbeitete Firmen ausgeblendet.': 'previously processed companies hidden.',
    'Antigravity (Google-Konto)': 'Antigravity (Google account)', 'Antigravity (Konto)': 'Antigravity (account)',
    'Antigravity prüfen': 'Check Antigravity', 'Codex-Modell': 'Codex model', 'Antigravity-Modell': 'Antigravity model',
    'Modelllisten neu laden': 'Reload model lists', 'Modelllisten geladen.': 'Model lists loaded.',
    'Modelle in models.json im Projektordner hinzufügen oder löschen.': 'Add or remove models in models.json in the project folder.',
    'Programmstandard': 'Program default', 'Bitte zuerst Modelllisten laden.': 'Load model lists first.',

    'Zusatzprogramme · Kontoanmeldung': 'Companion programs · Account sign-in',
    'Einmal im Zusatzprogramm anmelden. Es gelten die Grenzen deines Kontos.': 'Sign in once in the companion program. Your account limits apply.',
    'Gemini (Google-Konto)': 'Gemini (Google account)', 'Gemini (Konto)': 'Gemini (account)',
    'Gemini-Modell im Zusatzprogramm': 'Gemini model in companion program',
    'Codex-Zusatzprogramm prüfen': 'Check Codex companion', 'Gemini-Zusatzprogramm prüfen': 'Check Gemini companion',
    'Einrichtung: siehe Zusatzprogramme.md im Projektordner.': 'Setup: see Zusatzprogramme.md in the project folder.',
    'API-Anbindung · Anbieter und Schlüssel': 'API connection · Providers and keys',
    'Zugeklappte Anbieter bleiben aktiv, wenn sie ausgewählt sind. API-Kosten können anfallen.': 'Selected providers remain active when collapsed. API charges may apply.',
    'Aktive Verbindungen: ': 'Active connections: ',
    'Zusatzprogramm bereit. Eine Live-Suche wurde noch nicht geprüft.': 'Companion ready. Live search has not been tested yet.',

    'API-Schlüssel verwalten': 'Manage API keys', 'Schlüssel speichern': 'Save keys',
    'Schlüssel werden nur lokal gespeichert. Leere Felder behalten vorhandene Schlüssel bei.': 'Keys are saved locally only. Leave a field empty to keep its existing key.',
    'Schlüssel vorhanden': 'Key configured', 'Kein Schlüssel': 'No key configured',
    'OpenAI-Modell': 'OpenAI model', 'Gemini prüfen': 'Check Gemini', 'OpenAI prüfen': 'Check OpenAI',
    'OpenAI-Verbindung funktioniert.': 'OpenAI connection successful.',
    'Mindestens eine KI auswählen.': 'Select at least one AI provider.',
    'Dubletten in ApplicationList.json bereinigen': 'Remove duplicates from ApplicationList.json',
    'Dubletten zusammengeführt.': 'duplicates merged.', 'Dubletten entfernt.': 'duplicates removed.',
    'Die Suche übermittelt Ort, Umkreis und Beruf an die ausgewählten Anbieter. API- und Suchkosten können anfallen. Prüfe die Ergebnisse anhand der Quellen.': 'Search sends location, radius and role to the selected providers. API and search charges may apply. Check results against their sources.',
    'Aus deiner Firmenliste werden persönliche Bewerbungs-PDFs und E-Mail-Entwürfe.': 'Turn your company list into personalized application PDFs and email drafts.',
    '1 · Dateien auswählen': '1 · Select files', 'Datenordner': 'Data folder', 'Ordner laden': 'Load folder',
    'Firmenliste': 'Company list', 'Bereits bearbeitet': 'Already processed', 'Bewerbungsvorlage': 'Application template',
    'Betreff und Mailtext': 'Subject and email body', 'Absender': 'Sender', 'Absender neu laden': 'Reload senders',
    'Vorschau prüfen': 'Review preview', '2 · Vorschau': '2 · Preview', 'Bitte zuerst die Dateien auswählen.': 'Please select your files first.',
    'Firma': 'Company', 'Adresse': 'Address', 'Empfänger': 'Recipients', 'Status': 'Status',
    'Entwürfe mit PDF erstellen': 'Create drafts with PDF', 'Nach aktueller Firma stoppen': 'Stop after current company',
    'Es werden ausschließlich Entwürfe gespeichert. Bei einem unklaren Abbruch wird die betroffene Firma bis zur Prüfung gesperrt.': 'Only drafts are saved. After an uncertain interruption, the affected company is blocked until reviewed.',
    '3 · Fortschritt': '3 · Progress', 'Noch nicht gestartet.': 'Not started yet.',
    'Absender werden aus deinen Thunderbird-Konten geladen.': 'Senders are loaded from your Thunderbird accounts.',
    'Absender werden geladen…': 'Loading senders…', 'Kein E-Mail-Absender eingerichtet': 'No email sender configured',
    'Diese Absender stammen aus deinen Thunderbird-Konten. Weitere Adressen richtest du in den Konten-Einstellungen ein.': 'These senders come from your Thunderbird accounts. Add further addresses in Account Settings.',
    'Bitte zuerst dein E-Mail-Konto in Thunderbird einrichten (Konten-Einstellungen → Konten-Aktionen → E-Mail-Konto hinzufügen). Danach hier „Absender neu laden“ wählen.': 'First add your email account in Thunderbird (Account Settings → Account Actions → Add Mail Account). Then choose Reload senders here.',
    'Absender konnten nicht geladen werden': 'Could not load senders', 'Thunderbird-Konten konnten nicht gelesen werden: ': 'Could not read Thunderbird accounts: ',
    'Firmen bereit': 'companies ready', 'werden übersprungen': 'will be skipped', 'Entwürfe gespeichert': 'drafts saved',
    'Startet…': 'Starting…', 'Gestoppt': 'Stopped', 'Entwürfe fertig': 'Drafts ready', 'Vorgang beendet': 'Batch finished',
    'von': 'of', 'Entwürfen wurden gespeichert. Bitte vor dem Versenden prüfen.': 'drafts were saved. Please review before sending.',
    'Betreff und Anschreiben bearbeiten': 'Edit subject and email body',
    'Erste Zeile: Betreff. Danach eine Leerzeile und das Anschreiben. Änderungen gelten für diese Sitzung; die Quelldatei bleibt erhalten.': 'First line: subject. Then a blank line and the email body. Edits apply to this session; the source file is preserved.',
    'Alle verfügbaren Firmen auswählen': 'Select all available companies',
    'KI-Protokoll und Quellen': 'AI log and sources',
    'vorhandene oder bearbeitete Firmen ausgeblendet.': 'existing or processed companies hidden.',
    'Schließen': 'Close', 'Bereits gespeichert': 'Already saved', 'Unklarer früherer Vorgang – Entwürfe prüfen': 'Uncertain earlier batch – check drafts',
    'Doppelte Firma': 'Duplicate company', 'Keine E-Mail-Adresse': 'No email address', 'Adresse fehlt': 'Address missing', 'Bereit': 'Ready',
    'Entwurf gespeichert.': 'Draft saved.', 'Entwurf gespeichert, Nachbearbeitung fehlgeschlagen. ': 'Draft saved, post-processing failed. ',
    'FEHLER: ': 'ERROR: ', 'Vorgang angehalten. Vor erneutem Start Entwürfe und journal.json prüfen.': 'Batch stopped. Check drafts and journal.json before restarting.',
    'KI-Stellensuche': 'AI job search', 'Ort': 'Location', 'Umkreis (km)': 'Radius (km)', 'Beruf / Stelle': 'Job / role',
    'Gemini-Modell': 'Gemini model', 'Suchart': 'Search type', 'Aktuelle Stellenangebote': 'Current vacancies',
    'Firmen für Initiativbewerbungen': 'Companies for speculative applications', 'Verbindung prüfen': 'Check connection',
    'Stellen suchen': 'Search jobs', 'Ausgewählte Firmen anhängen': 'Append selected companies',
    'Die Suche übermittelt Ort, Umkreis und Beruf an Google Gemini. API- und Suchkosten können anfallen. Prüfe Stellen, Anschriften und E-Mail-Adressen anhand der Quellen vor dem Import.': 'Search sends location, radius and role to Google Gemini. API and search charges may apply. Check vacancies, addresses and emails against the sources before importing.',
    'Auswählen': 'Select', 'Quellen': 'Sources', 'Suche läuft…': 'Searching…', 'Gemini-Verbindung funktioniert.': 'Gemini connection successful.',
    'Firmen gefunden. Bitte Quellen prüfen und Firmen auswählen.': 'companies found. Review sources and select companies.',
    'Firmen angehängt.': 'companies appended.', 'Keine Treffer ausgewählt.': 'No results selected.',
    'PDF unvollständig übertragen.': 'Incomplete PDF transfer.', 'Ein Vorgang läuft bereits.': 'A batch is already running.',
    'Bitte Absender auswählen.': 'Please select a sender.',
    'Spalten benötigt: Firmenname, Adresse, E-Mail.': 'Required columns: Company Name, Address, Email.',
    'Unvollständige Tabellenzeile ': 'Incomplete table row ', 'Firmenname fehlt in Zeile ': 'Company name missing in row ',
    'Ungültige Dateiauswahl: ': 'Invalid file selection: ', 'Datenordner nicht gefunden.': 'Data folder not found.',
    'Ein anderer Vorgang arbeitet gerade in diesem Ordner.': 'Another process is using this folder.',
    'Maildatei: Betreff, Leerzeile, danach Anschreiben erforderlich.': 'Email file: subject, blank line, then email body required.',
    'Ungültiger Auftrag.': 'Invalid request.', 'Firma wurde inzwischen bearbeitet oder muss geprüft werden.': 'Company has already been processed or requires review.',
    'Vorlage wurde verändert. Bitte Vorschau neu laden.': 'Template changed. Please reload the preview.',
    'PDF-Erstellung fehlgeschlagen.': 'PDF creation failed.', 'Ungültiger Dateiabschnitt.': 'Invalid file chunk.',
    'Firma wurde inzwischen bearbeitet.': 'Company has already been processed.', 'Reservierung fehlt.': 'Reservation missing.',
    'LibreOffice konnte nicht gestartet werden.': 'Could not start LibreOffice.',
    'Zeitüberschreitung beim Start von LibreOffice.': 'LibreOffice startup timed out.',
    'Dokument konnte nicht geöffnet werden.': 'Could not open document.',
    'Kein Firmenname-Platzhalter in der Vorlage gefunden.': 'No company name placeholder found in template.',
    'Kein Adress-Platzhalter in der Vorlage gefunden.': 'No address placeholder found in template.'
  };
  function t(value) {return language === 'en' ? (en[value] || value) : value;}
  function log(value) {
    if (language !== 'en') return value;
    for (const [de, english] of Object.entries(en).sort((a,b) => b[0].length-a[0].length)) {
      if (de.length > 12) value = value.split(de).join(english);
    }
    return value;
  }
  async function init() {
    language = (await browser.storage.local.get('language')).language === 'en' ? 'en' : 'de';
    document.documentElement.lang = language;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      if (node.parentElement.closest('script, pre')) continue;
      const text = node.textContent.trim();
      if (en[text]) node.textContent = node.textContent.replace(text, t(text));
    }
    const toggle = document.getElementById('language');
    if (toggle) {
      toggle.value = language;
      for (const [id, value] of [['langDe', 'de'], ['langEn', 'en']]) {
        const button = document.getElementById(id);
        if (!button) continue;
        button.setAttribute('aria-pressed', String(language === value));
        button.onclick = async () => {if (toggle.disabled) return; await browser.storage.local.set({language: value}); location.reload();};
      }
      toggle.onchange = async () => {await browser.storage.local.set({language: toggle.value}); location.reload();};
    }
  }
  return {t, log, init, get language() {return language;}};
})();
