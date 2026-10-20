"""Tests de helpers de fechas."""

from __future__ import annotations

import base64
import json
from datetime import date, datetime, timedelta, timezone

import pytest

from pagotic import (
    PagoTICValidationError,
    build_qr_image_url,
    collector_id_from_token,
    decode_jwt_payload,
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


def _make_jwt(payload: dict[str, object]) -> str:
    def encode(value: dict[str, object]) -> str:
        raw = json.dumps(value).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{encode({'alg': 'none'})}.{encode(payload)}.firma"


def test_decode_jwt_payload_returns_claims() -> None:
    token = _make_jwt({"signature": "14020", "sub": "uuid"})

    payload = decode_jwt_payload(token)

    assert payload["signature"] == "14020"
    assert payload["sub"] == "uuid"


def test_collector_id_from_token_uses_signature() -> None:
    token = _make_jwt({"signature": "14020", "family_name": "otro"})

    assert collector_id_from_token(token) == "14020"


def test_collector_id_from_token_falls_back_to_family_name() -> None:
    token = _make_jwt({"family_name": "14020"})

    assert collector_id_from_token(token) == "14020"


def test_collector_id_from_token_rejects_missing_claim() -> None:
    token = _make_jwt({"sub": "uuid"})

    with pytest.raises(PagoTICValidationError):
        collector_id_from_token(token)


def test_decode_jwt_payload_rejects_empty_token() -> None:
    with pytest.raises(PagoTICValidationError):
        decode_jwt_payload("")


def test_decode_jwt_payload_rejects_malformed_token() -> None:
    with pytest.raises(PagoTICValidationError):
        decode_jwt_payload("no-es-un-jwt")


def test_decode_jwt_payload_rejects_non_object_payload() -> None:
    token = f"header.{base64.urlsafe_b64encode(b'[1, 2]').rstrip(b'=').decode()}.firma"

    with pytest.raises(PagoTICValidationError):
        decode_jwt_payload(token)
