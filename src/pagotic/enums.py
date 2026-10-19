"""Enumeraciones y constantes de la API de PagoTIC."""

from __future__ import annotations

from enum import Enum, IntEnum


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


class MediaPayment(IntEnum):
    """Medios de pago documentados por PagoTIC.

    El valor coincide con ``media_payment_id`` y se puede usar tanto en
    ``Presets.media_payment_ids`` (checkout) como en
    ``PaymentMethod.media_payment_id`` (pago directo).

    Ejemplo de presets para tarjetas y QR::

        Presets(media_payment_ids=[m for m in MediaPayment.cards()] + [MediaPayment.QR])
    """

    CBU = 1
    AMERICAN_EXPRESS = 2
    DINERS = 3
    JCB = 4
    MASTERCARD = 5
    CABAL = 6
    NARANJA = 7
    KADICARD = 8
    VISA = 9
    VISA_DEBITO = 10
    VISA_NARANJA = 11
    FAVACARD = 12
    LIDER = 13
    CREDIMAS = 14
    NEVADA = 15
    PATAGONIA_365 = 16
    SOL = 17
    T_SHOPPING = 18
    ITALCRED = 19
    CENCOSUD = 20
    PYME_NACION = 21
    ARGENTA = 22
    NATIVA = 23
    ARGENCARD = 24
    MAESTRO = 25
    CORDOBESA = 26
    MASTERCARD_DEBITO = 27
    CORDOBESA_VISA = 29
    NATIVA_VISA = 30
    CABAL_DEBITO = 31
    COOPEPLUS = 32
    QR = 85
    BANCON = 86
    INTERBANKING = 87
    PAGO_MIS_CUENTAS = 88
    PROVINCIA_NET = 89
    CREDITS = 90
    LINK_PAGOS = 91
    CRYPTO = 92
    TRANSFERENCIA = 94
    EFECTIVO = 95
    CHEQUE = 96
    RAPIPAGO = 97
    PAGOFACIL = 98
    UNDEFINED = 99
    COBRO_EXPRESS = 100

    @classmethod
    def credit_cards(cls) -> tuple[MediaPayment, ...]:
        """Tarjetas de crédito documentadas."""
        return (
            cls.AMERICAN_EXPRESS,
            cls.DINERS,
            cls.JCB,
            cls.MASTERCARD,
            cls.CABAL,
            cls.NARANJA,
            cls.KADICARD,
            cls.VISA,
            cls.VISA_NARANJA,
            cls.FAVACARD,
            cls.LIDER,
            cls.CREDIMAS,
            cls.NEVADA,
            cls.PATAGONIA_365,
            cls.SOL,
            cls.T_SHOPPING,
            cls.ITALCRED,
            cls.CENCOSUD,
            cls.PYME_NACION,
            cls.ARGENTA,
            cls.NATIVA,
            cls.ARGENCARD,
            cls.CORDOBESA,
            cls.CORDOBESA_VISA,
            cls.NATIVA_VISA,
            cls.COOPEPLUS,
        )

    @classmethod
    def debit_cards(cls) -> tuple[MediaPayment, ...]:
        """Tarjetas de débito documentadas."""
        return (cls.VISA_DEBITO, cls.MAESTRO, cls.MASTERCARD_DEBITO, cls.CABAL_DEBITO)

    @classmethod
    def cards(cls) -> tuple[MediaPayment, ...]:
        """Tarjetas de crédito y débito."""
        return cls.credit_cards() + cls.debit_cards()

    @classmethod
    def coupons(cls) -> tuple[MediaPayment, ...]:
        """Medios de cupón documentados (Rapipago, Pago Fácil y similares)."""
        return (cls.PROVINCIA_NET, cls.RAPIPAGO, cls.PAGOFACIL, cls.COBRO_EXPRESS)


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
