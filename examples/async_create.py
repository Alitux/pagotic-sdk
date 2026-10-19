"""Crea un pago con el cliente asincrónico.

ADVERTENCIA: ejecuta una operación real en el entorno configurado.
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from pagotic import AsyncPagoTIC

load_dotenv()


async def main() -> None:
    async with AsyncPagoTIC(
        username=os.getenv("PAGOTIC_USERNAME") or os.getenv("USERNAME"),
        password=os.getenv("PAGOTIC_PASSWORD") or os.getenv("PASSWORD"),
        client_id=os.getenv("PAGOTIC_CLIENT_ID") or os.getenv("CLIENT_ID"),
        client_secret=os.getenv("PAGOTIC_CLIENT_SECRET") or os.getenv("CLIENT_SECRET"),
    ) as sdk:
        payment = await sdk.payments.create(
            {
                "external_transaction_id": "ejemplo-async-001",
                "currency_id": "ARS",
                "details": [{"external_reference": "item-1", "amount": 1000}],
                "payer": {"name": "Ana Pérez", "email": "ana@example.com"},
            }
        )
        print(f"Pago creado: {payment.id} ({payment.status})")


if __name__ == "__main__":
    asyncio.run(main())
