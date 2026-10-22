import { useEffect, useRef, useState } from 'react';
import ResultBox from './ResultBox';
import DiseaseCare from './DiseaseCare';
import { prepareCameraPhoto } from '../utils/cameraPhoto';
import { useI18n } from '../i18n/I18nContext';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

export function formatCategory(category, t) {
  const [crop, condition] = category.split('___');
  const cropKey = crop.startsWith('Tomato')
    ? 'crop.tomato'
    : crop.startsWith('Potato')
      ? 'crop.potato'
      : 'crop.pepper';
  const conditionKeys = {
    healthy: 'disease.healthy',
    Bacterial_spot: 'disease.bacterialSpot',
    Early_blight: 'disease.earlyBlight',
    Late_blight: 'disease.lateBlight',
    Leaf_Mold: 'disease.leafMold',
    Septoria_leaf_spot: 'disease.septoria',
    'Spider_mites Two-spotted_spider_mite': 'disease.spiderMite',
    Target_Spot: 'disease.targetSpot',
    Tomato_Yellow_Leaf_Curl_Virus: 'disease.yellowCurl',
    Tomato_mosaic_virus: 'disease.mosaic',
  };
  return `${t(cropKey)} — ${t(conditionKeys[condition]) || condition.replaceAll('_', ' ')}`;
}

