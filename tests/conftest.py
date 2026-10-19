"""Fixtures compartidas por los tests."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
import respx
from dotenv import load_dotenv

from pagotic import PagoTIC

load_dotenv()

API_URL = "https://api.paypertic.com"
AUTH_URL = "https://a.paypertic.com"
TOKEN_URL = f"{AUTH_URL}/auth/realms/entidades/protocol/openid-connect/token"

USERNAME = "test-user"
PASSWORD = "test-password"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"


def token_payload(
    *,
    access_token: str = "access-1",
    refresh_token: str = "refresh-1",
    expires_in: int = 300,
) -> dict[str, Any]:
    return {
        "access_token": access_token,
        "expires_in": expires_in,
        "refresh_token": refresh_token,
        "refresh_expires_in": 1800,
        "token_type": "bearer",
        "not-before-policy": 0,
        "session_state": "session-1",
    }


PAYMENT_JSON: dict[str, Any] = {
    "id": "pay-1",
    "external_transaction_id": "ext-1",
    "collector_id": "col-1",
    "collector_detail": {"name": "Comercio de prueba"},
    "form_url": "https://checkout.example/pay-1",
    "currency_id": "ARS",
    "details": [
        {
            "external_reference": "ref-1",
            "concept_id": 920,
            "concept_description": "Servicio",
            "amount": 1000.5,
        }
    ],
    "payment_methods": [
        {
            "amount": 1000.5,
            "final_amount": 1000.5,
            "media_payment_id": 97,
            "payment_method_id": 1,
            "coupon_number": "1234567890",
            "gateway": {"transaction_id": "gw-1"},
        }
    ],
    "payer": {
        "name": "Ana Pérez",
        "email": "ana@example.com",
        "identification": {"type": "DNI_ARG", "number": "12345678", "country": "ARG"},
    },
    "final_amount": 1000.5,
    "status": "approved",
    "status_detail": "accredited",
    "request_date": "2025-01-01T10:00:00-0300",
    "paid_date": "2025-01-01T10:05:00-0300",
    "fee_details": [
        {"type": "fee", "fee_payer": "collector", "description": "Comisión", "amount": 10.0}
    ],
    "refunds": [],
    "relateds": [],
}

PAYMENT_REQUEST: dict[str, Any] = {
    "external_transaction_id": "ext-1",
    "currency_id": "ARS",
    "notification_url": "https://example.com/webhooks/pagotic",
    "details": [
        {
            "external_reference": "ref-1",
            "concept_id": 920,
            "concept_description": "Servicio",
            "amount": 1000.5,
        }
    ],
    "payer": {
        "name": "Ana Pérez",
        "email": "ana@example.com",
        "identification": {"type": "DNI_ARG", "number": "12345678", "country": "ARG"},
    },
}


@pytest.fixture
def mock_router() -> Iterator[respx.MockRouter]:
    """Router de respx que intercepta todas las requests."""
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def client() -> Iterator[PagoTIC]:
    """Cliente sincrónico con credenciales de prueba."""
    with PagoTIC(
        USERNAME,
        PASSWORD,
        CLIENT_ID,
        CLIENT_SECRET,
        max_retries=0,
        retry_backoff=0,
        token_leeway=0,
    ) as sdk:
        yield sdk


def request_json(request: httpx.Request) -> Any:
    """Decodifica el body JSON de un request capturado por respx."""
    return json.loads(request.content)


def mock_token(router: respx.MockRouter, **kwargs: Any) -> respx.Route:
    return router.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json=token_payload(**kwargs))
    )


def mock_json(
    router: respx.MockRouter,
    method: str,
    path: str,
    data: Any,
    *,
    status: int = 200,
) -> respx.Route:
    return router.request(method, f"{API_URL}{path}").mock(
        return_value=httpx.Response(status, json=data)
    )
