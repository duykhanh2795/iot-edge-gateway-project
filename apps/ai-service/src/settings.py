from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "iot-ai-service"

    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")


settings = Settings()

