"""Modelos de importación masiva de pagos."""

from __future__ import annotations

from typing import Any

from pagotic.enums import ImportStatus
from pagotic.models.base import Amount, PagoTICModel


class ImportSummary(PagoTICModel):
    """Cabecera de una importación masiva."""

    import_id: str | int | None = None
    collector_id: str | None = None
    status: ImportStatus | str | None = None
    status_code: int | str | None = None
    request_date: str | None = None
    approved_date: str | None = None
    cancel_date: str | None = None
    total_records: int | None = None
    processed_records: int | None = None
    successful_records: int | None = None
    failed_records: int | None = None
    file_name: str | None = None
    metadata: dict[str, Any] | None = None


class ImportDetail(PagoTICModel):
    """Resultado de un pago individual dentro de una importación."""

    external_transaction_id: str | None = None
    external_reference: str | None = None
    concept_id: int | str | None = None
    concept_description: str | None = None
    currency_id: str | None = None
    amount: Amount | None = None
    payer_reference: str | None = None
    payer_name: str | None = None
    payer_email: str | None = None
    payer_id_number: str | None = None
    status: str | None = None
    status_code: int | str | None = None
    error_description: str | None = None
    payment_id: str | None = None
