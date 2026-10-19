# PagoTIC SDK para Python

!!! warning "Paquete no oficial"
    Este SDK es mantenido por la comunidad y **no está afiliado, respaldado ni
    soportado por PagoTIC**. Usá la API oficial bajo tu propia responsabilidad.

SDK en Python para integrar la pasarela de pagos **PagoTIC** (Pay per TIC).
Incluye cliente sincrónico y asincrónico, autenticación OAuth2 automática,
modelos tipados con Pydantic, pagos, distribución programada, importación
masiva, suscripciones y utilidades para webhooks.

## Características

- Cliente sincrónico (`PagoTIC`) y asincrónico (`AsyncPagoTIC`) sobre `httpx`.
- Autenticación contra Keycloak con caché de token, refresh automático y
  reintento ante `401`.
- Modelos Pydantic v2 con `extra="allow"` para tolerar campos nuevos de la API.
- Pagos: creación, consulta, listado con filtros, cancelación, devoluciones,
  agrupaciones y cupones.
- Distribución programada entre cuentas CBU, con validación de CUIT y de la
  suma de importes.
- Importación masiva de pagos desde CSV.
- Generación local de códigos QR con el extra `qr`.
- Tipado completo (`py.typed`), tests con `respx`, lint con `ruff` y `mypy`.

## Instalación

```bash
pip install pagotic-sdk
```

Para generar QR localmente:

```bash
pip install "pagotic-sdk[qr]"
```

## Inicio rápido

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    payment = sdk.payments.create(
        {
            "external_transaction_id": "orden-123",
            "currency_id": "ARS",
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
    print(payment.form_url)
```

Las credenciales se leen de las variables `PAGOTIC_*` o se pasan al
constructor. Ver [Configuración](configuracion.md).

## Guías

- [Pagos](pagos.md)
- [Distribución programada](distribucion.md)
- [Medios de pago y QR](medios-de-pago.md)
- [Importación masiva](importaciones.md)
- [Suscripciones](suscripciones.md)
- [Webhooks](webhooks.md)
- [Errores](errores.md)

## Mantenimiento

Mantenido por **Alitux** — [alitux@disroot.org](mailto:alitux@disroot.org).

Licencia [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html).
