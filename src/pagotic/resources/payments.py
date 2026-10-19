"""Recurso de pagos."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from pagotic.enums import PaymentType, RefundType
from pagotic.exceptions import PagoTICValidationError
from pagotic.models.base import validate_model
from pagotic.models.payments import (
    Filter,
    Payment,
    PaymentRequest,
    PaymentSearchRequest,
    RefundRequest,
    RefundResponse,
)
from pagotic.resources._utils import build_query_params, path_id

if TYPE_CHECKING:
    from pagotic.client import AsyncPagoTIC, PagoTIC

COUPON_MEDIA_PAYMENT_IDS = frozenset({97, 98})


def _payment_payload(payment: PaymentRequest | Mapping[str, Any]) -> dict[str, Any]:
    request = validate_model(PaymentRequest, payment)
    return request.model_dump(mode="json", exclude_none=True)


class PaymentsResource:
    """Operaciones sobre pagos."""

    def __init__(self, client: PagoTIC) -> None:
        self._client = client

    def create(self, payment: PaymentRequest | Mapping[str, Any]) -> Payment:
        """Crea un pago con ``POST /pagos``."""
        data = self._client.request("POST", "/pagos", json=_payment_payload(payment))
        return validate_model(Payment, data)

    def create_coupon(
        self,
        payment: PaymentRequest | Mapping[str, Any],
        *,
        media_payment_id: int = 97,
    ) -> Payment:
        """Crea un cupón (Rapipago 97 o Pago Fácil 98).

        Reemplaza ``type`` por ``coupon`` y arma ``payment_methods`` con el
        importe total de los detalles.
        """
        if media_payment_id not in COUPON_MEDIA_PAYMENT_IDS:
            raise PagoTICValidationError(
                "media_payment_id debe ser 97 (Rapipago) u 98 (Pago Fácil)"
            )
        request = validate_model(PaymentRequest, payment)
        total = sum((detail.amount for detail in request.details), Decimal("0"))
        payload = request.model_dump(mode="json", exclude_none=True)
        payload["type"] = PaymentType.COUPON.value
        payload["payment_methods"] = [
            {"amount": float(total), "media_payment_id": media_payment_id}
        ]
        data = self._client.request("POST", "/pagos", json=payload)
        return validate_model(Payment, data)

    def get(self, payment_id: str | int) -> Payment:
        """Obtiene un pago por ID."""
        data = self._client.request("GET", f"/pagos/{path_id(payment_id)}")
        return validate_model(Payment, data)

    def search(
        self,
        query: PaymentSearchRequest | Mapping[str, Any] | None = None,
    ) -> Any:
        """Búsqueda legacy con ``POST /pagos/busqueda``."""
        request = validate_model(PaymentSearchRequest, query or {})
        payload = request.model_dump(mode="json", exclude_none=True)
        return self._client.request("POST", "/pagos/busqueda", json=payload)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> Any:
        """Lista pagos con filtros, orden y paginación."""
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        return self._client.request("GET", "/pagos", params=params)

    def cancel(self, payment_id: str | int, status_detail: str) -> Payment:
        """Cancela un pago en estado ``pending`` o ``issued``."""
        data = self._client.request(
            "POST",
            f"/pagos/cancelar/{path_id(payment_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    def cancel_objection(self, payment_id: str | int, status_detail: str) -> Payment:
        """Cancela la objeción de un pago en estado ``objected``."""
        data = self._client.request(
            "POST",
            f"/pagos/cancelar-objecion/{path_id(payment_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    def group(self, payment_ids: Sequence[str | int]) -> Payment:
        """Agrupa dos o más pagos."""
        if len(payment_ids) < 2:
            raise PagoTICValidationError("Se requieren al menos dos pagos para agrupar")
        data = self._client.request("POST", "/pagos/agrupar", json=list(payment_ids))
        return validate_model(Payment, data)

    def cancel_group(self, group_id: str | int, status_detail: str) -> Payment:
        """Cancela una agrupación de pagos."""
        data = self._client.request(
            "POST",
            f"/pagos/cancelar-agrupacion/{path_id(group_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    def refund(
        self,
        payment_id: str | int,
        refund: RefundRequest | Mapping[str, Any] | None = None,
    ) -> RefundResponse:
        """Solicita una devolución (por defecto ``type='online'``)."""
        request = validate_model(RefundRequest, refund or {"type": RefundType.ONLINE})
        payload = request.model_dump(mode="json", exclude_none=True)
        data = self._client.request(
            "POST",
            f"/pagos/devolucion/{path_id(payment_id)}",
            json=payload,
        )
        return validate_model(RefundResponse, data)


class AsyncPaymentsResource:
    """Operaciones asincrónicas sobre pagos."""

    def __init__(self, client: AsyncPagoTIC) -> None:
        self._client = client

    async def create(self, payment: PaymentRequest | Mapping[str, Any]) -> Payment:
        data = await self._client.request("POST", "/pagos", json=_payment_payload(payment))
        return validate_model(Payment, data)

    async def create_coupon(
        self,
        payment: PaymentRequest | Mapping[str, Any],
        *,
        media_payment_id: int = 97,
    ) -> Payment:
        if media_payment_id not in COUPON_MEDIA_PAYMENT_IDS:
            raise PagoTICValidationError(
                "media_payment_id debe ser 97 (Rapipago) u 98 (Pago Fácil)"
            )
        request = validate_model(PaymentRequest, payment)
        total = sum((detail.amount for detail in request.details), Decimal("0"))
        payload = request.model_dump(mode="json", exclude_none=True)
        payload["type"] = PaymentType.COUPON.value
        payload["payment_methods"] = [
            {"amount": float(total), "media_payment_id": media_payment_id}
        ]
        data = await self._client.request("POST", "/pagos", json=payload)
        return validate_model(Payment, data)

    async def get(self, payment_id: str | int) -> Payment:
        data = await self._client.request("GET", f"/pagos/{path_id(payment_id)}")
        return validate_model(Payment, data)

    async def search(
        self,
        query: PaymentSearchRequest | Mapping[str, Any] | None = None,
    ) -> Any:
        request = validate_model(PaymentSearchRequest, query or {})
        payload = request.model_dump(mode="json", exclude_none=True)
        return await self._client.request("POST", "/pagos/busqueda", json=payload)

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> Any:
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        return await self._client.request("GET", "/pagos", params=params)

    async def cancel(self, payment_id: str | int, status_detail: str) -> Payment:
        data = await self._client.request(
            "POST",
            f"/pagos/cancelar/{path_id(payment_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    async def cancel_objection(self, payment_id: str | int, status_detail: str) -> Payment:
        data = await self._client.request(
            "POST",
            f"/pagos/cancelar-objecion/{path_id(payment_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    async def group(self, payment_ids: Sequence[str | int]) -> Payment:
        if len(payment_ids) < 2:
            raise PagoTICValidationError("Se requieren al menos dos pagos para agrupar")
        data = await self._client.request("POST", "/pagos/agrupar", json=list(payment_ids))
        return validate_model(Payment, data)

    async def cancel_group(self, group_id: str | int, status_detail: str) -> Payment:
        data = await self._client.request(
            "POST",
            f"/pagos/cancelar-agrupacion/{path_id(group_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Payment, data)

    async def refund(
        self,
        payment_id: str | int,
        refund: RefundRequest | Mapping[str, Any] | None = None,
    ) -> RefundResponse:
        request = validate_model(RefundRequest, refund or {"type": RefundType.ONLINE})
        payload = request.model_dump(mode="json", exclude_none=True)
        data = await self._client.request(
            "POST",
            f"/pagos/devolucion/{path_id(payment_id)}",
            json=payload,
        )
        return validate_model(RefundResponse, data)
