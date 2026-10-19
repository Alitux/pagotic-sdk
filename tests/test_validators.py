"""Tests de validadores (CUIT)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pagotic import DistributionDestination, DistributionTransfer, normalize_cuit


@pytest.mark.parametrize(
    "value",
    [
        "20123456786",
        "30714405329",
        "20111111112",
        "20111111120",
        "20999999999",
    ],
)
def test_normalize_cuit_accepts_valid_values(value: str) -> None:
    assert normalize_cuit(value) == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20-12345678-6", "20123456786"),
        ("20.123.456.786", "20123456786"),
        (" 30 71440532 9 ", "30714405329"),
    ],
)
def test_normalize_cuit_removes_separators(value: str, expected: str) -> None:
    assert normalize_cuit(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "123",
        "2011111111",
        "201111111122",
        "20A11111112",
        "20111111111",
        "20123456787",
    ],
)
def test_normalize_cuit_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError, match="CUIT"):
        normalize_cuit(value)


def test_distribution_transfer_normalizes_cuit() -> None:
    transfer = DistributionTransfer(
        cuit="20-11111111-2",
        cbu="0000000000000000000001",
        name="Titular",
        amount=100,
    )

    assert transfer.cuit == "20111111112"


def test_distribution_destination_rejects_invalid_cuit() -> None:
    with pytest.raises(ValidationError, match="dígito verificador"):
        DistributionDestination(
            value="0000000000000000000001",
            cuit="20111111111",
            name="Titular",
        )
