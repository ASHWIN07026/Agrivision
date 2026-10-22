import DetectedSupplies from './DetectedSupplies';
import { useId } from 'react';
import CareProtocol from './CareProtocol';
import ShopSearch from './ShopSearch';
import { useI18n } from '../i18n/I18nContext';

const TOMATO = 'https://ipm.ucanr.edu/agriculture/tomato/';
const POTATO = 'https://ipm.ucanr.edu/agriculture/potato/';
const PEPPER = 'https://ipm.ucanr.edu/agriculture/peppers/';
const TNAU_MOSAIC = 'https://agritech.tnau.ac.in/crop_protection/tomato_diseases_12.html';
const TNAU_SEPTORIA = 'https://agritech.tnau.ac.in/crop_protection/tomato_diseases_4.html';

export default function DiseaseCare({ category }) {
  const { t } = useI18n();
  const shopId = useId();
  if (!category || !category.includes('___')) return null;
  const healthy = category.endsWith('___healthy');
  const crop = category.startsWith('Potato') ? 'potato' : category.startsWith('Pepper') ? 'peppers' : 'tomato';
  let source = crop === 'potato' ? POTATO : crop === 'peppers' ? PEPPER : TOMATO;
  let steps = [t('care.confirm'), t('care.inspect')];
  let supplies = [t('care.handLens'), t('care.tools')];
  if (healthy) {
    steps = [t('care.healthyOne'), t('care.healthyTwo')];
    supplies = [t('care.monitoringLens')];
  } else if (category.includes('Bacterial_spot')) {
    source += 'bacterial-spot/';
    steps.push(t('care.bacterial'));
  } else if (category.includes('Early_blight') || category.includes('Late_blight')) {
    source += category.includes('Early_blight') ? 'early-blight/' : 'late-blight/';
    steps.push(t('care.blight'));
  } else if (category.includes('Yellow_Leaf_Curl')) {
    source = 'https://agritech.tnau.ac.in/crop_protection/tomato_diseases_6.html';
    steps.push(t('care.yellowCurl'));
    supplies = [t('care.stickyTraps'), t('care.undersideLens')];
  } else if (category.includes('mosaic_virus')) {
    source = TNAU_MOSAIC;
    steps.push(t('care.mosaic'));
  } else if (category.includes('Septoria')) {
    source = TNAU_SEPTORIA;
  }

  return (
    <section className="result-note care-details" aria-label={t('disease.careDetails')}>
      <h3>{healthy ? t('care.healthyTitle') : t('care.nextTitle')}</h3>
      <p>{t('care.disclaimer')}</p>
      {category === 'Tomato___Early_blight' && <CareProtocol protocolId="tomato_early_blight" title="Tomato — Early Blight: step-by-step care" />}
      <ol>{steps.map((step) => <li key={step}>{step}</li>)}</ol>
      <p><a href={source} target="_blank" rel="noopener noreferrer">{t('care.cropGuide')}</a></p>
      <p>{t('care.regionalNote')}</p>
      <h3>{t('care.supplies')}</h3>
      <ul>{supplies.map((item) => <li key={item}>{item}</li>)}</ul>
      <DetectedSupplies category={category} />
      <ShopSearch idPrefix={shopId} />
    </section>
  );
}
