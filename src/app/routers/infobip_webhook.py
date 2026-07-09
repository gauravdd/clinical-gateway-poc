from __future__ import annotations

import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import Settings, get_settings
from app.models.messages import OutboundMessage
from app.services.clinical_backend_client import ClinicalBackend
from app.services.idempotency import InMemoryIdempotencyStore
from app.services.infobip_sender import send_outbound
from app.services.normalizer import normalize_infobip_inbound

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
idempotency_store = InMemoryIdempotencyStore()
clinical_backend = ClinicalBackend()
logger = logging.getLogger(__name__)


@router.post("/infobip/inbound")
async def infobip_inbound(request: Request, settings: Settings = Depends(get_settings)) -> dict:
    payload = await request.json()
    inbound = normalize_infobip_inbound(payload, settings)
    logger.info(
        "Received Infobip webhook",
        extra={
            "message_id": inbound.message_id,
            "thread_id": inbound.thread_id,
            "clinic_id": inbound.clinic_id,
            "patient_id": inbound.patient_id,
            "channel": inbound.channel.value,
        },
    )

    if not idempotency_store.add_if_new(inbound.message_id):
        logger.info("Skipped duplicate Infobip webhook", extra={"message_id": inbound.message_id})
        return {"status": "duplicate", "message_id": inbound.message_id}

    correlation_id = str(uuid.uuid4())

    processed = clinical_backend.process_packet(inbound)
    outbound = OutboundMessage(
        channel=inbound.channel,
        clinic_identifier=inbound.clinic_identifier,
        patient_identifier=inbound.patient_identifier,
        thread_id=inbound.thread_id,
        text=processed["reply_text"],
        correlation_id=correlation_id,
    )

    async with httpx.AsyncClient() as client:
        try:
            provider_result = await send_outbound(outbound, settings, client)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"infobip outbound error: {exc}") from exc

    logger.info(
        "Sent outbound reply via Infobip",
        extra={
            "message_id": inbound.message_id,
            "correlation_id": correlation_id,
            "clinic_id": inbound.clinic_id,
            "patient_id": inbound.patient_id,
            "channel": inbound.channel.value,
        },
    )

    return {
        "status": "sent",
        "message_id": inbound.message_id,
        "correlation_id": correlation_id,
        "processed": processed,
        "provider_result": provider_result,
    }
