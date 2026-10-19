# Inicio rápido

## Crear un pago

El campo `external_transaction_id` es obligatorio y debe ser único. Si no se
envía `type` ni `payment_methods`, la API crea un pago pendiente y devuelve una
`form_url` para que el pagador elija el medio de pago en el checkout.

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    payment = sdk.payments.create(
        {
            "external_transaction_id": "orden-123",
            "currency_id": "ARS",
            "notification_url": "https://mi-sitio.com/webhooks/pagotic",
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
                    "number": "30111222",
                    "country": "ARG",
                },
            },
        }
    )

    print(payment.id)
    print(payment.status)
    print(payment.form_url)
```

## Consultar un pago

```python
payment = sdk.payments.get("f45e218c-1a20-4802-8cb9-97581b7711a6")
print(payment.status, payment.final_amount)
```

## Cancelar un pago

Solo se pueden cancelar pagos en estado `pending` o `issued`:

```python
sdk.payments.cancel("f45e218c-1a20-4802-8cb9-97581b7711a6", "cancelado por el comercio")
```

## Versión asincrónica

```python
import asyncio
from pagotic import AsyncPagoTIC


async def main() -> None:
    async with AsyncPagoTIC() as sdk:
        payment = await sdk.payments.get("id-del-pago")
        print(payment.status)


asyncio.run(main())
```

## Próximos pasos

- [Pagos](pagos.md): filtros, devoluciones, cupones y agrupaciones.
- [Distribución programada](distribucion.md): repartir el pago entre varias
  cuentas CBU.
- [Medios de pago y QR](medios-de-pago.md): presets y códigos QR.
