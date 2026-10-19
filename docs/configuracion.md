# Configuración

## Credenciales

El SDK se autentica contra Keycloak con el *password grant* de OAuth2. Necesitás
cuatro datos que provee PagoTIC:

| Parámetro | Variable de entorno | Descripción |
|---|---|---|
| `username` | `PAGOTIC_USERNAME` | Usuario de la entidad. |
| `password` | `PAGOTIC_PASSWORD` | Contraseña del usuario. |
| `client_id` | `PAGOTIC_CLIENT_ID` | Client ID de la aplicación. |
| `client_secret` | `PAGOTIC_CLIENT_SECRET` | Client Secret de la aplicación. |

```python
from pagotic import PagoTIC

sdk = PagoTIC(
    username="usuario",
    password="contraseña",
    client_id="client-id",
    client_secret="client-secret",
)
```

Las credenciales y las URLs se normalizan quitando espacios al inicio y al
final. Un valor compuesto solo por espacios se considera ausente.

## Variables de entorno

Si no pasás los parámetros al constructor, se leen del entorno:

| Variable | Valor por defecto |
|---|---|
| `PAGOTIC_AUTH_URL` | `https://a.paypertic.com` |
| `PAGOTIC_API_URL` | `https://api.paypertic.com` |
| `PAGOTIC_REALM` | `entidades` |
| `PAGOTIC_TIMEOUT` | `30` segundos |
| `PAGOTIC_MAX_RETRIES` | `2` |
| `PAGOTIC_RETRY_BACKOFF` | `0.25` segundos |
| `PAGOTIC_TOKEN_LEEWAY` | `30` segundos |

El endpoint de token se arma como:

```
{auth_url}/auth/realms/{realm}/protocol/openid-connect/token
```

## Cliente sincrónico y asincrónico

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    payment = sdk.payments.get("id-del-pago")
```

```python
from pagotic import AsyncPagoTIC

async with AsyncPagoTIC() as sdk:
    payment = await sdk.payments.get("id-del-pago")
```

Los clientes también se pueden cerrar explícitamente con `close()` y
`aclose()`.

## Cliente HTTP propio

Podés inyectar un `httpx.Client` o `httpx.AsyncClient` ya configurado. El SDK no
lo cierra al finalizar:

```python
import httpx
from pagotic import PagoTIC

with httpx.Client(timeout=10) as http_client:
    sdk = PagoTIC(http_client=http_client)
    sdk.payments.get("id-del-pago")
```

## Autenticación y reintentos

- El token se solicita en la primera llamada y se reutiliza hasta que expira.
- Al expirar se renueva con el `refresh_token`; si el refresh falla, se vuelve
  al *password grant*.
- Ante un `401` se invalida el token y se reintenta una vez.
- Los reintentos automáticos aplican a `GET`/`HEAD` ante errores de conexión,
  `429` y `5xx`. Los `POST` no se reintentan para evitar duplicados.

## Alternativa con `.env`

El SDK no carga archivos `.env` por sí solo. En ejemplos y tests se usa
`python-dotenv` como dependencia de desarrollo:

```python
from dotenv import load_dotenv

load_dotenv()
```

Recordá mantener `.env` fuera del control de versiones.
