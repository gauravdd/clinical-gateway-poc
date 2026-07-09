from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Channel(str, Enum):
    WHATSAPP = "whatsapp"
    LINE = "line"
    ZALO = "zalo"
    MESSENGER = "messenger"
    UNKNOWN = "unknown"


class IdentifierType(str, Enum):
    PHONE_NUMBER = "PHONE_NUMBER"


class NormalizedInboundMessage(BaseModel):
    channel: Channel
    clinic_id: str
    clinic_id_type: IdentifierType = IdentifierType.PHONE_NUMBER
    clinic_identifier: str = Field(description="Channel sender ID or phone")
    patient_id: str
    patient_id_type: IdentifierType = IdentifierType.PHONE_NUMBER
    patient_identifier: str = Field(description="Patient phone number")
    thread_id: str
    message_id: str
    text: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: dict = Field(default_factory=dict)


class OutboundMessage(BaseModel):
    channel: Channel
    clinic_identifier: str
    patient_identifier: str
    thread_id: str
    text: str
    correlation_id: str
