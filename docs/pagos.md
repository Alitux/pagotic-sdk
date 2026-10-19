# Pagos

## Crear un pago

`payments.create()` acepta un `PaymentRequest` o un diccionario. Campos
principales:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `external_transaction_id` | `str` | Sí | Identificador único de la operación. |
| `currency_id` | `str` | No | Moneda, por ejemplo `ARS`. |
| `details` | `list[Detail]` | Sí | Detalle de conceptos e importes. |
| `payer` | `Payer` | Sí | Datos del pagador. |
| `type` | `PaymentType` | No | `debit`, `online`, `transfer`, `debin` o `coupon`. |
| `collector_id` | `str` | No | Comercio cobrador. |
| `return_url` | `str` | No | Retorno del checkout. |
| `back_url` | `str` | No | URL de vuelta. |
| `notification_url` | `str` | No | Webhook de notificaciones. |
| `due_date` | `str` | No | Vencimiento en ISO 8601. |
| `last_due_date` | `str` | No | Último vencimiento. |
| `payment_methods` | `list` | No | Medios de pago para un cobro directo. |
| `presets` | `Presets` | No | Filtros del checkout. |
| `metadata` | `dict` | No | Datos libres. |
| `distribution` | `Distribution` | No | Distribución programada. |

Si omitís `type` y `payment_methods`, se crea un pago pendiente y la respuesta
incluye `form_url` para que el pagador complete el checkout.

## Obtener un pago

```python
payment = sdk.payments.get("id-del-pago")
print(payment.status)
print(payment.final_amount)
```

Los importes se exponen como `Decimal`.

## Listar pagos

```python
from pagotic import Filter, FilterOperation

page = sdk.payments.list(
    page=1,
    limit=20,
    sorts={"request_date": "descending"},
    filters=[
        Filter("collector_id", FilterOperation.EQUAL, "14020"),
        Filter(
            "request_date",
            FilterOperation.GREATER_THAN_OR_EQUAL_TO,
            "20261001T000000000-0300",
        ),
    ],
)
```

La respuesta es el diccionario crudo de la API. En la API v2 el listado trae
las claves `rows`, `size`, `page`, `limit` y `filters`.

### Operaciones de filtrado

`EQUAL`, `IN`, `EXISTS`, `CONTAINS`, `CONTAINS_IGNORE_CASE`, `LESS_THAN`,
`LESS_THAN_OR_EQUAL_TO`, `GREATER_THAN_OR_EQUAL_TO` y `GREATER_THAN`.

Los valores de tipo lista se serializan separados por coma.

### Fechas

El formato de filtro es `yyyyMMdd'T'HHmmssSSSZ`, por ejemplo
`20250101T000000000-0300`. El helper `format_filter_datetime()` convierte
objetos `datetime` o `date` a ese formato:

```python
from datetime import datetime, timedelta, timezone
from pagotic import Filter, FilterOperation, format_filter_datetime

desde = datetime.now(timezone.utc) - timedelta(days=30)

filters = [
    Filter("collector_id", FilterOperation.EQUAL, "14020"),
    Filter(
        "request_date",
        FilterOperation.GREATER_THAN_OR_EQUAL_TO,
        format_filter_datetime(desde),
    ),
]
```

No existe `BETWEEN`: para un rango usá dos filtros separados sobre el mismo
campo.

### Filtros mínimos

La API exige combinaciones mínimas. Algunas válidas:

- `collector_id` + `request_date`
- `collector_id` + `paid_date`
- `collector_id` + `rejected_date`
- `collector_id` + `accreditation_date`
- `collector_id` + `refunded_date`
- `collector_id` + `payment_id`
- `owner.type` + `owner.id`
- `payer.email` + `request_date`
- `type` + `payment_methods.gateway.name`

Si no se cumple, la API responde `extended_code=4501`.

## Búsqueda legacy

```python
result = sdk.payments.search(
    {
        "type": "online",
        "status": "approved",
        "payer_email": "ana@example.com",
    }
)
```

## Cancelar

Solo para pagos `pending` o `issued`:

```python
sdk.payments.cancel("id-del-pago", "cancelado por el comercio")
```

Para un pago objetado existe:

```python
sdk.payments.cancel_objection("id-del-pago", "se retira la objeción")
```

## Devoluciones

```python
refund = sdk.payments.refund(
    "id-del-pago",
    {
        "type": "online",
        "reason": "Devolución solicitada por el cliente",
        "external_reference": "refund-001",
    },
)
print(refund.status)  # approved | rejected
```

El campo `type` es obligatorio y por defecto se envía `online`.

## Agrupaciones

Para agrupar dos o más pagos:

```python
grouped = sdk.payments.group(["id-1", "id-2"])
```

La cancelación de una agrupación se hace con:

```python
sdk.payments.cancel_group(grouped.id, "cancelación de la agrupación")
```

## Cupones

```python
coupon = sdk.payments.create_coupon(payment, media_payment_id=97)
print(coupon.payment_methods[0].coupon_number)
print(coupon.form_url)
```

`97` es Rapipago y `98` es Pago Fácil. El helper reemplaza el `type` por
`coupon` y arma un único medio de pago por el total del pago.

## Estados

`pending`, `issued`, `in_process`, `approved`, `rejected`, `cancelled`,
`refunded`, `deferred`, `objected`, `review`, `validate` y `overdue`.

## Tipos de pago

`debit`, `online`, `transfer`, `debin` y `coupon`.
