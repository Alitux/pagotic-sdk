"""Clientes sincrónico y asincrónico de PagoTIC."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from pagotic._version import __version__
from pagotic.auth import AsyncAuthManager, AuthManager
from pagotic.exceptions import (
    PagoTICAPIError,
    PagoTICAuthError,
    PagoTICConnectionError,
)
from pagotic.resources.imports import AsyncImportsResource, ImportsResource
from pagotic.resources.payments import AsyncPaymentsResource, PaymentsResource
from pagotic.resources.subscriptions import (
    AsyncSubscriptionsResource,
    SubscriptionsResource,
)
from pagotic.settings import Settings, resolve_settings
from pagotic.utils import collector_id_from_token

_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


def _payload_from_response(response: httpx.Response) -> Any:
    if not response.content:
        return None
    content_type = response.headers.get("content-type", "").lower()
    if "json" in content_type:
        try:
            return response.json()
        except ValueError:
            return response.text
    return response.text


def _raise_api_error(response: httpx.Response) -> None:
    payload = _payload_from_response(response)
    status_code = response.status_code

    if isinstance(payload, dict):
        error = payload.get("error")
        if error is not None and "code" not in payload:
            description = payload.get("error_description")
            message = str(description or error)
            raise PagoTICAuthError(
                message,
                error=str(error),
                description=str(description) if description is not None else None,
                status_code=status_code,
                payload=payload,
            )
        message = str(
            payload.get("message") or payload.get("description") or f"Error HTTP {status_code}"
        )
        raise PagoTICAPIError(
            message,
            status_code=status_code,
            code=payload.get("code"),
            extended_code=payload.get("extended_code"),
            payload=payload,
        )

    raise PagoTICAPIError(
        f"Error HTTP {status_code}: {payload}" if payload else f"Error HTTP {status_code}",
        status_code=status_code,
        payload=payload,
    )


def _handle_response(response: httpx.Response) -> Any:
    if 200 <= response.status_code < 300:
        return _payload_from_response(response)
    _raise_api_error(response)
    raise AssertionError("inalcanzable")  # pragma: no cover


class PagoTIC:
    """Cliente sincrónico del SDK.

    Las credenciales se pueden pasar explícitamente o definir mediante
    ``PAGOTIC_USERNAME``, ``PAGOTIC_PASSWORD``, ``PAGOTIC_CLIENT_ID`` y
    ``PAGOTIC_CLIENT_SECRET``.
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        *,
        auth_url: str | None = None,
        api_url: str | None = None,
        realm: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_backoff: float | None = None,
        token_leeway: float | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = resolve_settings(
            username,
            password,
            client_id,
            client_secret,
            auth_url=auth_url,
            api_url=api_url,
            realm=realm,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            token_leeway=token_leeway,
        )
        self._http = http_client or httpx.Client(
            timeout=self._settings.timeout,
            follow_redirects=True,
        )
        self._owns_http = http_client is None
        self._auth = AuthManager(self._http, self._settings)
        self.payments = PaymentsResource(self)
        self.imports = ImportsResource(self)
        self.subscriptions = SubscriptionsResource(self)

    @property
    def settings(self) -> Settings:
        """Configuración efectiva del cliente."""
        return self._settings

    def get_collector_id(self) -> str:
        """Devuelve el ``collector_id`` del token de acceso.

        PagoTIC incluye el identificador del comercio en el claim
        ``signature`` (o ``family_name``) del JWT. No confundir con ``sub``
        ni con el ``client_id``.

        Returns:
            El identificador del comercio asociado al usuario.

        Raises:
            PagoTICAuthError: Si falla la autenticación.
            PagoTICValidationError: Si el token no contiene el claim esperado.
        """
        return collector_id_from_token(self._auth.get_token())

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        auth: bool = True,
        retry: bool | None = None,
    ) -> Any:
        """Ejecuta una request contra la API, manejando auth y reintentos."""
        url = f"{self._settings.api_url.rstrip('/')}/{path.lstrip('/')}"
        safe_to_retry = retry if retry is not None else method.upper() in {"GET", "HEAD"}
        headers = {
            "Accept": "application/json",
            "User-Agent": f"pagotic-sdk/{__version__}",
        }
        attempts = 0
        auth_retried = False

        while True:
            if auth:
                headers["Authorization"] = f"Bearer {self._auth.get_token()}"
            try:
                response = self._http.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                if safe_to_retry and attempts < self._settings.max_retries:
                    attempts += 1
                    time.sleep(self._backoff(attempts))
                    continue
                raise PagoTICConnectionError(
                    f"No se pudo conectar con PagoTIC: {exc}", exc
                ) from exc

            if response.status_code == 401 and auth and not auth_retried:
                auth_retried = True
                self._auth.invalidate()
                continue

            if (
                safe_to_retry
                and response.status_code in _RETRYABLE_STATUS
                and attempts < self._settings.max_retries
            ):
                attempts += 1
                time.sleep(self._backoff(attempts))
                continue

            return _handle_response(response)

    def _backoff(self, attempt: int) -> float:
        return min(5.0, self._settings.retry_backoff * (2.0 ** (attempt - 1)))

    def close(self) -> None:
        """Cierra el cliente HTTP si el SDK es su dueño."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> PagoTIC:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"PagoTIC(api_url={self._settings.api_url!r})"


class AsyncPagoTIC:
    """Cliente asincrónico del SDK."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        *,
        auth_url: str | None = None,
        api_url: str | None = None,
        realm: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_backoff: float | None = None,
        token_leeway: float | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = resolve_settings(
            username,
            password,
            client_id,
            client_secret,
            auth_url=auth_url,
            api_url=api_url,
            realm=realm,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            token_leeway=token_leeway,
        )
        self._http = http_client or httpx.AsyncClient(
            timeout=self._settings.timeout,
            follow_redirects=True,
        )
        self._owns_http = http_client is None
        self._auth = AsyncAuthManager(self._http, self._settings)
        self.payments = AsyncPaymentsResource(self)
        self.imports = AsyncImportsResource(self)
        self.subscriptions = AsyncSubscriptionsResource(self)

    @property
    def settings(self) -> Settings:
        """Configuración efectiva del cliente."""
        return self._settings

    async def get_collector_id(self) -> str:
        """Devuelve el ``collector_id`` del token de acceso.

        PagoTIC incluye el identificador del comercio en el claim
        ``signature`` (o ``family_name``) del JWT. No confundir con ``sub``
        ni con el ``client_id``.

        Returns:
            El identificador del comercio asociado al usuario.

        Raises:
            PagoTICAuthError: Si falla la autenticación.
            PagoTICValidationError: Si el token no contiene el claim esperado.
        """
        return collector_id_from_token(await self._auth.get_token())

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        auth: bool = True,
        retry: bool | None = None,
    ) -> Any:
        """Ejecuta una request contra la API, manejando auth y reintentos."""
        url = f"{self._settings.api_url.rstrip('/')}/{path.lstrip('/')}"
        safe_to_retry = retry if retry is not None else method.upper() in {"GET", "HEAD"}
        headers = {
            "Accept": "application/json",
            "User-Agent": f"pagotic-sdk/{__version__}",
        }
        attempts = 0
        auth_retried = False

        while True:
            if auth:
                headers["Authorization"] = f"Bearer {await self._auth.get_token()}"
            try:
                response = await self._http.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                if safe_to_retry and attempts < self._settings.max_retries:
                    attempts += 1
                    await asyncio.sleep(self._backoff(attempts))
                    continue
                raise PagoTICConnectionError(
                    f"No se pudo conectar con PagoTIC: {exc}", exc
                ) from exc

            if response.status_code == 401 and auth and not auth_retried:
                auth_retried = True
                await self._auth.invalidate()
                continue

            if (
                safe_to_retry
                and response.status_code in _RETRYABLE_STATUS
                and attempts < self._settings.max_retries
            ):
                attempts += 1
                await asyncio.sleep(self._backoff(attempts))
                continue

            return _handle_response(response)

    def _backoff(self, attempt: int) -> float:
        return min(5.0, self._settings.retry_backoff * (2.0 ** (attempt - 1)))

    async def aclose(self) -> None:
        """Cierra el cliente HTTP si el SDK es su dueño."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncPagoTIC:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncPagoTIC(api_url={self._settings.api_url!r})"
