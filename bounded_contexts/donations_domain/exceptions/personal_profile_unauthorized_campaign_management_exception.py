from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class PersonalProfileUnauthorizedCampaignManagementException(BaseDonationException):
    def __init__(self, actor_account_id: str) -> None:
        self.actor_account_id = actor_account_id
