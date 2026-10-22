export default function OverviewPanel({ modelStatus, user, onNavigate, historyNotice }) {
  return <section className="card module-card"><h2 className="card-title">Farm dashboard</h2><p>{user ? `Welcome, ${user.email}` : 'Explore AgriVision. Log in to save your new predictions.'}</p>
    <div className="dashboard-tiles">{[
      ['disease', 'Analyze a leaf', modelStatus.disease_model_available ? 'Disease model ready · camera or upload' : 'Checking disease model'],
      ['yield', 'Estimate yield', modelStatus.yield_model_available ? 'Yield model ready · historical estimates' : 'Checking yield model'],
      ['supplies', 'Products & nearby shops', 'Browse agricultural supplies and external retailer offers'],
      ['history', 'Your history', user ? 'View saved predictions and revisit care guidance' : 'Sign in for private history'],
    ].map(([id, title, note]) => <button className="dashboard-tile" key={id} onClick={() => onNavigate(id)}><strong>{title}</strong><span>{note}</span></button>)}</div>
    {historyNotice && <p className="scope-notice" role="status">{historyNotice}</p>}
    {!user && <p><button className="btn btn-primary" onClick={() => onNavigate('account')}>Log in / Sign up</button></p>}
  </section>;
}
