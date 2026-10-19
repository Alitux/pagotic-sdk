"""Modelos de pagos y distribución programada."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any

from pydantic import Field, model_validator

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


class DistributionDestination(PagoTICModel):
    """Cuenta destino de una transferencia programada."""

    type: DestinationType | str = DestinationType.CBU
    value: str
    cuit: str
    name: str


class DistributionDetail(PagoTICModel):
    """Transferencia programada hacia un destino."""

    type: DistributionType | str = DistributionType.SCHEDULED
    amount: Amount
    destination: DistributionDestination


class Distribution(PagoTICModel):
    """Distribución de los fondos de un pago entre una o más cuentas."""

    details: list[DistributionDetail] = Field(min_length=1)

    @classmethod
    def scheduled(
        cls,
        transfers: Iterable[Mapping[str, Any] | DistributionDetail],
    ) -> Distribution:
        """Atajo para armar una distribución ``scheduled`` a cuentas CBU.

        Cada transferencia puede ser un :class:`DistributionDetail` o un mapping
        con las claves ``cbu``, ``cuit``, ``name`` y ``amount``.
        """
        details: list[DistributionDetail] = []
        for transfer in transfers:
            if isinstance(transfer, DistributionDetail):
                details.append(transfer)
                continue
            try:
                amount = transfer["amount"]
                cbu = transfer["cbu"]
                cuit = transfer["cuit"]
                name = transfer["name"]
            except KeyError as exc:
                raise PagoTICValidationError(
                    f"Transferencia inválida: falta la clave {exc.args[0]!r}"
                ) from exc
            details.append(
                DistributionDetail(
                    amount=amount,
                    destination=DistributionDestination(
                        value=cbu,
                        cuit=cuit,
                        name=name,
                    ),
                )
            )
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
        distribution_total = sum(
            (detail.amount for detail in self.distribution.details), Decimal("0")
        )
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
    validation: str | None = None
    review: str | None = None
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
