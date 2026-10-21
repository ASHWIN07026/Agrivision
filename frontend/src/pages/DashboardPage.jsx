import DiseaseCard from '../components/DiseaseCard';
import YieldCard from '../components/YieldCard';
import MarketCard from '../components/MarketCard';
import Header from '../components/Header';

/**
 * DashboardPage – assembles all three AI module cards.
 */
export default function DashboardPage() {
  return (
    <div className="dashboard-container">
      <Header />
      <div className="grid">
        <DiseaseCard />
        <YieldCard />
        <MarketCard />
      </div>
    </div>
  );
}
