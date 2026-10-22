import { useState } from 'react';
import CareProtocol from './CareProtocol';
import careData from '../data/leafCareLookup.json';

export default function LeafCareLookup() {
  const [leaf, setLeaf] = useState('');
  const [issue, setIssue] = useState('');
  const entry = careData.entries.find((item) => item.leaf_name === leaf && item.issue === issue);
  const protocol = entry ? careData.protocols[entry.protocol_id] : null;

  return <section className="card module-card" aria-labelledby="leaf-care-title">
    <h2 className="card-title" id="leaf-care-title">Leaf care lookup — step-by-step methods</h2>
    <p className="scope-notice">Choose the plant and a confirmed issue manually. This lookup does not diagnose an image or add new conditions to the image model.</p>
    <div className="form-grid">
      <div className="form-group">
        <label htmlFor="care-leaf-name">Leaf name</label>
        <select id="care-leaf-name" className="form-control" value={leaf} onChange={(event) => setLeaf(event.target.value)}>
          <option value="">Choose a leaf</option>
          {careData.leaf_names.map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="care-issue">Confirmed issue / care topic</label>
        <select id="care-issue" className="form-control" value={issue} onChange={(event) => setIssue(event.target.value)}>
          <option value="">Choose an issue</option>
          {careData.issues.map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
      </div>
    </div>
    {protocol ? <CareProtocol protocolId={entry.protocol_id} title={`${leaf} — ${issue}`} /> : <p className="result-note">Select a leaf and issue to see the care steps. No treatment has been selected yet.</p>}
  </section>;
}
