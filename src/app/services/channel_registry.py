from __future__ import annotations

from app.models.messages import Channel


class ChannelRegistry:
    @staticmethod
    def normalize(channel_value: str | None) -> Channel:
        if not channel_value:
            return Channel.UNKNOWN
        value = channel_value.lower().strip()
        if value == Channel.WHATSAPP.value:
            return Channel.WHATSAPP
        if value == Channel.LINE.value:
            return Channel.LINE
        if value == Channel.ZALO.value:
            return Channel.ZALO
        if value in {"facebook-messenger", "messenger"}:
            return Channel.MESSENGER
        return Channel.UNKNOWN
