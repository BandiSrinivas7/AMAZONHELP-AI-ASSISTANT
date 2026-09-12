# AmazonHelp AI Backend

Standalone FastAPI backend for the BrandSupport-AI project.

## Run

From this directory:

```bash
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Endpoints:

- `GET /health`
- `POST /api/support`

Example:

```bash
curl -X POST http://localhost:8000/api/support \
  -H "Content-Type: application/json" \
  -d '{"message":"My package says delivered but I cannot find it","top_k":5}'
```

The supplied trained intent model and train-only retrieval corpus are included under `data/processed/`.

## Architecture

Customer message → intent classifier → hybrid retrieval → grounded reply generation → AUTO-HANDLE / ESCALATE.

The existing project deliberately does not perform account actions, order lookups, refunds, payments, or autonomous public posting.
