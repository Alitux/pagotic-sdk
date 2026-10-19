"""Tests de autenticación, caché y renovación de tokens."""

from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from pagotic import (
    PagoTIC,
    PagoTICAuthError,
    PagoTICConfigError,
    PagoTICConnectionError,
)
from tests.conftest import (
    CLIENT_ID,
    CLIENT_SECRET,
    PASSWORD,
    PAYMENT_JSON,
    TOKEN_URL,
    USERNAME,
    mock_json,
    mock_token,
    token_payload,
)


def test_login_is_cached(client, mock_router) -> None:
    token_route = mock_token(mock_router)
    pay_route = mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)

    client.payments.get("pay-1")
    client.payments.get("pay-1")

    assert token_route.call_count == 1
    assert pay_route.calls[0].request.headers["Authorization"] == "Bearer access-1"


def test_expired_access_token_uses_refresh(client, mock_router) -> None:
    token_route = mock_router.post(TOKEN_URL).mock(
        side_effect=[
            httpx.Response(200, json=token_payload(access_token="access-1", expires_in=0)),
            httpx.Response(200, json=token_payload(access_token="access-2", expires_in=300)),
        ]
    )
    pay_route = mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)

    client.payments.get("pay-1")
    client.payments.get("pay-1")

    assert token_route.call_count == 2
    forms = [parse_qs(call.request.content.decode()) for call in token_route.calls]
    assert forms[0]["grant_type"] == ["password"]
    assert forms[1]["grant_type"] == ["refresh_token"]
    assert forms[1]["refresh_token"] == ["refresh-1"]
    assert pay_route.calls[1].request.headers["Authorization"] == "Bearer access-2"


def test_refresh_failure_falls_back_to_password(client, mock_router) -> None:
    token_route = mock_router.post(TOKEN_URL).mock(
        side_effect=[
            httpx.Response(200, json=token_payload(access_token="access-1", expires_in=0)),
            httpx.Response(
                400,
                json={"error": "invalid_grant", "error_description": "Invalid refresh token"},
            ),
            httpx.Response(200, json=token_payload(access_token="access-2", expires_in=300)),
        ]
    )
    mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)

    client.payments.get("pay-1")
    client.payments.get("pay-1")

    assert token_route.call_count == 3
    forms = [parse_qs(call.request.content.decode()) for call in token_route.calls]
    assert forms[1]["grant_type"] == ["refresh_token"]
    assert forms[2]["grant_type"] == ["password"]


def test_401_reauthenticates_and_retries(client, mock_router) -> None:
    token_route = mock_token(mock_router)
    pay_route = mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=[
            httpx.Response(401, json={"error": "unauthorized"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    payment = client.payments.get("pay-1")

    assert payment.id == "pay-1"
    assert token_route.call_count == 2
    assert pay_route.call_count == 2
    assert pay_route.calls[1].request.headers["Authorization"] == "Bearer access-1"


def test_auth_error_is_parsed(client, mock_router) -> None:
    mock_router.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            401,
            json={
                "error": "invalid_grant",
                "error_description": "Invalid user credentials",
            },
        )
    )

    with pytest.raises(PagoTICAuthError) as exc_info:
        client.payments.get("pay-1")

    error = exc_info.value
    assert error.error == "invalid_grant"
    assert error.description == "Invalid user credentials"
    assert error.status_code == 401
    assert "Invalid user credentials" in str(error)


def test_connection_error_in_auth(client, mock_router) -> None:
    mock_router.post(TOKEN_URL).mock(side_effect=httpx.ConnectError("sin red"))

    with pytest.raises(PagoTICConnectionError) as exc_info:
        client.payments.get("pay-1")

    assert exc_info.value.original is not None


def test_missing_credentials(monkeypatch) -> None:
    for name in (
        "PAGOTIC_USERNAME",
        "PAGOTIC_PASSWORD",
        "PAGOTIC_CLIENT_ID",
        "PAGOTIC_CLIENT_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(PagoTICConfigError):
        PagoTIC()


def test_credentials_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("PAGOTIC_USERNAME", "env-user")
    monkeypatch.setenv("PAGOTIC_PASSWORD", "env-pass")
    monkeypatch.setenv("PAGOTIC_CLIENT_ID", "env-id")
    monkeypatch.setenv("PAGOTIC_CLIENT_SECRET", "env-secret")

    sdk = PagoTIC()
    try:
        assert sdk.settings.username == "env-user"
        assert sdk.settings.client_id == "env-id"
        assert sdk.settings.token_url == TOKEN_URL
    finally:
        sdk.close()


def test_invalid_configuration() -> None:
    with pytest.raises(PagoTICConfigError):
        PagoTIC(
            USERNAME,
            PASSWORD,
            CLIENT_ID,
            CLIENT_SECRET,
            timeout=0,
        )
    with pytest.raises(PagoTICConfigError):
        PagoTIC(
            USERNAME,
            PASSWORD,
            CLIENT_ID,
            CLIENT_SECRET,
            max_retries=-1,
        )
