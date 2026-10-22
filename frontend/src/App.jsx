import { AuthProvider, useAuth } from './account/AuthContext';
import AccountPanel from './account/AccountPanel';
import HistoryPanel from './account/HistoryPanel';
import { historyRecord } from './account/history';
import OverviewPanel from './components/OverviewPanel';
import { useEffect, useRef, useState } from 'react';
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
  const { client, user, recovery } = useAuth();
  const [historyRevision, setHistoryRevision] = useState(0);
  const [historyNotice, setHistoryNotice] = useState('');
  const accountRef = useRef(null);
  accountRef.current = user?.id;
  useEffect(() => { setHistoryNotice(''); setDiseaseResult(null); }, [user?.id]);
  useEffect(() => { if (recovery) setActivePanel('account'); }, [recovery]);
  async function savePrediction(module, result, summary) {
    const owner = user?.id;
    const record = historyRecord(owner, module, result, summary);
    if (!record || !client) return;
    try {
      const { error } = await client.from('user_prediction_history').insert(record);
      if (accountRef.current !== owner) return;
      setHistoryNotice(error ? 'Prediction completed, but history was not saved. Check database setup or your connection.' : 'Prediction saved to your private history.');
      if (!error) setHistoryRevision(value => value + 1);
    } catch {
      if (accountRef.current === owner) setHistoryNotice('Prediction completed, but history could not be saved.');
    }
  }

  const [activePanel, setActivePanel] = useState(() => {
    const requested = new URLSearchParams(window.location.search).get('panel');
    return ['dashboard', 'history', 'account', 'disease', 'yield', 'supplies'].includes(requested) ? requested : 'dashboard';
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
          <section id="panel-dashboard" role="tabpanel" aria-labelledby="tab-dashboard" hidden={activePanel !== 'dashboard'}>
            <OverviewPanel modelStatus={modelStatus} user={user} onNavigate={setActivePanel} historyNotice={historyNotice} />
          </section>
          <section id="panel-account" role="tabpanel" aria-labelledby="tab-account" hidden={activePanel !== 'account'}><AccountPanel /></section>
          <section id="panel-history" role="tabpanel" aria-labelledby="tab-history" hidden={activePanel !== 'history'}>
            <HistoryPanel revision={historyRevision} onLogin={() => setActivePanel('account')} onReview={(details) => { setDiseaseResult({ ...details, status: 'ok', from_history: true }); setActivePanel('disease'); }} />
          </section>
          {historyNotice && activePanel !== 'dashboard' && <p className="scope-notice" role="status">{historyNotice}</p>}
          <section
            id="panel-disease"
            className="tab-panel"
            role="tabpanel"
            aria-labelledby="tab-disease"
            tabIndex={0}
            hidden={activePanel !== 'disease'}
          >
            <DiseaseCard modelStatus={modelStatus} onResultChange={setDiseaseResult} onPredictionComplete={savePrediction} />
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
            <YieldCard modelStatus={modelStatus} options={yieldOptions} onPredictionComplete={savePrediction} />
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
      <AuthProvider><Dashboard /></AuthProvider>
    </I18nProvider>
  );
}

export default App;
