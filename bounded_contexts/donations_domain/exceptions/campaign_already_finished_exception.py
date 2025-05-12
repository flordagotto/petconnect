from bounded_contexts.donations_domain.exceptions.base_donation_exception import (
    BaseDonationException,
)


class CampaignAlreadyFinishedException(BaseDonationException):
    def __init__(self, campaign_id: str) -> None:
        self.campaign_id = campaign_id
