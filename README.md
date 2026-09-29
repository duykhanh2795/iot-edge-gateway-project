# IoT Environmental Monitoring Dashboard

Clean monorepo starter for an ESP32-based IoT course project.

## MVP Scope

- ESP32 + DHT11 publishes environmental telemetry through MQTT.
- NestJS gateway receives MQTT messages from the local edge broker, stores telemetry, tracks device status, evaluates threshold alerts, exposes dashboard APIs, and can bridge processed telemetry to a cloud broker.
- Next.js dashboard displays devices, latest readings, alerts, and relay state.
- Python AI service provides an inference boundary for anomaly/risk scoring. The current predictor is deterministic and will be replaced by a trained model later.

## Repository Layout

```txt
apps/
  api/          NestJS backend
  ai-service/   Python FastAPI AI boundary
  dashboard/    Next.js dashboard
docs/           architecture notes
infra/          local infrastructure config
work/           scratch/context notes
```

## Local Services

Start Docker Desktop first, then run:

```bash
docker compose up -d
```

This starts:

- PostgreSQL on `localhost:5432`
- Mosquitto MQTT edge broker on `localhost:1883`
- AI service on `localhost:8000`

## Development

```bash
npm install
npm run dev
```

Backend API: `http://localhost:3001`

Dashboard: `http://localhost:3000`

AI service: `http://localhost:8000/health`

The dashboard uses Tailwind CSS, shadcn-style local UI components, Recharts, Lucide icons, and date-fns.

If the API does not listen on `localhost:3001`, check that Docker Desktop is running and that PostgreSQL is healthy:

```bash
docker compose ps
npm run dev:api
```

The backend uses TypeORM with `synchronize=true` for the local school-project MVP. Replace this with migrations before a production-style deployment.

## CloudBridge Mode

The local edge broker is still used for ESP32-to-gateway traffic. CloudBridge publishes processed telemetry from the NestJS gateway to a public cloud MQTT broker such as HiveMQ Cloud.

```txt
ESP32 -> local Mosquitto -> NestJS Gateway -> HiveMQ Cloud
```

Set these environment variables for HiveMQ Cloud:

```env
CLOUD_MQTT_ENABLED=true
CLOUD_MQTT_URL=mqtts://your-cluster.s1.eu.hivemq.cloud:8883
CLOUD_MQTT_USERNAME=your-hivemq-username
CLOUD_MQTT_PASSWORD=your-hivemq-password
```

Cloud topics:

```txt
cloud/iot/devices/{deviceId}/telemetry
cloud/iot/gateways/{gatewayId}/status
```

## MQTT Topics

Telemetry from ESP32:

```txt
iot/devices/{deviceId}/telemetry
```

Control command to ESP32:

```txt
iot/devices/{deviceId}/control
```

Example telemetry payload:

```json
{
  "temperature": 30.5,
  "humidity": 72,
  "relayStatus": "OFF",
  "timestamp": "2026-09-14T13:30:00.000Z"
}
```
