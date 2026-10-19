# Webhooks

PagoTIC envía una notificación HTTP a la `notification_url` indicada al crear
el pago. El cuerpo es el JSON completo del pago.

## Parsear una notificación

```python
from pagotic import parse_notification

payment = parse_notification(payload)
print(payment.id, payment.status)
```

`parse_notification()` acepta un diccionario, un string JSON o bytes. También
reconoce el sobre `{"payment": {...}}`.

## Ejemplo con FastAPI

```python
from fastapi import FastAPI, Request
from pagotic import parse_notification

app = FastAPI()


@app.post("/webhooks/pagotic")
async def pagotic_webhook(request: Request) -> dict[str, str]:
    payload = await request.json()
    payment = parse_notification(payload)

    if payment.status == "approved":
        # Entregar el producto o servicio.
        ...

    return {"status": "ok"}
```

## Seguridad

!!! danger "Sin firma documentada"
    PagoTIC no documenta un mecanismo de firma para las notificaciones. El SDK
    no puede verificar su autenticidad.

Recomendaciones:

1. No confíes ciegamente en el cuerpo recibido.
2. Ante una notificación, consultá el pago con `sdk.payments.get(payment.id)`
   y usá el estado devuelto por la API.
3. Validá que el `collector_id` corresponda a tu comercio.
4. Implementá idempotencia: una misma notificación puede reintentarse.
5. Respondé rápido con `2xx`; procesá en segundo plano si es necesario.

## Idempotencia

Guardá el `id` del pago o el `external_transaction_id` y evitá procesar dos
veces la misma transición de estado.

```python
procesados: set[str] = set()


def procesar(payment) -> None:
    if payment.id in procesados:
        return
    procesados.add(payment.id)
    # ...
```
