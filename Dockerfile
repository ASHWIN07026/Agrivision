FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm ci
COPY ./frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    PORT=7860

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements-deploy.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt

COPY ./backend/app/ /app/backend/app/
COPY ./models/ /app/models/
COPY ./scripts/download_leaf_validator.py /app/scripts/download_leaf_validator.py
RUN python /app/scripts/download_leaf_validator.py
COPY --from=frontend /build/frontend/dist/ /app/backend/static/

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser
WORKDIR /app/backend

EXPOSE 7860
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1 --limit-concurrency 4"]
