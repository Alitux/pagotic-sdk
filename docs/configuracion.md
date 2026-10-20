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

## Descubrir el collector_id

PagoTIC incluye el identificador del comercio en los claims `signature` y
`family_name` del `access_token`. El SDK puede leerlo por vos:

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    collector_id = sdk.get_collector_id()
    print(collector_id)  # por ejemplo: 14020
```

En el cliente asincrónico:

```python
collector_id = await sdk.get_collector_id()
```

El método dispara la autenticación si todavía no hay token. Los claims `sub` y
el `client_id` **no** son el `collector_id`.

Para validarlo de forma read-only contra la API, listá un pago filtrando por
ese identificador:

```python
from pagotic import Filter, FilterOperation

page = sdk.payments.list(
    page=1,
    limit=1,
    filters=[Filter("collector_id", FilterOperation.EQUAL, collector_id)],
)
```

Si el `collector_id` no corresponde al usuario, la API responde
`400 Unrelated collector` (`extended_code=4201`).

!!! note "Sin verificación de firma"
    `collector_id_from_token()` y `decode_jwt_payload()` decodifican el JWT
    localmente sin verificar su firma. Usalos para descubrir configuración, no
    como mecanismo de seguridad. La validación definitiva la hace la API.

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
