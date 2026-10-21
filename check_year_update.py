import sys,json,hashlib,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'backend'))
from fastapi.testclient import TestClient
from app.main import app
from app.services.yield_service import predict_yield as direct
with TestClient(app) as c:
 o=c.get('/api/yield/options').json(); lo,hi=o['accepted_prediction_year_range']; print('options',json.dumps({k:v for k,v in o.items() if 'range' in k}))
 for y in [2012,2016,2024,2026,2027,hi]:
  r=c.post('/api/yield/predict',data={'country':'India','crop':'Maize (corn)','year':y}); d=r.json()
  assert r.status_code==200,(y,d)
  assert d['estimate_type']==('experimental' if y>2024 else 'historical')
  assert d['future_accuracy_validated'] is False
  if y==2016:assert d['expected_yield_kg_per_hectare']==5949.99
  assert direct('India','Maize (corn)',y)['estimate_type']==d['estimate_type']
  print(y,d['expected_yield_kg_per_hectare'],d['estimate_label'])
 for y in [lo-1,hi+1]:
  assert c.post('/api/yield/predict',data={'country':'India','crop':'Maize (corn)','year':y}).status_code==422
 assert c.post('/api/yield/predict',data={'country':'invalid','crop':'Maize (corn)','year':2026}).status_code==422
 print('year boundaries, invalid country, helper/API consistency PASS')
