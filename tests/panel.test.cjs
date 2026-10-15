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

test('list selectors offer JSON only and migrate saved Markdown selections', async () => {
  const elements=new Map();
  const get=id=>{if(!elements.has(id))elements.set(id,{value:'',options:[],addEventListener(){},replaceChildren(...items){this.options=items;this.value=items[0]?.value||'';}});return elements.get(id);};
  get('folder').value='test';
  const files=['ApplicationFinished.MD','ApplicationFinished.json','ApplicationList.MD','ApplicationList.json','custom.MD','custom.json','ApplicationMail.MD','ApplicationLetter.odt'];
  const context={browser:{runtime:{sendMessage:async message=>message.request.action==='files'?{files}:{text:'Subject\n\nBody'}}},Lang:{init:()=>new Promise(()=>{}),t:v=>v,log:v=>v},document:{getElementById:get},Option:function(text,value){this.text=text;this.value=value;}};
  vm.runInNewContext(fs.readFileSync('addon/panel.js','utf8'),context);
  await vm.runInNewContext("loadFiles({list:'ApplicationList.MD',finished:'ApplicationFinished.MD'})",context);
  assert.equal(get('list').value,'ApplicationList.json');
  assert.equal(get('finished').value,'ApplicationFinished.json');
  assert.ok(get('list').options.every(o=>o.value.endsWith('.json')));
  assert.ok(get('finished').options.every(o=>o.value.endsWith('.json')));
  await vm.runInNewContext("loadFiles({list:'custom.MD'})",context);
  assert.equal(get('list').value,'custom.json');
});
