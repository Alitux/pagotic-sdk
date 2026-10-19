# PagoTIC SDK para Python

> **Paquete no oficial.** Este SDK es mantenido por la comunidad y **no está
> afiliado, respaldado ni soportado por PagoTIC**. Usá la API oficial bajo tu
> propia responsabilidad.

SDK en Python para integrar la pasarela de pagos **PagoTIC** (Pay per TIC).
Incluye cliente sincrónico y asincrónico, autenticación OAuth2 automática,
modelos tipados con Pydantic, pagos, distribución programada, importación
masiva, suscripciones y utilidades para webhooks.

- Python 3.10+
- `httpx` + `pydantic` v2
- Tipado completo (`py.typed`)
- Tests con `respx`, lint con `ruff`, chequeo de tipos con `mypy`

## Instalación

```bash
pip install pagotic-sdk
```

Con [`pipx`](https://pipx.pypa.io/) para instalarlo aislado:

```bash
pipx install pagotic-sdk
```

Para generar códigos QR localmente (sin servicios externos) agregá el extra `qr`:

```bash
pip install "pagotic-sdk[qr]"
pipx install "pagotic-sdk[qr]"   # alternativa con pipx
```

Con Poetry:

```bash
poetry add pagotic-sdk
poetry add "pagotic-sdk[qr]"  # opcional, para QR local
```

También podés instalarlo desde el repositorio:

```bash
pip install "pagotic-sdk @ git+https://github.com/Alitux/pagotic-sdk.git"
```

## Inicio rápido

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    payment = sdk.payments.create(
        {
            "external_transaction_id": "orden-123",
            "currency_id": "ARS",
            "details": [
                {
                    "external_reference": "item-1",
                    "concept_id": 920,
                    "concept_description": "Suscripción mensual",
                    "amount": 1500.50,
                }
            ],
            "payer": {
                "name": "Ana Pérez",
                "email": "ana@example.com",
                "identification": {
                    "type": "DNI_ARG",
                    "number": "12345678",
                    "country": "ARG",
                },
            },
            "notification_url": "https://example.com/webhooks/pagotic",
        }
    )

    print(payment.id, payment.status, payment.form_url)
```

## Configuración

Las credenciales se pueden pasar al constructor o definir por entorno:

| Variable | Descripción |
| --- | --- |
| `PAGOTIC_USERNAME` | Usuario de la API |
| `PAGOTIC_PASSWORD` | Contraseña |
| `PAGOTIC_CLIENT_ID` | Client ID de Keycloak |
| `PAGOTIC_CLIENT_SECRET` | Client Secret de Keycloak |
| `PAGOTIC_AUTH_URL` | Default: `https://a.paypertic.com` |
| `PAGOTIC_API_URL` | Default: `https://api.paypertic.com` |
| `PAGOTIC_REALM` | Default: `entidades` |
| `PAGOTIC_TIMEOUT` | Timeout HTTP en segundos (default: `30`) |
| `PAGOTIC_MAX_RETRIES` | Reintentos en GET/HEAD (default: `2`) |
| `PAGOTIC_RETRY_BACKOFF` | Base del backoff exponencial (default: `0.25`) |
| `PAGOTIC_TOKEN_LEEWAY` | Margen de renovación del token (default: `30`) |

Las credenciales y URLs se normalizan automáticamente: se ignoran los espacios
al inicio y al final, y un valor con solo espacios se considera ausente. En los
ejemplos y tests de integración el `.env` se carga con `override=True` para que
variables del sistema (por ejemplo `USERNAME`) no pisen las credenciales.

```python
from pagotic import PagoTIC

sdk = PagoTIC(
    username="...",
    password="...",
    client_id="...",
    client_secret="...",
)
```

El token se solicita de forma lazy, se cachea según `expires_in`, se renueva
con `refresh_token` y, ante un `401`, se reintenta una vez. Los reintentos por
red o `5xx`/`429` solo aplican a métodos idempotentes (`GET`/`HEAD`), nunca a la
creación de pagos.

## Pagos

### Crear, obtener y cancelar

```python
payment = sdk.payments.create({...})
same = sdk.payments.get(payment.id)
sdk.payments.cancel(payment.id, "Solicitado por el comercio")
sdk.payments.cancel_objection(payment.id, "Objeción resuelta")
```

### Listar con filtros

```python
result = sdk.payments.list(
    page=1,
    limit=20,
    sorts={"request_date": "descending"},
    filters=[
        {"field": "collector_id", "operation": "EQUAL", "value": "123"},
        {
            "field": "request_date",
            "operation": "GREATER_THAN_OR_EQUAL_TO",
            "value": "20250101T000000000-0300",
        },
    ],
)
```

La API exige combinaciones mínimas de filtros (por ejemplo
`collector_id + request_date`). No uses `BETWEEN`: enviá dos filtros sobre el
mismo campo. Para fechas podés usar `format_filter_datetime`.

### Búsqueda legacy

```python
sdk.payments.search({"payer_email": "ana@example.com", "status": "approved"})
```

### Devoluciones, agrupaciones y cupones

```python
refund = sdk.payments.refund(payment.id, {"reason": "Reintegro"})

grouped = sdk.payments.group([payment_a.id, payment_b.id])
sdk.payments.cancel_group(grouped.id, "Cancelación de la agrupación")

coupon = sdk.payments.create_coupon(payment, media_payment_id=97)  # 97 Rapipago, 98 Pago Fácil
print(coupon.payment_methods[0].coupon_number)
```

### Medios de pago y presets

`MediaPayment` enumera los `media_payment_id` documentados. Podés combinar
tarjetas de crédito, débito y QR en el checkout con `presets`:

```python
from pagotic import MediaPayment, PaymentRequest, Presets

payment = sdk.payments.create(
    PaymentRequest(
        external_transaction_id="orden-125",
        currency_id="ARS",
        details=[{"external_reference": "a", "amount": 1500}],
        payer={"name": "Ana Pérez", "email": "ana@example.com"},
        presets=Presets(
            media_payment_ids=[
                *MediaPayment.cards(),  # crédito + débito
                MediaPayment.QR,
            ]
        ),
    )
)
print(payment.form_url)  # checkout filtrado a esos medios
```

`presets` solo filtra las opciones del checkout: no cobra en el momento. Para
habilitar el QR interoperable usá `MediaPayment.QR` (85). También podés agrupar
por tipo: `MediaPayment.credit_cards()`, `MediaPayment.debit_cards()`,
`MediaPayment.cards()` y `MediaPayment.coupons()`.

Cuando se cobra directo con tarjeta (`type="online"` + `payment_methods`), el
QR no participa del flujo. Los IDs deben estar habilitados para el comercio.

### QR

El pago se crea con QR como medio (por ejemplo, `presets` con
`MediaPayment.QR`). Una vez creado, `raw_qr` aparece en `payment_methods[]` al
consultar `sdk.payments.get(id)` o en el webhook:

```python
from pagotic import save_qr

payment = sdk.payments.get(payment_id)
if payment.raw_qr:
    path = save_qr(payment.raw_qr, "qr.png", scale=6)
    print(f"QR guardado en {path}")
```

El QR se genera localmente con [`segno`](https://github.com/heuer/segno) (Python
puro, sin Pillow ni servicios externos). Para eso instalá el extra:

```bash
pip install "pagotic-sdk[qr]"
```

También están `render_qr_png` y `render_qr_svg` para obtener los bytes o el SVG
en memoria. Si preferís delegar la imagen a un servicio externo, seguí usando
`build_qr_image_url`.

Cada QR es de un solo uso: una vez pagado queda invalidado.

## Distribución programada

Al crear un pago se puede repartir el monto entre varias cuentas CBU:

```python
from pagotic import Distribution, PaymentRequest

payment = sdk.payments.create(
    PaymentRequest(
        external_transaction_id="orden-124",
        currency_id="ARS",
        details=[
            {"external_reference": "a", "amount": 800},
            {"external_reference": "b", "amount": 200},
        ],
        payer={"name": "Ana Pérez", "email": "ana@example.com"},
        distribution=Distribution.scheduled(
            [
                {
                    "cbu": "0000000000000000000000",
                    "cuit": "20123456789",
                    "name": "Proveedor A",
                    "amount": 800,
                },
                {
                    "cbu": "1111111111111111111111",
                    "cuit": "20987654321",
                    "name": "Proveedor B",
                    "amount": 200,
                },
            ]
        ),
    )
)
```

**Validación obligatoria:** la suma de `distribution.details[].amount` debe ser
exactamente igual a la suma de `details[].amount`. Si no coincide, el SDK lanza
`PagoTICValidationError` y no envía la request.

## Importación masiva

El CSV debe estar sin encabezados y tener como máximo 40.000 registros. Al menos
uno de los flags debe ser `true`; si `match_identification=True`, los otros dos
deben ser `false`.

```python
summary = sdk.imports.preimport("pagos.csv", match_payer=True)
sdk.imports.get(summary.import_id)
details = sdk.imports.details(summary.import_id)
sdk.imports.approve(summary.import_id)
# o bien:
sdk.imports.cancel(summary.import_id, "Importación duplicada")
```

También están disponibles las rutas legacy `verify_legacy`, `approve_legacy` y
`cancel_legacy`.

## Suscripciones (experimental)

> Esta funcionalidad solo aparece en la colección Postman, no en la
> documentación PDF. La API podría cambiarla sin previo aviso.

```python
subscription = sdk.subscriptions.create(
    {
        "currency_id": "ARS",
        "due_day": "30",
        "recurrence": "monthly",
        "detail": {
            "external_reference": "plan-1",
            "concept_description": "Plan mensual",
            "amount": 5000,
        },
        "payment_method": {
            "number": "4111111111111111",
            "holder": {
                "name": "Ana Pérez",
                "identification": {"type": "DNI_ARG", "number": "12345678", "country": "ARG"},
            },
        },
        "payer": {"name": "Ana Pérez", "email": "ana@example.com"},
    }
)
sdk.subscriptions.list()
sdk.subscriptions.search({"payer_email": "ana@example.com"})
sdk.subscriptions.cancel(subscription.id, "Baja solicitada")
```

## Webhooks

PagoTIC envía el JSON del pago a `notification_url`. La documentación no define
firma ni secreto, así que el SDK solo parsea el payload:

```python
from fastapi import FastAPI, Request
from pagotic import parse_notification

app = FastAPI()


@app.post("/webhooks/pagotic")
async def pagotic_webhook(request: Request):
    payment = parse_notification(await request.body())
    if payment.status == "approved":
        ...
    return {"ok": True}
```

## Errores

```python
from pagotic import (
    PagoTICAPIError,
    PagoTICAuthError,
    PagoTICConnectionError,
    PagoTICValidationError,
)

try:
    sdk.payments.get("no-existe")
except PagoTICAPIError as exc:
    print(exc.status_code, exc.code, exc.extended_code, exc.message, exc.payload)
```

Jerarquía: `PagoTICError` → `PagoTICConfigError`, `PagoTICValidationError`,
`PagoTICConnectionError`, `PagoTICAPIError`, `PagoTICAuthError`.

## Cliente asincrónico

```python
from pagotic import AsyncPagoTIC

async with AsyncPagoTIC() as sdk:
    payment = await sdk.payments.create({...})
    await sdk.payments.cancel(payment.id, "Cancelado")
```

## Desarrollo

```bash
poetry install
make lint        # ruff check + format --check
make typecheck   # mypy
make test        # pytest
make test-cov    # pytest + cobertura
make build       # wheel + sdist
```

Los tests unitarios usan `respx` y no tocan la red. Los tests de integración
están marcados con `integration` y se saltean si no hay credenciales:

```bash
cp .env.example .env   # completá tus credenciales
PAGOTIC_RUN_INTEGRATION=1 poetry run pytest -m integration
```

`.env` está ignorado por git; nunca commitees credenciales.

## Mantenimiento

Mantenido por **Alitux** — [alitux@disroot.org](mailto:alitux@disroot.org).

## Licencia

GNU General Public License v3.0 o posterior. Ver [LICENSE](LICENSE).
