"""Tests para descubrir el collector_id desde el token de acceso."""

from __future__ import annotations

import asyncio
import base64
import json
from unittest.mock import AsyncMock

from pagotic import AsyncPagoTIC, PagoTIC


def _make_jwt(payload: dict[str, object]) -> str:
    def encode(value: dict[str, object]) -> str:
        raw = json.dumps(value).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{encode({'alg': 'none'})}.{encode(payload)}.firma"


def test_get_collector_id_uses_signature_claim(monkeypatch) -> None:
    token = _make_jwt({"signature": "14020", "sub": "uuid"})
    sdk = PagoTIC(username="u", password="p", client_id="i", client_secret="s")
    monkeypatch.setattr(sdk._auth, "get_token", lambda: token)

    try:
        assert sdk.get_collector_id() == "14020"
    finally:
        sdk.close()


def test_async_get_collector_id_uses_family_name_claim(monkeypatch) -> None:
    token = _make_jwt({"family_name": "14020"})

    async def scenario() -> str:
        sdk = AsyncPagoTIC(
            username="u",
            password="p",
            client_id="i",
            client_secret="s",
        )
        monkeypatch.setattr(sdk._auth, "get_token", AsyncMock(return_value=token))
        try:
            return await sdk.get_collector_id()
        finally:
            await sdk.aclose()

    assert asyncio.run(scenario()) == "14020"
