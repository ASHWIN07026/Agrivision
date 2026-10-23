export default function OverviewPanel({ modelStatus, onNavigate }) {
  return <section className="card module-card"><h2 className="card-title">Farm dashboard</h2><p>Explore crop health, yield estimates and agricultural supplies. All tools are available directly.</p>
    <div className="dashboard-tiles">{[
      ['disease', 'Analyze a leaf', modelStatus.disease_model_available ? 'Disease model ready · camera or upload' : 'Checking disease model'],
      ['yield', 'Estimate yield', modelStatus.yield_model_available ? 'Yield model ready · historical estimates' : 'Checking yield model'],
      ['supplies', 'Products & nearby shops', 'Browse agricultural supplies and external retailer offers'],
    ].map(([id, title, note]) => <button className="dashboard-tile" key={id} onClick={() => onNavigate(id)}><strong>{title}</strong><span>{note}</span></button>)}</div>
  </section>;
}
