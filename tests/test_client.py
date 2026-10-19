"""Tests del cliente HTTP: reintentos, cierre y configuración."""

from __future__ import annotations

import httpx
import pytest

from pagotic import PagoTIC, PagoTICAPIError
from tests.conftest import (
    CLIENT_ID,
    CLIENT_SECRET,
    PASSWORD,
    PAYMENT_JSON,
    PAYMENT_REQUEST,
    USERNAME,
    mock_token,
)


def _retry_client() -> PagoTIC:
    return PagoTIC(
        USERNAME,
        PASSWORD,
        CLIENT_ID,
        CLIENT_SECRET,
        max_retries=1,
        retry_backoff=0,
        token_leeway=0,
    )


def test_get_retries_on_5xx(mock_router) -> None:
    mock_token(mock_router)
    route = mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=[
            httpx.Response(500, json={"code": 5001, "message": "internal"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    with _retry_client() as sdk:
        payment = sdk.payments.get("pay-1")

    assert payment.id == "pay-1"
    assert route.call_count == 2


def test_post_is_not_retried(mock_router) -> None:
    mock_token(mock_router)
    route = mock_router.post("https://api.paypertic.com/pagos").mock(
        side_effect=[
            httpx.Response(500, json={"code": 5001, "message": "internal"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    with _retry_client() as sdk, pytest.raises(PagoTICAPIError):
        sdk.payments.create(PAYMENT_REQUEST)

    assert route.call_count == 1


def test_custom_http_client_is_not_closed(mock_router) -> None:
    http_client = httpx.Client()
    sdk = PagoTIC(
        USERNAME,
        PASSWORD,
        CLIENT_ID,
        CLIENT_SECRET,
        http_client=http_client,
    )
    try:
        sdk.close()
        assert not http_client.is_closed
    finally:
        http_client.close()


def test_owned_http_client_is_closed() -> None:
    sdk = PagoTIC(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET)
    sdk.close()
    assert sdk._http.is_closed


def test_repr_does_not_expose_secrets() -> None:
    sdk = PagoTIC(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET)
    try:
        text = repr(sdk)
        assert PASSWORD not in text
        assert CLIENT_SECRET not in text
        assert "https://api.paypertic.com" in text
    finally:
        sdk.close()


def test_settings_property() -> None:
    with PagoTIC(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET) as sdk:
        assert sdk.settings.timeout == 30.0
        assert sdk.settings.realm == "entidades"
