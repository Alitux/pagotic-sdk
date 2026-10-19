"""Excepciones públicas del SDK."""

from __future__ import annotations

from typing import Any


class PagoTICError(Exception):
    """Excepción base de todos los errores del SDK."""


class PagoTICConfigError(PagoTICError):
    """Falta una credencial o un parámetro de configuración."""


class PagoTICValidationError(PagoTICError):
    """Los datos enviados no son válidos y no llegaron a la API."""

    def __init__(self, message: str, errors: list[Any] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class PagoTICConnectionError(PagoTICError):
    """No se pudo establecer comunicación con PagoTIC."""

    def __init__(self, message: str, original: Exception | None = None) -> None:
        super().__init__(message)
        self.original = original


class PagoTICAPIError(PagoTICError):
    """La API respondió con un error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: int | str | None = None,
        extended_code: int | str | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.extended_code = extended_code
        self.payload = payload

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"HTTP {self.status_code}")
        if self.code is not None:
            parts.append(f"code={self.code}")
        if self.extended_code is not None:
            parts.append(f"extended_code={self.extended_code}")
        return " | ".join(parts)


class PagoTICAuthError(PagoTICAPIError):
    """Falló la autenticación contra Keycloak."""

    def __init__(
        self,
        message: str,
        *,
        error: str | None = None,
        description: str | None = None,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            code=error,
            payload=payload,
        )
        self.error = error
        self.description = description
