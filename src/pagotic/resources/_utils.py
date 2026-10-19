"""Utilidades compartidas por los recursos."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import IO, Any
from urllib.parse import quote

from pagotic.enums import FilterOperation, SortOrder
from pagotic.exceptions import PagoTICValidationError
from pagotic.models.base import validate_model
from pagotic.models.payments import Filter


def path_id(value: str | int) -> str:
    """Escapa un identificador para usarlo como segmento de path."""
    return quote(str(value), safe="")


def build_query_params(
    *,
    page: int | None = None,
    limit: int | None = None,
    sorts: Mapping[str, SortOrder | str] | None = None,
    filters: Sequence[Filter | Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Arma los parámetros ``page``, ``limit``, ``sorts`` y ``filters``."""
    params: dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit

    for field, order in (sorts or {}).items():
        params[f"sorts[{field}]"] = order.value if isinstance(order, SortOrder) else order

    for index, raw_filter in enumerate(filters or []):
        item = validate_model(Filter, raw_filter)
        value = item.value
        if isinstance(value, (list, tuple, set)):
            value = ",".join(str(element) for element in value)
        params[f"filters[{index}][field]"] = item.field
        params[f"filters[{index}][operation]"] = (
            item.operation.value if isinstance(item.operation, FilterOperation) else item.operation
        )
        params[f"filters[{index}][value]"] = value

    return params


def validate_import_flags(
    *,
    match_payer: bool,
    match_concept: bool,
    match_identification: bool,
) -> None:
    """Aplica las reglas de flags de la preimportación."""
    if not any((match_payer, match_concept, match_identification)):
        raise PagoTICValidationError(
            "La importación requiere al menos un flag en true: "
            "match_payer, match_concept o match_identification"
        )
    if match_identification and (match_payer or match_concept):
        raise PagoTICValidationError(
            "Si match_identification es true, match_payer y match_concept deben ser false"
        )


def read_csv_source(
    source: bytes | bytearray | str | Path | IO[bytes] | IO[str],
) -> tuple[str, bytes]:
    """Devuelve ``(nombre, contenido)`` a partir de bytes, path o archivo abierto."""
    if isinstance(source, Path):
        return source.name, source.read_bytes()
    if isinstance(source, str):
        candidate = Path(source)
        if candidate.exists():
            return candidate.name, candidate.read_bytes()
        return "pagos.csv", source.encode("utf-8")
    if isinstance(source, (bytes, bytearray)):
        return "pagos.csv", bytes(source)

    name = Path(getattr(source, "name", "pagos.csv")).name
    content = source.read()
    if isinstance(content, str):
        content = content.encode("utf-8")
    return name, content
