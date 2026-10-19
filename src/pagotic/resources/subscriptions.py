"""Recurso de suscripciones (experimental)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from pagotic.models.base import validate_model
from pagotic.models.subscriptions import (
    Subscription,
    SubscriptionRequest,
    SubscriptionSearchRequest,
)
from pagotic.resources._utils import path_id

if TYPE_CHECKING:
    from pagotic.client import AsyncPagoTIC, PagoTIC


class SubscriptionsResource:
    """Suscripciones. Funcionalidad experimental: solo figura en Postman."""

    def __init__(self, client: PagoTIC) -> None:
        self._client = client

    def create(self, subscription: SubscriptionRequest | Mapping[str, Any]) -> Subscription:
        request = validate_model(SubscriptionRequest, subscription)
        payload = request.model_dump(mode="json", exclude_none=True)
        data = self._client.request("POST", "/suscripciones", json=payload)
        return validate_model(Subscription, data)

    def list(self) -> Any:
        return self._client.request("GET", "/suscripciones/listado")

    def search(
        self,
        query: SubscriptionSearchRequest | Mapping[str, Any] | None = None,
    ) -> Any:
        request = validate_model(SubscriptionSearchRequest, query or {})
        payload = request.model_dump(mode="json", exclude_none=True)
        return self._client.request("POST", "/suscripciones/busqueda", json=payload)

    def cancel(self, subscription_id: str | int, status_detail: str) -> Subscription:
        data = self._client.request(
            "POST",
            f"/suscripciones/cancelar/{path_id(subscription_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Subscription, data)


class AsyncSubscriptionsResource:
    """Versión asincrónica de :class:`SubscriptionsResource`."""

    def __init__(self, client: AsyncPagoTIC) -> None:
        self._client = client

    async def create(self, subscription: SubscriptionRequest | Mapping[str, Any]) -> Subscription:
        request = validate_model(SubscriptionRequest, subscription)
        payload = request.model_dump(mode="json", exclude_none=True)
        data = await self._client.request("POST", "/suscripciones", json=payload)
        return validate_model(Subscription, data)

    async def list(self) -> Any:
        return await self._client.request("GET", "/suscripciones/listado")

    async def search(
        self,
        query: SubscriptionSearchRequest | Mapping[str, Any] | None = None,
    ) -> Any:
        request = validate_model(SubscriptionSearchRequest, query or {})
        payload = request.model_dump(mode="json", exclude_none=True)
        return await self._client.request("POST", "/suscripciones/busqueda", json=payload)

    async def cancel(self, subscription_id: str | int, status_detail: str) -> Subscription:
        data = await self._client.request(
            "POST",
            f"/suscripciones/cancelar/{path_id(subscription_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(Subscription, data)
