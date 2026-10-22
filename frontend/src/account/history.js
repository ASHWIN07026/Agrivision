// Store bounded model summaries only, never photos, credentials or session tokens.
export function historyRecord(userId, module, result, inputSummary = '') {
  if (!userId || !['disease', 'yield'].includes(module) || result?.status !== 'ok') return null;
  const disease = module === 'disease';
  const summary = disease ? result.disease : `${result.crop}: ${result.expected_yield_kg_per_hectare} kg/ha`;
  if (typeof summary !== 'string' || (disease && !summary.includes('___'))) return null;
  const fields = disease ? ['disease', 'crop', 'confidence', 'model_id'] : ['crop', 'country', 'year', 'expected_yield_kg_per_hectare', 'estimate_type', 'model_id'];
  const details = Object.fromEntries(fields.filter(key => ['string', 'number'].includes(typeof result[key])).map(key => [key, result[key]]));
  return { user_id: userId, module, input_summary: String(inputSummary).slice(0, 250), result_summary: summary.slice(0, 250), result_details: details };
}
