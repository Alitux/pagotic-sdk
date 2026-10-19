# Referencia de API

Esta sección se genera automáticamente a partir de los docstrings del paquete.

## Clientes

::: pagotic.client.PagoTIC
    options:
      show_source: false

::: pagotic.client.AsyncPagoTIC
    options:
      show_source: false

## Recursos

### Pagos

::: pagotic.resources.payments.PaymentsResource
    options:
      show_source: false
      members_order: source

::: pagotic.resources.payments.AsyncPaymentsResource
    options:
      show_source: false
      members_order: source

### Importaciones

::: pagotic.resources.imports.ImportsResource
    options:
      show_source: false
      members_order: source

::: pagotic.resources.imports.AsyncImportsResource
    options:
      show_source: false
      members_order: source

### Suscripciones

::: pagotic.resources.subscriptions.SubscriptionsResource
    options:
      show_source: false
      members_order: source

::: pagotic.resources.subscriptions.AsyncSubscriptionsResource
    options:
      show_source: false
      members_order: source

## Modelos de pagos

::: pagotic.models.payments.PaymentRequest
    options:
      show_source: false

::: pagotic.models.payments.Payment
    options:
      show_source: false

::: pagotic.models.payments.Filter
    options:
      show_source: false

::: pagotic.models.payments.PaymentSearchRequest
    options:
      show_source: false

::: pagotic.models.payments.RefundRequest
    options:
      show_source: false

::: pagotic.models.payments.RefundResponse
    options:
      show_source: false

## Distribución

::: pagotic.models.payments.Distribution
    options:
      show_source: false

::: pagotic.models.payments.DistributionTransfer
    options:
      show_source: false

::: pagotic.models.payments.DistributionDetail
    options:
      show_source: false

::: pagotic.models.payments.DistributionDestination
    options:
      show_source: false

## Modelos comunes

::: pagotic.models.common.Detail
    options:
      show_source: false

::: pagotic.models.common.Payer
    options:
      show_source: false

::: pagotic.models.common.Identification
    options:
      show_source: false

::: pagotic.models.common.Phone
    options:
      show_source: false

::: pagotic.models.common.PaymentMethod
    options:
      show_source: false

::: pagotic.models.common.Presets
    options:
      show_source: false

## Importaciones y suscripciones

::: pagotic.models.imports.ImportSummary
    options:
      show_source: false

::: pagotic.models.imports.ImportDetail
    options:
      show_source: false

::: pagotic.models.subscriptions.SubscriptionRequest
    options:
      show_source: false

::: pagotic.models.subscriptions.Subscription
    options:
      show_source: false

## Enumeraciones

::: pagotic.enums.MediaPayment
    options:
      show_source: false

::: pagotic.enums.PaymentStatus
    options:
      show_source: false

::: pagotic.enums.PaymentType
    options:
      show_source: false

::: pagotic.enums.FilterOperation
    options:
      show_source: false

## Excepciones

::: pagotic.exceptions.PagoTICError
    options:
      show_source: false

::: pagotic.exceptions.PagoTICConfigError
    options:
      show_source: false

::: pagotic.exceptions.PagoTICValidationError
    options:
      show_source: false

::: pagotic.exceptions.PagoTICConnectionError
    options:
      show_source: false

::: pagotic.exceptions.PagoTICAPIError
    options:
      show_source: false

::: pagotic.exceptions.PagoTICAuthError
    options:
      show_source: false

## Utilidades

::: pagotic.validators.normalize_cuit
    options:
      show_source: false

::: pagotic.utils.format_filter_datetime
    options:
      show_source: false

::: pagotic.utils.format_import_datetime
    options:
      show_source: false

::: pagotic.utils.build_qr_image_url
    options:
      show_source: false

::: pagotic.qr.render_qr_png
    options:
      show_source: false

::: pagotic.qr.render_qr_svg
    options:
      show_source: false

::: pagotic.qr.save_qr
    options:
      show_source: false

::: pagotic.webhooks.parse_notification
    options:
      show_source: false
