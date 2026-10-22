import LanguageSelect from './LanguageSelect';
import { useI18n } from '../i18n/I18nContext';

export default function Header({ modelStatus, apiError }) {
  const { t } = useI18n();
  const diseaseReady = modelStatus?.disease_model_available;
  const yieldReady = modelStatus?.yield_model_available;
  const shopsConfigured = modelStatus?.shop_provider_configured === true;

  return (
    <header className="header">
      <div className="header-topline">
        <div className="header-badge">{t('header.badge')}</div>
        <LanguageSelect className="language-control--desktop" />
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
        <span className={`status-pill ${shopsConfigured ? 'status-ready' : 'status-pending'}`} role="status">
          {t('status.nearbyShops')}: {shopsConfigured ? t('status.shopConfigured') : t('status.marketUnavailable')}
        </span>
      </div>
      {apiError && <p className="error-msg" role="alert">{apiError}</p>}
    </header>
  );
}
