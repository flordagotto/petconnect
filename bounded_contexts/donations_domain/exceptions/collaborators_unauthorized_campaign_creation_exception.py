from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class CollaboratorUnauthorizedCampaignManagementException(BaseDonationException):
    def __init__(self, actor_account_id: str, donation_campaign: str | None) -> None:
        self.actor_account_id = actor_account_id
        self.donation_campaign = donation_campaign
