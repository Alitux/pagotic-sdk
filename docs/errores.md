# Errores

## Jerarquía

```text
PagoTICError
├── PagoTICConfigError
├── PagoTICValidationError
├── PagoTICConnectionError
└── PagoTICAPIError
    └── PagoTICAuthError
```

| Excepción | Cuándo ocurre |
|---|---|
| `PagoTICConfigError` | Falta una credencial o un parámetro de configuración. |
| `PagoTICValidationError` | Los datos no son válidos y no se llamó a la API. |
| `PagoTICConnectionError` | No se pudo conectar con PagoTIC. |
| `PagoTICAPIError` | La API respondió con un error. |
| `PagoTICAuthError` | Falló la autenticación contra Keycloak. |

## Atributos

`PagoTICValidationError` expone `errors` con el detalle de validación.

`PagoTICAPIError` expone:

- `message`
- `status_code`
- `code`
- `extended_code`
- `payload`

`PagoTICAuthError` agrega `error` y `description`.

## Capturar errores

```python
from pagotic import (
    PagoTICAPIError,
    PagoTICAuthError,
    PagoTICConnectionError,
    PagoTICValidationError,
)

try:
    payment = sdk.payments.get("id-inexistente")
except PagoTICAuthError as exc:
    print("Credenciales inválidas:", exc.description)
except PagoTICAPIError as exc:
    print(exc.message, exc.status_code, exc.code, exc.extended_code)
except PagoTICValidationError as exc:
    print("Datos inválidos:", exc.errors)
except PagoTICConnectionError as exc:
    print("Sin conexión:", exc.original)
```

## Códigos de la API

| Código | Significado |
|---:|---|
| 4000 | Request inválido. |
| 4001 | ID de pago inválido. |
| 4003 | Estado de pago inválido. |
| 4004 | Collector inválido. |
| 4019 | Acción inválida. |
| 4035 | Método de devolución no permitido. |
| 4050 | Parámetro no permitido. |
| 4051 | Collector no relacionado. |
| 4060 | Parámetro no encontrado. |
| 4100 | Acceso denegado. |
| 4501 | Faltan los filtros mínimos requeridos. |
| 4601 | Filtros inválidos. |
| 5000 / 5001 | Error interno. |

La API devuelve los errores con la forma:

```json
{
  "code": 400,
  "message": "Query not have the minimum fields required for realm",
  "extended_code": 4501
}
```

## Errores de autenticación

Keycloak devuelve `{error, error_description}`. Los casos habituales:

| `error` | Causa |
|---|---|
| `invalid_request` | Falta un parámetro obligatorio. |
| `invalid_grant` | Usuario, contraseña o refresh token inválidos. |
| `unauthorized_client` | `client_id` o `client_secret` inválidos. |

## Errores de validación del SDK

Antes de enviar el request, el SDK valida:

- Que la suma de `distribution.details` coincida con la de `details`.
- Que los importes de distribución sean mayores que cero.
- Que el CUIT tenga 11 dígitos y dígito verificador correcto.
- Que el CSV de importación tenga al menos un flag de emparejamiento.
- Que se agrupen al menos dos pagos.

## Reintentos

Los errores de conexión, `429` y `5xx` se reintentan automáticamente en
`GET`/`HEAD`. Los `POST` no se reintentan para evitar operaciones duplicadas.
