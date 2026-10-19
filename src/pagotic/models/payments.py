"""Modelos de pagos y distribución programada."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any

from pydantic import Field, ValidationError, model_validator

from pagotic.enums import (
    DestinationType,
    DistributionType,
    FilterOperation,
    PaymentStatus,
    PaymentType,
    RefundStatus,
    RefundType,
)
from pagotic.exceptions import PagoTICValidationError
from pagotic.models.base import Amount, PagoTICModel
from pagotic.models.common import (
    Carrier,
    CollectorDetail,
    Detail,
    FeeDetail,
    Payer,
    PaymentMethod,
    PaymentMethodInfo,
    Presets,
    RefundInfo,
    RelatedPayment,
    Source,
)
from pagotic.validators import Cuit


class DistributionDestination(PagoTICModel):
    """Cuenta destino de una transferencia programada."""

    type: DestinationType | str = DestinationType.CBU
    value: str
    cuit: Cuit
    name: str


class DistributionDetail(PagoTICModel):
    """Transferencia programada hacia un destino."""

    type: DistributionType | str = DistributionType.SCHEDULED
    amount: Amount = Field(gt=0)
    destination: DistributionDestination


class DistributionTransfer(PagoTICModel):
    """Destinatario de una transferencia programada.

    Reúne los datos que pide PagoTIC para cada destinatario: tipo de
    transferencia, CUIT y CBU de la cuenta, nombre del titular y monto.
    """

    type: DistributionType | str = DistributionType.SCHEDULED
    cuit: Cuit
    cbu: str = Field(min_length=1)
    name: str = Field(min_length=1)
    amount: Amount = Field(gt=0)

    def to_detail(self) -> DistributionDetail:
        """Convierte la transferencia al formato anidado que espera la API."""
        return DistributionDetail(
            type=self.type,
            amount=self.amount,
            destination=DistributionDestination(
                type=DestinationType.CBU,
                value=self.cbu,
                cuit=self.cuit,
                name=self.name,
            ),
        )


class Distribution(PagoTICModel):
    """Distribución de los fondos de un pago entre una o más cuentas."""

    details: list[DistributionDetail] = Field(min_length=1)

    @property
    def total(self) -> Decimal:
        """Suma de los importes de todas las transferencias."""
        return sum((detail.amount for detail in self.details), Decimal("0"))

    @classmethod
    def scheduled(
        cls,
        transfers: Iterable[DistributionTransfer | DistributionDetail | Mapping[str, Any]],
    ) -> Distribution:
        """Atajo para armar una distribución ``scheduled`` a cuentas CBU.

        Cada transferencia puede ser un :class:`DistributionTransfer`, un
        :class:`DistributionDetail` o un mapping con las claves ``cbu``,
        ``cuit``, ``name`` y ``amount``.
        """
        details: list[DistributionDetail] = []
        for transfer in transfers:
            if isinstance(transfer, DistributionDetail):
                details.append(transfer)
                continue
            if isinstance(transfer, DistributionTransfer):
                details.append(transfer.to_detail())
                continue
            try:
                parsed = DistributionTransfer.model_validate(transfer)
            except ValidationError as exc:
                errors = exc.errors()
                detalle = "; ".join(str(error.get("msg", error)) for error in errors)
                raise PagoTICValidationError(
                    f"Transferencia inválida: {detalle}",
                    errors=errors,
                ) from exc
            details.append(parsed.to_detail())
        return cls(details=details)


class PaymentRequest(PagoTICModel):
    """Cuerpo de ``POST /pagos``.

    Si se incluye ``distribution``, la suma de sus importes debe coincidir
    exactamente con la suma de los importes de ``details``.
    """

    type: PaymentType | str | None = None
    collector_id: str | None = None
    return_url: str | None = None
    back_url: str | None = None
    notification_url: str | None = None
    external_transaction_id: str
    currency_id: str | None = None
    details: list[Detail] = Field(min_length=1)
    payment_methods: list[PaymentMethod] | None = None
    payer: Payer
    due_date: str | None = None
    last_due_date: str | None = None
    metadata: dict[str, Any] | None = None
    carrier: Carrier | None = None
    presets: Presets | None = None
    distribution: Distribution | None = None

    @model_validator(mode="after")
    def _validate_distribution_totals(self) -> PaymentRequest:
        if self.distribution is None:
            return self
        payment_total = sum((detail.amount for detail in self.details), Decimal("0"))
        distribution_total = self.distribution.total
        if payment_total != distribution_total:
            raise ValueError(
                "La suma de distribution.details "
                f"({distribution_total}) debe ser igual a la suma de details "
                f"({payment_total})"
            )
        return self


class Payment(PagoTICModel):
    """Pago devuelto por la API."""

    id: str
    external_transaction_id: str | None = None
    collector_id: str | None = None
    collector_detail: CollectorDetail | None = None
    form_url: str | None = None
    details: list[Detail] = Field(default_factory=list)
    currency_id: str | None = None
    payment_methods: list[PaymentMethodInfo] = Field(default_factory=list)
    payer: Payer | None = None
    final_amount: Amount | None = None
    status: PaymentStatus | str | None = None
    status_detail: str | None = None
    validation: bool | str | None = None
    review: bool | str | None = None
    upgradeable: bool | None = None
    request_date: str | None = None
    due_date: str | None = None
    last_due_date: str | None = None
    process_date: str | None = None
    paid_date: str | None = None
    rejected_date: str | None = None
    cancel_date: str | None = None
    objected_date: str | None = None
    accreditation_date: str | None = None
    review_validation_date: str | None = None
    payer_validation_date: str | None = None
    payer_deferred_date: str | None = None
    last_update_date: str | None = None
    metadata: dict[str, Any] | None = None
    carrier: Carrier | None = None
    source: Source | None = None
    fee_details: list[FeeDetail] = Field(default_factory=list)
    refunds: list[RefundInfo] = Field(default_factory=list)
    relateds: list[RelatedPayment] = Field(default_factory=list)
    distribution: Distribution | None = None

    @property
    def raw_qr(self) -> str | None:
        """Primer ``raw_qr`` disponible del pago.

        La API lo devuelve dentro de ``payment_methods[]`` (o a nivel raíz en
        las notificaciones). Devuelve ``None`` si el pago no tiene un QR.
        """
        extra = self.model_extra or {}
        top_level = extra.get("raw_qr")
        if isinstance(top_level, str) and top_level:
            return top_level
        for method in self.payment_methods:
            if method.raw_qr:
                return method.raw_qr
        return None


class PaymentSearchRequest(PagoTICModel):
    """Cuerpo de ``POST /pagos/busqueda`` (búsqueda legacy)."""

    type: PaymentType | str | None = None
    status: PaymentStatus | str | None = None
    details_external_reference: str | None = None
    details_concept_id: int | str | None = None
    details_concept_description: str | None = None
    payer_name: str | None = None
    payer_external_reference: str | None = None
    payer_email: str | None = None
    payer_identification_number: str | None = None
    payment_methods_card_last_four_numbers: str | None = None


class Filter(PagoTICModel):
    """Filtro de un listado paginado."""

    field: str
    operation: FilterOperation | str = FilterOperation.EQUAL
    value: Any


class RefundRequest(PagoTICModel):
    """Cuerpo de ``POST /pagos/devolucion/{id}``."""

    type: RefundType | str = RefundType.ONLINE
    status_detail: str | None = None
    external_reference: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] | None = None


class RefundResponse(PagoTICModel):
    """Respuesta de una devolución."""

    id: str | None = None
    status: RefundStatus | str | None = None
    type: RefundType | str | None = None
    status_detail: str | None = None
    reference: str | None = None
    external_reference: str | None = None
    amount: Amount | None = None
    reason: str | None = None
    fee_details: list[FeeDetail] = Field(default_factory=list)
    source: Source | None = None
    metadata: dict[str, Any] | None = None
