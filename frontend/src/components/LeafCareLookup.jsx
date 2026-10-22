import { useState } from 'react';
import careData from '../data/leafCareLookup.json';

function Steps({ title, items }) {
  return <section><h3>{title}</h3><ol>{items.map((step) => <li key={step}>{step}</li>)}</ol></section>;
}

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
    {protocol ? <div className="care-details" aria-live="polite">
      <h3>{leaf} — {issue}</h3>
      <p className="warning-banner">{protocol.summary}</p>
      <p className="result-note">{protocol.evidence_note}</p>
      <Steps title="1. Confirm and prepare the plant" items={protocol.start_steps} />
      <Steps title="2. Organic / nonchemical option" items={protocol.organic_steps} />
      <Steps title="3. Chemical alternative, where labelled" items={protocol.chemical_steps} />
      <p className="scope-notice">Organic and chemical options are alternatives, not instructions to mix them. No universal dose or guaranteed cure applies to every product and plant.</p>
      <Steps title="4. How to prepare and apply a permitted product" items={careData.application_steps} />
      <Steps title="5. Follow-up and harvest" items={protocol.follow_up_steps} />
      <h3>Sources and crop scope</h3>
      <ul>{protocol.source_ids.map((id) => <li key={id}><a href={careData.sources[id].url} target="_blank" rel="noopener noreferrer">{careData.sources[id].title}</a></li>)}</ul>
    </div> : <p className="result-note">Select a leaf and issue to see the care steps. No treatment has been selected yet.</p>}
  </section>;
}
