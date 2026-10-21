# data/processed

Place **pre-processed, model-ready** data here after running the preprocessing scripts.

## Expected contents

| File | Description |
|---|---|
| `X_train.npy` | Training images (numpy array, shape: N×64×64×3) |
| `y_train.npy` | Training labels (numpy array, shape: N,) |
| `X_val.npy` | Validation images |
| `y_val.npy` | Validation labels |
| `yield_features.csv` | Feature-engineered yield dataset |

Run `ml/training/run_all_training.py` to populate this folder automatically.
