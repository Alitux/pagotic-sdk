# Distribución programada

La distribución programada permite repartir el importe de un pago entre una o
más cuentas CBU. Se envía dentro del cuerpo de `POST /pagos`, en el campo
`distribution`.

## Datos de cada destinatario

| Campo | Obligatorio | Descripción |
|---|---|---|
| `type` | No | Tipo de transferencia. Documentado: `scheduled`. |
| `cuit` | Sí | CUIT del titular. Se valida y normaliza. |
| `cbu` | Sí | CBU de la cuenta destino. |
| `name` | Sí | Nombre y apellido del titular. |
| `amount` | Sí | Importe a transferir. Debe ser mayor que cero. |

El CUIT puede enviarse con guiones, puntos o espacios: el SDK lo normaliza a
11 dígitos y valida el dígito verificador (módulo 11). Un CUIT inválido lanza
`PagoTICValidationError` antes de llamar a la API.

## JSON que recibe la API

```json
{
  "distribution": {
    "details": [
      {
        "type": "scheduled",
        "amount": 800,
        "destination": {
          "type": "cbu",
          "value": "0170099220000067797370",
          "cuit": "20123456786",
          "name": "Ana Pérez"
        }
      },
      {
        "type": "scheduled",
        "amount": 200,
        "destination": {
          "type": "cbu",
          "value": "0720000188000012345678",
          "cuit": "20987654326",
          "name": "Bruno Gómez"
        }
      }
    ]
  }
}
```

## Uso con `DistributionTransfer`

```python
from pagotic import Detail, Distribution, DistributionTransfer, PagoTIC, Payer

with PagoTIC() as sdk:
    payment = sdk.payments.create(
        {
            "external_transaction_id": "orden-distribuida-1",
            "currency_id": "ARS",
            "details": [
                Detail(
                    external_reference="item-1",
                    concept_id=920,
                    concept_description="Servicio",
                    amount=800,
                ),
                Detail(
                    external_reference="item-2",
                    concept_id=10,
                    concept_description="Servicio adicional",
                    amount=200,
                ),
            ],
            "payer": Payer(
                name="Ana Pérez",
                email="ana@example.com",
                identification={
                    "type": "DNI_ARG",
                    "number": "30111222",
                    "country": "ARG",
                },
            ),
            "distribution": Distribution.scheduled(
                [
                    DistributionTransfer(
                        cbu="0170099220000067797370",
                        cuit="20-12345678-6",
                        name="Ana Pérez",
                        amount=800,
                    ),
                    DistributionTransfer(
                        cbu="0720000188000012345678",
                        cuit="20-98765432-6",
                        name="Bruno Gómez",
                        amount=200,
                    ),
                ]
            ),
        }
    )
```

También se aceptan diccionarios:

```python
distribution = Distribution.scheduled(
    [
        {
            "cbu": "0170099220000067797370",
            "cuit": "20123456786",
            "name": "Ana Pérez",
            "amount": 800,
        },
        {
            "cbu": "0720000188000012345678",
            "cuit": "20987654326",
            "name": "Bruno Gómez",
            "amount": 200,
        },
    ]
)
```

Y objetos `DistributionDetail` ya armados.

## Validaciones

1. **Suma exacta:** la suma de `distribution.details[].amount` debe coincidir
   con la suma de `details[].amount` del pago. Si no coincide, se lanza
   `PagoTICValidationError` y no se envía el request.
2. **Importes positivos:** cada transferencia debe ser mayor que cero.
3. **CUIT válido:** 11 dígitos y dígito verificador correcto.
4. **Destinatarios:** al menos uno.

```python
distribution = Distribution.scheduled([...])
print(distribution.total)  # Decimal('1000')
```

!!! note "Alcance documentado"
    La documentación de PagoTIC solo define `type: "scheduled"` y destinos
    `type: "cbu"`. Si la API incorpora otros tipos, se pueden enviar como
    cadenas sin cambiar el modelo.

!!! tip "CBU"
    El CBU tiene 22 dígitos. El SDK solo exige que no esté vacío para no
    rechazar formatos con separadores; la validación definitiva la hace la API.
