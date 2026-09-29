# Project Rules For Codex

## Product Context

This is an IoT school project using real ESP32 hardware, currently focused on environmental monitoring with DHT11 temperature/humidity data and optional relay control. Do not frame the core MVP as an EV charging station unless the hardware changes.

Current MVP:

- ESP32 publishes temperature, humidity, relay status, and heartbeat through MQTT.
- NestJS receives MQTT telemetry, stores readings, updates device status, evaluates rules, and exposes REST APIs.
- Next.js dashboard displays real-time-ish device, telemetry, alert, and relay-control state.
- A future Python AI service may be added for anomaly detection and forecasting.

## Architecture Rules

- Keep a monorepo layout with `apps/api`, `apps/dashboard`, and later `apps/ai-service`.
- Backend code must be feature-module based. Do not put business logic in `main.ts`, `app.module.ts`, or a giant shared service.
- Use thin controllers. Controllers validate/route requests only; services own business behavior.
- Keep MQTT concerns in `mqtt` module. Do not directly use MQTT clients from unrelated modules.
- Keep database access behind focused repository/service methods. Do not scatter raw Prisma calls across controllers.
- Put reusable helpers in `common` or feature-local helpers when they are truly feature-specific.
- Use TypeORM entities/repositories for persistence. Do not introduce Prisma unless the user explicitly asks to migrate.
- Use explicit DTOs and small mapping functions for data crossing module/API boundaries.
- Avoid premature microservices. Use one NestJS backend process until there is a real scaling or AI reason to split.
- Python belongs in the future AI service only, not in the core telemetry/backend path.
- The AI service boundary lives in `apps/ai-service`; keep it FastAPI/Pydantic-based and replace predictors behind the service contract rather than calling model code from NestJS.

## Code Quality Rules

- Prefer small files with one clear responsibility.
- Keep functions short and name them by intent.
- Avoid duplicate constants for MQTT topics, thresholds, status values, or units.
- Do not hardcode environment-specific values in source code. Use `.env` and config helpers.
- Keep UI components presentational where possible; data fetching belongs in `lib` or feature services.
- Dashboard UI should use Tailwind CSS plus shadcn-style reusable components in `components/ui`.
- Prefer proven UI/data libraries when they reduce custom code: `lucide-react` for icons, `recharts` for charts, `date-fns` for date formatting, and `class-variance-authority`/`tailwind-merge` for component variants.
- Use TypeScript types/interfaces for shared API shapes.
- Do not create decorative abstractions. Create helpers only when they remove real duplication or clarify domain logic.

## IoT Domain Rules

- Preserve IoT-specific features in the project: MQTT topics, heartbeat/last-seen tracking, device online/offline status, relay command path, and sensor threshold alerts.
- Telemetry messages count as heartbeat unless a separate heartbeat topic is introduced later.
- Treat DHT11 readings as low-precision educational readings; avoid pretending they are industrial-grade data.
- Relay control should be demonstrated safely. Do not suggest switching real 220V loads unless safety constraints are explicit.
- If an energy-metering sensor such as PZEM-004T is added later, create a separate metering module rather than mixing it into DHT11 telemetry logic.

## Folder Structure Target

```txt
apps/
  api/
    src/
      common/
      config/
      database/
      features/
        alerts/
        automation/
        dashboard/
        devices/
        mqtt/
        telemetry/
  dashboard/
    src/
      app/
      components/
      features/
      lib/
  ai-service/        # future
infra/
  mosquitto/
docs/
```
