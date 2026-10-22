import { useI18n } from '../i18n/I18nContext';

export default function LanguageSelect({ className = '' }) {
  const { language, languages, setLanguage, t } = useI18n();
  return (
    <label className={`language-control ${className}`.trim()}>
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
  );
}
