/* The batch runs in the background so closing the interface does not interrupt saving. */
let state = {running: false, log: [], completed: 0, total: 0};
let cancelled = false;
const host = async (request) => {
  const result = await browser.runtime.sendNativeMessage('de.bewerbungskatapult', request);
  if (!result.ok) throw new Error(result.error);
  return result;
};
async function runBatch(config, job, identityId) {
  state = {running: true, log: [], completed: 0, total: job.rows.filter(r => r.status === 'Bereit').length};
  cancelled = false;
  await browser.storage.local.set({lastRun: state});
  try {
    for (const row of job.rows.filter(r => r.status === 'Bereit')) {
      if (cancelled) break;
      state.current = row.name;
      const request = {folder: config.folder, token: job.token, key: row.key};
      let tab, saved = false;
      try {
        const pdf = await host({...request, action: 'generate'});
        const parts = [];
        for (let offset = 0; offset < pdf.size; offset += 384 * 1024) {
          const chunk = await host({...request, action: 'chunk', offset});
          const bytes = Uint8Array.from(atob(chunk.data), c => c.charCodeAt(0));
          if (bytes.length !== Math.min(384 * 1024, pdf.size - offset)) throw new Error('PDF unvollständig übertragen.');
          parts.push(bytes);
        }
        if (cancelled) break;
        await host({...request, action: 'reserve'});
        tab = await browser.compose.beginNew({identityId, to: row.emails,
          subject: job.subject, plainTextBody: job.body, isPlainText: true});
        await browser.compose.addAttachment(tab.id, {file: new File(parts, pdf.name, {type: 'application/pdf'})});
        const result = await browser.compose.saveMessage(tab.id, {mode: 'draft'});
        saved = true;
        state.completed++;
        const commit = await host({...request, action: 'commit', drafts: result.messages?.map(m => m.id) || []});
        state.log.push(row.name + ': Entwurf gespeichert.' + (commit.warning ? ' ' + commit.warning : ''));
        await browser.tabs.remove(tab.id);
      } catch (error) {
        state.log.push(row.name + ': ' + (saved ? 'Entwurf gespeichert, Nachbearbeitung fehlgeschlagen. ' : 'FEHLER: ') + error.message);
        state.log.push('Vorgang angehalten. Vor erneutem Start Entwürfe und journal.json prüfen.');
        break;
      }
      await browser.storage.local.set({lastRun: state});
    }
  } catch (error) {
    state.log.push('FEHLER: ' + error.message);
  } finally {
    state.running = false;
    state.current = '';
    state.cancelled = cancelled;
    await browser.storage.local.set({lastRun: state});
    await host({action: 'sound'}).catch(() => {});
    await browser.windows.create({url: browser.runtime.getURL('complete.html'), type: 'popup', width: 600, height: 430});
  }
}
browser.browserAction.onClicked.addListener(() => browser.tabs.create({url: browser.runtime.getURL('panel.html')}));
browser.runtime.onMessage.addListener(async message => {
  if (message.type === 'status') return state;
  if (message.type === 'cancel') {cancelled = true; return {};}
  if (message.type === 'native') return host(message.request);
  if (message.type === 'start') {
    if (state.running) throw new Error('Ein Vorgang läuft bereits.');
    if (!message.identityId) throw new Error('Bitte Absender auswählen.');
    // Re-read the stored preview through the host during each operation; no caller-provided paths are executed.
    void runBatch(message.config, message.job, message.identityId).catch(console.error);
    return {started: true};
  }
});
