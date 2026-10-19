"""Tests de helpers de fechas."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from pagotic import format_filter_datetime, format_import_datetime


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
