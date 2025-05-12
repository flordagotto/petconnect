from dataclasses import dataclass


@dataclass
class CollectedMoney:
    donation_campaign_id: str
    donation_campaign_name: str
    organization_name: str
    money_goal: float
    collected_amount: float
    application_collected_amount: float
    campaign_is_active: bool
