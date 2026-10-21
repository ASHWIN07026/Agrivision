/**
 * api.js – centralised API service layer for all backend calls.
 * All components should call these functions instead of raw fetch().
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export async function predictDisease(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  const res = await fetch(`${BASE_URL}/api/disease/predict`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error(`Disease API error: ${res.status}`);
  return res.json();
}

export async function predictYield({ country, crop, year }) {
  const formData = new FormData();
  formData.append('crop', crop);
  formData.append('country', country);
  formData.append('year', year);
  const res = await fetch(`${BASE_URL}/api/yield/predict`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error(`Yield API error: ${res.status}`);
  return res.json();
}

export async function getMarketPrice(crop, region = 'India') {
  const res = await fetch(`${BASE_URL}/api/market/price?crop=${encodeURIComponent(crop)}&region=${encodeURIComponent(region)}`);
  if (!res.ok) throw new Error(`Market API error: ${res.status}`);
  return res.json();
}
