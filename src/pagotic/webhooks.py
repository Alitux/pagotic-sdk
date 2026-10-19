"""Utilidades para procesar notificaciones (webhooks) de PagoTIC.

PagoTIC envía el JSON completo del pago a ``notification_url``. La
documentación disponible no define una firma ni un secreto compartido, por lo
que este módulo no valida autenticidad: si necesitás verificar el origen,
hacelo en tu infraestructura (por ejemplo, listas de IP o un proxy).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from pagotic.exceptions import PagoTICValidationError
from pagotic.models.base import validate_model
from pagotic.models.payments import Payment


def parse_notification(payload: Mapping[str, Any] | str | bytes | bytearray) -> Payment:
    """Convierte el body de una notificación en un :class:`Payment`.

    Acepta un mapping, JSON en ``str``/``bytes`` o un sobre ``{"payment": {...}}``.
    """
    data: Any
    if isinstance(payload, (str, bytes, bytearray)):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise PagoTICValidationError(f"Notificación JSON inválida: {exc}") from exc
    else:
        data = payload

    if not isinstance(data, Mapping):
        raise PagoTICValidationError(
            "La notificación debe ser un objeto JSON con los datos del pago"
        )

    if "id" not in data and isinstance(data.get("payment"), Mapping):
        data = data["payment"]

    return validate_model(Payment, data)
