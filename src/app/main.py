from __future__ import annotations

import logging
import sys

from fastapi import FastAPI

from app.config import get_settings
from app.routers.infobip_webhook import router as webhook_router


class PrettyFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = f"{record.levelname:<8} {record.name}: {record.getMessage()}"
        fields = []
        for field_name in ("message_id", "thread_id", "clinic_id", "patient_id", "channel", "correlation_id"):
            value = getattr(record, field_name, None)
            if value not in (None, ""):
                fields.append(f"{field_name}={value}")
        if fields:
            base = f"{base} | " + " ".join(fields)
        return base


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(PrettyFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


configure_logging()

app = FastAPI(title=get_settings().app_name)
app.include_router(webhook_router)


@app.get("/")
def root() -> dict:
    return {
        "service": "Clinical Gateway Proto",
        "status": "ok",
        "endpoints": ["/healthz", "/webhooks/infobip/inbound"],
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
