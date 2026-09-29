from fastapi import FastAPI

from .schemas import HealthResponse, PredictionRequest, PredictionResponse
from .settings import settings
from .services.predictor import HeuristicEnvironmentPredictor

app = FastAPI(
    title=settings.service_name,
    version="0.1.0",
    description="AI boundary service for IoT environmental anomaly detection.",
)
predictor = HeuristicEnvironmentPredictor()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.service_name)


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    return predictor.predict(payload)

