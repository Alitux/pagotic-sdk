"""Modelos base y utilidades de validación."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any, TypeVar

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    PlainSerializer,
    ValidationError,
)

from pagotic.exceptions import PagoTICValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)


def _decimal_from_float(value: Any) -> Any:
    """Convierte floats vía str para evitar artefactos binarios."""
    if isinstance(value, float):
        return Decimal(str(value))
    return value


#: Importe monetario. Se serializa como número JSON (no como string).
Amount = Annotated[
    Decimal,
    BeforeValidator(_decimal_from_float),
    PlainSerializer(float, return_type=float, when_used="json"),
]


class PagoTICModel(BaseModel):
    """Base de todos los modelos: tolera campos nuevos de la API."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


def validate_model(model: type[ModelT], data: Any) -> ModelT:
    """Valida datos y traduce los errores de Pydantic a la jerarquía del SDK."""
    if isinstance(data, model):
        return data
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise PagoTICValidationError(
            f"Datos inválidos para {model.__name__}: {exc}",
            errors=exc.errors(),
        ) from exc
