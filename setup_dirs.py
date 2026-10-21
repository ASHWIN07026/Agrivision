import os

dirs = [
    "backend/app/api",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/repositories",
    "backend/app/ml",
    "backend/app/integrations",
    "backend/app/utils",
    "ml/disease",
    "ml/yield",
    "ml/notebooks",
    "ml/training",
    "ml/evaluation",
    "data/raw",
    "data/processed",
    "data/knowledge",
    "data/cache",
    "supabase/migrations",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/layouts",
    "frontend/src/hooks",
    "frontend/src/services",
    "frontend/src/store",
    "frontend/src/i18n",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
