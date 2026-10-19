"""Tests de helpers de fechas."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from pagotic import (
    PagoTICValidationError,
    build_qr_image_url,
    format_filter_datetime,
    format_import_datetime,
)


def test_format_datetime_with_offset() -> None:
    value = datetime(2025, 1, 1, 10, 30, 45, 123456, tzinfo=timezone(timedelta(hours=-3)))

    assert format_filter_datetime(value) == "20250101T103045123-0300"


def test_format_naive_datetime_as_utc() -> None:
    value = datetime(2025, 1, 1, 0, 0, 0)

    assert format_filter_datetime(value) == "20250101T000000000+0000"


def test_format_date() -> None:
    assert format_filter_datetime(date(2025, 1, 1)) == "20250101T000000000-0000"


def test_format_string_passthrough() -> None:
    value = "20250101T000000000-0300"

    assert format_filter_datetime(value) == value
    assert format_import_datetime(value) == value


def test_format_import_datetime() -> None:
    value = datetime(2025, 1, 1, 10, 30, 45, tzinfo=timezone(timedelta(hours=-3)))

    assert format_import_datetime(value) == "20250101T103045-0300"
    assert format_import_datetime(date(2025, 1, 1)) == "20250101T000000-0000"


def test_build_qr_image_url() -> None:
    url = build_qr_image_url("000201010212", size=300)

    assert url == ("https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=000201010212")


def test_build_qr_image_url_encodes_special_characters() -> None:
    url = build_qr_image_url("a b&c=d/é")

    assert url.endswith("data=a%20b%26c%3Dd%2F%C3%A9")


def test_build_qr_image_url_rejects_empty_value() -> None:
    with pytest.raises(PagoTICValidationError):
        build_qr_image_url("")


def test_build_qr_image_url_rejects_invalid_size() -> None:
    with pytest.raises(PagoTICValidationError):
        build_qr_image_url("abc", size=0)
