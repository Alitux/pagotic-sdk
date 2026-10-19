"""Crea un pago de ejemplo.

ADVERTENCIA: ejecuta una operación real en el entorno configurado.
"""

from __future__ import annotations

from examples._client import build_client


def main() -> None:
    with build_client() as sdk:
        payment = sdk.payments.create(
            {
                "external_transaction_id": "ejemplo-001",
                "currency_id": "ARS",
                "details": [
                    {
                        "external_reference": "item-1",
                        "concept_id": 920,
                        "concept_description": "Servicio de ejemplo",
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

        print(f"Pago creado: {payment.id}")
        print(f"Estado: {payment.status}")
        print(f"Checkout: {payment.form_url}")


if __name__ == "__main__":
    main()
