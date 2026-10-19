"""Helpers de fechas para filtros de la API."""

from __future__ import annotations

from datetime import date, datetime, timezone


def format_filter_datetime(value: datetime | date | str) -> str:
    """Formatea una fecha para filtros de pagos.

    Formato de la API: ``yyyyMMdd'T'HHmmssSSSZ`` (por ejemplo
    ``20250101T000000000-0300``). Si recibe un string lo devuelve sin cambios.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        current = value
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        milliseconds = current.microsecond // 1000
        return f"{current:%Y%m%dT%H%M%S}{milliseconds:03d}{current:%z}"
    return f"{value:%Y%m%d}T000000000-0000"


def format_import_datetime(value: datetime | date | str) -> str:
    """Formatea una fecha para filtros de importaciones (sin milisegundos)."""
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        current = value
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        return f"{current:%Y%m%dT%H%M%S}{current:%z}"
    return f"{value:%Y%m%d}T000000-0000"
