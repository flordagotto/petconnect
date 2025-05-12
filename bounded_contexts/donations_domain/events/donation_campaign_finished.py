from infrastructure.uow_abstraction import Event


class DonationCampaignFinishedEvent(Event):
    def __init__(
        self,
        actor_account_id: str,
        issued: float,
        donation_campaign_id: str,
    ) -> None:
        super().__init__(
            actor_account_id=actor_account_id,
            issued=issued,
        )

        self.donation_campaign_id = donation_campaign_id
