import { useState } from 'react';
import DiseaseCare from './DiseaseCare';
import CareProtocol from './CareProtocol';
import careData from '../data/leafCareLookup.json';

export default function LeafCareLookup({ prediction }) {
  const [mode, setMode] = useState('auto');
  const automaticProtocol = prediction?.status === 'ok' && prediction.disease === 'Tomato___Early_blight' ? 'tomato_early_blight' : null;
  const [leaf, setLeaf] = useState('');
  const [issue, setIssue] = useState('');
  const entry = careData.entries.find((item) => item.leaf_name === leaf && item.issue === issue);
  const protocol = entry ? careData.protocols[entry.protocol_id] : null;

  return <section className="card module-card" aria-labelledby="leaf-care-title">
    <h2 className="card-title" id="leaf-care-title">Leaf care lookup — step-by-step methods</h2>
    <div className="form-group">
      <label htmlFor="care-mode">Care response</label>
      <select id="care-mode" className="form-control" value={mode} onChange={(event) => setMode(event.target.value)}>
        <option value="auto">Automatically use the image result</option>
        <option value="manual">Choose a leaf and confirmed issue manually</option>
      </select>
    </div>
    {mode === 'auto' ? <div aria-live="polite">
      {prediction?.from_history && <p className="warning-banner">Showing care for a saved history result. Analyze a new photo to check the current condition.</p>}
      <p className="scope-notice">Care follows the latest supported image result. A model label is not a confirmed diagnosis. Tomato varieties and Tulsi are not identified automatically.</p>
      {automaticProtocol ? <CareProtocol protocolId={automaticProtocol} title="Tomato — Early Blight: automatically selected care" />
        : <p className="result-note">{prediction?.status === 'ok'
          ? 'Care guidance for the latest classification is shown below. The seven-leaf Early Blight / Powdery Mildew reference remains available in manual mode.'
          : 'Take or upload a leaf photo and analyze it above. Matching care steps will appear here automatically. Tulsi and Powdery Mildew require a confirmed issue in manual mode.'}</p>}
      {!automaticProtocol && prediction?.status === 'ok' && <DiseaseCare category={prediction.disease} />}
    </div> : <>
    <p className="scope-notice">Choose the plant and a confirmed issue manually. Care steps appear immediately after both selections. This does not diagnose an image.</p>
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
    </>}
  </section>;
}
