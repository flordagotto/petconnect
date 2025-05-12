from common.entities import BaseDomainEntity


class IndividualDonation(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        donation_campaign_id: str,
        donor_account_id: str,
        amount: float,
        mercadopago_fee: float,
        application_fee: float,
        mp_transaction_id: str,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.donation_campaign_id = donation_campaign_id
        self.donor_account_id = donor_account_id
        self.amount = amount
        self.mercadopago_fee = mercadopago_fee
        self.application_fee = application_fee
        self.mp_transaction_id = mp_transaction_id
