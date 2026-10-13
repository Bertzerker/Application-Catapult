const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

async function panel(accounts) {
  const elements = new Map();
  function get(id) {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', options: [], disabled: false,
      replaceChildren(...children) {this.options = children; this.value = children[0]?.value || '';},
      addEventListener() {}
    });
    return elements.get(id);
  }
  let folderFlag;
  const browser = {
    accounts: {list: async flag => {folderFlag = flag; return accounts;}},
    storage: {local: {get: async () => ({})}},
    runtime: {sendMessage: async m => {
      if (m.type === 'native') throw new Error('Hilfsprogramm nicht erreichbar');
      return {running: false, completed: 0, total: 0, log: []};
    }}
  };
  vm.runInNewContext(fs.readFileSync('addon/panel.js', 'utf8'), {
    browser, Lang: {t: v => v, log: v => v, init: async () => {}}, document: {getElementById: get},
    Option: function(text, value) {this.text = text; this.value = value;}, setInterval: () => {}
  });
  await new Promise(resolve => setImmediate(resolve));
  return {get, folderFlag};
}
test('sender loads even when native helper fails', async () => {
  const {get, folderFlag} = await panel([{name: 'Testkonto', identities: [{id: 'id1', email: 'a@example.org'}]}]);
  assert.equal(get('identity').value, 'id1');
  assert.equal(folderFlag, false);
  assert.match(get('error').textContent, /Hilfsprogramm/);
});
test('no configured account explains setup and disables start', async () => {
  const {get} = await panel([{name: 'Lokale Ordner', identities: []}]);
  assert.equal(get('identity').value, '');
  assert.match(get('identityHint').textContent, /E-Mail-Konto hinzufügen/);
  assert.equal(get('start').disabled, true);
});
