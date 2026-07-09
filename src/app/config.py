from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Clinical Gateway Proto"
    infobip_base_url: str = Field(default="https://your-domain.api.infobip.com", alias="INFOBIP_BASE_URL")
    infobip_api_key: str = Field(default="replace-me", alias="INFOBIP_API_KEY")
    infobip_webhook_secret: str | None = Field(default=None, alias="INFOBIP_WEBHOOK_SECRET")
    clinic_sender_map: str = Field(default="", alias="CLINIC_SENDER_MAP")

    def parse_clinic_sender_map(self) -> dict[tuple[str, str], str]:
        mapping: dict[tuple[str, str], str] = {}
        if not self.clinic_sender_map.strip():
            return mapping

        for item in self.clinic_sender_map.split(","):
            raw = item.strip()
            if not raw:
                continue
            key, clinic = raw.split("=")
            channel, sender = key.split(":")
            mapping[(channel.strip().lower(), sender.strip())] = clinic.strip()
        return mapping


@lru_cache
def get_settings() -> Settings:
    return Settings()
