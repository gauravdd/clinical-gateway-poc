import asyncio

from app.config import Settings
from app.models.messages import Channel, OutboundMessage
from app.services.infobip_sender import _messages_endpoint


def test_messages_endpoint_builder() -> None:
    assert _messages_endpoint("https://example.api.infobip.com") == "https://example.api.infobip.com/messages-api/1/messages"


def test_outbound_model_shape() -> None:
    outbound = OutboundMessage(
        channel=Channel.WHATSAPP,
        clinic_identifier="+14155550100",
        patient_identifier="+15550001111",
        thread_id="thread-1",
        text="Doctor-verified mock response",
        correlation_id="corr-1",
    )
    assert outbound.channel == Channel.WHATSAPP
    assert outbound.patient_identifier.startswith("+")


def test_settings_minimum_env_contract() -> None:
    settings = Settings(
        INFOBIP_BASE_URL="https://example.api.infobip.com",
        INFOBIP_API_KEY="k",
    )
    assert settings.infobip_base_url.startswith("https://")


async def _dummy() -> int:
    return 1


def test_async_sanity() -> None:
    assert asyncio.run(_dummy()) == 1
