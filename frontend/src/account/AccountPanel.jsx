import { useState } from 'react';
import { useAuth } from './AuthContext';

export default function AccountPanel() {
  const { client, user, ready, error: configError, recovery, setRecovery } = useAuth();
  const [mode, setMode] = useState('login');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const selectedMode = recovery ? 'update' : mode;
  async function submit(event) {
    event.preventDefault();
    if (!client || busy) return;
    const form = event.currentTarget;
    const values = new FormData(form);
    const email = String(values.get('email') || '').trim();
    const password = String(values.get('password') || '');
    setBusy(true); setError(''); setNotice('');
    try {
      let result;
      const redirectTo = `${window.location.origin}/?panel=account`;
      if (selectedMode === 'signup') {
        if (password !== values.get('confirm')) throw new Error('Passwords do not match.');
        result = await client.auth.signUp({ email, password, options: { emailRedirectTo: redirectTo } });
        if (!result.error) setNotice(result.data.session ? 'Account created. You are signed in.' : 'Check your email to confirm your account before logging in.');
      } else if (selectedMode === 'reset') {
        result = await client.auth.resetPasswordForEmail(email, { redirectTo });
        if (!result.error) setNotice('If this email is registered, a reset link will be sent.');
      } else if (selectedMode === 'update') {
        if (password !== values.get('confirm')) throw new Error('Passwords do not match.');
        result = await client.auth.updateUser({ password });
        if (!result.error) { setRecovery(false); setNotice('Password updated.'); }
      } else result = await client.auth.signInWithPassword({ email, password });
      if (result.error) throw result.error;
      form.reset();
    } catch (failure) { setError(failure.message || 'Account request failed.'); }
    finally { setBusy(false); }
  }
  async function logout() {
    setBusy(true); setError('');
    try { const { error } = await client.auth.signOut(); if (error) throw error; setNotice('Signed out.'); }
    catch (failure) { setError(failure.message || 'Sign out failed. Please retry.'); }
    finally { setBusy(false); }
  }
  return <section className="card module-card">
    <h2 className="card-title">{user && !recovery ? 'Your account' : ({ login: 'Log in / Sign in', signup: 'Create an account', reset: 'Reset password', update: 'Choose a new password' })[selectedMode]}</h2>
    {!ready && <p role="status">Connecting to account service…</p>}
    {configError && <p className="warning-banner" role="alert">{configError}</p>}
    {notice && <p className="scope-notice" role="status">{notice}</p>}
    {error && <p className="error-msg" role="alert">{error}</p>}
    {user && !recovery ? <><p>Signed in as {user.email}</p><p>Your successful new predictions can be saved to your private history. Photos are not uploaded to history.</p><button className="btn btn-secondary" disabled={busy} onClick={logout}>Log out</button></> : <>
      <form key={selectedMode} onSubmit={submit}>
        {selectedMode !== 'update' && <div className="form-group"><label htmlFor="account-email">Email</label><input id="account-email" className="form-control" name="email" type="email" autoComplete="email" required disabled={busy} /></div>}
        {selectedMode !== 'reset' && <div className="form-group"><label htmlFor="account-password">Password</label><input id="account-password" className="form-control" name="password" type="password" autoComplete={selectedMode === 'login' ? 'current-password' : 'new-password'} minLength={selectedMode === 'login' ? 1 : 8} required disabled={busy} /></div>}
        {['signup', 'update'].includes(selectedMode) && <div className="form-group"><label htmlFor="account-confirm">Confirm password</label><input id="account-confirm" className="form-control" name="confirm" type="password" autoComplete="new-password" minLength={8} required disabled={busy} /></div>}
        <button className="btn btn-primary" disabled={!ready || !client || busy}>{busy ? 'Please wait…' : ({ login: 'Log in', signup: 'Sign up', reset: 'Send reset link', update: 'Update password' })[selectedMode]}</button>
      </form>
      {!recovery && <div className="account-actions">{[['login', 'Log in'], ['signup', 'Sign up'], ['reset', 'Forgot password?']].filter(([value]) => value !== mode).map(([value, label]) => <button className="btn btn-secondary" key={value} disabled={busy} onClick={() => { setMode(value); setError(''); setNotice(''); }}>{label}</button>)}</div>}
    </>}
  </section>;
}
