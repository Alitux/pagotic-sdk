"""Webhook mínimo con FastAPI.

Requiere: ``pip install fastapi uvicorn``.
La documentación de PagoTIC no define firma, así que validá el origen por tu
cuenta (IP allowlist, proxy, etc.).
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from pagotic import PagoTICValidationError, parse_notification

app = FastAPI()


@app.post("/webhooks/pagotic")
async def pagotic_webhook(request: Request) -> dict[str, bool]:
    try:
        payment = parse_notification(await request.body())
    except PagoTICValidationError:
        return {"ok": False}

    if payment.status == "approved":
        print(f"Pago aprobado: {payment.id} por {payment.final_amount}")

    return {"ok": True}
