# IoT AI Service

FastAPI service that defines the AI boundary for environmental anomaly detection.

This first version intentionally uses a deterministic heuristic predictor. It is not presented as a trained model yet. The goal is to make the AI module contract real and stable before replacing the implementation with a trained model artifact later.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `POST /predict`

Example:

```json
{
  "device_id": "esp32_001",
  "temperature": 29.3,
  "humidity": 56,
  "relay_status": "OFF",
  "observed_at": "2026-09-14T14:00:00.000Z"
}
```

