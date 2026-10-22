import NearbyShopsCard from './NearbyShopsCard';

const STORE_LINKS = [
  { title: 'Seeds', url: 'https://www.agribegri.com/seeds' },
  { title: 'Fertilizers', url: 'https://www.agribegri.com/fertilizers' },
  { title: 'Crop protection', url: 'https://www.agribegri.com/crop-protection' },
  { title: 'Irrigation supplies', url: 'https://www.agribegri.com/buy-online-irrigation-products-online-in-india.php' },
];

export default function MarketplaceCard() {
  return (
    <section className="market-panel" aria-labelledby="shopping-title">
      <h2 className="card-title" id="shopping-title">Buy agricultural supplies &amp; view offers</h2>
      <p className="card-subtitle">Browse products on AgriBegri, an external agricultural retailer.</p>
      <p className="scope-notice">Prices, discounts, stock and delivery availability are shown on the retailer’s website. Confirm the final amount and terms there before ordering.</p>
      <div className="form-grid">
        {STORE_LINKS.map((store) => (
          <a className="btn btn-secondary" key={store.title} href={store.url} target="_blank" rel="noopener noreferrer">
            {store.title} on AgriBegri ↗
          </a>
        ))}
      </div>
      <p><a className="btn btn-secondary" href="https://www.agribegri.com/collections/today_offers.php" target="_blank" rel="noopener noreferrer">View retailer’s offers ↗</a>{' '}<a href="https://www.agribegri.com/" target="_blank" rel="noopener noreferrer">Browse all supplies ↗</a></p>
      <p className="result-note">These links open an external store. Orders and payments take place there. AgriVision does not verify product suitability, seller claims or savings. Crop-selling listings are not currently available through AgriVision.</p>
      <NearbyShopsCard />
    </section>
  );
}
