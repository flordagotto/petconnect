from dataclasses import dataclass
from typing import Sequence

from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.social_domain.entities import PersonalProfile


@dataclass
class DonationCampaignView:
    entity_id: str
    organization_id: str
    campaign_picture: str
    campaign_name: str
    money_goal: float
    campaign_description: str
    additional_information: str
    money_raised: int
    active: bool
    organization_name: str


@dataclass
class FullDonationCampaignView(DonationCampaignView):
    merchant_public_id: str


@dataclass
class IndividualDonationView:
    entity_id: str
    donation_campaign_id: str
    donor_account_id: str
    amount: float


class DonationsViewFactory:
    def create_full_donation_campaign_view(
        self,
        donation_campaign: DonationCampaign,
        money_raised: int,
        merchant_public_id: str,
        organization_name: str,
    ) -> FullDonationCampaignView:
        return FullDonationCampaignView(
            entity_id=donation_campaign.entity_id,
            organization_id=donation_campaign.organization_id,
            campaign_picture=donation_campaign.campaign_picture,
            campaign_name=donation_campaign.campaign_name,
            money_goal=donation_campaign.money_goal,
            campaign_description=donation_campaign.campaign_description,
            additional_information=donation_campaign.additional_information,
            active=donation_campaign.active,
            money_raised=money_raised,
            merchant_public_id=merchant_public_id,
            organization_name=organization_name,
        )

    def create_donation_campaign_view(
        self,
        donation_campaign: DonationCampaign,
        money_raised: int,
        organization_name: str,
    ) -> DonationCampaignView:
        return DonationCampaignView(
            entity_id=donation_campaign.entity_id,
            organization_id=donation_campaign.organization_id,
            campaign_picture=donation_campaign.campaign_picture,
            campaign_name=donation_campaign.campaign_name,
            money_goal=donation_campaign.money_goal,
            campaign_description=donation_campaign.campaign_description,
            additional_information=donation_campaign.additional_information,
            active=donation_campaign.active,
            money_raised=money_raised,
            organization_name=organization_name,
        )

    def create_individual_donation_view(
        self,
        actor_profile: PersonalProfile,
        individual_donation_id: str,
        donation_campaign: DonationCampaign,
        amount: float,
    ) -> IndividualDonationView:
        return IndividualDonationView(
            entity_id=individual_donation_id,
            donation_campaign_id=donation_campaign.entity_id,
            donor_account_id=actor_profile.account.entity_id,
            amount=amount,
        )

    def create_multiple_donation_campaign_views(
        self,
        donation_campaigns: Sequence[DonationCampaign],
        donation_campaign_amounts: dict[str, int],
        organization_names: dict[str, str],
    ) -> list[DonationCampaignView]:
        return [
            self.create_donation_campaign_view(
                donation_campaign=donation_campaign,
                money_raised=donation_campaign_amounts.get(
                    donation_campaign.entity_id, 0
                ),
                organization_name=organization_names[donation_campaign.organization_id],
            )
            for donation_campaign in donation_campaigns
        ]
