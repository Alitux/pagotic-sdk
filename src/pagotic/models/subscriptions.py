"""Modelos de suscripciones (experimental)."""

from __future__ import annotations

from typing import Any

from pagotic.enums import PaymentStatus, Recurrence
from pagotic.models.base import Amount, PagoTICModel
from pagotic.models.common import Holder, Payer, Source


class SubscriptionDetail(PagoTICModel):
    """Detalle que se cobra en cada período."""

    external_reference: str | None = None
    concept_id: int | str | None = None
    concept_description: str | None = None
    amount: Amount


class SubscriptionPaymentMethod(PagoTICModel):
    """Tarjeta asociada a la suscripción."""

    number: str | None = None
    holder: Holder | None = None


class SubscriptionRequest(PagoTICModel):
    """Cuerpo de ``POST /suscripciones``."""

    type: str = "subscription"
    currency_id: str | None = None
    due_day: str | int | None = None
    recurrence: Recurrence | str = Recurrence.MONTHLY
    notification_url: str | None = None
    detail: SubscriptionDetail
    payment_method: SubscriptionPaymentMethod
    payer: Payer
    metadata: dict[str, Any] | None = None


class Subscription(PagoTICModel):
    """Suscripción devuelta por la API."""

    id: str | None = None
    external_reference: str | None = None
    status: PaymentStatus | str | None = None
    status_detail: str | None = None
    currency_id: str | None = None
    due_day: str | int | None = None
    recurrence: Recurrence | str | None = None
    detail: SubscriptionDetail | None = None
    payment_method: SubscriptionPaymentMethod | None = None
    payer: Payer | None = None
    source: Source | None = None
    request_date: str | None = None
    last_update_date: str | None = None
    metadata: dict[str, Any] | None = None


class SubscriptionSearchRequest(PagoTICModel):
    """Cuerpo de ``POST /suscripciones/busqueda``."""

    type: str | None = None
    status: PaymentStatus | str | None = None
    detail_external_reference: str | None = None
    detail_concept_id: int | str | None = None
    detail_concept_description: str | None = None
    payer_name: str | None = None
    payer_external_reference: str | None = None
    payer_email: str | None = None
    payer_identification_number: str | None = None
    payment_method_card_last_four_digits: str | None = None
