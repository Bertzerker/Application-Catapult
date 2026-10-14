const providerInputs = {'codex': 'useCodex', 'gemini-cli': 'useGeminiCLI', 'gemini': 'useGemini', 'openai': 'useOpenAI'};
const providerNames = {'codex': 'Codex', 'gemini-cli': 'Antigravity (Konto)', 'gemini': 'Gemini API', 'openai': 'OpenAI API'};
const chosenProviders = () => Object.keys(providerInputs).filter(p => $(providerInputs[p]).checked);
const showProviders = () => {$('activeProviders').textContent = Lang.t('Aktive Verbindungen: ') + chosenProviders().map(p => Lang.t(providerNames[p])).join(' · ');};
for (const id of Object.values(providerInputs)) $(id).onchange = showProviders;
for (const [id, provider] of [['checkCodexCLI', 'codex'], ['checkGeminiCLI', 'gemini-cli']]) {
  $(id).onclick = guard(async () => {
    $(id).disabled = true;
    try {await native({action: 'checkCLI', provider}); $('searchStatus').textContent = Lang.t('Zusatzprogramm bereit. Eine Live-Suche wurde noch nicht geprüft.');}
    finally {$(id).disabled = false;}
  });
}
let searchResult = null;
async function keyStatus() {
  const result = await native({action: 'keyStatus'});
  $('keyStatus').textContent = ['gemini', 'openai'].map(p => p + ': ' + Lang.t(result.keys[p] ? 'Schlüssel vorhanden' : 'Kein Schlüssel')).join(' · ');
}
$('saveKeys').onclick = guard(async () => {
  $('saveKeys').disabled = true;
  try {
    await native({action: 'saveKeys', keys: {gemini: $('geminiKey').value, openai: $('openaiKey').value}});
    $('geminiKey').value = ''; $('openaiKey').value = '';
    await keyStatus();
  } finally {$('saveKeys').disabled = false;}
});
$('checkOpenAI').onclick = guard(async () => {
  $('checkOpenAI').disabled = true;
  try {await native({action: 'checkOpenAI'}); $('searchStatus').textContent = Lang.t('OpenAI-Verbindung funktioniert.');}
  finally {$('checkOpenAI').disabled = false;}
});
$('dedupeList').onclick = guard(async () => {
  $('dedupeList').disabled = true;
  try {
    const result = await native({action: 'dedupeList', folder: $('folder').value, list: $('list').value});
    $('searchStatus').textContent = result.removed + ' ' + Lang.t('Dubletten entfernt.');
    invalidate();
  } finally {$('dedupeList').disabled = false;}
});
const modelFields = {codex: 'codexModel', antigravity: 'antigravityModel', gemini: 'searchModel', openai: 'openaiModel'};
let modelsLoaded = false;
async function loadModels(preferred = {}) {
  const result = await native({action: 'modelCatalog'});
  for (const [provider, id] of Object.entries(modelFields)) {
    const values = result.models[provider];
    const previous = preferred[id] ?? $(id).value;
    $(id).replaceChildren();
    for (const value of values) {
      const option = document.createElement('option');
      option.value = value; option.textContent = value || Lang.t('Programmstandard');
      $(id).append(option);
    }
    $(id).value = values.includes(previous) ? previous : values[0];
  }
  modelsLoaded = true;
  $('modelStatus').textContent = Lang.t('Modelllisten geladen.');
}
$('reloadModels').onclick = guard(async () => {
  $('reloadModels').disabled = true;
  try {await loadModels();} finally {$('reloadModels').disabled = false;}
});
const searchReady = uiReady.then(async () => {
  const {searchSettings: s} = await browser.storage.local.get('searchSettings');
  if (s) {
    for (const [p, id] of Object.entries(providerInputs)) $(id).checked = (s.providers || []).includes(p);
    $('apiSettings').open = !!s.apiOpen;
  }
  showProviders();
  await loadModels(s ? {codexModel: s.codexModel, antigravityModel: s.antigravityModel,
    searchModel: s.model, openaiModel: s.openaiModel} : {});
});
searchReady.catch(e => {$('modelStatus').textContent = String(e.message || e);});
uiReady.then(keyStatus).catch(() => {});
const selectedCompanies = () => [...document.querySelectorAll('#searchRows input:checked')].map(input => input.value);
function updateSelection() {
  const inputs = [...document.querySelectorAll('#searchRows input')].filter(input => !input.disabled);
  const count = inputs.filter(input => input.checked).length;
  $('selectAll').disabled = !inputs.length;
  $('selectAll').checked = !!inputs.length && count === inputs.length;
  $('selectAll').indeterminate = count > 0 && count < inputs.length;
  $('appendSearch').disabled = !count;
}
$('selectAll').onchange = () => {
  for (const input of document.querySelectorAll('#searchRows input')) if (!input.disabled) input.checked = $('selectAll').checked;
  updateSelection();
};
$('checkGemini').onclick = guard(async () => {
  $('checkGemini').disabled = true;
  try {await native({action: 'checkGemini'}); $('searchStatus').textContent = Lang.t('Gemini-Verbindung funktioniert.');}
  finally {$('checkGemini').disabled = false;}
});
$('searchJobs').onclick = guard(async () => {
  const providers = chosenProviders();
  if (!providers.length) throw new Error(Lang.t('Mindestens eine KI auswählen.'));
  if (!modelsLoaded) throw new Error(Lang.t('Bitte zuerst Modelllisten laden.'));
  $('searchJobs').disabled = true; $('appendSearch').disabled = true; $('language').disabled = true;
  searchResult = null; $('searchRows').replaceChildren(); $('searchSources').replaceChildren();
  $('selectAll').checked = false; $('selectAll').indeterminate = false; $('selectAll').disabled = true;
  $('searchDetails').textContent = ''; $('suggestions').hidden = true;
  $('searchStatus').textContent = Lang.t('Suche läuft…');
  try {
    const folder = $('folder').value;
    await browser.storage.local.set({searchSettings: {providers, apiOpen: $('apiSettings').open, codexModel: $('codexModel').value, antigravityModel: $('antigravityModel').value, model: $('searchModel').value, openaiModel: $('openaiModel').value}});
    searchResult = await native({action: 'searchJobs', folder, list: $('list').value, finished: $('finished').value, city: $('searchCity').value,
      radius: Number($('searchRadius').value), role: $('searchRole').value,
      providers, codexModel: $('codexModel').value, antigravityModel: $('antigravityModel').value, model: $('searchModel').value, openaiModel: $('openaiModel').value, speculative: $('searchMode').value === 'speculative', language: Lang.language});
    searchResult.folder = folder;
    for (const row of searchResult.rows) {
      const tr = document.createElement('tr'), td = document.createElement('td'), checkbox = document.createElement('input');
      checkbox.type = 'checkbox'; checkbox.value = row.key; checkbox.setAttribute('aria-label', row.name);
      checkbox.disabled = !row.emails.length || !row.address;
      checkbox.onchange = updateSelection;
      td.append(checkbox); tr.append(td);
      for (const value of [row.name + (row.providers?.length ? ' (' + row.providers.map(p => Lang.t(providerNames[p] || p)).join(' + ') + ')' : ''), row.address, row.emails.join('; ')]) {
        const cell = document.createElement('td'); cell.textContent = value; tr.append(cell);
      }
      $('searchRows').append(tr);
    }
    updateSelection();
    for (const source of searchResult.sources) {
      const a = document.createElement('a'); a.textContent = source.title || source.uri;
      a.href = source.uri; a.target = '_blank'; a.rel = 'noopener noreferrer';
      const p = document.createElement('p'); p.append(a); $('searchSources').append(p);
    }
    $('searchDetails').textContent = searchResult.text;
    if (searchResult.errors?.length) $('error').textContent = searchResult.errors.join('\n');
    if (searchResult.suggestions) {
      // Remote markup is confined to a scriptless, origin-isolated frame.
      $('suggestions').srcdoc = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">' + searchResult.suggestions;
      $('suggestions').hidden = false;
    }
    $('searchStatus').textContent = searchResult.rows.length + ' ' + Lang.t('Firmen gefunden. Bitte Quellen prüfen und Firmen auswählen.') + ' · ' + (searchResult.duplicates || 0) + ' ' + Lang.t('Dubletten zusammengeführt.') + ' · ' + (searchResult.excludedFinished || 0) + ' ' + Lang.t('vorhandene oder bearbeitete Firmen ausgeblendet.');
  } catch (e) {$('searchStatus').textContent = ''; throw e;}
  finally {$('searchJobs').disabled = false; $('language').disabled = false;}
});
$('appendSearch').onclick = guard(async () => {
  const selected = selectedCompanies();
  if (!selected.length || !searchResult) throw new Error(Lang.t('Keine Treffer ausgewählt.'));
  $('appendSearch').disabled = true;
  const result = await native({action: 'appendSearch', folder: searchResult.folder, token: searchResult.token, selected});
  $('searchStatus').textContent = result.added + ' ' + Lang.t('Firmen angehängt.') + ' · ' + result.removed + ' ' + Lang.t('Dubletten entfernt.');
  for (const input of document.querySelectorAll('#searchRows input')) if (input.checked) {input.checked = false; input.disabled = true;}
  updateSelection();
  if ($('folder').value === searchResult.folder) await loadFiles({...config(), list: result.filename});
});
