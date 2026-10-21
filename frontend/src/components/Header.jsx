import { useI18n } from '../i18n/I18nContext';

export default function Header({ modelStatus, apiError }) {
  const { language, languages, setLanguage, t } = useI18n();
  const diseaseReady = modelStatus?.disease_model_available;
  const yieldReady = modelStatus?.yield_model_available;
  const marketReady = modelStatus?.market_data_available === true;

  return (
    <header className="header">
      <div className="header-topline">
        <div className="header-badge">{t('header.badge')}</div>
        <label className="language-control">
          <span>{t('language.label')}</span>
          <select
            className="language-select"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            aria-label={t('language.label')}
          >
            {Object.entries(languages).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
        </label>
      </div>
      <h1>AgriVision</h1>
      <p>{t('header.subtitle')}</p>

      <div className="status-row">
        <span className={`status-pill ${diseaseReady ? 'status-ready' : 'status-pending'}`} role="status">
          {t('status.disease')}: {diseaseReady ? t('status.ready') : modelStatus?.api_available ? t('status.unavailable') : t('status.apiUnavailable')}
        </span>
        <span className={`status-pill ${yieldReady ? 'status-ready' : 'status-pending'}`} role="status">
          {t('status.yield')}: {yieldReady ? t('status.ready') : modelStatus?.api_available ? t('status.unavailable') : t('status.apiUnavailable')}
        </span>
        <span className={`status-pill ${marketReady ? 'status-ready' : 'status-pending'}`} role="status">
          {t('status.liveMarket')}: {marketReady ? t('status.ready') : t('status.marketUnavailable')}
        </span>
      </div>
      {apiError && <p className="error-msg" role="alert">{apiError}</p>}
    </header>
  );
}
