from ..schemas import PredictionRequest, PredictionResponse


class HeuristicEnvironmentPredictor:
    """Stable AI-module boundary until a trained model artifact is available."""

    model_version = "heuristic-v0"

    def predict(self, payload: PredictionRequest) -> PredictionResponse:
        temperature_score = self._scale(payload.temperature, normal=32, critical=40)
        humidity_score = self._scale(payload.humidity, normal=75, critical=95)
        score = max(temperature_score, humidity_score)

        if score >= 0.75:
            return PredictionResponse(
                is_anomaly=True,
                risk_level="critical",
                anomaly_score=round(score, 3),
                suggested_action="TURN_RELAY_ON",
                reason="Temperature or humidity is far above the expected comfort range.",
                model_version=self.model_version,
            )

        if score >= 0.4:
            return PredictionResponse(
                is_anomaly=True,
                risk_level="warning",
                anomaly_score=round(score, 3),
                suggested_action="TURN_RELAY_ON",
                reason="Environment is drifting above the expected comfort range.",
                model_version=self.model_version,
            )

        return PredictionResponse(
            is_anomaly=False,
            risk_level="normal",
            anomaly_score=round(score, 3),
            suggested_action="NONE",
            reason="Environment is within the expected range.",
            model_version=self.model_version,
        )

    @staticmethod
    def _scale(value: float, normal: float, critical: float) -> float:
        if value <= normal:
            return 0
        if value >= critical:
            return 1
        return (value - normal) / (critical - normal)

