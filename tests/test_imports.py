"""Tests de importación masiva."""

from __future__ import annotations

from pathlib import Path

import pytest

from pagotic import PagoTICValidationError
from tests.conftest import mock_json, mock_token, request_json

IMPORT_SUMMARY = {
    "import_id": "imp-1",
    "collector_id": "col-1",
    "status": "PENDING",
    "status_code": 0,
    "request_date": "2025-01-01T10:00:00-0300",
}


def test_preimport_sends_multipart(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/importaciones/pagos", IMPORT_SUMMARY)

    summary = client.imports.preimport(
        b"ext-1,ref-1,920,100.5\n",
        collector_id="col-1",
        match_payer=True,
    )

    assert summary.import_id == "imp-1"
    request = route.calls.last.request
    assert request.headers["content-type"].startswith("multipart/form-data")
    body = request.content
    assert b'name="match_payer"' in body
    assert b"true" in body
    assert b'name="collector_id"' in body
    assert b'filename="pagos.csv"' in body


def test_preimport_accepts_path(client, mock_router, tmp_path: Path) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "POST", "/importaciones/pagos", IMPORT_SUMMARY)
    csv_file = tmp_path / "cobranzas.csv"
    csv_file.write_text("ext-1,ref-1,920,100.5\n", encoding="utf-8")

    client.imports.preimport(csv_file, match_concept=True)

    body = route.calls.last.request.content
    assert b'filename="cobranzas.csv"' in body
    assert b'name="match_concept"' in body


def test_preimport_requires_a_flag(client) -> None:
    with pytest.raises(PagoTICValidationError):
        client.imports.preimport(b"data")


def test_preimport_identification_conflict(client) -> None:
    with pytest.raises(PagoTICValidationError):
        client.imports.preimport(b"data", match_identification=True, match_payer=True)


def test_list_imports(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(mock_router, "GET", "/importaciones/pagos", [IMPORT_SUMMARY])

    result = client.imports.list(
        page=1,
        filters=[{"field": "collector_id", "value": "col-1"}],
    )

    assert result[0]["import_id"] == "imp-1"
    assert route.calls.last.request.url.params["filters[0][field]"] == "collector_id"


def test_get_import(client, mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "GET", "/importaciones/pagos/imp-1", IMPORT_SUMMARY)

    summary = client.imports.get("imp-1")

    assert summary.status == "PENDING"


def test_import_details(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "GET",
        "/importaciones/pagos/imp-1/detalles",
        [{"external_reference": "ref-1", "amount": 100.5, "status": "OK"}],
    )

    details = client.imports.details("imp-1", limit=10)

    assert details[0].external_reference == "ref-1"
    assert details[0].amount == 100.5
    assert route.calls.last.request.url.params["limit"] == "10"


def test_import_details_accepts_results_envelope(client, mock_router) -> None:
    mock_token(mock_router)
    mock_json(
        mock_router,
        "GET",
        "/importaciones/pagos/imp-1/detalles",
        {"results": [{"external_reference": "ref-1"}]},
    )

    details = client.imports.details("imp-1")

    assert details[0].external_reference == "ref-1"


def test_import_details_unexpected_payload(client, mock_router) -> None:
    mock_token(mock_router)
    mock_json(mock_router, "GET", "/importaciones/pagos/imp-1/detalles", "nope")

    with pytest.raises(PagoTICValidationError):
        client.imports.details("imp-1")


def test_approve_import(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/importaciones/pagos/aprobar/imp-1",
        {**IMPORT_SUMMARY, "status": "APPROVED"},
    )

    summary = client.imports.approve("imp-1")

    assert summary.status == "APPROVED"
    assert route.calls.last.request.method == "POST"


def test_cancel_import(client, mock_router) -> None:
    mock_token(mock_router)
    route = mock_json(
        mock_router,
        "POST",
        "/importaciones/pagos/cancelar/imp-1",
        {**IMPORT_SUMMARY, "status": "CANCELLED"},
    )

    summary = client.imports.cancel("imp-1", "Duplicada")

    assert summary.status == "CANCELLED"
    assert request_json(route.calls.last.request) == {"status_detail": "Duplicada"}


def test_legacy_routes(client, mock_router) -> None:
    mock_token(mock_router)
    verify = mock_json(mock_router, "GET", "/importar/ver/imp-1", IMPORT_SUMMARY)
    approve = mock_json(
        mock_router,
        "POST",
        "/importar/aprobar/imp-1",
        {**IMPORT_SUMMARY, "status": "APPROVED"},
    )
    cancel = mock_json(
        mock_router,
        "POST",
        "/importar/cancelar/imp-1",
        {**IMPORT_SUMMARY, "status": "CANCELLED"},
    )

    assert client.imports.verify_legacy("imp-1").import_id == "imp-1"
    assert client.imports.approve_legacy("imp-1").status == "APPROVED"
    assert client.imports.cancel_legacy("imp-1", "Baja").status == "CANCELLED"
    assert verify.called
    assert approve.called
    assert request_json(cancel.calls.last.request) == {"status_detail": "Baja"}
