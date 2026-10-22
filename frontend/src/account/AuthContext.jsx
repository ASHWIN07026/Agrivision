import { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext(null);
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
export function AuthProvider({ children }) {
  const [client, setClient] = useState(null);
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [recovery, setRecovery] = useState(false);
  useEffect(() => {
    let cancelled = false, subscription;
    async function init() {
      try {
        const response = await fetch(`${API_BASE}/api/public-config`);
        if (!response.ok) throw new Error('Account service configuration is unavailable.');
        const config = await response.json();
        if (!config.auth_configured) throw new Error('Accounts are not configured yet. The site owner must configure Supabase.');
        if (cancelled) return;
        const { createClient } = await import('@supabase/supabase-js');
        if (cancelled) return;
        const supabase = createClient(config.supabase_url, config.supabase_publishable_key);
        setClient(supabase);
        subscription = supabase.auth.onAuthStateChange((event, session) => {
          if (cancelled) return;
          setUser(session?.user || null);
          if (event === 'PASSWORD_RECOVERY') setRecovery(true);
          if (event === 'SIGNED_OUT') setRecovery(false);
        }).data.subscription;
        const { data, error: sessionError } = await supabase.auth.getSession();
        if (sessionError) throw sessionError;
        if (!cancelled) setUser(data.session?.user || null);
      } catch (failure) {
        if (!cancelled) setError(failure.message || 'Could not connect to the account service.');
      } finally { if (!cancelled) setReady(true); }
    }
    init();
    return () => { cancelled = true; subscription?.unsubscribe(); };
  }, []);
  return <AuthContext.Provider value={{ client, user, ready, error, recovery, setRecovery }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
