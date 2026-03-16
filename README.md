# EchoCheck

EchoCheck is a micro-SaaS foundation for:
- GEO AI visibility tracking
- Video content repurposing workflows

Current scaffold includes:
- FastAPI API service
- Celery worker service
- React + Vite + TanStack web shell
- Core planning and architecture docs

## Repository Layout
- apps/api: FastAPI service
- apps/worker: Celery worker
- apps/web: React frontend
- packages/shared: shared contracts
- docs: architecture and scope documents

## Quick Start

### 1) Start local dependencies
```bash
docker compose up -d
```

### 2) Run API
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3) Run worker
```bash
cd apps/worker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
celery -A worker.celery_app.celery_app worker --loglevel=info
```

### 4) Run frontend
```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173 and http://localhost:8000/health.

### 5) Run API smoke test
```bash
python3 tests/smoke/test_api_smoke.py
```

Optional custom API URL:
```bash
python3 tests/smoke/test_api_smoke.py --base-url http://localhost:8000
```

## Tests

Install dev test tooling:
```bash
pip install -r requirements-dev.txt
```

Pytest markers:
```bash
pytest -m unit tests/unit
pytest -m api tests/api
pytest -m smoke tests/smoke
```

Nox sessions:
```bash
nox -s unit
nox -s api
nox -s smoke
nox -s all_tests
```

Note: `nox -s smoke` expects a running API at `http://localhost:8000` by default.
Set `SMOKE_BASE_URL` to target another environment.
