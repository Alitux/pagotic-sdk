"""Generación local de códigos QR con la dependencia opcional ``segno``."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from pagotic.exceptions import PagoTICConfigError, PagoTICValidationError

if TYPE_CHECKING:
    import segno

_ERROR_LEVELS = {"l", "m", "q", "h"}


def _make_qr(raw_qr: str, error: str) -> segno.QRCode:
    if not raw_qr:
        raise PagoTICValidationError("raw_qr no puede estar vacío")
    level = error.lower()
    if level not in _ERROR_LEVELS:
        raise PagoTICValidationError("error debe ser uno de L, M, Q o H")
    try:
        import segno
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise PagoTICConfigError(
            "Para generar QR localmente instalá el extra: pip install pagotic-sdk[qr]"
        ) from exc
    return segno.make_qr(raw_qr, error=level)


def _validate_options(scale: int, border: int) -> None:
    if scale <= 0:
        raise PagoTICValidationError("scale debe ser mayor a cero")
    if border < 0:
        raise PagoTICValidationError("border no puede ser negativo")


def render_qr_png(
    raw_qr: str,
    *,
    scale: int = 4,
    border: int = 4,
    dark: str = "#000000",
    light: str | None = "#ffffff",
    error: str = "m",
) -> bytes:
    """Genera un PNG del ``raw_qr`` sin depender de servicios externos.

    Requiere el extra ``qr``: ``pip install pagotic-sdk[qr]``.
    """
    _validate_options(scale, border)
    qr = _make_qr(raw_qr, error)
    buffer = BytesIO()
    qr.save(buffer, kind="png", scale=scale, border=border, dark=dark, light=light)
    return buffer.getvalue()


def render_qr_svg(
    raw_qr: str,
    *,
    scale: int = 4,
    border: int = 4,
    dark: str = "#000000",
    light: str | None = "#ffffff",
    error: str = "m",
) -> str:
    """Genera un SVG del ``raw_qr`` sin depender de servicios externos."""
    _validate_options(scale, border)
    qr = _make_qr(raw_qr, error)
    return qr.svg_inline(scale=scale, border=border, dark=dark, light=light)


def save_qr(
    raw_qr: str,
    path: str | Path,
    *,
    scale: int = 4,
    border: int = 4,
    dark: str = "#000000",
    light: str | None = "#ffffff",
    error: str = "m",
) -> Path:
    """Guarda el QR en ``path``; el formato se deduce de la extensión.

    Requiere el extra ``qr``: ``pip install pagotic-sdk[qr]``.
    """
    _validate_options(scale, border)
    qr = _make_qr(raw_qr, error)
    destination = Path(path)
    qr.save(str(destination), scale=scale, border=border, dark=dark, light=light)
    return destination
