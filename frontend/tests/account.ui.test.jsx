// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import AccountPanel from '../src/account/AccountPanel';
import HistoryPanel from '../src/account/HistoryPanel';
import DetectedSupplies from '../src/components/DetectedSupplies';

const auth = vi.hoisted(() => ({ current: null }));
vi.mock('../src/account/AuthContext', () => ({ useAuth: () => auth.current, AuthProvider: ({ children }) => children }));
let root, host;
beforeEach(() => {
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  host = document.createElement('div'); document.body.append(host); root = createRoot(host);
  auth.current = { ready: true, client: null, user: null, error: '', recovery: false, setRecovery: vi.fn() };
});
afterEach(async () => { await act(async () => root.unmount()); host.remove(); });
const render = async element => { await act(async () => root.render(element)); };
const click = async text => { const button = [...host.querySelectorAll('button')].find(item => item.textContent === text); expect(button).toBeTruthy(); await act(async () => button.click()); };
const submit = async values => {
 for (const [name, value] of Object.entries(values)) host.querySelector(`[name="${name}"]`).value = value;
 await act(async () => host.querySelector('form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })));
};

test('missing account configuration disables login', async () => {
 auth.current.error = 'Accounts are not configured yet.';
 await render(<AccountPanel />);
 expect(host.textContent).toContain('not configured');
 expect(host.querySelector('button[type="submit"],form button').disabled).toBe(true);
});
test('login sends email and password to auth SDK and clears password', async () => {
 const signInWithPassword = vi.fn().mockResolvedValue({ data: {}, error: null });
 auth.current.client = { auth: { signInWithPassword } };
 await render(<AccountPanel />);
 await submit({ email: 'farmer@example.test', password: 'test-pass' });
 expect(signInWithPassword).toHaveBeenCalledWith({ email: 'farmer@example.test', password: 'test-pass' });
 expect(host.querySelector('[name=password]').value).toBe('');
});
test('signup requires matching password and reports confirmation instead of fake login', async () => {
 const signUp = vi.fn().mockResolvedValue({ data: { session: null }, error: null });
 auth.current.client = { auth: { signUp } };
 await render(<AccountPanel />); await click('Sign up');
 await submit({ email: 'farmer@example.test', password: 'test-pass', confirm: 'different' });
 expect(signUp).not.toHaveBeenCalled();
 expect(host.textContent).toContain('Passwords do not match');
 await submit({ email: 'farmer@example.test', password: 'test-pass', confirm: 'test-pass' });
 expect(signUp).toHaveBeenCalledOnce();
 expect(host.textContent).toContain('Check your email');
});
test('logout calls SDK and surfaces failure without pretending success', async () => {
 auth.current.user = { id: 'owner', email: 'farmer@example.test' };
 const signOut = vi.fn().mockResolvedValue({ error: new Error('Network unavailable') });
 auth.current.client = { auth: { signOut } };
 await render(<AccountPanel />); await click('Log out');
 expect(signOut).toHaveBeenCalledOnce(); expect(host.textContent).toContain('Network unavailable');
});
test('history makes no database request for a signed-out user', async () => {
 const from = vi.fn(); auth.current.client = { from };
 await render(<HistoryPanel onLogin={() => {}} />);
 expect(from).not.toHaveBeenCalled(); expect(host.textContent).toContain('Log in to view');
});
test('history queries owner and clears old rows after account switch', async () => {
 const rows = [{ id: 'one', module: 'disease', input_summary: 'photo', result_summary: 'PRIVATE FARM RESULT', result_details: {}, created_at: '2026-10-22T10:00:00Z' }];
 const limit = vi.fn().mockResolvedValue({ data: rows, error: null });
 const eq = vi.fn().mockReturnValue({ order: () => ({ limit }) });
 auth.current = { ...auth.current, user: { id: 'first' }, client: { from: () => ({ select: () => ({ eq }) }) } };
 await render(<HistoryPanel />); expect(eq).toHaveBeenCalledWith('user_id', 'first'); expect(host.textContent).toContain('PRIVATE FARM RESULT');
 auth.current = { ...auth.current, user: null };
 await render(<HistoryPanel />); expect(host.textContent).not.toContain('PRIVATE FARM RESULT');
});
test('healthy and virus results have no chemical product link or fake prices', async () => {
 for (const category of ['Tomato___healthy', 'Tomato___Tomato_mosaic_virus']) {
  await render(<DetectedSupplies category={category} />);
  expect(host.innerHTML).not.toContain('href="https://www.agribegri.com/crop-protection"');
  expect(host.textContent).not.toContain('₹');
 }
 await render(<DetectedSupplies category="Potato___Early_blight" />);
 expect(host.innerHTML).toContain('href="https://www.agribegri.com/crop-protection"');
 expect(host.textContent).toContain('adviser review required');
});

test('dashboard navigation opens protected history and account forms for a guest', async () => {
 auth.current.error = 'Accounts are not configured yet.';
 const { default: App } = await import('../src/App');
 const savedFetch = globalThis.fetch;
 globalThis.fetch = vi.fn(async url => ({ ok: true, json: async () => String(url).endsWith('public-config') ? { auth_configured: false } : { disease_model_available: false, yield_model_available: false, disease_supported_categories: [] } }));
 try {
  await render(<App />);
  expect(host.querySelector('#panel-dashboard').hidden).toBe(false);
  await act(async () => host.querySelector('#tab-history').click());
  expect(host.querySelector('#panel-history').hidden).toBe(false);
  expect(host.querySelector('#panel-history').textContent).toContain('Log in to view');
  await act(async () => host.querySelector('#tab-account').click());
  expect(host.querySelector('#panel-account').hidden).toBe(false);
  expect(host.querySelector('#panel-account').textContent).toContain('not configured');
 } finally { globalThis.fetch = savedFetch; }
});
