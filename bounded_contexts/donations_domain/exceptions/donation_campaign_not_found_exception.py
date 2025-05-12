from bounded_contexts.donations_domain.exceptions import BaseDonationException


class DonationCampaignNotFoundByIdException(BaseDonationException):
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id
