# Suscripciones

!!! warning "Funcionalidad experimental"
    Los endpoints de suscripciones solo aparecen en la colección Postman y no
    están descriptos en la documentación principal. La API podría cambiarlos.
    Probá esta funcionalidad en un entorno controlado antes de usarla en
    producción.

## Crear una suscripción

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    subscription = sdk.subscriptions.create(
        {
            "type": "subscription",
            "currency_id": "ARS",
            "due_day": "30",
            "recurrence": "monthly",
            "notification_url": "https://mi-sitio.com/webhooks/pagotic",
            "detail": {
                "external_reference": "plan-premium",
                "concept_id": 920,
                "concept_description": "Plan premium",
                "amount": 5000,
            },
            "payment_method": {
                "number": "4507990000004905",
                "holder": {
                    "name": "Ana Pérez",
                    "identification": {
                        "type": "DNI_ARG",
                        "number": "30111222",
                        "country": "ARG",
                    },
                },
            },
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
```

## Listar

```python
subscriptions = sdk.subscriptions.list()
```

## Buscar

```python
result = sdk.subscriptions.search(
    {
        "status": "active",
        "payer_email": "ana@example.com",
    }
)
```

Campos de búsqueda disponibles: `type`, `status`, `detail_external_reference`,
`detail_concept_id`, `detail_concept_description`, `payer_name`,
`payer_external_reference`, `payer_email`, `payer_identification_number` y
`payment_method_card_last_four_digits`.

## Cancelar

```python
sdk.subscriptions.cancel("subscription-id", "cancelada por el cliente")
```
