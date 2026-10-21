import ShopSearch from './ShopSearch';
import { useI18n } from '../i18n/I18nContext';

export default function SuppliesCard() {
  const { t } = useI18n();
  return (
    <section className="card module-card" id="supplies" aria-labelledby="supplies-title">
      <div className="card-header">
        <div className="card-icon supplies-icon" aria-hidden="true">⌖</div>
        <div>
          <h2 className="card-title" id="supplies-title">{t('supplies.title')}</h2>
          <p className="card-subtitle">{t('supplies.subtitle')}</p>
        </div>
      </div>

      <div className="workbench-grid supplies-grid">
        <div className="workbench-form">
          <h3 className="section-title">{t('supplies.searchTitle')}</h3>
          <p className="supporting-copy">{t('supplies.searchHint')}</p>
          <ShopSearch idPrefix="supplies-location" />
        </div>
        <aside className="trust-note">
          <h3>{t('supplies.buyTitle')}</h3>
          <p>{t('supplies.buyNote')}</p>
        </aside>
      </div>
    </section>
  );
}
