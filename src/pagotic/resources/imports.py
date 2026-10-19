"""Recurso de importación masiva."""

from __future__ import annotations

import builtins
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any

from pagotic.exceptions import PagoTICValidationError
from pagotic.models.base import validate_model
from pagotic.models.imports import ImportDetail, ImportSummary
from pagotic.models.payments import Filter
from pagotic.resources._utils import (
    build_query_params,
    path_id,
    read_csv_source,
    validate_import_flags,
)

if TYPE_CHECKING:
    from pagotic.client import AsyncPagoTIC, PagoTIC

CsvSource = bytes | bytearray | str | Path | IO[bytes] | IO[str]


def _multipart_data(
    *,
    collector_id: str | None,
    match_payer: bool,
    match_concept: bool,
    match_identification: bool,
) -> dict[str, str]:
    data = {
        "match_payer": str(match_payer).lower(),
        "match_concept": str(match_concept).lower(),
        "match_identification": str(match_identification).lower(),
    }
    if collector_id is not None:
        data["collector_id"] = collector_id
    return data


class ImportsResource:
    """Preimportación, consulta y aprobación de importaciones masivas."""

    def __init__(self, client: PagoTIC) -> None:
        self._client = client

    def preimport(
        self,
        file: CsvSource,
        *,
        collector_id: str | None = None,
        match_payer: bool = False,
        match_concept: bool = False,
        match_identification: bool = False,
    ) -> ImportSummary:
        """Preimporta un CSV (sin encabezados, máximo 40.000 registros)."""
        validate_import_flags(
            match_payer=match_payer,
            match_concept=match_concept,
            match_identification=match_identification,
        )
        filename, content = read_csv_source(file)
        data = _multipart_data(
            collector_id=collector_id,
            match_payer=match_payer,
            match_concept=match_concept,
            match_identification=match_identification,
        )
        payload = self._client.request(
            "POST",
            "/importaciones/pagos",
            data=data,
            files={"file": (filename, content, "text/csv")},
        )
        return validate_model(ImportSummary, payload)

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> Any:
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        return self._client.request("GET", "/importaciones/pagos", params=params)

    def get(self, import_id: str | int) -> ImportSummary:
        payload = self._client.request("GET", f"/importaciones/pagos/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    def details(
        self,
        import_id: str | int,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> builtins.list[ImportDetail]:
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        payload = self._client.request(
            "GET",
            f"/importaciones/pagos/{path_id(import_id)}/detalles",
            params=params,
        )
        if isinstance(payload, dict) and "results" in payload:
            payload = payload["results"]
        if not isinstance(payload, list):
            raise PagoTICValidationError(
                f"Respuesta inesperada de detalles de importación: {payload!r}"
            )
        return [validate_model(ImportDetail, item) for item in payload]

    def approve(self, import_id: str | int) -> ImportSummary:
        """Aprueba la importación y genera los pagos."""
        payload = self._client.request("POST", f"/importaciones/pagos/aprobar/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    def cancel(self, import_id: str | int, status_detail: str) -> ImportSummary:
        """Cancela la importación sin generar pagos."""
        payload = self._client.request(
            "POST",
            f"/importaciones/pagos/cancelar/{path_id(import_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(ImportSummary, payload)

    def verify_legacy(self, import_id: str | int) -> ImportSummary:
        """Ruta legacy ``GET /importar/ver/{id}`` (deprecada)."""
        payload = self._client.request("GET", f"/importar/ver/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    def approve_legacy(self, import_id: str | int) -> ImportSummary:
        """Ruta legacy ``POST /importar/aprobar/{id}`` (deprecada)."""
        payload = self._client.request("POST", f"/importar/aprobar/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    def cancel_legacy(self, import_id: str | int, status_detail: str) -> ImportSummary:
        """Ruta legacy ``POST /importar/cancelar/{id}`` (deprecada)."""
        payload = self._client.request(
            "POST",
            f"/importar/cancelar/{path_id(import_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(ImportSummary, payload)


class AsyncImportsResource:
    """Versión asincrónica de :class:`ImportsResource`."""

    def __init__(self, client: AsyncPagoTIC) -> None:
        self._client = client

    async def preimport(
        self,
        file: CsvSource,
        *,
        collector_id: str | None = None,
        match_payer: bool = False,
        match_concept: bool = False,
        match_identification: bool = False,
    ) -> ImportSummary:
        validate_import_flags(
            match_payer=match_payer,
            match_concept=match_concept,
            match_identification=match_identification,
        )
        filename, content = read_csv_source(file)
        data = _multipart_data(
            collector_id=collector_id,
            match_payer=match_payer,
            match_concept=match_concept,
            match_identification=match_identification,
        )
        payload = await self._client.request(
            "POST",
            "/importaciones/pagos",
            data=data,
            files={"file": (filename, content, "text/csv")},
        )
        return validate_model(ImportSummary, payload)

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> Any:
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        return await self._client.request("GET", "/importaciones/pagos", params=params)

    async def get(self, import_id: str | int) -> ImportSummary:
        payload = await self._client.request("GET", f"/importaciones/pagos/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    async def details(
        self,
        import_id: str | int,
        *,
        page: int | None = None,
        limit: int | None = None,
        sorts: Mapping[str, str] | None = None,
        filters: Sequence[Filter | Mapping[str, Any]] | None = None,
    ) -> builtins.list[ImportDetail]:
        params = build_query_params(page=page, limit=limit, sorts=sorts, filters=filters)
        payload = await self._client.request(
            "GET",
            f"/importaciones/pagos/{path_id(import_id)}/detalles",
            params=params,
        )
        if isinstance(payload, dict) and "results" in payload:
            payload = payload["results"]
        if not isinstance(payload, list):
            raise PagoTICValidationError(
                f"Respuesta inesperada de detalles de importación: {payload!r}"
            )
        return [validate_model(ImportDetail, item) for item in payload]

    async def approve(self, import_id: str | int) -> ImportSummary:
        payload = await self._client.request(
            "POST", f"/importaciones/pagos/aprobar/{path_id(import_id)}"
        )
        return validate_model(ImportSummary, payload)

    async def cancel(self, import_id: str | int, status_detail: str) -> ImportSummary:
        payload = await self._client.request(
            "POST",
            f"/importaciones/pagos/cancelar/{path_id(import_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(ImportSummary, payload)

    async def verify_legacy(self, import_id: str | int) -> ImportSummary:
        payload = await self._client.request("GET", f"/importar/ver/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    async def approve_legacy(self, import_id: str | int) -> ImportSummary:
        payload = await self._client.request("POST", f"/importar/aprobar/{path_id(import_id)}")
        return validate_model(ImportSummary, payload)

    async def cancel_legacy(self, import_id: str | int, status_detail: str) -> ImportSummary:
        payload = await self._client.request(
            "POST",
            f"/importar/cancelar/{path_id(import_id)}",
            json={"status_detail": status_detail},
        )
        return validate_model(ImportSummary, payload)
