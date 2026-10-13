(async () => {
  await Lang.init();
  const {lastRun: s} = await browser.storage.local.get('lastRun');
  document.getElementById('title').textContent = Lang.t(s.completed === s.total ? 'Entwürfe fertig' : 'Vorgang beendet');
  document.getElementById('summary').textContent = `${s.completed} ${Lang.t('von')} ${s.total} ${Lang.t('Entwürfen wurden gespeichert. Bitte vor dem Versenden prüfen.')}`;
  document.getElementById('log').textContent = Lang.log(s.log.join('\n'));
})();
document.getElementById('close').onclick = () => window.close();
