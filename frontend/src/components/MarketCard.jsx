import { useState } from 'react';
import ResultBox from './ResultBox';
import { useI18n } from '../i18n/I18nContext';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const CROP_OPTIONS = ['Tomato', 'Potato', 'Pepper', 'Rice', 'Wheat', 'Onion'];

export default function MarketCard({ modelStatus }) {
  const { t } = useI18n();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const marketAvailable = modelStatus?.market_data_available === true;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    const formData = new FormData(event.currentTarget);
    const crop = formData.get('crop');
    const region = formData.get('region') || 'India';

    try {
      const query = new URLSearchParams({ crop, region });
      const response = await fetch(`${API_BASE}/api/market/price?${query}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data?.message || `Market request failed (${response.status}).`);
      setResult(data);
    } catch (requestError) {
      setError(requestError.message || 'Market lookup cannot be completed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="market-panel" aria-labelledby="market-title">
      <div className="market-heading">
        <div>
          <h2 className="card-title" id="market-title">{t('market.title')}</h2>
          <p className="card-subtitle">{t('market.subtitle')}</p>
        </div>
        <span className={`status-pill ${marketAvailable ? 'status-ready' : 'status-pending'}`} role="status">
          {marketAvailable ? t('status.ready') : t('status.marketUnavailable')}
        </span>
      </div>
      {!marketAvailable && (
        <p className="market-unavailable">
          {t('market.unavailable')}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="market-crop">{t('market.crop')}</label>
            <select id="market-crop" name="crop" className="form-control" required>
              {CROP_OPTIONS.map((crop) => <option key={crop} value={crop}>{crop}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="market-region">{t('market.region')}</label>
            <input
              id="market-region"
              type="text"
              name="region"
              className="form-control"
              placeholder={t('market.regionPlaceholder')}
              defaultValue="India"
            />
          </div>
        </div>

        <button className="btn btn-secondary" type="submit" disabled={loading}>
          {loading ? (
            <span className="btn-loading"><span className="spinner" />{t('market.checking')}</span>
          ) : t('market.check')}
        </button>
      </form>

      {error && <p className="error-msg" role="alert">{error || t('market.error')}</p>}

      {result && (
        <ResultBox title={t('market.result')}>
          {result.status === 'ok' && result.current_price != null ? (
            <>
              <div className="result-row">
                <span className="result-label">{t('market.cropMarket')}</span>
                <span className="result-value">{result.crop} · {result.region || result.market}</span>
              </div>
              <div className="result-row">
                <span className="result-label">{t('market.price')}</span>
                <span className="result-value">{result.current_price} {result.units}</span>
              </div>
              <p className="result-note">{t('market.source')}: {result.source}</p>
              <p className="result-note">{t('market.updated')}: {result.updated_at}</p>
            </>
          ) : (
            <>
              <div className="status-banner">{t('market.liveUnavailable')}</div>
              <p className="result-note">{result.message || t('market.noPrice')}</p>
            </>
          )}
        </ResultBox>
      )}
    </section>
  );
}
