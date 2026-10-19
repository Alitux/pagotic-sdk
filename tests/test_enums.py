"""Tests de medios de pago y presets."""

from __future__ import annotations

from pagotic import MediaPayment, Presets, SourceType
from tests.conftest import PAYMENT_REQUEST, mock_json, mock_token, request_json


def test_media_payment_values() -> None:
    assert MediaPayment.VISA == 9
    assert MediaPayment.VISA_DEBITO == 10
    assert MediaPayment.MASTERCARD == 5
    assert MediaPayment.MASTERCARD_DEBITO == 27
    assert MediaPayment.QR == 85
    assert MediaPayment.TRANSFERENCIA == 94
    assert MediaPayment.RAPIPAGO == 97
    assert MediaPayment.PAGOFACIL == 98
    assert MediaPayment(94) is MediaPayment.TRANSFERENCIA


def test_media_payment_is_an_int() -> None:
    assert isinstance(MediaPayment.QR, int)
    assert MediaPayment.QR + 1 == 86


def test_backoffice_source_has_no_accent() -> None:
    assert SourceType.BACKOFFICE.value == "backoffice"
    assert SourceType.BACKOFFICE.value.isascii()


def test_media_payment_groups() -> None:
    credit = MediaPayment.credit_cards()
    debit = MediaPayment.debit_cards()
    cards = MediaPayment.cards()

    assert MediaPayment.VISA in credit
    assert MediaPayment.MASTERCARD in credit
    assert MediaPayment.VISA_DEBITO not in credit
    assert MediaPayment.VISA_DEBITO in debit
    assert MediaPayment.MAESTRO in debit
    assert MediaPayment.MASTERCARD_DEBITO in debit
    assert MediaPayment.CABAL_DEBITO in debit
    assert set(cards) == set(credit) | set(debit)
    assert not set(credit) & set(debit)

    coupons = MediaPayment.coupons()
    assert MediaPayment.RAPIPAGO in coupons
    assert MediaPayment.PAGOFACIL in coupons
    assert MediaPayment.VISA not in coupons


def test_presets_serialize_media_payment_members() -> None:
    presets = Presets(media_payment_ids=[MediaPayment.VISA, MediaPayment.QR])

    assert presets.model_dump(mode="json")["media_payment_ids"] == [9, 85]


def test_create_payment_sends_preset_ids_as_integers(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/pagos", {"id": "pay-1"})

    client.payments.create(
        {
            **PAYMENT_REQUEST,
            "presets": {
                "media_payment_ids": [
                    MediaPayment.VISA,
                    MediaPayment.VISA_DEBITO,
                    MediaPayment.QR,
                ]
            },
        }
    )

    body = request_json(route.calls.last.request)
    assert body["presets"]["media_payment_ids"] == [9, 10, 85]
