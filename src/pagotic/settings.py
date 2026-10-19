"""Configuración del cliente."""

from __future__ import annotations

import os
from dataclasses import dataclass

from pagotic.exceptions import PagoTICConfigError

DEFAULT_AUTH_URL = "https://a.paypertic.com"
DEFAULT_API_URL = "https://api.paypertic.com"
DEFAULT_REALM = "entidades"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF = 0.25
DEFAULT_TOKEN_LEEWAY = 30.0


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuración inmutable de una instancia del SDK."""

    username: str
    password: str
    client_id: str
    client_secret: str
    auth_url: str = DEFAULT_AUTH_URL
    api_url: str = DEFAULT_API_URL
    realm: str = DEFAULT_REALM
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF
    token_leeway: float = DEFAULT_TOKEN_LEEWAY

    @property
    def token_url(self) -> str:
        """URL completa del endpoint de tokens de Keycloak."""
        base = self.auth_url.rstrip("/")
        return f"{base}/auth/realms/{self.realm}/protocol/openid-connect/token"


def _pick(explicit: str | None, env_name: str) -> str | None:
    if explicit is not None:
        return explicit
    return os.environ.get(env_name)


def resolve_settings(
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
) -> Settings:
    """Resuelve la configuración desde argumentos y variables ``PAGOTIC_*``."""
    resolved_username = _pick(username, "PAGOTIC_USERNAME")
    resolved_password = _pick(password, "PAGOTIC_PASSWORD")
    resolved_client_id = _pick(client_id, "PAGOTIC_CLIENT_ID")
    resolved_client_secret = _pick(client_secret, "PAGOTIC_CLIENT_SECRET")

    missing = [
        name
        for name, value in (
            ("username", resolved_username),
            ("password", resolved_password),
            ("client_id", resolved_client_id),
            ("client_secret", resolved_client_secret),
        )
        if not value
    ]
    if missing:
        raise PagoTICConfigError(
            "Faltan credenciales de PagoTIC: "
            + ", ".join(missing)
            + ". Pasalas al cliente o definí PAGOTIC_* en el entorno."
        )

    resolved_timeout = timeout
    if resolved_timeout is None:
        resolved_timeout = float(os.environ.get("PAGOTIC_TIMEOUT", DEFAULT_TIMEOUT))
    if resolved_timeout <= 0:
        raise PagoTICConfigError("timeout debe ser mayor que cero")

    resolved_max_retries = max_retries
    if resolved_max_retries is None:
        resolved_max_retries = int(os.environ.get("PAGOTIC_MAX_RETRIES", DEFAULT_MAX_RETRIES))
    if resolved_max_retries < 0:
        raise PagoTICConfigError("max_retries debe ser mayor o igual a cero")

    resolved_backoff = retry_backoff
    if resolved_backoff is None:
        resolved_backoff = float(os.environ.get("PAGOTIC_RETRY_BACKOFF", DEFAULT_RETRY_BACKOFF))
    if resolved_backoff < 0:
        raise PagoTICConfigError("retry_backoff debe ser mayor o igual a cero")

    resolved_leeway = token_leeway
    if resolved_leeway is None:
        resolved_leeway = float(os.environ.get("PAGOTIC_TOKEN_LEEWAY", DEFAULT_TOKEN_LEEWAY))
    if resolved_leeway < 0:
        raise PagoTICConfigError("token_leeway debe ser mayor o igual a cero")

    return Settings(
        username=resolved_username or "",
        password=resolved_password or "",
        client_id=resolved_client_id or "",
        client_secret=resolved_client_secret or "",
        auth_url=auth_url or os.environ.get("PAGOTIC_AUTH_URL", DEFAULT_AUTH_URL),
        api_url=api_url or os.environ.get("PAGOTIC_API_URL", DEFAULT_API_URL),
        realm=realm or os.environ.get("PAGOTIC_REALM", DEFAULT_REALM),
        timeout=resolved_timeout,
        max_retries=resolved_max_retries,
        retry_backoff=resolved_backoff,
        token_leeway=resolved_leeway,
    )
