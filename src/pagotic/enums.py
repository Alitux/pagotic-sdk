"""Enumeraciones y constantes de la API de PagoTIC."""

from enum import Enum


class PaymentStatus(str, Enum):
    """Estados posibles de un pago."""

    PENDING = "pending"
    ISSUED = "issued"
    IN_PROCESS = "in_process"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DEFERRED = "deferred"
    OBJECTED = "objected"
    REVIEW = "review"
    VALIDATE = "validate"
    OVERDUE = "overdue"


class PaymentType(str, Enum):
    """Tipos de pago aceptados por la API."""

    DEBIT = "debit"
    ONLINE = "online"
    TRANSFER = "transfer"
    DEBIN = "debin"
    COUPON = "coupon"


class RefundType(str, Enum):
    """Tipos de devolución."""

    MANUAL = "manual"
    ONLINE = "online"
    BY_MEDIA_PAYMENT = "by_media_payment"


class RefundStatus(str, Enum):
    """Estados de una devolución."""

    APPROVED = "approved"
    REJECTED = "rejected"


class FeeType(str, Enum):
    """Tipos de comisión informados por la API."""

    FEE = "fee"
    CARRIER_FEE = "carrier_fee"
    MEDIA_PAYMENT_COST = "media_payment_cost"
    CARRIER_COST = "carrier_cost"
    REFUND_COST = "refund_cost"
    DEFERRED_COST = "deferred_cost"
    DISCOUNT = "discount"
    REBILLING_COST = "rebilling_cost"
    TARIFF = "tariff"
    FINANCIAL_COST = "financial_cost"
    OVERDUE_PAYMENT = "overdue_payment"
    OTHERS = "others"


class FeePayer(str, Enum):
    """Quién absorbe una comisión."""

    COLLECTOR = "collector"
    PAYER = "payer"


class SourceType(str, Enum):
    """Origen de una acción o pago."""

    COLLECTOR = "collector"
    SYSTEM = "system"
    BACKOFFICE = "backoffice"
    CUSTOMER = "customer"
    CARRIER = "carrier"


class IdentificationType(str, Enum):
    """Tipos de identificación documentados."""

    DNI_ARG = "DNI_ARG"
    CUIT_ARG = "CUIT_ARG"


class DistributionType(str, Enum):
    """Tipos de distribución de fondos."""

    SCHEDULED = "scheduled"


class DestinationType(str, Enum):
    """Tipos de destino de una transferencia."""

    CBU = "cbu"


class FilterOperation(str, Enum):
    """Operaciones de filtrado disponibles en los listados."""

    EQUAL = "EQUAL"
    IN = "IN"
    EXISTS = "EXISTS"
    CONTAINS = "CONTAINS"
    CONTAINS_IGNORE_CASE = "CONTAINS_IGNORE_CASE"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL_TO = "LESS_THAN_OR_EQUAL_TO"
    GREATER_THAN_OR_EQUAL_TO = "GREATER_THAN_OR_EQUAL_TO"
    GREATER_THAN = "GREATER_THAN"


class SortOrder(str, Enum):
    """Orden de un campo en un listado."""

    ASCENDING = "ascending"
    DESCENDING = "descending"


class ImportStatus(str, Enum):
    """Estados de una importación masiva."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"


class Recurrence(str, Enum):
    """Recurrencia de una suscripción."""

    MONTHLY = "monthly"
