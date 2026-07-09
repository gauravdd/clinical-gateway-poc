from __future__ import annotations

import httpx

from app.config import Settings
from app.models.messages import OutboundMessage


def _messages_endpoint(base_url: str) -> str:
    normalized = base_url.strip()
    if not normalized.startswith(("http://", "https://")):
        normalized = f"https://{normalized}"
    return f"{normalized.rstrip('/')}/messages-api/1/messages"


def _provider_channel(channel_value: str) -> str:
    mapping = {
        "whatsapp": "WHATSAPP",
        "messenger": "MESSENGER",
        "line": "LINE_ON",
        "zalo": "ZALO",
    }
    return mapping.get(channel_value.lower(), channel_value.upper())


async def send_outbound(
    outbound: OutboundMessage,
    settings: Settings,
    client: httpx.AsyncClient,
) -> dict:
    request_body = {
        "messages": [
            {
                "channel": _provider_channel(outbound.channel.value),
                "sender": outbound.clinic_identifier,
                "destinations": [{"to": outbound.patient_identifier}],
                "content": {
                    "body": {
                        "text": outbound.text,
                        "type": "TEXT",
                    }
                },
            }
        ]
    }
    headers = {
        "Authorization": f"App {settings.infobip_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = await client.post(_messages_endpoint(settings.infobip_base_url), json=request_body, headers=headers, timeout=10)
    if response.is_error:
        detail = response.text.strip() or "no response body"
        raise httpx.HTTPStatusError(
            f"{response.status_code} {response.reason_phrase}; infobip response: {detail}",
            request=response.request,
            response=response,
        )
    return response.json()
