import { useState } from 'react';
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export default function NearbyShopsCard() {
  const [town, setTown] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function lookup(params) {
    try {
      const response = await fetch(`${API_BASE}/api/shops/nearby?${new URLSearchParams({ ...params, radius_km: 25 })}`);
      const data = await response.json();
      if (!response.ok) {
        if (response.status === 429) throw new Error('Shop search is busy or its request limit has been reached. Try again later.');
        if (response.status === 503) throw new Error('Mapped shop search is not available yet. Please try again later.');
        throw new Error('Shop search could not be completed. Check the town or try again later.');
      }
      if (!Array.isArray(data.records)) throw new Error('Shop search returned an invalid response.');
      setResult(data);
    } catch (requestError) { setError(requestError.message || 'Shop search could not be completed.'); }
    finally { setLoading(false); }
  }

  function searchTown(event) {
    event.preventDefault(); setResult(null); setError('');
    if (!town.trim()) { setError('Enter a town or district, or use your location.'); return; }
    setLoading(true); lookup({ town: town.trim() });
  }

  function useLocation() {
    setResult(null); setError('');
    if (!navigator.geolocation) { setError('Location is unavailable. Search by town instead.'); return; }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(({ coords }) => {
      lookup({ latitude: coords.latitude, longitude: coords.longitude });
    }, () => { setError('Location could not be obtained. Search by town instead.'); setLoading(false); }, { timeout: 15000, maximumAge: 60000 });
  }

  return <section aria-labelledby="mapped-shops-title">
    <h3 id="mapped-shops-title">Nearby agricultural supply shops</h3>
    <p>Search existing mapped agricultural shops within 25 km. Your town or location is sent to the map provider when you search.</p>
    <form onSubmit={searchTown}>
      <div className="form-group">
        <label htmlFor="mapped-shop-town">Town or district</label>
        <input id="mapped-shop-town" className="form-control" value={town} onChange={(e) => { setTown(e.target.value); setResult(null); }} placeholder="For example, Tiruppur, Tamil Nadu" minLength={2} maxLength={100} disabled={loading} />
      </div>
      <p><button className="btn btn-secondary" type="submit" disabled={loading}>{loading ? 'Searching…' : 'Find mapped shops'}</button>{' '}<button className="btn btn-secondary" type="button" onClick={useLocation} disabled={loading}>Use my location</button></p>
    </form>
    {error && <p className="error-msg" role="alert">{error}</p>}
    {result && <div aria-live="polite">
      {result.location_label && <p>Search area: {result.location_label}</p>}
      {!result.records.length && <p className="status-banner">{result.message?.startsWith('Town not found') ? result.message : 'No agricultural shops were found in the map data within 25 km. Local shops may be missing from the map; try the external shop search above.'}</p>}
      {result.records.map((shop) => <article className="market-record" key={shop.id}>
        <h3>{shop.name} · {shop.distance_km} km away</h3>
        {shop.address && <p>{shop.address}</p>}
        {shop.opening_hours && <p>Reported opening hours: {shop.opening_hours}</p>}
        <p>{shop.phone && <><a href={`tel:${shop.phone.replace(/[^+0-9]/g, '')}`}>Call shop</a> · </>}<a target="_blank" rel="noreferrer" href={`https://www.google.com/maps/dir/?api=1&destination=${shop.latitude},${shop.longitude}`}>Directions</a>{shop.website && <> · <a href={shop.website} target="_blank" rel="noreferrer">Shop website</a></>}</p>
        <p className="result-note">Map listing · Confirm stock, prices, offers and opening hours directly with the shop.</p>
      </article>)}
      <p className="result-note">Retrieved {new Date(result.fetched_at).toLocaleString()}{result.cached ? ' · Cached for up to 5 minutes' : ''}</p>
    </div>}
    <p className="result-note">Powered by <a href="https://www.geoapify.com/" target="_blank" rel="noreferrer">Geoapify</a> · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap contributors</a>. Map coverage can be incomplete.</p>
  </section>;
}
