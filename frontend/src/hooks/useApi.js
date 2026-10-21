import { useState } from 'react';

/**
 * useApi – generic hook to call the AgriVision backend.
 * Usage:
 *   const { data, loading, error, call } = useApi('http://localhost:8000/api/yield/predict', 'POST');
 *   await call(formData);
 */
export function useApi(url, method = 'GET') {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const call = async (body = null) => {
    setLoading(true);
    setError(null);
    try {
      const options = { method, body };
      if (body && !(body instanceof FormData)) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
      }
      const res = await fetch(url, options);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      return json;
    } catch (e) {
      setError(e.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, call };
}
