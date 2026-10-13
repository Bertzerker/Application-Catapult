const t = value => Lang.t(value);
const $ = id => document.getElementById(id);
const send = message => browser.runtime.sendMessage(message);
const native = request => send({type: 'native', request});
let job = null, running = false;
const config = () => Object.fromEntries(['folder', 'list', 'finished', 'template', 'mail'].map(id => [id, $(id).value]));
const guard = fn => async () => { $('error').textContent = ''; try {await fn();} catch(e) {$('error').textContent = Lang.log(e.message);} };
function invalidate() {job = null; $('start').disabled = true;}
function updateStart() {
  $('start').disabled = running || !job?.rows.some(r => r.status === 'Bereit') || !$('identity').value;
}
async function loadIdentities() {
  const previous = $('identity').value;
  $('identity').replaceChildren(new Option(t('Absender werden geladen…'), ''));
  try {
    const accounts = await browser.accounts.list(false);
    const options = [];
    for (const account of accounts) for (const identity of account.identities || []) {
      if (identity.email?.trim()) options.push(new Option(`${identity.name || account.name} <${identity.email}>`, identity.id));
    }
    $('identity').replaceChildren(...(options.length ? options : [new Option(t('Kein E-Mail-Absender eingerichtet'), '')]));
    if (options.some(o => o.value === previous)) $('identity').value = previous;
    $('identityHint').textContent = options.length
      ? t('Diese Absender stammen aus deinen Thunderbird-Konten. Weitere Adressen richtest du in den Konten-Einstellungen ein.')
      : t('Bitte zuerst dein E-Mail-Konto in Thunderbird einrichten (Konten-Einstellungen → Konten-Aktionen → E-Mail-Konto hinzufügen). Danach hier „Absender neu laden“ wählen.');
  } catch (error) {
    $('identity').replaceChildren(new Option(t('Absender konnten nicht geladen werden'), ''));
    $('identityHint').textContent = t('Thunderbird-Konten konnten nicht gelesen werden: ') + error.message;
  }
  updateStart();
}
 $('reloadIdentities').onclick = guard(loadIdentities);
 $('identity').addEventListener('change', updateStart);
async function loadFiles(saved = {}) {
  invalidate();
  const result = await native({action: 'files', folder: $('folder').value});
  const patterns = {list: /\.(txt|md|csv|xls|xlsx|ods)$/i, finished: /\.(txt|md|csv)$/i, template: /\.(doc|docx|odt)$/i, mail: /\.(txt|md)$/i};
  const defaults = {list: 'ApplicationList.txt', finished: 'ApplicationFinished.txt', template: 'ApplicationLetter.odt', mail: 'ApplicationMail.txt'};
  for (const id of Object.keys(patterns)) {
    $(id).replaceChildren(...result.files.filter(f => patterns[id].test(f)).map(f => new Option(f, f)));
    const choice = saved[id] || defaults[id];
    if ([...$(id).options].some(o => o.value === choice)) $(id).value = choice;
  }
}
$('load').onclick = guard(() => loadFiles());
for (const id of ['folder', 'list', 'finished', 'template', 'mail']) $(id).addEventListener('change', invalidate);
$('preview').onclick = guard(async () => {
  const cfg = config();
  job = await native({...cfg, action: 'preview'});
  await browser.storage.local.set({config: cfg});
  $('rows').replaceChildren(...job.rows.map(r => {
    const tr = document.createElement('tr');
    for (const value of [r.name, r.address, r.emails.join('; '), t(r.status)]) {
      const td = document.createElement('td'); td.textContent = value; tr.append(td);
    } return tr;
  }));
  const ready = job.rows.filter(r => r.status === 'Bereit').length;
  $('summary').textContent = `${ready} ${t('Firmen bereit')} · ${job.rows.length - ready} ${t('werden übersprungen')}`;
  $('subject').textContent = job.subject; $('body').textContent = job.body;
  updateStart();
});
$('start').onclick = guard(async () => {
  $('start').disabled = true;
  await send({type: 'start', config: config(), job, identityId: $('identity').value});
  job = null;
  await refresh();
});
$('cancel').onclick = guard(() => send({type: 'cancel'}));
async function refresh() {
  const s = await send({type: 'status'}); running = s.running;
  for (const id of ['folder','load','list','finished','template','mail','identity','reloadIdentities','preview']) $(id).disabled = running;
  $('cancel').disabled = !running;
  updateStart();
  $('progress').textContent = `${s.completed} / ${s.total} ${t('Entwürfe gespeichert')}${s.running ? ' · ' + (s.current || t('Startet…')) : s.cancelled ? ' · ' + t('Gestoppt') : ''}`;
  $('log').textContent = Lang.log(s.log.join('\n'));
}
async function initializeFiles() {
  const saved = await browser.storage.local.get('config');
  const defaults = await native({action: 'defaults'});
  $('folder').value = saved.config?.folder || defaults.folder;
  await loadFiles(saved.config);
}
const uiReady = Lang.init();
uiReady.then(() => Promise.allSettled([loadIdentities(), guard(initializeFiles)(), refresh()]))
  .then(() => setInterval(() => refresh().catch(() => {}), 1000));
