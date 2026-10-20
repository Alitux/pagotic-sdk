# Changelog

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado adopta [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added

- `PagoTIC.get_collector_id()` y `AsyncPagoTIC.get_collector_id()` para
  descubrir el `collector_id` desde el token de acceso.
- Helpers `decode_jwt_payload` y `collector_id_from_token` para inspeccionar los
  claims del JWT sin verificar la firma.
- Guía "Alcance para partners" con las capacidades y limitaciones de las
  credenciales de entidad.
- Modelo `DistributionTransfer` para describir cada destinatario de una
  distribución programada con `type`, `cuit`, `cbu`, `name` y `amount`.
- Validación y normalización de CUIT (11 dígitos y dígito verificador módulo 11)
  en las distribuciones.
- Validación de importes positivos y propiedad `Distribution.total`.
- Documentación completa con MkDocs Material publicada en GitHub Pages.
- Workflow `docs` para construir y desplegar la documentación.

### Changed

- El README y la documentación describen el alcance de partner, el `concept_id`
  obligatorio en la práctica y la necesidad de medios de pago habilitados.
- El README documenta la distribución con `DistributionTransfer`, la validación
  de CUIT y el enlace a la documentación.

## [0.1.1] - 2026-10-19

### Changed

- El README documenta la instalación desde PyPI con `pip`, `pipx` y Poetry.

## [0.1.0] - 2026-10-19

### Added

- Cliente sincrónico `PagoTIC` y asincrónico `AsyncPagoTIC` sobre `httpx`.
- Autenticación OAuth2 contra Keycloak: password grant, refresh grant, caché
  de token, renovación automática y reintento ante `401`.
- Configuración por argumentos y variables de entorno `PAGOTIC_*`.
- Modelos Pydantic v2 (`extra="allow"`) y enums de estados, tipos, comisiones y
  operaciones de filtrado.
- Recurso de pagos: crear, obtener, buscar (legacy), listar con filtros/orden/
  paginación, cancelar, cancelar objeción, agrupar, cancelar agrupación,
  devolver y crear cupones (Rapipago/Pago Fácil).
- Distribución programada de pagos (`distribution`) con validación obligatoria
  de la suma de importes contra `details`.
- Importación masiva: preimportación CSV multipart, listado, cabecera, detalles,
  aprobación, cancelación y alias de rutas legacy.
- Suscripciones (experimental): crear, listar, buscar y cancelar.
- Jerarquía de errores tipada con `status_code`, `code`, `extended_code` y
  payload.
- Parser de notificaciones webhook (`parse_notification`).
- Helpers de formato de fechas para filtros de pagos e importaciones.
- Tests unitarios con `respx` y tests de integración opt-in.
- Configuración de `ruff`, `mypy`, `pre-commit`, `pytest`, cobertura y CI para
  Python 3.10–3.14.
- Ejemplos de uso sincrónico, asincrónico, cupones, distribución y webhook.
- README en español, licencia GPL-3.0-or-later y política de secretos con
  `.env` ignorado.
- Enum `MediaPayment` con todos los `media_payment_id` documentados y helpers
  `credit_cards()`, `debit_cards()`, `cards()` y `coupons()`.
- Campo tipado `PaymentMethodInfo.raw_qr` y propiedad `Payment.raw_qr` para
  obtener el código QR del pago.
- Helper `build_qr_image_url` y constante `QR_IMAGE_ENDPOINT` para generar la
  imagen del QR.
- Ejemplo `examples/qr_payment.py` y sección de medios de pago/QR en el README.
- Generación local de QR con `segno` (extra `pagotic-sdk[qr]`):
  `render_qr_png`, `render_qr_svg` y `save_qr`.
- Workflow de GitHub Actions `publish` que construye el paquete y lo publica en
  PyPI con Trusted Publishing al crear un release, con publicación manual
  opcional a TestPyPI.

### Fixed

- `Payment.validation` y `Payment.review` aceptan los booleanos que devuelve la
  API en pagos pendientes, además de strings.
- Las credenciales y URLs se normalizan quitando espacios al inicio y al final;
  un valor con solo espacios se considera ausente.
- Los ejemplos y tests de integración cargan `.env` con `override=True` para que
  variables del sistema como `USERNAME` no pisen las credenciales del archivo.
