import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { LANGUAGES, TRANSLATIONS } from './translations';

const I18nContext = createContext(null);
const STORAGE_KEY = 'agrivision-language';

export function I18nProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    return Object.prototype.hasOwnProperty.call(LANGUAGES, saved) ? saved : 'en';
  });

  useEffect(() => {
    document.documentElement.lang = language === 'tanglish' ? 'en' : language;
  }, [language]);

  const value = useMemo(() => ({
    language,
    locale: language === 'tanglish' ? 'en-IN' : `${language}-IN`,
    languages: LANGUAGES,
    setLanguage: (nextLanguage) => {
      if (!Object.prototype.hasOwnProperty.call(LANGUAGES, nextLanguage)) {
        throw new Error(`Unsupported language: ${nextLanguage}`);
      }
      window.localStorage.setItem(STORAGE_KEY, nextLanguage);
      setLanguage(nextLanguage);
    },
    t: (key, values = {}) => {
      const template = TRANSLATIONS[language][key] ?? TRANSLATIONS.en[key] ?? key;
      return Object.entries(values).reduce(
        (text, [name, replacement]) => text.replaceAll(`{${name}}`, String(replacement)),
        template,
      );
    },
  }), [language]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) throw new Error('useI18n must be used within I18nProvider.');
  return context;
}
