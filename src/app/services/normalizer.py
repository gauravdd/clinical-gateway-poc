from __future__ import annotations

from app.config import Settings
from app.models.messages import Channel, IdentifierType, NormalizedInboundMessage
from app.services.channel_registry import ChannelRegistry


def normalize_infobip_inbound(payload: dict, settings: Settings) -> NormalizedInboundMessage:
    # Support both direct payload and Infobip-style results wrapper.
    message = payload
    if isinstance(payload.get("results"), list) and payload["results"]:
        message = payload["results"][0]

    channel = ChannelRegistry.normalize(message.get("channel") or payload.get("channel"))
    from_id = message.get("from") or message.get("fromNumber") or ""
    to_id = message.get("to") or message.get("toNumber") or ""
    text = message.get("text") or message.get("message") or ""
    message_id = str(message.get("messageId") or message.get("id") or "")
    thread_id = str(message.get("conversationId") or message_id or from_id)

    clinic_map = settings.parse_clinic_sender_map()
    clinic_id = clinic_map.get((channel.value, to_id), to_id or "unknown-clinic")

    return NormalizedInboundMessage(
        channel=channel,
        clinic_id=clinic_id,
        clinic_identifier=to_id or clinic_id,
        clinic_id_type=IdentifierType.PHONE_NUMBER,
        patient_id=f"{channel.value}:{from_id}",
        patient_id_type=IdentifierType.PHONE_NUMBER,
        patient_identifier=from_id,
        thread_id=thread_id,
        message_id=message_id or thread_id,
        text=text,
        raw_payload=payload,
    )
