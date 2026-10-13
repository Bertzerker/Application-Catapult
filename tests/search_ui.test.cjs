const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
test('key inputs clear after save and only native bridge receives them', async () => {
  const elements = new Map(), calls = [], storageWrites = [];
  const $ = id => {
    if (!elements.has(id)) elements.set(id, {value: '', textContent: '', disabled: false, checked: false});
    return elements.get(id);
  };
  const native = async request => {calls.push(request); return {keys: {gemini: true, openai: true}};};
  const browser = {storage: {local: {get: async () => ({}), set: async value => storageWrites.push(value)}}};
  vm.runInNewContext(fs.readFileSync('addon/search.js','utf8'), {
    $, native, browser, guard: fn => fn, uiReady: Promise.resolve(), Lang: {t: x => x},
    document: {}, invalidate: () => {}, config: () => ({}), loadFiles: async () => {}
  });
  $('geminiKey').value = 'dummy-gemini'; $('openaiKey').value = 'dummy-openai';
  await $('saveKeys').onclick();
  assert.equal($('geminiKey').value, ''); assert.equal($('openaiKey').value, '');
  assert.equal(calls.find(r => r.action === 'saveKeys').keys.openai, 'dummy-openai');
  assert.equal(storageWrites.length, 0);
  await assert.rejects($('searchJobs').onclick(), /Mindestens eine KI/);
});

test('four connections can be selected separately and collapsed APIs remain selected', async () => {
  const elements = new Map(), calls = [];
  const $ = id => {
    if (!elements.has(id)) elements.set(id, {value: '', checked: false, open: false, replaceChildren() {}, append() {}});
    return elements.get(id);
  };
  const catalog = {codex:['','gpt-6.1-sol'],antigravity:['gemini-3.8-flash-high'],gemini:['gemini-2.5-pro'],openai:['gpt-5-mini']};
  const saved = {providers: ['gemini', 'openai'], model: 'gemini-2.5-pro', openaiModel: 'gpt-5-mini'};
  vm.runInNewContext(fs.readFileSync('addon/search.js','utf8'), {
    $, native: async r => {calls.push(r); if (r.action === 'searchJobs') throw new Error('captured'); return {keys:{}, models: catalog};},
    browser: {storage:{local:{get:async()=>({searchSettings:saved}),set:async()=>{}}}},
    guard:fn=>fn, uiReady:Promise.resolve(),Lang:{t:x=>x},document:{createElement:()=>({})}, invalidate(){}
  });
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal($('useCodex').checked,false);
  assert.equal($('useGemini').checked,true);
  assert.equal($('apiSettings').open,false);
  for (const [provider,id] of [['codex','useCodex'],['gemini-cli','useGeminiCLI'],['gemini','useGemini'],['openai','useOpenAI']]) {
    for (const other of ['useCodex','useGeminiCLI','useGemini','useOpenAI']) $(other).checked=other===id;
    await assert.rejects($('searchJobs').onclick(),/captured/);
    assert.deepEqual(Array.from(calls.at(-1).providers),[provider]);
  }
  for (const id of ['useCodex','useGeminiCLI','useGemini','useOpenAI']) $(id).checked=true;
  await assert.rejects($('searchJobs').onclick(),/captured/);
  assert.equal(calls.at(-1).providers.length,4);
  assert.equal(calls.at(-1).antigravityModel,'gemini-3.8-flash-high');
  $('codexModel').value='gpt-6.1-sol';
  await assert.rejects($('searchJobs').onclick(),/captured/);
  assert.equal(calls.at(-1).codexModel,'gpt-6.1-sol');
  catalog.codex=['gpt-new'];
  await $('reloadModels').onclick();
  assert.equal($('codexModel').value,'gpt-new');
  assert.equal($('antigravityModel').value,'gemini-3.8-flash-high');
});
