"""Modelos compartidos entre pagos, importaciones y suscripciones."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from pagotic.enums import (
    FeePayer,
    FeeType,
    IdentificationType,
    SourceType,
)
from pagotic.models.base import Amount, PagoTICModel


class Identification(PagoTICModel):
    """Documento del pagador o del titular de la tarjeta."""

    type: IdentificationType | str | None = None
    number: str | None = None
    country: str | None = None


class Phone(PagoTICModel):
    """Teléfono de contacto del pagador."""

    description: str | None = None
    country_code: str | None = None
    area_code: str | None = None
    number: str | None = None
    extension: str | None = None


class Payer(PagoTICModel):
    """Pagador de una operación."""

    id: str | None = None
    external_reference: str | None = None
    name: str
    email: str | None = None
    identification: Identification | None = None
    phones: list[Phone] | None = None


class Holder(PagoTICModel):
    """Titular de una tarjeta."""

    name: str | None = None
    identification: Identification | None = None


class Detail(PagoTICModel):
    """Detalle (concepto) de un pago."""

    external_reference: str | None = None
    concept_id: int | str | None = None
    concept_description: str | None = None
    amount: Amount
    rate: float | None = None
    charge_delay: int | None = None


class PaymentMethod(PagoTICModel):
    """Medio de pago enviado al crear una operación."""

    authorization_transaction_id: str | None = None
    amount: Amount | None = None
    media_payment_id: int | None = None
    number: str | None = None
    installments: int | None = None
    promotion_id: int | None = None
    expiration_year: int | None = None
    expiration_month: int | None = None
    security_code: str | None = None
    holder: Holder | None = None


class Gateway(PagoTICModel):
    """Datos de la pasarela o terminal que procesó el pago."""

    establishment_number: str | None = None
    merchant_id: str | None = None
    transaction_id: str | None = None
    batch_number: str | None = None
    ticket_number: str | None = None


class PaymentMethodInfo(PagoTICModel):
    """Medio de pago tal como lo devuelve la API."""

    amount: Amount | None = None
    final_amount: Amount | None = None
    media_payment_id: int | None = None
    payment_method_id: int | str | None = None
    gateway: Gateway | None = None
    coupon_number: str | None = None
    raw_qr: str | None = None
    first_six_digits: str | None = None
    last_four_digits: str | None = None
    installments: int | None = None
    promotion_id: int | None = None
    expiration_year: int | None = None
    expiration_month: int | None = None
    authorization_code: str | None = None
    ticket_number: str | None = None
    holder: Holder | None = None


class PresetAction(PagoTICModel):
    """Acción configurable de un preset."""

    retry: bool | None = None


class Presets(PagoTICModel):
    """Presets de medios de pago para el checkout."""

    media_payment_ids: list[int] | None = None
    type: str | None = None
    promotion_ids: list[int] | None = None
    installments: int | None = None
    actions: list[PresetAction] | None = None


class FeeDetail(PagoTICModel):
    """Comisión o descuento aplicado a una operación."""

    type: FeeType | str | None = None
    fee_payer: FeePayer | str | None = None
    description: str | None = None
    amount: Amount | None = None


class Source(PagoTICModel):
    """Origen de una acción, devolución o pago."""

    id: str | None = None
    name: str | None = None
    type: SourceType | str | None = None


class CollectorDetail(PagoTICModel):
    """Datos del comercio cobrador."""

    name: str | None = None


class RefundInfo(PagoTICModel):
    """Devolución embebida en la respuesta de un pago."""

    id: str | None = None
    amount: Amount | None = None
    status: str | None = None
    type: str | None = None
    source: Source | None = None
    metadata: dict[str, Any] | None = None


class RelatedPayment(PagoTICModel):
    """Pago relacionado (por ejemplo, una agrupación)."""

    type: str | None = None
    payment_id: str | None = None


class Carrier(PagoTICModel):
    """Datos del carrier o transportador."""

    id: str | None = None
    name: str | None = None
    type: str | None = None


class Pagination(PagoTICModel):
    """Metadatos de paginación cuando la API los incluye."""

    page: int | None = None
    limit: int | None = None
    total: int | None = None
    total_pages: int | None = None


class ListResponse(PagoTICModel):
    """Respuesta genérica para listados paginados."""

    results: list[dict[str, Any]] = Field(default_factory=list)
    paging: Pagination | None = None
