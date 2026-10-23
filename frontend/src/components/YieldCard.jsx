import { useState } from 'react';
import ResultBox from './ResultBox';
import { useI18n } from '../i18n/I18nContext';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export default function YieldCard({ modelStatus, options }) {
  const { t, locale } = useI18n();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setError('');
    if (!modelStatus?.api_available) {
      setError(t('yield.apiError'));
      return;
    }
    if (!modelStatus?.yield_model_available || !options) {
      setResult({
        status: 'not_trained',
        message: t('yield.notTrained'),
        expected_yield_kg_per_hectare: null,
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/yield/predict`, {
        method: 'POST',
        body: new FormData(event.currentTarget),
      });
      const data = await response.json();
      if (data?.status === 'not_trained') {
        setResult(data);
      } else if (!response.ok || data?.status !== 'ok') {
        throw new Error(data?.message || `Prediction failed (${response.status}).`);
      } else {
        setResult(data);
      }
    } catch (requestError) {
      setError(requestError.message || 'The yield model could not produce a prediction.');
    } finally {
      setLoading(false);
    }
  };

  const defaultCountry = options?.countries?.includes('India')
    ? 'India'
    : options?.countries?.[0] || '';
  const yearRange = options?.accepted_prediction_year_range || options?.recommended_prediction_year_range || [];
  const datasetYearRange = options?.dataset_year_range || [];
  const datasetEndYear = datasetYearRange[1];
  const isExperimental = result?.estimate_type === 'experimental'
    || (result?.year != null && datasetEndYear != null && Number(result.year) > Number(datasetEndYear));

  return (
    <section className="card module-card" id="yield" aria-labelledby="yield-title">
      <div className="card-header">
        <div className="card-icon yield-icon" aria-hidden="true">🌾</div>
        <div>
          <h2 className="card-title" id="yield-title">{t('yield.title')}</h2>
          <p className="card-subtitle">{t('yield.subtitle')}</p>
        </div>
      </div>

      <p className="scope-notice">
        {t('yield.scope')}
      </p>

      {modelStatus?.api_available && !modelStatus?.yield_model_available && (
        <div className="status-banner" role="status">{t('yield.unavailable')}</div>
      )}

      {options && datasetEndYear != null && (
        <>
          <p className="warning-banner" role="note">
            {t('yield.experimentalIntro', { year: datasetEndYear })}
          </p>
          <details className="disclosure">
            <summary>{t('yield.datasetDetails')}</summary>
            <p>{t('yield.savedDataset', {
              years: datasetYearRange.join('–'),
              training: options.train_year_range?.join('–') || 'Not provided',
            })}</p>
            <p>{t('yield.noExtrapolation')}</p>
            <p>{t('yield.modelId', { id: options.model_id || 'Not provided' })}</p>
          </details>
        </>
      )}

      <div className="workbench-grid">
        <div className="workbench-form">
          <form key={options?.model_id || 'loading'} onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="yield-country">{t('yield.country')}</label>
                <select
                  id="yield-country"
                  name="country"
                  className="form-control"
                  defaultValue={defaultCountry}
                  required
                  disabled={!options}
                >
                  {options?.countries?.map((country) => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="yield-crop">{t('yield.crop')}</label>
                <select
                  id="yield-crop"
                  name="crop"
                  className="form-control"
                  defaultValue={options?.crops?.[0] || ''}
                  required
                  disabled={!options}
                >
                  {options?.crops?.map((crop) => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="yield-year">{t('yield.year')}</label>
                <input
                  id="yield-year"
                  type="number"
                  name="year"
                  className="form-control"
                  min={yearRange[0]}
                  max={yearRange[1]}
                  defaultValue={Math.min(new Date().getFullYear(), yearRange[1] || new Date().getFullYear())}
                  required
                  disabled={!options}
                />
                {yearRange.length === 2 && (
                  <span className="field-hint">
                    {t('yield.acceptedYears', { min: yearRange[0], max: yearRange[1] })}
                  </span>
                )}
              </div>
            </div>

            <button className="btn btn-primary" type="submit" disabled={loading || !options}>
              {loading ? (
                <span className="btn-loading"><span className="spinner" />{t('yield.calculating')}</span>
              ) : t('yield.estimate')}
            </button>
          </form>
          {error && <p className="error-msg" role="alert">{error}</p>}
        </div>

        <div className="workbench-result" aria-live="polite">
          {result ? (
            <ResultBox title={t('yield.result')}>
              {result.expected_yield_kg_per_hectare != null ? (
                <>
                  <div className="yield-display">
                    <span className="yield-number">
                      {Number(result.expected_yield_kg_per_hectare).toLocaleString(locale)}
                    </span>
                    <span className="yield-unit">{t('yield.unit')}</span>
                  </div>
                  <div className="result-row">
                    <span className="result-label">{t('yield.locationCrop')}</span>
                    <span className="result-value">{result.country} · {result.crop} · {result.year}</span>
                  </div>
                  {isExperimental && (
                    <p className="warning-banner" role="status">
                      {t('yield.experimental')}
                    </p>
                  )}
                  <details className="disclosure">
                    <summary>{t('yield.details')}</summary>
                    <p>{result.warning || t('yield.historicalWarning')}</p>
                    <div className="result-row">
                      <span className="result-label">{t('disease.modelId')}</span>
                      <span className="result-value">{result.model_id}</span>
                    </div>
                    <div className="result-row">
                      <span className="result-label">{t('disease.inference')}</span>
                      <span className="result-value">{Number(result.inference_ms).toLocaleString(locale, { maximumFractionDigits: 1 })} ms</span>
                    </div>
                  </details>
                </>
              ) : (
                <div className="status-banner">{result.message || t('yield.notTrained')}</div>
              )}
            </ResultBox>
          ) : (
            <div className="empty-state">
              <span className="empty-state-icon" aria-hidden="true">↗</span>
              <p>{t('yield.emptyTitle')}</p>
              <span>{t('yield.emptyHint')}</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
