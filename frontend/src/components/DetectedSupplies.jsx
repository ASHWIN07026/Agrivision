// External browsing links; no prices, inventory, efficacy claims or chemical prescriptions.
export default function DetectedSupplies({ category }) {
  if (!category?.includes('___')) return null;
  const healthy = category.endsWith('___healthy');
  const virus = /virus|Yellow_Leaf_Curl/.test(category);
  const items = [
    { title: 'Leaf inspection and routine care tools', note: 'Browse equipment for inspecting and handling plants.', url: 'https://www.agribegri.com/equipments' },
    ...(/Yellow_Leaf_Curl/.test(category) ? [{ title: 'Pest monitoring traps', note: 'Monitoring supplies; these do not cure an infected plant.', url: 'https://www.agribegri.com/equipments/traps/sticky-traps' }] : []),
    ...(!healthy && !virus ? [{ title: 'Crop protection products — adviser review required', note: 'Browse only after confirming the issue. Buy a product only if its current label permits your crop and target problem.', url: 'https://www.agribegri.com/crop-protection' }] : []),
    ...(!healthy && !virus ? [{ title: 'Example equipment: Pad Corp 16 L spray pump', note: 'Equipment listing only, not a recommendation to spray. Check capacity and suitability; use treatments only as permitted by the product label.', url: 'https://www.agribegri.com/products/buy-16-liter-spray-machine-online--spray-pump-with-nozzle-set.php' }] : []),
    { title: 'Irrigation supplies', note: 'Browse watering equipment for routine crop care.', url: 'https://www.agribegri.com/buy-online-irrigation-products-online-in-india.php' },
  ];
  return <section className="detected-supplies"><h3>Supplies related to this result</h3><p>{virus ? 'A pesticide cannot cure a virus-infected plant. Confirm the diagnosis and discuss management with an agricultural adviser.' : healthy ? 'No disease treatment is indicated by this classification. Continue monitoring.' : 'Confirm the cause before buying a treatment. These are browsing suggestions, not prescriptions.'}</p>
    <ul>{items.map(item => <li key={item.title}><a href={item.url} target="_blank" rel="noopener noreferrer">{item.title} ↗</a><p>{item.note}</p></li>)}</ul><p>External retailer: AgriBegri. Check current product labels, price, stock, delivery and offers there. AgriVision does not verify these or sell products.</p><a href="https://www.agribegri.com/collections/today_offers.php" target="_blank" rel="noopener noreferrer">View retailer offers ↗</a>
  </section>;
}
