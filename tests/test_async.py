"""Tests del cliente asincrónico."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from pagotic import AsyncPagoTIC, PagoTICAPIError
from tests.conftest import (
    CLIENT_ID,
    CLIENT_SECRET,
    PASSWORD,
    PAYMENT_JSON,
    PAYMENT_REQUEST,
    USERNAME,
    mock_json,
    mock_token,
    request_json,
)


def _client() -> AsyncPagoTIC:
    return AsyncPagoTIC(
        USERNAME,
        PASSWORD,
        CLIENT_ID,
        CLIENT_SECRET,
        max_retries=0,
        retry_backoff=0,
        token_leeway=0,
    )


def test_async_get(mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)

    async def run() -> str:
        async with _client() as sdk:
            payment = await sdk.payments.get("pay-1")
            return payment.id

    assert asyncio.run(run()) == "pay-1"


def test_async_create(mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos", PAYMENT_JSON)

    async def run() -> str:
        async with _client() as sdk:
            payment = await sdk.payments.create(PAYMENT_REQUEST)
            return payment.id

    assert asyncio.run(run()) == "pay-1"
    assert request_json(route.calls.last.request) == PAYMENT_REQUEST


def test_async_401_retries(mock_router) -> None:
    token_route = mock_token(mock_router)
    pay_route = mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=[
            httpx.Response(401, json={"error": "unauthorized"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    async def run() -> str:
        async with _client() as sdk:
            payment = await sdk.payments.get("pay-1")
            return payment.id

    assert asyncio.run(run()) == "pay-1"
    assert token_route.call_count == 2
    assert pay_route.call_count == 2


def test_async_api_error(mock_router) -> None:
    mock_token(mock_router)
    mock_json(
        mock_router,
        "GET",
        "/pagos/nope",
        {"code": 4001, "message": "invalid payment id", "extended_code": 4001},
        status=400,
    )

    async def run() -> None:
        async with _client() as sdk:
            with pytest.raises(PagoTICAPIError) as exc_info:
                await sdk.payments.get("nope")
            assert exc_info.value.code == 4001

    asyncio.run(run())


def test_async_payment_operations(mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "GET", "/pagos/pay-1", PAYMENT_JSON)
    mock_json(mock_router, "POST", "/pagos/busqueda", {"results": []})
    mock_json(mock_router, "GET", "/pagos", {"results": []})
    mock_json(mock_router, "POST", "/pagos/cancelar/pay-1", PAYMENT_JSON)
    mock_json(mock_router, "POST", "/pagos/cancelar-objecion/pay-1", PAYMENT_JSON)
    mock_json(mock_router, "POST", "/pagos/agrupar", PAYMENT_JSON)
    mock_json(mock_router, "POST", "/pagos/cancelar-agrupacion/group-1", PAYMENT_JSON)
    mock_json(
        mock_router,
        "POST",
        "/pagos/devolucion/pay-1",
        {"id": "refund-1", "status": "approved"},
    )

    async def run() -> None:
        async with _client() as sdk:
            assert (await sdk.payments.get("pay-1")).id == "pay-1"
            assert await sdk.payments.search({"status": "approved"}) == {"results": []}
            assert await sdk.payments.list(page=1) == {"results": []}
            assert (await sdk.payments.cancel("pay-1", "x")).id == "pay-1"
            assert (await sdk.payments.cancel_objection("pay-1", "x")).id == "pay-1"
            assert (await sdk.payments.group(["pay-1", "pay-2"])).id == "pay-1"
            assert (await sdk.payments.cancel_group("group-1", "x")).id == "pay-1"
            assert (await sdk.payments.refund("pay-1")).id == "refund-1"

    asyncio.run(run())


def test_async_create_coupon(mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos", PAYMENT_JSON)

    async def run() -> None:
        async with _client() as sdk:
            coupon = await sdk.payments.create_coupon(PAYMENT_REQUEST, media_payment_id=98)
            assert coupon.id == "pay-1"

    asyncio.run(run())
    assert request_json(route.calls.last.request)["type"] == "coupon"


def test_async_imports(mock_router) -> None:
    mock_token(mock_router)
    summary = {"import_id": "imp-1", "status": "PENDING"}
    mock_json(mock_router, "POST", "/importaciones/pagos", summary)
    mock_json(mock_router, "GET", "/importaciones/pagos", [summary])
    mock_json(mock_router, "GET", "/importaciones/pagos/imp-1", summary)
    mock_json(
        mock_router,
        "GET",
        "/importaciones/pagos/imp-1/detalles",
        [{"external_reference": "ref-1"}],
    )
    mock_json(mock_router, "POST", "/importaciones/pagos/aprobar/imp-1", summary)
    mock_json(mock_router, "POST", "/importaciones/pagos/cancelar/imp-1", summary)
    mock_json(mock_router, "GET", "/importar/ver/imp-1", summary)
    mock_json(mock_router, "POST", "/importar/aprobar/imp-1", summary)
    mock_json(mock_router, "POST", "/importar/cancelar/imp-1", summary)

    async def run() -> None:
        async with _client() as sdk:
            assert (await sdk.imports.preimport(b"data", match_payer=True)).import_id == "imp-1"
            assert await sdk.imports.list() == [summary]
            assert (await sdk.imports.get("imp-1")).import_id == "imp-1"
            assert (await sdk.imports.details("imp-1"))[0].external_reference == "ref-1"
            assert (await sdk.imports.approve("imp-1")).import_id == "imp-1"
            assert (await sdk.imports.cancel("imp-1", "x")).import_id == "imp-1"
            assert (await sdk.imports.verify_legacy("imp-1")).import_id == "imp-1"
            assert (await sdk.imports.approve_legacy("imp-1")).import_id == "imp-1"
            assert (await sdk.imports.cancel_legacy("imp-1", "x")).import_id == "imp-1"

    asyncio.run(run())


def test_async_subscriptions(mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "POST", "/suscripciones", {"id": "sub-1"})
    mock_json(mock_router, "GET", "/suscripciones/listado", {"results": []})
    mock_json(mock_router, "POST", "/suscripciones/busqueda", {"results": []})
    mock_json(mock_router, "POST", "/suscripciones/cancelar/sub-1", {"id": "sub-1"})

    async def run() -> None:
        async with _client() as sdk:
            assert (
                await sdk.subscriptions.create(
                    {
                        "detail": {"amount": 10},
                        "payment_method": {},
                        "payer": {"name": "Ana"},
                    }
                )
            ).id == "sub-1"
            assert await sdk.subscriptions.list() == {"results": []}
            assert await sdk.subscriptions.search({}) == {"results": []}
            assert (await sdk.subscriptions.cancel("sub-1", "x")).id == "sub-1"

    asyncio.run(run())


def test_async_retry_on_5xx(mock_router) -> None:
    mock_token(mock_router)
    route = mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=[
            httpx.Response(500, json={"code": 5001, "message": "internal"}),
            httpx.Response(200, json=PAYMENT_JSON),
        ]
    )

    async def run() -> str:
        sdk = AsyncPagoTIC(
            USERNAME,
            PASSWORD,
            CLIENT_ID,
            CLIENT_SECRET,
            max_retries=1,
            retry_backoff=0,
            token_leeway=0,
        )
        async with sdk:
            return (await sdk.payments.get("pay-1")).id

    assert asyncio.run(run()) == "pay-1"
    assert route.call_count == 2


def test_async_connection_error(mock_router) -> None:
    mock_token(mock_router)
    mock_router.get("https://api.paypertic.com/pagos/pay-1").mock(
        side_effect=httpx.ConnectError("sin red")
    )

    async def run() -> None:
        async with _client() as sdk:
            with pytest.raises(Exception, match="No se pudo conectar"):
                await sdk.payments.get("pay-1")

    asyncio.run(run())


def test_async_repr() -> None:
    sdk = _client()
    try:
        assert "AsyncPagoTIC" in repr(sdk)
    finally:
        asyncio.run(sdk.aclose())
