"""Tests del parser de webhooks."""

from __future__ import annotations

import json

import pytest

from pagotic import PagoTICValidationError, parse_notification
from tests.conftest import PAYMENT_JSON


def test_parse_mapping() -> None:
    payment = parse_notification(PAYMENT_JSON)

    assert payment.id == "pay-1"
    assert payment.status == "approved"


def test_parse_json_string() -> None:
    payment = parse_notification(json.dumps(PAYMENT_JSON))

    assert payment.id == "pay-1"


def test_parse_json_bytes() -> None:
    payment = parse_notification(json.dumps(PAYMENT_JSON).encode())

    assert payment.final_amount == 1000.5


def test_parse_payment_envelope() -> None:
    payment = parse_notification({"payment": PAYMENT_JSON})

    assert payment.id == "pay-1"


def test_invalid_json() -> None:
    with pytest.raises(PagoTICValidationError, match="JSON inválida"):
        parse_notification("{no-es-json")


def test_non_object_payload() -> None:
    with pytest.raises(PagoTICValidationError, match="objeto JSON"):
        parse_notification([1, 2, 3])


def test_payment_without_id() -> None:
    with pytest.raises(PagoTICValidationError):
        parse_notification({"status": "approved"})
