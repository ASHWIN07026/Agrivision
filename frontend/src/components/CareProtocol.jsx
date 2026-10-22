import careData from '../data/leafCareLookup.json';

function Steps({ title, items }) {
  return <section><h3>{title}</h3><ol>{items.map((step) => <li key={step}>{step}</li>)}</ol></section>;
}

export default function CareProtocol({ protocolId, title }) {
  const protocol = careData.protocols[protocolId];
  if (!protocol) return null;
  return <div className="care-details" aria-live="polite">
      <h3>{title}</h3>
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
    </div>;
}
