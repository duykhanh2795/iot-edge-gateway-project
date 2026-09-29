# Architecture Notes

## Why NestJS + Future Python AI

NestJS is the primary backend because the current project needs API structure, MQTT ingestion, device management, relay commands, WebSocket-ready dashboard integration, and clean TypeScript boundaries.

Python should be introduced later as a separate AI service when there is enough stored telemetry to train or evaluate anomaly detection/forecasting. Keeping AI separate avoids mixing model code with the operational backend.

## Backend Modules

- `mqtt`: owns broker connection, topic naming, publish/subscribe behavior.
- `telemetry`: validates and stores incoming sensor readings.
- `devices`: owns device state, last seen timestamp, relay state, and status.
- `automation`: evaluates domain rules, such as high humidity or high temperature.
- `alerts`: creates and lists environment/device alerts.
- `dashboard`: composes read models for the UI.
- `cloud-bridge`: publishes processed telemetry from the local gateway to a public cloud MQTT broker such as HiveMQ Cloud.
- `database`: wraps TypeORM datasource configuration.

## Topic Contract

Telemetry topic:

```txt
iot/devices/{deviceId}/telemetry
```

Control topic:

```txt
iot/devices/{deviceId}/control
```

## AI Service

The Python FastAPI service is a real module boundary for anomaly detection and future forecasting.

Current flow:

```txt
NestJS telemetry ingestion -> Python AI service /predict -> TypeORM telemetry AI fields -> Dashboard
```

The current predictor is deterministic (`heuristic-v0`) so that the contract is stable before training. A trained model can replace `HeuristicEnvironmentPredictor` later without changing NestJS or dashboard contracts.

## Edge Gateway And CloudBridge

The project uses two MQTT layers when CloudBridge is enabled:

```txt
[ESP32 nodes] -> [Local MQTT Broker] -> [NestJS Gateway] -> [Cloud MQTT Broker]
                    Edge layer             Bridge logic          Cloud layer
```

Local broker:

- Mosquitto by default for stable classroom demos.
- Handles ESP32 telemetry and command/control topics on the local WiFi network.

Cloud broker:

- HiveMQ Cloud or another public MQTT broker.
- Receives processed telemetry after AI inference and gateway enrichment.

The gateway service is responsible for controlling what leaves the edge network. Raw device traffic is not blindly mirrored; the bridge publishes normalized payloads with `gatewayId`, telemetry id, timestamps, relay state, and AI result.

## Dashboard Libraries

- Tailwind CSS for styling.
- shadcn-style local UI components in `src/components/ui`.
- `lucide-react` for icons.
- `recharts` for telemetry charts.
- `date-fns` for human-readable timestamps.
