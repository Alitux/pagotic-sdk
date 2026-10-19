"""Tests de suscripciones (experimental)."""

from __future__ import annotations

from tests.conftest import mock_json, mock_token, request_json

SUBSCRIPTION_REQUEST = {
    "currency_id": "ARS",
    "due_day": "30",
    "recurrence": "monthly",
    "detail": {
        "external_reference": "plan-1",
        "concept_description": "Plan mensual",
        "amount": 5000,
    },
    "payment_method": {
        "number": "4111111111111111",
        "holder": {
            "name": "Ana Pérez",
            "identification": {"type": "DNI_ARG", "number": "12345678", "country": "ARG"},
        },
    },
    "payer": {"name": "Ana Pérez", "email": "ana@example.com"},
}


def test_create_subscription(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/suscripciones",
        {"id": "sub-1", "status": "pending", "recurrence": "monthly"},
    )

    subscription = client.subscriptions.create(SUBSCRIPTION_REQUEST)

    assert subscription.id == "sub-1"
    body = request_json(route.calls.last.request)
    assert body["type"] == "subscription"
    assert body["detail"]["amount"] == 5000.0


def test_list_subscriptions(client, mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "GET", "/suscripciones/listado", {"results": []})

    result = client.subscriptions.list()

    assert result == {"results": []}


def test_search_subscriptions(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/suscripciones/busqueda", {"results": []})

    client.subscriptions.search({"payer_email": "ana@example.com"})

    assert request_json(route.calls.last.request) == {"payer_email": "ana@example.com"}


def test_cancel_subscription(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/suscripciones/cancelar/sub-1",
        {"id": "sub-1", "status": "cancelled"},
    )

    subscription = client.subscriptions.cancel("sub-1", "Baja")

    assert subscription.status == "cancelled"
    assert request_json(route.calls.last.request) == {"status_detail": "Baja"}
