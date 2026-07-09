from __future__ import annotations


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def add_if_new(self, key: str) -> bool:
        if key in self._seen:
            return False
        self._seen.add(key)
        return True
