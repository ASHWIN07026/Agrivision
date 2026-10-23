// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import App from '../src/App';

let host, root, fetchMock;
beforeEach(() => {
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  host = document.createElement('div'); document.body.append(host); root = createRoot(host);
  fetchMock = vi.fn(async url => ({ ok: true, json: async () => String(url).endsWith('/api/health') ? { disease_model_available: true, yield_model_available: false, disease_supported_categories: [] } : {} }));
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(async () => { await act(async () => root.unmount()); host.remove(); vi.unstubAllGlobals(); window.history.replaceState({}, '', '/'); });
async function render() { await act(async () => root.render(<App />)); }

test('desktop and mobile share public navigation without account controls or requests', async () => {
  await render();
  expect(host.querySelectorAll('[role="tab"]').length).toBe(4);
  expect(host.textContent).not.toMatch(/log in|login|sign in|sign up|signup|logout|log out/i);
  expect(host.querySelector('#panel-dashboard').hidden).toBe(false);
  expect(host.querySelectorAll('.dashboard-tile').length).toBe(3);
  expect(fetchMock.mock.calls.every(([url]) => !/auth|public-config|supabase|history/.test(String(url)))).toBe(true);
  for (const id of ['disease', 'yield', 'supplies', 'dashboard']) {
    await act(async () => host.querySelector(`#tab-${id}`).click());
    expect(host.querySelector(`#panel-${id}`).hidden).toBe(false);
  }
  expect(host.querySelector('#disease button[type="submit"]')).not.toBeNull();
  expect(host.textContent).toContain('Take photo');
});

test.each(['account', 'history', 'login', 'signup'])('old %s links open the dashboard without an account flow', async panel => {
  window.history.replaceState({}, '', `/?panel=${panel}`);
  await render();
  expect(host.querySelector('#panel-dashboard').hidden).toBe(false);
  expect(host.querySelector('#panel-account')).toBeNull();
  expect(host.querySelector('#panel-history')).toBeNull();
});
