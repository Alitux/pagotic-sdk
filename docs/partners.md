# Alcance para partners

!!! info "Credenciales de entidad"
    Un **partner** opera con las credenciales de una entidad (usuario,
    contraseña, `client_id` y `client_secret`). No necesita un token de
    backoffice para las operaciones de esta página.

## Qué podés hacer

| Capacidad | ¿Disponible? |
|---|---|
| Autenticarte y renovar el token automáticamente | Sí |
| Descubrir tu `collector_id` desde el JWT | Sí |
| Crear, consultar y listar tus pagos | Sí |
| Cancelar, devolver, agrupar y crear cupones | Sí |
| Filtrar tus pagos por `collector_id` | Sí |
| Preimportar y aprobar importaciones | Sí |
| Gestionar suscripciones (experimental) | Sí |
| Parsear notificaciones webhook | Sí |
| Listar otros comercios o crear subcuentas | No: requiere token de backoffice |
| Configurar medios de pago de un comercio | No: requiere token de backoffice |
| Consultar `GET /comercios/{collector_id}` | No: requiere token de backoffice |

Las operaciones de backoffice (Marca Blanca) usan otro token y otro nivel de
permisos. Con credenciales de entidad, la API responde `401` con
`extended_code=4606` (`Access denied`).

## El `collector_id`

El `collector_id` es el identificador de tu comercio. PagoTIC lo incluye en el
access token que devuelve Keycloak:

| Claim | Contenido |
|---|---|
| `signature` | `collector_id` (por ejemplo, `"14020"`). |
| `family_name` | También suele contener el `collector_id`. |
| `sub` | UUID del usuario. **No** es el `collector_id`. |
| `azp` / `client_id` | ID de la aplicación. **No** es el `collector_id`. |

El SDK lo extrae por vos:

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    collector_id = sdk.get_collector_id()
    print(collector_id)  # "14020"
```

En asincrónico:

```python
from pagotic import AsyncPagoTIC

async with AsyncPagoTIC() as sdk:
    collector_id = await sdk.get_collector_id()
```

### Validar el `collector_id`

La forma más simple es listar tus propios pagos filtrando por ese valor:

```python
from pagotic import Filter, FilterOperation, PagoTIC

with PagoTIC() as sdk:
    collector_id = sdk.get_collector_id()

    page = sdk.payments.list(
        page=1,
        limit=5,
        filters=[
            Filter("collector_id", FilterOperation.EQUAL, collector_id),
        ],
    )

    print(page["size"])
```

Si el `collector_id` no corresponde a tu usuario, la API responde
`400 Unrelated collector` con `extended_code=4201`.

!!! warning "No verifica la firma"
    `decode_jwt_payload()` y `collector_id_from_token()` decodifican el JWT
    **sin verificar su firma**. Sirven para descubrir el identificador, no para
    tomar decisiones de seguridad. La autorización real la valida la API.

## Flujo recomendado

1. Crear el cliente con las credenciales de la entidad.
2. Obtener el `collector_id` con `get_collector_id()`.
3. Usarlo en los filtros de pagos, importaciones o suscripciones.
4. Guardarlo en configuración si tu integración siempre opera con el mismo
   comercio.

```python
collector_id = sdk.get_collector_id()

payment = sdk.payments.create(
    {
        "collector_id": collector_id,
        "external_transaction_id": "orden-123",
        "currency_id": "ARS",
        "details": [
            {
                "external_reference": "item-1",
                "concept_id": 920,
                "concept_description": "Servicio",
                "amount": 1500,
            }
        ],
        "payer": {
            "name": "Ana Pérez",
            "email": "ana@example.com",
        },
    }
)
```

## Limitaciones

- No se pueden listar los comercios de la plataforma ni crear entidades hijas.
- No se pueden habilitar medios de pago de otros comercios.
- No se puede activar una entidad para producción.
- El alcance siempre está limitado al comercio asociado a las credenciales.

Si tu integración necesita operar sobre varios comercios o crear subcuentas,
tenés que coordinar con PagoTIC el acceso de backoffice.
