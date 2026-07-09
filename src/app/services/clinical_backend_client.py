from __future__ import annotations

import logging
import random
import uuid

from app.models.messages import NormalizedInboundMessage


logger = logging.getLogger(__name__)


class ClinicalBackend:
    _dummy_replies = (
        "Thanks for the message. We received your inquiry  Please wait for the clinician follow-up.",
        "We have captured the request and attached the original message metadata.",
    )

    def process_packet(self, inbound: NormalizedInboundMessage) -> dict:
        logger.info(
            "Received inbound packet",
            extra={
                "message_id": inbound.message_id,
                "thread_id": inbound.thread_id,
                "clinic_id": inbound.clinic_id,
                "patient_id": inbound.patient_id,
                "channel": inbound.channel.value,
            },
        )

        reply_text = random.choice(self._dummy_replies)
        dummy_message_id = uuid.uuid4().hex

        return {
            "dummy_message": {
                "message_id": dummy_message_id,
                "text": reply_text,
            },
            "source_message": {
                "message_id": inbound.message_id,
                "thread_id": inbound.thread_id,
                "clinic_id": inbound.clinic_id,
                "clinic_identifier": inbound.clinic_identifier,
                "patient_id": inbound.patient_id,
                "patient_identifier": inbound.patient_identifier,
                "channel": inbound.channel.value,
                "text": inbound.text,
            },
            "reply_text": f"{reply_text} Ref: {inbound.message_id}",
        }
