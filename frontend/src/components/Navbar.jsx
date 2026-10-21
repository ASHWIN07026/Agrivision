import { useRef } from 'react';
import { useI18n } from '../i18n/I18nContext';

const PANELS = [
  { id: 'disease', labelKey: 'nav.disease' },
  { id: 'yield', labelKey: 'nav.yield' },
  { id: 'supplies', labelKey: 'nav.supplies' },
];

export default function Navbar({ activePanel, onPanelChange }) {
  const { t } = useI18n();
  const tabRefs = useRef([]);

  const handleKeyDown = (event, index) => {
    let nextIndex;
    if (event.key === 'ArrowRight') nextIndex = (index + 1) % PANELS.length;
    else if (event.key === 'ArrowLeft') nextIndex = (index - 1 + PANELS.length) % PANELS.length;
    else if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = PANELS.length - 1;
    else return;

    event.preventDefault();
    onPanelChange(PANELS[nextIndex].id);
    tabRefs.current[nextIndex]?.focus();
  };

  return (
    <nav className="navbar">
      <a className="navbar-brand" href="#main-content" aria-label={t('nav.home')}>
        <span className="navbar-logo">🌿</span>
        <span className="navbar-title">AgriVision</span>
      </a>
      <div className="navbar-links" role="tablist" aria-label={t('nav.label')} aria-orientation="horizontal">
        {PANELS.map((panel, index) => (
          <button
            key={panel.id}
            ref={(element) => { tabRefs.current[index] = element; }}
            id={`tab-${panel.id}`}
            className="nav-link"
            type="button"
            role="tab"
            aria-selected={activePanel === panel.id}
            aria-controls={`panel-${panel.id}`}
            tabIndex={activePanel === panel.id ? 0 : -1}
            onClick={() => onPanelChange(panel.id)}
            onKeyDown={(event) => handleKeyDown(event, index)}
          >
            {t(panel.labelKey)}
          </button>
        ))}
      </div>
    </nav>
  );
}
