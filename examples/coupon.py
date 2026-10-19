"""Crea un cupón de Rapipago (97) o Pago Fácil (98).

ADVERTENCIA: ejecuta una operación real en el entorno configurado.
"""

from __future__ import annotations

from examples._client import build_client


def main() -> None:
    with build_client() as sdk:
        coupon = sdk.payments.create_coupon(
            {
                "external_transaction_id": "ejemplo-cupon-001",
                "currency_id": "ARS",
                "details": [
                    {
                        "external_reference": "item-1",
                        "concept_description": "Cupón de ejemplo",
                        "amount": 2500,
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
            },
            media_payment_id=97,
        )

        print(f"Cupón: {coupon.id}")
        print(f"Número: {coupon.payment_methods[0].coupon_number}")
        print(f"Descarga: {coupon.form_url}")


if __name__ == "__main__":
    main()
