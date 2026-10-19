"""Pago con distribución programada entre dos CBU.

La suma de ``distribution.details`` debe igualar la suma de ``details``.
ADVERTENCIA: ejecuta una operación real en el entorno configurado.
"""

from __future__ import annotations

from examples._client import build_client
from pagotic import Distribution, PaymentRequest


def main() -> None:
    request = PaymentRequest(
        external_transaction_id="ejemplo-distribucion-001",
        currency_id="ARS",
        details=[
            {"external_reference": "a", "concept_id": 920, "amount": 800},
            {"external_reference": "b", "concept_id": 10, "amount": 200},
        ],
        payer={
            "name": "Ana Pérez",
            "email": "ana@example.com",
            "identification": {"type": "DNI_ARG", "number": "12345678", "country": "ARG"},
        },
        distribution=Distribution.scheduled(
            [
                {
                    "cbu": "0000000000000000000001",
                    "cuit": "20111111112",
                    "name": "Proveedor A",
                    "amount": 800,
                },
                {
                    "cbu": "0000000000000000000002",
                    "cuit": "20222222223",
                    "name": "Proveedor B",
                    "amount": 200,
                },
            ]
        ),
    )

    with build_client() as sdk:
        payment = sdk.payments.create(request)
        print(f"Pago con distribución: {payment.id} ({payment.status})")


if __name__ == "__main__":
    main()
