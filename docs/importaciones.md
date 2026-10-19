# Importación masiva

La importación permite cargar pagos desde un archivo CSV. El archivo se envía
como `multipart/form-data` y queda en estado `PENDING` hasta que se aprueba.

## Formato del CSV

- Sin encabezados.
- Hasta 40.000 registros.
- Se envía junto con el `collector_id`.

Además hay que indicar cómo emparejar los registros:

| Flag | Descripción |
|---|---|
| `match_payer` | Empareja por pagador. |
| `match_concept` | Empareja por concepto. |
| `match_identification` | Empareja por identificación. |

Se exige al menos un flag en `True`. Si `match_identification=True`, los otros
dos deben ser `False`.

## Preimportar

```python
from pagotic import PagoTIC

with PagoTIC() as sdk:
    summary = sdk.imports.preimport(
        "pagos.csv",
        collector_id="14020",
        match_concept=True,
    )
    print(summary.import_id)
    print(summary.status)
```

`file` acepta una ruta (`str` o `Path`), el contenido CSV (`str` o `bytes`) o
un archivo abierto en modo binario.

## Métodos

| Método | Descripción |
|---|---|
| `preimport(file, *, collector_id=None, match_payer=False, match_concept=False, match_identification=False)` | Sube el CSV. |
| `list(*, page, limit, sorts, filters)` | Lista cabeceras de importación. |
| `get(import_id)` | Obtiene una cabecera. |
| `details(import_id, *, page, limit, sorts, filters)` | Lista los detalles. |
| `approve(import_id)` | Aprueba la importación y genera los pagos. |
| `cancel(import_id, status_detail)` | Cancela sin generar pagos. |
| `verify_legacy(import_id)` | Alias legacy `GET /importar/ver/{id}`. |
| `approve_legacy(import_id)` | Alias legacy `POST /importar/aprobar/{id}`. |
| `cancel_legacy(import_id, status_detail)` | Alias legacy `POST /importar/cancelar/{id}`. |

## Consultar

```python
headers = sdk.imports.list(page=1, limit=20)
summary = sdk.imports.get("import-id")
details = sdk.imports.details("import-id", page=1, limit=50)

for item in details:
    print(item.external_transaction_id, item.status)
```

`details()` acepta respuestas en forma de lista o envueltas en
`{"results": [...]}`.

## Aprobar o cancelar

```python
sdk.imports.approve("import-id")
sdk.imports.cancel("import-id", "cancelada por el comercio")
```

## Estados

`PENDING`, `APPROVED` y `CANCELLED`.

!!! warning "Permisos"
    La preimportación requiere el permiso `import-payment` en el usuario de la
    entidad.
