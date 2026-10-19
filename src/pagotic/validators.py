"""Validadores reutilizables para datos argentinos."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import BeforeValidator

_CUIT_PATTERN = re.compile(r"^\d{11}$")
_CUIT_SEPARATORS = re.compile(r"[\s.\-]")
_CUIT_WEIGHTS = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)


def normalize_cuit(value: str) -> str:
    """Valida y normaliza un CUIT argentino.

    Acepta los 11 dígitos con o sin guiones, puntos y espacios. Devuelve el
    CUIT sin separadores y verifica el dígito verificador (módulo 11).

    Raises:
        ValueError: si el valor no tiene 11 dígitos o el dígito verificador
            no es correcto.
    """
    if not isinstance(value, str):
        raise ValueError("El CUIT debe ser una cadena de texto")

    normalized = _CUIT_SEPARATORS.sub("", value.strip())
    if not _CUIT_PATTERN.fullmatch(normalized):
        raise ValueError("El CUIT debe tener 11 dígitos")

    total = sum(
        int(digit) * weight for digit, weight in zip(normalized[:10], _CUIT_WEIGHTS, strict=True)
    )
    check_digit = 11 - (total % 11)
    if check_digit == 11:
        check_digit = 0
    elif check_digit == 10:
        check_digit = 9

    if int(normalized[-1]) != check_digit:
        raise ValueError("El CUIT tiene un dígito verificador inválido")

    return normalized


Cuit = Annotated[str, BeforeValidator(normalize_cuit)]
"""Tipo de CUIT validado y normalizado a 11 dígitos."""
