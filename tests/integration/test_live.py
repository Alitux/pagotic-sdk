"""Tests de integración contra la API real.

Se ejecutan solo con ``PAGOTIC_RUN_INTEGRATION=1`` y credenciales disponibles
en ``PAGOTIC_*`` o en las variables genéricas del ``.env``. No crean pagos.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from pagotic import PagoTIC, PagoTICAPIError

# ``override=True`` evita que variables del sistema (por ejemplo ``USERNAME``)
# pisen las credenciales definidas en el ``.env``.
load_dotenv(override=True)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("PAGOTIC_RUN_INTEGRATION") != "1",
        reason="Definí PAGOTIC_RUN_INTEGRATION=1 para correr tests de integración",
    ),
]


def _cred(prefix: str, generic: str) -> str | None:
    return os.getenv(f"PAGOTIC_{prefix}") or os.getenv(generic)


def _build_client() -> PagoTIC:
    username = _cred("USERNAME", "USERNAME")
    password = _cred("PASSWORD", "PASSWORD")
    client_id = _cred("CLIENT_ID", "CLIENT_ID")
    client_secret = _cred("CLIENT_SECRET", "CLIENT_SECRET")

    if not all((username, password, client_id, client_secret)):
        pytest.skip("No hay credenciales de PagoTIC disponibles")

    return PagoTIC(
        username,
        password,
        client_id,
        client_secret,
        max_retries=0,
    )


def test_authentication_and_not_found() -> None:
    with _build_client() as sdk, pytest.raises(PagoTICAPIError) as exc_info:
        sdk.payments.get("00000000-0000-0000-0000-000000000000")

    assert exc_info.value.status_code in (400, 404)


def test_payments_list_requires_filters() -> None:
    with _build_client() as sdk, pytest.raises(PagoTICAPIError) as exc_info:
        sdk.payments.list(page=1, limit=1)

    assert exc_info.value.status_code == 400
    assert exc_info.value.extended_code == 4501


def test_subscriptions_list_is_reachable() -> None:
    with _build_client() as sdk:
        result = sdk.subscriptions.list()

    assert isinstance(result, dict)
    assert "size" in result


def test_imports_list_is_reachable() -> None:
    with _build_client() as sdk:
        result = sdk.imports.list(page=1, limit=1)

    assert isinstance(result, dict)
    assert "size" in result
