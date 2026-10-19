"""Tests de modelos y serialización."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from pagotic import (
    Detail,
    Distribution,
    DistributionDetail,
    PagoTICValidationError,
    Payer,
    Payment,
    PaymentRequest,
    validate_model,
)
from tests.conftest import PAYMENT_REQUEST


def test_amount_serializes_as_json_number() -> None:
    detail = Detail(amount=Decimal("10.10"))

    payload = detail.model_dump(mode="json")

    assert payload["amount"] == 10.1
    assert isinstance(payload["amount"], float)


def test_amount_accepts_string_and_keeps_precision() -> None:
    detail = Detail(amount="0.1")

    assert detail.amount == Decimal("0.1")


def test_extra_fields_are_preserved() -> None:
    payment = Payment.model_validate({"id": "pay-1", "campo_nuevo": "valor"})

    assert payment.model_extra == {"campo_nuevo": "valor"}


def test_enums_serialize_to_values() -> None:
    request = PaymentRequest.model_validate({**PAYMENT_REQUEST, "type": "coupon"})

    assert request.model_dump(mode="json")["type"] == "coupon"


def test_payer_requires_name() -> None:
    with pytest.raises(ValidationError):
        Payer.model_validate({"email": "ana@example.com"})


def test_validate_model_wraps_errors() -> None:
    with pytest.raises(PagoTICValidationError) as exc_info:
        validate_model(Payment, {})

    assert exc_info.value.errors


def test_payment_request_requires_details() -> None:
    with pytest.raises(ValidationError):
        PaymentRequest.model_validate(
            {
                "external_transaction_id": "ext-1",
                "details": [],
                "payer": {"name": "Ana"},
            }
        )


def test_distribution_requires_destination() -> None:
    with pytest.raises(ValidationError):
        DistributionDetail.model_validate(
            {
                "type": "scheduled",
                "amount": 100,
            }
        )


def test_distribution_model_roundtrip() -> None:
    distribution = Distribution.scheduled(
        [{"cbu": "0000000000000000000001", "cuit": "20111111112", "name": "A", "amount": 100}]
    )

    restored = Distribution.model_validate(distribution.model_dump(mode="json"))

    assert restored == distribution


def test_payment_accepts_boolean_validation_and_review() -> None:
    payment = Payment.model_validate(
        {
            "id": "pay-1",
            "status": "pending",
            "validation": False,
            "review": False,
        }
    )

    assert payment.validation is False
    assert payment.review is False


def test_payment_accepts_string_validation_and_review() -> None:
    payment = Payment.model_validate(
        {
            "id": "pay-1",
            "validation": "required",
            "review": "requested",
        }
    )

    assert payment.validation == "required"
    assert payment.review == "requested"


def test_payment_raw_qr_from_payment_methods() -> None:
    payment = Payment.model_validate(
        {
            "id": "pay-1",
            "payment_methods": [{"media_payment_id": 85, "raw_qr": "000201010212"}],
        }
    )

    assert payment.raw_qr == "000201010212"


def test_payment_raw_qr_prefers_top_level_value() -> None:
    payment = Payment.model_validate(
        {
            "id": "pay-1",
            "raw_qr": "top-level",
            "payment_methods": [{"raw_qr": "anidado"}],
        }
    )

    assert payment.raw_qr == "top-level"


def test_payment_raw_qr_is_none_without_qr() -> None:
    payment = Payment.model_validate({"id": "pay-1"})

    assert payment.raw_qr is None
