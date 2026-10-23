import test from 'node:test';
import assert from 'node:assert/strict';
import { clearRetiredAccountSession } from '../src/utils/retiredAccounts.js';
test('retired account tokens are removed without reading tokens or deleting language preferences', () => {
 const records = new Map([['sb-projectref-auth-token', 'private'], ['sb-projectref-auth-token-code-verifier', 'private'], ['sb-projectref-auth-token-user', 'private'], ['agrivision-locale', 'ta'], ['other-data', 'keep']]);
 const storage = { get length() { return records.size; }, key: i => [...records.keys()][i], removeItem: key => records.delete(key) };
 clearRetiredAccountSession(storage);
 assert.deepEqual([...records], [['agrivision-locale', 'ta'], ['other-data', 'keep']]);
});
test('restricted storage does not break public tools', () => {
 assert.doesNotThrow(() => clearRetiredAccountSession({ get length() { throw new Error('denied'); } }));
});
