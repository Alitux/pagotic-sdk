"""Crea un pago con tarjetas y QR, y guarda la imagen del QR localmente.

Requiere el extra ``qr``: ``pip install pagotic-sdk[qr]``.

ADVERTENCIA: ejecuta una operación real en el entorno configurado.
"""

from __future__ import annotations

import time

from examples._client import build_client
from pagotic import MediaPayment, PaymentRequest, Presets, save_qr

POLL_ATTEMPTS = 10
POLL_SECONDS = 3


def main() -> None:
    with build_client() as sdk:
        payment = sdk.payments.create(
            PaymentRequest(
                external_transaction_id="ejemplo-qr-001",
                currency_id="ARS",
                details=[
                    {
                        "external_reference": "item-1",
                        "concept_id": 920,
                        "concept_description": "Servicio de ejemplo",
                        "amount": 1500.50,
                    }
                ],
                payer={
                    "name": "Ana Pérez",
                    "email": "ana@example.com",
                    "identification": {
                        "type": "DNI_ARG",
                        "number": "12345678",
                        "country": "ARG",
                    },
                },
                presets=Presets(media_payment_ids=[*MediaPayment.cards(), MediaPayment.QR]),
                notification_url="https://example.com/webhooks/pagotic",
            )
        )

        print(f"Pago creado: {payment.id}")
        print(f"Checkout: {payment.form_url}")

        for attempt in range(1, POLL_ATTEMPTS + 1):
            current = sdk.payments.get(payment.id)
            if current.raw_qr:
                path = save_qr(current.raw_qr, "qr.png", scale=6)
                print(f"QR (intento {attempt}) guardado en {path}")
                return
            time.sleep(POLL_SECONDS)

        print("El QR todavía no está disponible; volvé a consultar más tarde.")


if __name__ == "__main__":
    main()
