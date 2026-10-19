"""Tests de distribución programada."""

from __future__ import annotations

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
)
from tests.conftest import PAYMENT_REQUEST, mock_json, mock_token, request_json


def _request(distribution: Distribution) -> PaymentRequest:
    return PaymentRequest(
        external_transaction_id="ext-dist-1",
        currency_id="ARS",
        details=[
            Detail(external_reference="a", amount=800),
            Detail(external_reference="b", amount=200),
        ],
        payer=Payer(name="Ana Pérez", email="ana@example.com"),
        distribution=distribution,
    )


def test_distribution_scheduled_serialization() -> None:
    request = _request(
        Distribution.scheduled(
            [
                {
                    "cbu": "0000000000000000000001",
                    "cuit": "20111111111",
                    "name": "A",
                    "amount": 800,
                },
                {
                    "cbu": "0000000000000000000002",
                    "cuit": "20222222222",
                    "name": "B",
                    "amount": 200,
                },
            ]
        )
    )

    payload = request.model_dump(mode="json")

    assert payload["distribution"] == {
        "details": [
            {
                "type": "scheduled",
                "amount": 800.0,
                "destination": {
                    "type": "cbu",
                    "value": "0000000000000000000001",
                    "cuit": "20111111111",
                    "name": "A",
                },
            },
            {
                "type": "scheduled",
                "amount": 200.0,
                "destination": {
                    "type": "cbu",
                    "value": "0000000000000000000002",
                    "cuit": "20222222222",
                    "name": "B",
                },
            },
        ]
    }


def test_distribution_accepts_detail_objects() -> None:
    detail = DistributionDetail(
        amount=1000,
        destination={
            "type": "cbu",
            "value": "0000000000000000000003",
            "cuit": "20333333333",
            "name": "C",
        },
    )
    request = _request(Distribution.scheduled([detail]))

    assert request.distribution is not None
    assert request.distribution.details[0].destination.cuit == "20333333333"


def test_distribution_scheduled_missing_key() -> None:
    with pytest.raises(PagoTICValidationError, match="falta la clave"):
        Distribution.scheduled([{"cbu": "000", "cuit": "20111111111", "name": "A"}])


def test_distribution_sum_mismatch_raises_on_model() -> None:
    with pytest.raises(ValidationError, match=r"distribution\.details"):
        _request(
            Distribution.scheduled(
                [
                    {
                        "cbu": "0000000000000000000001",
                        "cuit": "20111111111",
                        "name": "A",
                        "amount": 900,
                    }
                ]
            )
        )


def test_distribution_sum_mismatch_raises_before_request(client) -> None:
    request = {
        **PAYMENT_REQUEST,
        "distribution": {
            "details": [
                {
                    "type": "scheduled",
                    "amount": 100,
                    "destination": {
                        "type": "cbu",
                        "value": "0000000000000000000001",
                        "cuit": "20111111111",
                        "name": "A",
                    },
                }
            ]
        },
    }

    with pytest.raises(PagoTICValidationError):
        client.payments.create(request)


def test_distribution_is_sent_to_api(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/pagos",
        {
            "id": "pay-dist",
            "status": "pending",
            "distribution": {
                "details": [
                    {
                        "type": "scheduled",
                        "amount": 1000.5,
                        "destination": {
                            "type": "cbu",
                            "value": "0000000000000000000001",
                            "cuit": "20111111111",
                            "name": "A",
                        },
                    }
                ]
            },
        },
    )

    payment = client.payments.create(
        {
            **PAYMENT_REQUEST,
            "distribution": {
                "details": [
                    {
                        "type": "scheduled",
                        "amount": 1000.5,
                        "destination": {
                            "type": "cbu",
                            "value": "0000000000000000000001",
                            "cuit": "20111111111",
                            "name": "A",
                        },
                    }
                ]
            },
        }
    )

    assert payment.distribution is not None
    assert payment.distribution.details[0].destination.value == "0000000000000000000001"
    assert request_json(route.calls.last.request)["distribution"]["details"][0]["amount"] == 1000.5


def test_payment_response_parses_distribution() -> None:
    payment = Payment.model_validate(
        {
            "id": "pay-dist",
            "distribution": {
                "details": [
                    {
                        "type": "scheduled",
                        "amount": 500,
                        "destination": {
                            "type": "cbu",
                            "value": "0000000000000000000009",
                            "cuit": "20999999999",
                            "name": "Destino",
                        },
                    }
                ]
            },
        }
    )

    assert isinstance(payment.distribution, Distribution)
    assert payment.distribution.details[0].amount == 500
