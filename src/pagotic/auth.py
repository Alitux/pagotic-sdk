"""Gestión de tokens OAuth2 contra Keycloak."""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass, replace
from typing import Any

import httpx
from pydantic import Field, ValidationError

from pagotic.exceptions import PagoTICAuthError, PagoTICConnectionError
from pagotic.models.base import PagoTICModel
from pagotic.settings import Settings


class Token(PagoTICModel):
    """Respuesta del endpoint de tokens."""

    access_token: str
    expires_in: int = 300
    refresh_token: str | None = None
    refresh_expires_in: int | None = None
    token_type: str = "Bearer"
    scope: str | None = None
    session_state: str | None = None
    not_before_policy: int | None = Field(default=None, alias="not-before-policy")


@dataclass(slots=True)
class TokenState:
    """Token vigente y sus vencimientos (reloj monotónico)."""

    access_token: str
    refresh_token: str | None
    access_expires_at: float
    refresh_expires_at: float | None

    def access_is_valid(self, leeway: float) -> bool:
        return bool(self.access_token) and time.monotonic() < self.access_expires_at - leeway

    def refresh_is_valid(self) -> bool:
        if not self.refresh_token:
            return False
        return self.refresh_expires_at is None or time.monotonic() < self.refresh_expires_at


def _state_from_token(token: Token) -> TokenState:
    now = time.monotonic()
    refresh_expires_at = (
        now + token.refresh_expires_in if token.refresh_expires_in is not None else None
    )
    return TokenState(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        access_expires_at=now + token.expires_in,
        refresh_expires_at=refresh_expires_at,
    )


def _parse_token_response(response: httpx.Response) -> Token:
    try:
        payload: Any = response.json()
    except ValueError as exc:
        raise PagoTICAuthError(
            "Respuesta de autenticación inválida",
            status_code=response.status_code,
            payload=response.text,
        ) from exc

    if response.status_code >= 400:
        raise _auth_error_from_payload(response.status_code, payload)

    try:
        return Token.model_validate(payload)
    except ValidationError as exc:
        raise PagoTICAuthError(
            "La respuesta de autenticación no contiene access_token",
            status_code=response.status_code,
            payload=payload,
        ) from exc


def _auth_error_from_payload(status_code: int, payload: Any) -> PagoTICAuthError:
    if isinstance(payload, dict):
        error = payload.get("error")
        description = payload.get("error_description")
        message = description or error or f"Error de autenticación (HTTP {status_code})"
        return PagoTICAuthError(
            str(message),
            error=str(error) if error is not None else None,
            description=str(description) if description is not None else None,
            status_code=status_code,
            payload=payload,
        )
    return PagoTICAuthError(
        f"Error de autenticación (HTTP {status_code})",
        status_code=status_code,
        payload=payload,
    )


def _form_data(settings: Settings) -> dict[str, str]:
    return {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
    }


class AuthManager:
    """Obtiene y renueva tokens de forma sincrónica."""

    def __init__(self, http: httpx.Client, settings: Settings) -> None:
        self._http = http
        self._settings = settings
        self._state: TokenState | None = None
        self._lock = threading.Lock()

    def get_token(self) -> str:
        with self._lock:
            state = self._state
            if state is not None and state.access_is_valid(self._settings.token_leeway):
                return state.access_token
            if state is not None and state.refresh_is_valid():
                try:
                    return self._refresh(state.refresh_token or "")
                except PagoTICAuthError:
                    self._state = None
            return self._login()

    def invalidate(self) -> None:
        """Descarta el access token conservando el refresh token si sigue vigente."""
        with self._lock:
            if self._state is not None:
                self._state = replace(self._state, access_token="", access_expires_at=0.0)

    def _login(self) -> str:
        data = {
            **_form_data(self._settings),
            "username": self._settings.username,
            "password": self._settings.password,
            "grant_type": "password",
        }
        token = self._post_token(data)
        self._state = _state_from_token(token)
        return token.access_token

    def _refresh(self, refresh_token: str) -> str:
        data = {
            **_form_data(self._settings),
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        token = self._post_token(data)
        self._state = _state_from_token(token)
        return token.access_token

    def _post_token(self, data: dict[str, str]) -> Token:
        try:
            response = self._http.post(
                self._settings.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.RequestError as exc:
            raise PagoTICConnectionError(
                f"No se pudo conectar con el servicio de autenticación: {exc}", exc
            ) from exc
        return _parse_token_response(response)


class AsyncAuthManager:
    """Obtiene y renueva tokens de forma asincrónica."""

    def __init__(self, http: httpx.AsyncClient, settings: Settings) -> None:
        self._http = http
        self._settings = settings
        self._state: TokenState | None = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        async with self._lock:
            state = self._state
            if state is not None and state.access_is_valid(self._settings.token_leeway):
                return state.access_token
            if state is not None and state.refresh_is_valid():
                try:
                    return await self._refresh(state.refresh_token or "")
                except PagoTICAuthError:
                    self._state = None
            return await self._login()

    async def invalidate(self) -> None:
        """Descarta el access token conservando el refresh token si sigue vigente."""
        async with self._lock:
            if self._state is not None:
                self._state = replace(self._state, access_token="", access_expires_at=0.0)

    async def _login(self) -> str:
        data = {
            **_form_data(self._settings),
            "username": self._settings.username,
            "password": self._settings.password,
            "grant_type": "password",
        }
        token = await self._post_token(data)
        self._state = _state_from_token(token)
        return token.access_token

    async def _refresh(self, refresh_token: str) -> str:
        data = {
            **_form_data(self._settings),
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        token = await self._post_token(data)
        self._state = _state_from_token(token)
        return token.access_token

    async def _post_token(self, data: dict[str, str]) -> Token:
        try:
            response = await self._http.post(
                self._settings.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except httpx.RequestError as exc:
            raise PagoTICConnectionError(
                f"No se pudo conectar con el servicio de autenticación: {exc}", exc
            ) from exc
        return _parse_token_response(response)
