import { useState } from 'react';
import NearbyShopsCard from './NearbyShopsCard';
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const CATEGORIES = ['produce', 'seeds', 'fertilizers', 'crop_protection', 'tools', 'machinery', 'irrigation', 'animal_feed'];
const label = (value) => value.replaceAll('_', ' ');

export default function MarketplaceCard() {
  const [intent, setIntent] = useState('sell');
  const [category, setCategory] = useState('');
  const [district, setDistrict] = useState('');
  const [offersOnly, setOffersOnly] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function loadListings(event) {
    event.preventDefault();
    setLoading(true); setError(''); setResults(null);
    try {
      const query = new URLSearchParams({ intent, offers_only: String(intent === 'sell' && offersOnly) });
      if (category) query.set('category', category);
      if (district.trim()) query.set('district', district.trim());
      const response = await fetch(`${API_BASE}/api/marketplace/listings?${query}`);
      if (!response.ok) throw new Error('The marketplace is unavailable. Please try again later.');
      const data = await response.json();
      if (!Array.isArray(data.records)) throw new Error('The marketplace returned an invalid response.');
      setResults(data);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  return (
    <section className="market-panel" aria-labelledby="marketplace-title">
      <h2 className="card-title" id="marketplace-title">Agriculture marketplace</h2>
      <p className="card-subtitle">Browse agricultural materials, crop listings and seller offers.</p>
      <p className="scope-notice">Prices are submitted by sellers and buyers. Confirm availability and terms directly with them.</p>
      <form onSubmit={loadListings}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="listing-intent">What are you looking for?</label>
            <select id="listing-intent" className="form-control" value={intent} onChange={(e) => { setIntent(e.target.value); setResults(null); }} disabled={loading}>
              <option value="sell">Products for sale — I want to buy</option>
              <option value="buy">Buyer requests — I want to sell</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="listing-category">Agriculture category</label>
            <select id="listing-category" className="form-control" value={category} onChange={(e) => { setCategory(e.target.value); setResults(null); }} disabled={loading}>
              <option value="">All agricultural categories</option>
              {CATEGORIES.map((item) => <option key={item} value={item}>{label(item)}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="listing-district">District (optional)</label>
            <input id="listing-district" className="form-control" value={district} onChange={(e) => { setDistrict(e.target.value); setResults(null); }} maxLength={100} placeholder="For example, Tiruppur" disabled={loading} />
          </div>
        </div>
        {intent === 'sell' && <label><input type="checkbox" checked={offersOnly} onChange={(e) => { setOffersOnly(e.target.checked); setResults(null); }} disabled={loading} /> Active discounts only</label>}
        <p><button className="btn btn-secondary" type="submit" disabled={loading}>{loading ? 'Searching…' : 'Search listings'}</button></p>
      </form>
      {error && <p className="error-msg" role="alert">{error}</p>}
      {results && <div aria-live="polite">
        {results.records.length === 0 && <p className="status-banner">No matching listings have been published yet.</p>}
        {results.records.map((item) => <article className="market-record" key={item.id}>
          <h3>{item.title}</h3>
          <p>{item.description}</p>
          <p>{item.district}, {item.state} · {label(item.category)}</p>
          <p><strong>₹{item.effective_price_inr}/{item.unit}</strong>{item.offer_active && <> · Regular ₹{item.price_inr} · {item.discount_percent}% off</>}</p>
          {item.offer_active && <p>Offer ends {new Date(item.offer_expires_at).toLocaleString()}</p>}
          <p>Quantity: {item.quantity} {item.unit} · {item.price_kind}</p>
          <p>{item.contact.name} · <a href={`tel:${item.contact.phone.replace(/[^+0-9]/g, '')}`}>Call {item.contact.phone}</a></p>
          <p className="result-note">Seller/buyer submitted · Independently unverified · Enquiries only</p>
        </article>)}
        {results.total > results.records.length && <p className="result-note">Showing the first {results.records.length} listings. Narrow your filters for more specific results.</p>}
      </div>}
      <NearbyShopsCard />
    </section>
  );
}
