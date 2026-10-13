const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const {File} = require('node:buffer');

async function scenario(failAt) {
  const calls = [];
  let listener, completed;
  const finished = new Promise(resolve => completed = resolve);
  const bytes = Buffer.from('%PDF-test');
  const browser = {
    runtime: {getURL: x => x, onMessage: {addListener: f => listener = f},
      sendNativeMessage: async (name, req) => {
        calls.push(req.action);
        if (req.action === failAt) return {ok: false, error: 'Testfehler'};
        if (req.action === 'generate') return {ok: true, size: bytes.length, name: 'Test.pdf'};
        if (req.action === 'chunk') return {ok: true, data: bytes.toString('base64')};
        return {ok: true};
      }},
    compose: {
      beginNew: async details => {calls.push('beginNew'); assert.equal(details.to.length, 2); return {id: 7};},
      addAttachment: async (id, {file}) => {
        calls.push('attach'); assert.equal(file.type, 'application/pdf');
        assert.equal(await file.text(), '%PDF-test');
      },
      saveMessage: async (id, opts) => {
        calls.push('save'); assert.equal(opts.mode, 'draft');
        if (failAt === 'save') throw new Error('Speichern fehlgeschlagen');
        return {messages: [{id: 9}]};
      }
    },
    storage: {local: {set: async () => {}}},
    tabs: {remove: async () => calls.push('close'), create: async () => {}},
    windows: {create: async () => {completed();}},
    browserAction: {onClicked: {addListener: () => {}}}
  };
  vm.runInNewContext(fs.readFileSync('addon/background.js', 'utf8'), {browser, File, Uint8Array, atob, console});
  const job = {token: 'abc', subject: 'Bewerbung', body: 'Hallo', rows: [
    {key: 'firma', name: 'Firma', emails: ['a@example.org', 'b@example.org'], status: 'Bereit'},
    {key: 'skip', name: 'Ohne Mail', emails: [], status: 'Keine E-Mail-Adresse'}]};
  await listener({type: 'start', config: {folder: 'test'}, job, identityId: 'id1'});
  await finished;
  return {calls, state: await listener({type: 'status'})};
}
test('PDF, reserve, draft, commit in correct order; skipped rows untouched', async () => {
  const {calls, state} = await scenario();
  assert.deepEqual(calls, ['generate','chunk','reserve','beginNew','attach','save','commit','close','sound']);
  assert.equal(state.completed, 1);
});
test('failed draft save never marks company finished', async () => {
  const {calls, state} = await scenario('save');
  assert.equal(calls.includes('commit'), false);
  assert.equal(calls.includes('close'), false);
  assert.equal(state.completed, 0);
});
test('failed PDF conversion never opens compose', async () => {
  const {calls} = await scenario('generate');
  assert.equal(calls.includes('beginNew'), false);
});
test('failed journal commit is visible and retains saved draft', async () => {
  const {calls, state} = await scenario('commit');
  assert.equal(state.completed, 1);
  assert.equal(calls.includes('close'), false);
  assert.match(state.log.join('\n'), /Nachbearbeitung fehlgeschlagen/);
});
