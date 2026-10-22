import { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import Header from './components/Header';
import DiseaseCard from './components/DiseaseCard';
import LeafCareLookup from './components/LeafCareLookup';
import YieldCard from './components/YieldCard';
import MarketplaceCard from './components/MarketplaceCard';
import SuppliesCard from './components/SuppliesCard';
import { I18nProvider } from './i18n/I18nContext';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const INITIAL_STATUS = {
  api_available: false,
  disease_model_available: false,
  yield_model_available: false,
  disease_supported_categories: [],
  shop_provider_configured: false,
};

function Dashboard() {
  const [activePanel, setActivePanel] = useState(() => {
    const requested = new URLSearchParams(window.location.search).get('panel');
    return ['disease', 'yield', 'supplies'].includes(requested) ? requested : 'disease';
  });
  const [modelStatus, setModelStatus] = useState(INITIAL_STATUS);
  const [yieldOptions, setYieldOptions] = useState(null);
  const [apiError, setApiError] = useState('');
  const [diseaseResult, setDiseaseResult] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const loadStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/health`);
        if (!response.ok) throw new Error(`API health check failed (${response.status}).`);
        const status = await response.json();
        if (cancelled) return;
        setModelStatus({ ...status, api_available: true });
        setApiError('');

        if (status.yield_model_available) {
          const optionsResponse = await fetch(`${API_BASE}/api/yield/options`);
          if (!optionsResponse.ok) throw new Error(`Yield options unavailable (${optionsResponse.status}).`);
          const options = await optionsResponse.json();
          if (!cancelled) setYieldOptions(options);
        }
      } catch (error) {
        if (cancelled) return;
        setApiError(error.message || 'FastAPI backend is unavailable.');
      }
    };

    loadStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <Navbar
        activePanel={activePanel}
        onPanelChange={setActivePanel}
      />
      <div className="dashboard-container">
        <Header modelStatus={modelStatus} apiError={apiError} />
        <main id="main-content" className="module-panels">
          <section
            id="panel-disease"
            className="tab-panel"
            role="tabpanel"
            aria-labelledby="tab-disease"
            tabIndex={0}
            hidden={activePanel !== 'disease'}
          >
            <DiseaseCard modelStatus={modelStatus} onResultChange={setDiseaseResult} />
            <LeafCareLookup prediction={diseaseResult} />
          </section>
          <section
            id="panel-yield"
            className="tab-panel"
            role="tabpanel"
            aria-labelledby="tab-yield"
            tabIndex={0}
            hidden={activePanel !== 'yield'}
          >
            <YieldCard modelStatus={modelStatus} options={yieldOptions} />
          </section>
          <section
            id="panel-supplies"
            className="tab-panel"
            role="tabpanel"
            aria-labelledby="tab-supplies"
            tabIndex={0}
            hidden={activePanel !== 'supplies'}
          >
            <SuppliesCard />
            <MarketplaceCard />
          </section>
        </main>
      </div>
    </>
  );
}

function App() {
  return (
    <I18nProvider>
      <Dashboard />
    </I18nProvider>
  );
}

export default App;
