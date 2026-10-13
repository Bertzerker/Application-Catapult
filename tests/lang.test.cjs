const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
test('English language selection and fallback preserve company data', async () => {
  const context = vm.createContext({browser: {storage: {local: {get: async () => ({language: 'en'})}}},
    document: {documentElement: {}, createTreeWalker: () => ({nextNode: () => false}), getElementById: () => null},
    NodeFilter: {SHOW_TEXT: 4}});
  vm.runInContext(fs.readFileSync('addon/lang.js', 'utf8'), context);
  await vm.runInContext('Lang.init()', context);
  assert.equal(vm.runInContext("Lang.t('Absender')", context), 'Sender');
  assert.equal(vm.runInContext("Lang.t('Example GmbH')", context), 'Example GmbH');
  assert.equal(vm.runInContext("Lang.t('Bereit')", context), 'Ready');
});
