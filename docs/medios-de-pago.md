# Medios de pago y QR

## Enum `MediaPayment`

`MediaPayment` es un `IntEnum` con los identificadores documentados por PagoTIC.
Además de los valores individuales, incluye helpers:

```python
from pagotic import MediaPayment

MediaPayment.credit_cards()  # tarjetas de crédito
MediaPayment.debit_cards()  # tarjetas de débito
MediaPayment.cards()  # crédito + débito
MediaPayment.coupons()  # cuponeras
```

## Tabla de medios

| ID | Nombre | Tipo | Transacciones |
|---:|---|---|---|
| 1 | CBU | BANK ACCOUNT | DEBIT, DEBIN |
| 2 | AMERICAN_EXPRESS | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 3 | DINERS | CREDIT CARD | ONLINE, CLOVER |
| 4 | JCB | CREDIT CARD | ONLINE, CLOVER |
| 5 | MASTERCARD | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 6 | CABAL | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 7 | NARANJA | CREDIT CARD | ONLINE, CLOVER |
| 8 | KADICARD | CREDIT CARD | ONLINE, CLOVER |
| 9 | VISA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 10 | VISA_DEBITO | DEBIT CARD | DEBIT, ONLINE, CLOVER |
| 11 | VISA_NARANJA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 12 | FAVACARD | CREDIT CARD | ONLINE, CLOVER |
| 13 | LIDER | CREDIT CARD | ONLINE, CLOVER |
| 14 | CREDIMAS | CREDIT CARD | ONLINE, CLOVER |
| 15 | NEVADA | CREDIT CARD | ONLINE, CLOVER |
| 16 | PATAGONIA_365 | CREDIT CARD | ONLINE, CLOVER |
| 17 | SOL | CREDIT CARD | ONLINE, CLOVER |
| 18 | T_SHOPPING | CREDIT CARD | ONLINE, CLOVER |
| 19 | ITALCRED | CREDIT CARD | ONLINE, CLOVER |
| 20 | CENCOSUD | CREDIT CARD | ONLINE, CLOVER |
| 21 | PYME_NACION | CREDIT CARD | ONLINE, CLOVER |
| 22 | ARGENTA | CREDIT CARD | ONLINE, CLOVER |
| 23 | NATIVA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 24 | ARGENCARD | CREDIT CARD | ONLINE, CLOVER |
| 25 | MAESTRO | DEBIT CARD | ONLINE, CLOVER |
| 26 | CORDOBESA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 27 | MASTERCARD_DEBIT | DEBIT CARD | DEBIT, ONLINE, CLOVER |
| 29 | CORDOBESA_VISA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 30 | NATIVA_VISA | CREDIT CARD | DEBIT, ONLINE, CLOVER |
| 31 | CABAL_DEBIT | DEBIT CARD | DEBIT, ONLINE, CLOVER |
| 32 | COOPEPLUS | CREDIT CARD | ONLINE, CLOVER |
| 85 | QR | QR | CLOVER, QR |
| 86 | BANCON | BANCON | BANCON |
| 87 | INTERBANKING | INTERBANKING | INTERBANKING |
| 88 | PAGO_MIS_CUENTAS | PAGO MIS CUENTAS | PAGO_MIS_CUENTAS |
| 89 | PROVINCIA_NET | COUPON | COUPON |
| 90 | CREDITS | CREDITS | CREDITS |
| 91 | LINK_PAGOS | LINK PAGOS | LINK_PAGOS |
| 92 | CRYPTO | CRYPTO | CRYPTO |
| 94 | TRANSFERENCIA | TRANSFERENCIA | TRANSFER |
| 95 | EFECTIVO | EFECTIVO | COBRO |
| 96 | CHEQUE | CHEQUE | COBRO |
| 97 | RAPIPAGO | COUPON | COUPON |
| 98 | PAGOFACIL | COUPON | COUPON |
| 99 | UNDEFINED | — | — |
| 100 | COBRO EXPRESS | COUPON | COUPON |

## Presets

El objeto `presets` filtra o fuerza las opciones disponibles en el checkout.
El atributo principal es `media_payment_ids`:

```python
from pagotic import MediaPayment, PagoTIC

with PagoTIC() as sdk:
    payment = sdk.payments.create(
        {
            "external_transaction_id": "checkout-tarjetas-qr",
            "currency_id": "ARS",
            "details": [...],
            "payer": {...},
            "presets": {
                "media_payment_ids": [
                    MediaPayment.VISA,
                    MediaPayment.MASTERCARD,
                    MediaPayment.VISA_DEBITO,
                    MediaPayment.MASTERCARD_DEBIT,
                    MediaPayment.QR,
                ]
            },
        }
    )
    print(payment.form_url)
```

Al usar `presets` conviene omitir `type` y `payment_methods`: el pago queda
pendiente y el checkout muestra solo los medios indicados.

!!! warning "Disponibilidad"
    Los medios deben estar habilitados para el comercio. Si un ID no está
    habilitado, el checkout puede no mostrarlo o la API puede rechazar la
    operación.

## Pago directo con tarjeta

Para cobrar sin checkout, enviá `type: "online"` y `payment_methods` con los
datos de la tarjeta. En ese flujo el QR no participa.

```python
payment = sdk.payments.create(
    {
        "type": "online",
        "external_transaction_id": "cobro-directo-1",
        "currency_id": "ARS",
        "details": [...],
        "payer": {...},
        "payment_methods": [
            {
                "amount": 1500.50,
                "media_payment_id": 9,
                "number": "4507990000004905",
                "installments": 1,
                "expiration_year": 2030,
                "expiration_month": 12,
                "security_code": "123",
                "holder": {
                    "name": "Ana Pérez",
                    "identification": {
                        "type": "DNI_ARG",
                        "number": "30111222",
                        "country": "ARG",
                    },
                },
            }
        ],
    }
)
```

## QR

El string `raw_qr` viene en la respuesta del pago (o en el webhook):

```python
payment = sdk.payments.get("id-del-pago")
print(payment.raw_qr)
```

`Payment.raw_qr` busca el valor en la raíz del pago o en
`payment_methods[].raw_qr`.

### Generar la imagen localmente

Requiere el extra `qr`:

```python
from pagotic import save_qr

payment = sdk.payments.get("id-del-pago")
if payment.raw_qr:
    path = save_qr(payment.raw_qr, "qr.png", scale=6)
    print(path)
```

También existen:

- `render_qr_png(raw_qr, scale=4, border=4, ...)` → `bytes`
- `render_qr_svg(raw_qr, ...)` → `str`

### Servicio externo opcional

Si preferís no instalar `segno`:

```python
from pagotic import build_qr_image_url

url = build_qr_image_url(payment.raw_qr, size=300)
```

!!! note "Un solo uso"
    Cada QR es de un solo uso: una vez pagado queda invalidado.

## Flujo recomendado

1. Crear el pago con `presets.media_payment_ids` que incluyan `QR`.
2. Mostrar `form_url` o el QR generado.
3. Hacer polling con `payments.get()` o esperar el webhook.
4. Leer `status` y `raw_qr` de la respuesta.
