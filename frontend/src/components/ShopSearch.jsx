import { useState } from 'react';
import { useI18n } from '../i18n/I18nContext';

export default function ShopSearch({ idPrefix }) {
  const { t } = useI18n();
  const [location, setLocation] = useState('');
  const query = encodeURIComponent(`agricultural input shop ${location.trim() || 'near me'}`);

  return (
    <div className="shop-search">
      <label htmlFor={`${idPrefix}-input`}>{t('shop.location')}</label>
      <div className="shop-search-row">
        <input
          id={`${idPrefix}-input`}
          className="form-control"
          type="search"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          placeholder={t('shop.placeholder')}
          maxLength={100}
        />
        <a
          className="btn btn-secondary shop-search-button"
          href={`https://www.google.com/maps/search/?api=1&query=${query}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {t('shop.search')}
        </a>
      </div>
      <p className="disclaimer">
        {t('shop.disclaimer')}
      </p>
    </div>
  );
}
