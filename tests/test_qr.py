"""Tests de generación local de códigos QR."""

from __future__ import annotations

from pathlib import Path

import pytest

from pagotic import (
    PagoTICValidationError,
    render_qr_png,
    render_qr_svg,
    save_qr,
)

RAW_QR = "00020101021243650016COM.PAGOTIC0117qr-de-prueba-001"


def _png_width(data: bytes) -> int:
    return int.from_bytes(data[16:20], "big")


def test_render_qr_png() -> None:
    data = render_qr_png(RAW_QR)

    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 100


def test_render_qr_png_respects_scale() -> None:
    small = render_qr_png(RAW_QR, scale=2)
    large = render_qr_png(RAW_QR, scale=10)

    assert _png_width(large) > _png_width(small)


def test_render_qr_svg() -> None:
    svg = render_qr_svg(RAW_QR)

    assert "<svg" in svg
    assert "</svg>" in svg


def test_save_qr_png(tmp_path: Path) -> None:
    path = save_qr(RAW_QR, tmp_path / "qr.png")

    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG")


def test_save_qr_svg(tmp_path: Path) -> None:
    path = save_qr(RAW_QR, tmp_path / "qr.svg")

    assert path.exists()
    assert "<svg" in path.read_text(encoding="utf-8")


def test_empty_raw_qr_is_rejected() -> None:
    with pytest.raises(PagoTICValidationError):
        render_qr_png("")


def test_invalid_scale_is_rejected() -> None:
    with pytest.raises(PagoTICValidationError):
        render_qr_png(RAW_QR, scale=0)


def test_invalid_border_is_rejected() -> None:
    with pytest.raises(PagoTICValidationError):
        render_qr_png(RAW_QR, border=-1)


def test_invalid_error_level_is_rejected() -> None:
    with pytest.raises(PagoTICValidationError):
        render_qr_png(RAW_QR, error="x")
