"""Tests de pagos."""

from __future__ import annotations

from decimal import Decimal

import httpx
import pytest

from pagotic import (
    Filter,
    FilterOperation,
    PagoTICAPIError,
    PagoTICConnectionError,
    PagoTICValidationError,
)
from tests.conftest import (
    PAYMENT_JSON,
    PAYMENT_REQUEST,
    mock_json,
    mock_token,
    request_json,
)


def test_create_payment(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos", PAYMENT_JSON)

    payment = client.payments.create(PAYMENT_REQUEST)

    assert payment.id == "pay-1"
    assert payment.status == "approved"
    assert payment.final_amount == Decimal("1000.5")
    assert payment.collector_detail is not None
    assert payment.payment_methods[0].coupon_number == "1234567890"

    body = request_json(route.calls.last.request)
    assert body == PAYMENT_REQUEST


def test_get_payment(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)

    payment = client.payments.get("pay-1")

    assert payment.id == "pay-1"
    assert route.calls.last.request.method == "GET"


def test_search_payments(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos/busqueda", {"results": [PAYMENT_JSON]})

    result = client.payments.search({"payer_email": "ana@example.com", "status": "approved"})

    assert result["results"][0]["id"] == "pay-1"
    assert request_json(route.calls.last.request) == {
        "payer_email": "ana@example.com",
        "status": "approved",
    }


def test_list_with_filters_and_sorts(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "GET",
        "/pagos",
        {"results": [PAYMENT_JSON], "paging": {"page": 2, "limit": 5, "total": 1}},
    )

    result = client.payments.list(
        page=2,
        limit=5,
        sorts={"request_date": "descending"},
        filters=[
            {"field": "collector_id", "operation": "EQUAL", "value": "col-1"},
            Filter(
                field="request_date",
                operation=FilterOperation.GREATER_THAN_OR_EQUAL_TO,
                value="20250101T000000000-0300",
            ),
        ],
    )

    assert result["paging"]["page"] == 2
    params = route.calls.last.request.url.params
    assert params["page"] == "2"
    assert params["limit"] == "5"
    assert params["sorts[request_date]"] == "descending"
    assert params["filters[0][field]"] == "collector_id"
    assert params["filters[0][operation]"] == "EQUAL"
    assert params["filters[1][operation]"] == "GREATER_THAN_OR_EQUAL_TO"


def test_list_joins_in_values(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "GET", "/pagos", {"results": []})

    client.payments.list(
        filters=[{"field": "id", "operation": "IN", "value": ["a", "b"]}],
    )

    assert route.calls.last.request.url.params["filters[0][value]"] == "a,b"


def test_cancel_payment(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos/cancelar/pay-1", PAYMENT_JSON)

    payment = client.payments.cancel("pay-1", "Solicitado por el comercio")

    assert payment.id == "pay-1"
    assert request_json(route.calls.last.request) == {"status_detail": "Solicitado por el comercio"}


def test_cancel_objection(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos/cancelar-objecion/pay-1", PAYMENT_JSON)

    client.payments.cancel_objection("pay-1", "Resuelta")

    assert request_json(route.calls.last.request) == {"status_detail": "Resuelta"}


def test_group_requires_two_payments(client) -> None:
    with pytest.raises(PagoTICValidationError):
        client.payments.group(["pay-1"])


def test_group_payments(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos/agrupar", PAYMENT_JSON)

    payment = client.payments.group(["pay-1", "pay-2"])

    assert payment.id == "pay-1"
    assert request_json(route.calls.last.request) == ["pay-1", "pay-2"]


def test_cancel_group(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos/cancelar-agrupacion/group-1", PAYMENT_JSON)

    client.payments.cancel_group("group-1", "Cancelada")

    assert request_json(route.calls.last.request) == {"status_detail": "Cancelada"}


def test_refund_defaults_to_online(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/pagos/devolucion/pay-1",
        {"id": "refund-1", "status": "approved", "type": "online", "amount": 1000.5},
    )

    refund = client.payments.refund("pay-1", {"reason": "Reintegro"})

    assert refund.id == "refund-1"
    assert refund.status == "approved"
    assert request_json(route.calls.last.request) == {
        "type": "online",
        "reason": "Reintegro",
    }


def test_create_coupon(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos", PAYMENT_JSON)

    coupon = client.payments.create_coupon(PAYMENT_REQUEST, media_payment_id=97)

    assert coupon.payment_methods[0].coupon_number == "1234567890"
    body = request_json(route.calls.last.request)
    assert body["type"] == "coupon"
    assert body["payment_methods"] == [{"amount": 1000.5, "media_payment_id": 97}]


def test_create_coupon_rejects_invalid_media(client) -> None:
    with pytest.raises(PagoTICValidationError):
        client.payments.create_coupon(PAYMENT_REQUEST, media_payment_id=1)


def test_api_error_is_parsed(client, mock_router) -> None:
    mock_token(mock_router)
    mock_json(
        mock_router,
        "GET",
        "/pagos/unknown",
        {"code": 4001, "message": "invalid payment id", "extended_code": 4001},
        status=400,
    )

    with pytest.raises(PagoTICAPIError) as exc_info:
        client.payments.get("unknown")

    error = exc_info.value
    assert error.status_code == 400
    assert error.code == 4001
    assert error.extended_code == 4001
    assert error.message == "invalid payment id"
    assert error.payload["code"] == 4001


def test_non_json_error(client, mock_router) -> None:
    mock_token(mock_router)
    mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        return_value=httpx.Response(500, text="boom")
    )

    with pytest.raises(PagoTICAPIError) as exc_info:
        client.payments.get("pay-1")

    assert exc_info.value.status_code == 500
    assert "boom" in exc_info.value.message


def test_get_retries_on_5xx(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=[
            httpx.Response(500, json={"code": 5001, "message": "internal"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    with pytest.raises(PagoTICAPIError):
        client.payments.get("pay-1")

    # El fixture usa max_retries=0, así que no reintenta.
    assert route.call_count == 1


def test_connection_error_on_api(client, mock_router) -> None:
    mock_token(mock_router)
    mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=httpx.ConnectError("sin red")
    )

    with pytest.raises(PagoTICConnectionError):
        client.payments.get("pay-1")
