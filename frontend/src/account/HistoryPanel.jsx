import { useEffect, useRef, useState } from 'react';
import { useAuth } from './AuthContext';

export default function HistoryPanel({ revision, onLogin, onReview }) {
  const { client, user, ready } = useAuth();
  const [state, setState] = useState({ owner: null, rows: [], loading: false, error: '' });
  const [refresh, setRefresh] = useState(0);
  const request = useRef(0);
  useEffect(() => {
    const sequence = ++request.current;
    if (!user || !client) { setState({ owner: null, rows: [], loading: false, error: '' }); return; }
    setState({ owner: user.id, rows: [], loading: true, error: '' });
    client.from('user_prediction_history').select('id,module,input_summary,result_summary,result_details,created_at').eq('user_id', user.id).order('created_at', { ascending: false }).limit(100)
      .then(({ data, error }) => {
        if (sequence !== request.current) return;
        setState({ owner: user.id, rows: data || [], loading: false, error: error ? 'History could not be loaded. Check your connection and database setup, then refresh.' : '' });
      }).catch(() => { if (sequence === request.current) setState({ owner: user.id, rows: [], loading: false, error: 'History could not be loaded. Please refresh.' }); });
    return () => { request.current++; };
  }, [client, user?.id, revision, refresh]);
  const rows = state.owner === user?.id ? state.rows : [];
  async function remove(id) {
    if (!user) return;
    try {
    const { error } = await client.from('user_prediction_history').delete().eq('user_id', user.id).eq('id', id);
    if (error) setState(previous => ({ ...previous, error: 'Could not delete this record. Please retry.' }));
    else setRefresh(value => value + 1);
    } catch { setState(previous => ({ ...previous, error: 'Could not delete this record. Please retry.' })); }
  }
  return <section className="card module-card"><h2 className="card-title">Prediction history</h2>
    {!ready ? <p>Checking your session…</p> : !user ? <><p>Log in to view your private prediction history.</p><button className="btn btn-primary" onClick={onLogin}>Log in / Sign up</button></> : <>
      <p>Latest 100 saved results for your account. Image classifications are not confirmed diagnoses. Photos are not stored here.</p>
      <button className="btn btn-secondary" onClick={() => setRefresh(value => value + 1)}>Refresh history</button>
      {state.loading && <p role="status">Loading history…</p>}{state.error && <p className="error-msg" role="alert">{state.error}</p>}
      {!state.loading && !state.error && rows.length === 0 && <p>No saved predictions yet. Analyze a leaf or estimate yield while signed in.</p>}
      {rows.map(row => <article className="history-record" key={row.id}><h3>{row.module === 'disease' ? 'Leaf classification' : 'Yield estimate'}</h3><p>{row.result_summary.replaceAll('___', ' — ').replaceAll('_', ' ')}</p><p>{row.input_summary}</p><time dateTime={row.created_at}>{new Date(row.created_at).toLocaleString()}</time><div className="account-actions">{row.module === 'disease' && <button className="btn btn-secondary" onClick={() => onReview(row.result_details)}>View care and supply links</button>}<button className="btn btn-secondary" onClick={() => remove(row.id)}>Delete record</button></div></article>)}
    </>}
  </section>;
}
