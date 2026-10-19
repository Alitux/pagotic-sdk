# Desarrollo

## Entorno

```bash
git clone https://github.com/Alitux/pagotic-sdk.git
cd pagotic-sdk
poetry install --with docs
```

El proyecto usa un virtualenv local (`.venv`) configurado en `poetry.toml`.

## Comandos

| Comando | Descripción |
|---|---|
| `make install` | Instala dependencias. |
| `make lint` | Ejecuta `ruff check`. |
| `make format` | Formatea con `ruff format`. |
| `make typecheck` | Ejecuta `mypy` sobre `src`. |
| `make test` | Corre los tests. |
| `make test-cov` | Tests con cobertura. |
| `make build` | Construye wheel y sdist. |
| `make docs` | Sirve la documentación en local. |
| `make docs-build` | Compila la documentación con `--strict`. |
| `make clean` | Limpia artefactos y cachés. |

## Tests

```bash
poetry run pytest -q
poetry run pytest --cov=pagotic --cov-report=term-missing
```

Los tests unitarios usan `respx` y no hacen llamadas reales.

Los tests de integración están marcados y se saltean por defecto. Para
ejecutarlos hacen falta credenciales válidas en `.env` o en variables
`PAGOTIC_*`:

```bash
PAGOTIC_RUN_INTEGRATION=1 poetry run pytest -m integration -vv
```

## Calidad

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy src
```

La configuración de `ruff`, `mypy`, `pytest` y cobertura vive en
`pyproject.toml`. La cobertura mínima es 90%.

## Documentación

```bash
make docs        # http://127.0.0.1:8000
make docs-build  # compila en site/
```

La documentación se publica automáticamente en GitHub Pages al hacer push a
`main`, mediante `.github/workflows/docs.yml`. En GitHub hay que configurar
*Settings → Pages → Source: GitHub Actions*.

## Estructura

```text
src/pagotic/
├── client.py          # PagoTIC y AsyncPagoTIC
├── auth.py            # Login, refresh y caché de tokens
├── settings.py        # Configuración y variables de entorno
├── enums.py           # Estados, tipos y medios de pago
├── exceptions.py      # Jerarquía de errores
├── models/            # Modelos Pydantic
├── resources/         # Pagos, importaciones y suscripciones
├── qr.py              # Generación local de QR
├── validators.py      # Validación de CUIT
├── utils.py           # Fechas y helpers
└── webhooks.py        # Parser de notificaciones
```

## Contribuciones

Las contribuciones son bienvenidas. Antes de abrir un pull request:

1. Ejecutá `make lint`, `make typecheck` y `make test-cov`.
2. Agregá tests para los cambios de comportamiento.
3. Actualizá `CHANGELOG.md` en la sección `[Unreleased]`.
4. Mantené el estilo y el idioma de la documentación.

## Licencia

GPL-3.0-or-later. Ver `LICENSE`.

Mantenido por **Alitux** — [alitux@disroot.org](mailto:alitux@disroot.org).