export default function DiseaseCard({ modelStatus, onResultChange, onPredictionComplete }) {
  const { t, locale } = useI18n();
  const [imagePreview, setImagePreview] = useState(null);
  const [fileName, setFileName] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('auto');
  const [selectedFile, setSelectedFile] = useState(null);
  const cameraInput = useRef(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    onResultChange?.(result?.status === 'ok' ? result : null);
  }, [result, onResultChange]);

  useEffect(() => {
    if (!imagePreview) return undefined;
    return () => URL.revokeObjectURL(imagePreview);
  }, [imagePreview]);

  const handleImageChange = async (event, fromCamera = false) => {
    const original = event.target.files?.[0];
    event.target.value = '';
    if (!original) return;
    setResult(null);
    setError('');
    setSelectedFile(null);
    setImagePreview(null);
    setFileName('');
    setLoading(true);
    try {
      const file = fromCamera ? await prepareCameraPhoto(original) : original;
      setSelectedFile(file);
      setFileName(file.name);
      setImagePreview(URL.createObjectURL(file));
    } catch (photoError) {
      setError(photoError.message || 'Could not read this photo. Try a JPG or PNG.');
    } finally {
      setLoading(false);
    }
  };

  const handleCropChange = (event) => {
    const crop = event.target.value;
    setSelectedCrop(crop);
    setResult(null);
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setResult(null);
    setError('');
    if (!['auto', 'tomato', 'potato', 'pepper'].includes(selectedCrop)) {
      setError('unsupported-crop');
      return;
    }
    const file = selectedFile;
    if (!file) {
      setError(t('disease.fileError'));
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      setError(t('disease.sizeError'));
      return;
    }
    if (!modelStatus?.api_available) {
      setError(t('disease.apiError'));
      return;
    }
    if (!modelStatus?.disease_model_available) {
      setResult({ status: 'not_trained', disease: t('disease.notTrained'), confidence: null });
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('crop', selectedCrop);
      const response = await fetch(`${API_BASE}/api/disease/predict`, { method: 'POST', body: formData });
      const data = await response.json();
      if (data?.status === 'not_trained') {
        setResult(data);
      } else if (!response.ok || data?.status !== 'ok') {
        throw new Error(data?.message || `Prediction failed (${response.status}).`);
      } else {
        setResult(data);
        onPredictionComplete?.('disease', data, `Leaf photo · selected crop: ${selectedCrop}`);
      }
    } catch (requestError) {
      setError(requestError.message || 'The model could not produce a prediction.');
    } finally {
      setLoading(false);
    }
  };

  const confidence = result?.confidence == null ? null : result.confidence * 100;

  return (
    <section className="card module-card" id="disease" aria-labelledby="disease-title">
      <div className="card-header">
        <div className="card-icon disease-icon">🔬</div>
        <div>
          <h2 className="card-title" id="disease-title">{t('disease.title')}</h2>
          <p className="card-subtitle">{t('disease.subtitle')}</p>
        </div>
      </div>

      <p className="scope-notice">{t('disease.support')}</p>
      <p className="warning-banner" role="note">{t('disease.validationWarning')}</p>

      {modelStatus?.disease_supported_categories?.length > 0 && (
        <details className="disclosure">
          <summary>{t('disease.conditions')}</summary>
          <ul className="compact-list">
            {modelStatus.disease_supported_categories.map((category) => (
              <li key={category}>{formatCategory(category, t)}</li>
            ))}
          </ul>
        </details>
      )}

      <div className="workbench-grid">
        <div className="workbench-form">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="disease-crop">{t('disease.cropLabel')}</label>
              <select
                id="disease-crop"
                className="form-control"
                value={selectedCrop}
                onChange={handleCropChange}
                disabled={loading}
              >
                <option value="auto">Auto-detect supported crop</option>
                <option value="tomato">{t('disease.tomato')}</option>
                <option value="potato">{t('disease.potato')}</option>
                <option value="pepper">{t('disease.pepper')}</option>
                <option value="unsure">{t('disease.unsure')}</option>
              </select>
              {selectedCrop === 'unsure' && (
                <span className="field-hint" role="status">{t('disease.unsupported')}</span>
              )}
            </div>
            <div className="form-group">
              <label htmlFor="disease-file-input">{t('disease.fileLabel')}</label>
              <div className="file-upload-wrapper">
                <div className={`upload-area ${imagePreview ? 'has-image' : ''}`}>
                  {imagePreview ? (
                    <div className="preview-container">
                      <img src={imagePreview} alt={t('disease.imagePreviewAlt')} className="image-preview" />
                      <span className="file-name">{fileName}</span>
                    </div>
                  ) : (
                    <div className="upload-placeholder">
                      <span className="upload-icon" aria-hidden="true">📷</span>
                      <span className="upload-text">{t('disease.upload')}</span>
                      <span className="upload-hint">{t('disease.uploadHint')}</span>
                    </div>
                  )}
                </div>
                <input
                  id="disease-file-input"
                  name="leaf-image"
                  type="file"
                  accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                  onChange={handleImageChange}
                  disabled={loading}
                />
              </div>
            </div>

            <input ref={cameraInput} type="file" accept="image/jpeg,image/png" capture="environment"
              hidden disabled={loading} aria-label="Take a leaf photo"
              onChange={(event) => handleImageChange(event, true)} />
            <button className="btn" type="button" disabled={loading} onClick={() => cameraInput.current?.click()}>
              Take photo
            </button>
            <p className="field-hint">Use your rear camera for a close-up leaf photo. If camera capture is unavailable, upload a photo. Large camera photos are resized before analysis.</p>
            <p className="field-hint">Automatic detection covers tomato, potato and bell pepper only; it cannot identify tomato varieties, Tulsi or Powdery Mildew.</p>
            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading || !['auto', 'tomato', 'potato', 'pepper'].includes(selectedCrop)}
            >
              {loading ? (
                <span className="btn-loading"><span className="spinner" />{t('disease.analyzing')}</span>
              ) : t('disease.analyze')}
            </button>
          </form>
          {error && (
            <p className="error-msg" role="alert">
              {error === 'unsupported-crop' ? t('disease.unsupported') : error}
            </p>
          )}
        </div>

        <div className="workbench-result" aria-live="polite">
          {result ? (
            <ResultBox title={t('disease.result')}>
              <div className="result-row">
                <span className="result-label">{t('disease.predicted')}</span>
                <span className="result-value disease-name">
                  {modelStatus?.disease_supported_categories?.includes(result.disease)
                    ? formatCategory(result.disease, t)
                    : result.disease || result.message}
                </span>
              </div>
              {confidence != null && (
                <>
                  <div className="result-row">
                    <span className="result-label">{t('disease.score')}</span>
                    <span className="result-value">
                      {confidence.toLocaleString(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%
                    </span>
                  </div>
                  <div
                    className="confidence-bar-bg"
                    role="meter"
                    aria-label={t('disease.score')}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={Math.min(confidence, 100)}
                  >
                    <div className="confidence-bar" style={{ width: `${Math.min(confidence, 100)}%` }} />
                  </div>
                  <details className="disclosure">
                    <summary>{t('disease.modelDetails')}</summary>
                    <div className="result-row">
                      <span className="result-label">{t('disease.modelId')}</span>
                      <span className="result-value">{result.model_id}</span>
                    </div>
                    <div className="result-row">
                      <span className="result-label">{t('disease.inference')}</span>
                      <span className="result-value">{Number(result.inference_ms).toFixed(1)} ms</span>
                    </div>
                  </details>
                  <details className="disclosure" open key={result.disease}>
                    <summary>{t('disease.careDetails')}</summary>
                    {result.guidance && <p className="result-note">{result.guidance}</p>}
                    <DiseaseCare category={result.disease} />
                  </details>
                </>
              )}
              {result.status === 'not_trained' && <div className="status-banner">{t('disease.modelUnavailable')}</div>}
            </ResultBox>
          ) : (
            <div className="empty-state">
              <span className="empty-state-icon" aria-hidden="true">✳</span>
              <p>{t('disease.emptyTitle')}</p>
              <span>{t('disease.emptyHint')}</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
