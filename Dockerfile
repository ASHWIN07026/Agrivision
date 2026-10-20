FROM python:3.12-slim-bookworm AS source
WORKDIR /source
COPY AgriVision_Render_Free.zip /tmp/project.zip
RUN python -c "import zipfile; zipfile.ZipFile('/tmp/project.zip').extractall('/source')"

FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY --from=source /source/frontend/package.json /source/frontend/package-lock.json ./
RUN npm ci
COPY --from=source /source/frontend/ ./
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

COPY --from=source /source/backend/requirements-deploy.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt

COPY --from=source /source/backend/app/ /app/backend/app/
COPY --from=source /source/models/ /app/models/
COPY --from=frontend /build/frontend/dist/ /app/backend/static/

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser
WORKDIR /app/backend

EXPOSE 7860
CMD ["sh", "-c", "exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1 --limit-concurrency 4"]
