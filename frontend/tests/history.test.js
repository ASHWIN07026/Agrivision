import test from 'node:test';
import assert from 'node:assert/strict';
import { historyRecord } from '../src/account/history.js';
test('history excludes rejected images, guests, arbitrary modules and sensitive data', () => {
  assert.equal(historyRecord(null, 'disease', { status: 'ok' }), null);
  assert.equal(historyRecord('owner', 'disease', { status: 'error', disease: 'Tomato___Early_blight' }), null);
  assert.equal(historyRecord('owner', 'unknown', { status: 'ok' }), null);
  const row = historyRecord('owner', 'disease', { status: 'ok', disease: 'Tomato___Early_blight', confidence: .9, access_token: 'secret', image: 'photo', password: 'private' }, 'a'.repeat(300));
  assert.equal(row.user_id, 'owner');
  assert.equal(row.input_summary.length, 250);
  assert.deepEqual(row.result_details, { disease: 'Tomato___Early_blight', confidence: .9 });
});
test('history stores historical yield units and model context', () => {
 const row = historyRecord('owner', 'yield', { status: 'ok', crop: 'Potatoes', country: 'India', year: 2026, expected_yield_kg_per_hectare: 1500, estimate_type: 'experimental' });
 assert.match(row.result_summary, /1500 kg\/ha/);
 assert.equal(row.result_details.estimate_type, 'experimental');
});
