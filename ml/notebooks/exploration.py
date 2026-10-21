"""Dataset exploration script for real AgriVision training.

This script intentionally avoids fabricated class counts. It exits with clear
instructions when the required public datasets are not present.
"""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / 'data' / 'raw'

print('=== AgriVision Dataset Exploration ===')
print('This environment does not contain the required real datasets.')
print()
print(f'Expected dataset directories under: {DATA_DIR}')
print('  - PlantVillage/ (Kaggle subset for disease training)')
print('  - yield_historical.csv (crop yield labels)')
print()
plantvillage = DATA_DIR / 'PlantVillage'
if not plantvillage.exists():
    print('Status: PlantVillage dataset missing')
else:
    print(f'Status: PlantVillage dataset found at {plantvillage}')

yield_csv = DATA_DIR / 'yield_historical.csv'
if not yield_csv.exists():
    print('Status: yield_historical.csv missing')
else:
    print(f'Status: yield data found at {yield_csv}')

print()
print('Next step: download the real datasets, then run the training scripts in ml/disease and ml/yield.')
