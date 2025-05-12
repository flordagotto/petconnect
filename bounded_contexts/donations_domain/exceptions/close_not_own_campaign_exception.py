from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class CloseNotOwnCampaignException(BaseDonationException):
    def __init__(self, actor_account_id: str, campaign_id: str) -> None:
        self.actor_account_id = actor_account_id
        self.campaign_id = campaign_id
