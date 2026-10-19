"""Helpers de fechas para filtros de la API y de códigos QR."""

from __future__ import annotations

from datetime import date, datetime, timezone
from urllib.parse import quote

from pagotic.exceptions import PagoTICValidationError

QR_IMAGE_ENDPOINT = "https://api.qrserver.com/v1/create-qr-code/"


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


def build_qr_image_url(raw_qr: str, size: int = 200) -> str:
    """Arma la URL de la imagen QR a partir del ``raw_qr`` de un pago.

    El valor se URL-encodea, tal como indica la guía oficial de PagoTIC. La
    imagen se obtiene haciendo ``GET`` a la URL resultante.
    """
    if not raw_qr:
        raise PagoTICValidationError("raw_qr no puede estar vacío")
    if size <= 0:
        raise PagoTICValidationError("size debe ser mayor a cero")
    return f"{QR_IMAGE_ENDPOINT}?size={size}x{size}&data={quote(raw_qr, safe='')}"
