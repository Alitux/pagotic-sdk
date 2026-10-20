"""Helpers de fechas para filtros de la API y de códigos QR."""

from __future__ import annotations

import base64
import json
from datetime import date, datetime, timezone
from typing import Any
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


def decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decodifica el payload de un JWT sin verificar la firma.

    Sirve para inspeccionar claims del ``access_token``, por ejemplo el
    ``collector_id`` que PagoTIC incluye en ``signature``.

    Args:
        token: JWT en formato ``header.payload.signature``.

    Returns:
        El payload decodificado como diccionario.

    Raises:
        PagoTICValidationError: Si el token está vacío, no tiene tres partes o
            el payload no es un objeto JSON.
    """
    if not token or not token.strip():
        raise PagoTICValidationError("El token JWT no puede estar vacío")
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise PagoTICValidationError(
            "El token JWT no tiene el formato esperado (header.payload.signature)"
        )
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload + padding)
        decoded = json.loads(raw)
    except ValueError as exc:
        raise PagoTICValidationError("No se pudo decodificar el payload del token JWT") from exc
    if not isinstance(decoded, dict):
        raise PagoTICValidationError("El payload del token JWT no es un objeto")
    return {str(key): value for key, value in decoded.items()}


def collector_id_from_token(token: str) -> str:
    """Obtiene el ``collector_id`` de un access token de PagoTIC.

    PagoTIC incluye el identificador del comercio en el claim ``signature``
    (y también en ``family_name``). Los claims ``sub`` y el ``client_id`` no
    son el ``collector_id``.

    Args:
        token: JWT devuelto por la autenticación.

    Returns:
        El ``collector_id`` como string.

    Raises:
        PagoTICValidationError: Si el token no contiene ``signature`` ni
            ``family_name`` con un valor utilizable.
    """
    payload = decode_jwt_payload(token)
    value = payload.get("signature")
    if value is None or not str(value).strip():
        value = payload.get("family_name")
    if value is None or not str(value).strip():
        raise PagoTICValidationError(
            "El token JWT no contiene 'signature' ni 'family_name' con el collector_id"
        )
    return str(value).strip()
