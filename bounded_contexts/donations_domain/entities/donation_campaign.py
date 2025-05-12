from common.entities import BaseDomainEntity


class DonationCampaign(BaseDomainEntity):
    def __init__(
        self,
        entity_id: str,
        organization_id: str,
        campaign_picture: str,
        campaign_name: str,
        money_goal: float,
        campaign_description: str,
        additional_information: str,
        active: bool = True,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self.organization_id = organization_id

        self.campaign_name = campaign_name
        self.money_goal = money_goal
        self.campaign_description = campaign_description
        self.additional_information = additional_information
        self.campaign_picture = campaign_picture

        self.active = active
