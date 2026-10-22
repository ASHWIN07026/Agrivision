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
  const marketConfigured = modelStatus?.market_api_configured === true;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    const formData = new FormData(event.currentTarget);
    const crop = formData.get('crop');

    try {
      const query = new URLSearchParams({ crop });
      for (const field of ['state', 'district', 'market', 'date']) {
        const value = formData.get(field);
        if (value) query.set(field, value);
      }
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
        <span className={`status-pill ${marketConfigured ? 'status-ready' : 'status-pending'}`} role="status">
          {marketConfigured ? t('market.providerConfigured') : t('status.marketUnavailable')}
        </span>
      </div>
      {!marketConfigured && (
        <p className="market-unavailable">
          {t('market.unavailable', { key: 'DATA_GOV_IN_API_KEY' })}
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
            <label htmlFor="market-state">{t('market.state')}</label>
            <input
              id="market-state"
              type="text"
              name="state"
              className="form-control"
              placeholder={t('market.statePlaceholder')}
              autoComplete="address-level1"
            />
          </div>
          <div className="form-group">
            <label htmlFor="market-district">{t('market.district')}</label>
            <input
              id="market-district"
              type="text"
              name="district"
              className="form-control"
              placeholder={t('market.districtPlaceholder')}
              autoComplete="address-level2"
            />
          </div>
          <div className="form-group">
            <label htmlFor="market-name">{t('market.marketName')}</label>
            <input
              id="market-name"
              type="text"
              name="market"
              className="form-control"
              placeholder={t('market.marketPlaceholder')}
            />
          </div>
          <div className="form-group">
            <label htmlFor="market-date">{t('market.date')}</label>
            <input
              id="market-date"
              type="date"
              name="date"
              className="form-control"
            />
          </div>
        </div>

        <button className="btn btn-secondary" type="submit" disabled={loading}>
          {loading ? (
            <span className="btn-loading"><span className="spinner" />{t('market.checking')}</span>
          ) : t('market.check')}
        </button>
      </form>
      <p className="result-note">{t('market.latestNote')}</p>

      {error && <p className="error-msg" role="alert">{error || t('market.error')}</p>}

      {result && (
        <ResultBox title={t('market.result')}>
          {result.status === 'ok' && result.records?.length ? (
            <>
              <p className="result-note">{result.freshness}</p>
              {result.records.map((record, index) => (
                <article
                  className="market-record"
                  key={`${record.state}-${record.district}-${record.market}-${record.arrival_date}-${index}`}
                >
                  <h3>{record.commodity} · {record.market}</h3>
                  <p>{record.district}, {record.state}{record.variety ? ` · ${record.variety}` : ''}</p>
                  <div className="result-row">
                    <span className="result-label">{t('market.minPrice')}</span>
                    <span className="result-value">{record.min_price ?? t('market.notReported')} {record.min_price != null && record.price_unit}</span>
                  </div>
                  <div className="result-row">
                    <span className="result-label">{t('market.maxPrice')}</span>
                    <span className="result-value">{record.max_price ?? t('market.notReported')} {record.max_price != null && record.price_unit}</span>
                  </div>
                  <div className="result-row">
                    <span className="result-label">{t('market.modalPrice')}</span>
                    <span className="result-value">{record.modal_price ?? t('market.notReported')} {record.modal_price != null && record.price_unit}</span>
                  </div>
                  <p className="result-note">{t('market.arrivalDate')}: {record.arrival_date}</p>
                  <p className="result-note">
                    {t('market.source')}: <a href={record.source_url} target="_blank" rel="noreferrer">{record.source}</a>
                  </p>
                </article>
              ))}
            </>
          ) : (
            <>
              <div className="status-banner">{t('market.noPublishedResults')}</div>
              <p className="result-note">{result.message || t('market.noPrice')}</p>
            </>
          )}
        </ResultBox>
      )}
    </section>
  );
}
