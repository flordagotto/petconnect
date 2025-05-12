from enum import Enum


class MercadoPagoResponseStatuses(Enum):
    PENDING: str = "PENDING"
    REJECTED: str = "REJECTED"
    APPROVED: str = "APPROVED"
