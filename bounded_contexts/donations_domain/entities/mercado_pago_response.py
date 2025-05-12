from dataclasses import dataclass
from datetime import datetime

from bounded_contexts.donations_domain.enum import MercadoPagoResponseStatuses
from common.entities import BaseDomainEntity


@dataclass
class PayerInfo:
    email: str
    identification_type: str
    identification_number: str
    name: str


@dataclass
class MercadoPagoRequest:
    transaction_amount: float
    token: str
    description: str
    installments: int
    payment_method_id: str
    payer: PayerInfo
    application_fee: float


@dataclass
class MercadoPagoResponse:
    status: str
    status_detail: str
    id: str
    date_approved: str | None
    payer: PayerInfo
    payment_method_id: str
    payment_type_id: str
    refunds: list[str] | None
    transaction_amount: float
    mercadopago_fee: float
    application_fee: float


class MercadoPagoTransaction(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        status: MercadoPagoResponseStatuses,
        status_detail: str,
        payer_email: str,
        payer_name: str,
        payer_identification_type: str,
        payer_identification_number: str,
        payment_method_id: str,
        payment_type_id: str,
        donation_campaign_id: str,
        date_approved: datetime | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.status = status
        self.status_detail = status_detail
        self.payer_email = payer_email
        self.payer_name = payer_name
        self.payer_identification_type = payer_identification_type
        self.payer_identification_number = payer_identification_number
        self.payment_method_id = payment_method_id
        self.payment_type_id = payment_type_id
        self.donation_campaign_id = donation_campaign_id
        self.date_approved = date_approved
