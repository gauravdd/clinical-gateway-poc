from app.config import Settings
from app.services.normalizer import normalize_infobip_inbound


def test_normalize_infobip_payload_results_wrapper() -> None:
    settings = Settings(
        INFOBIP_BASE_URL="https://example.api.infobip.com",
        INFOBIP_API_KEY="x",
        CLINIC_SENDER_MAP="whatsapp:+14155550100=clinic-a",
    )

    payload = {
        "results": [
            {
                "channel": "whatsapp",
                "from": "+15550001111",
                "to": "+14155550100",
                "text": "I have a fever",
                "messageId": "m-1",
                "conversationId": "c-1",
            }
        ]
    }

    normalized = normalize_infobip_inbound(payload, settings)

    assert normalized.channel.value == "whatsapp"
    assert normalized.clinic_id == "clinic-a"
    assert normalized.patient_identifier == "+15550001111"
    assert normalized.thread_id == "c-1"
    assert normalized.message_id == "m-1"
    assert normalized.text == "I have a fever"
