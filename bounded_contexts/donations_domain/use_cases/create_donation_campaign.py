from dataclasses import dataclass
from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.donations_domain.services.donations_service import (
    CreateDonationCampaignData,
)
from bounded_contexts.donations_domain.use_cases import BaseDonationCampaignUseCase
from bounded_contexts.donations_domain.views import DonationCampaignView
from bounded_contexts.social_domain.entities import BaseProfile
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class CreateDonationCampaignUseCase(BaseDonationCampaignUseCase):
    @dataclass
    class Request:
        actor_account_id: str
        donation_campaign_data: CreateDonationCampaignData

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> DonationCampaignView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow,
                account_id=request.actor_account_id,
            )
        )

        donation_campaign: DonationCampaign = (
            await self.donations_service.create_donation_campaign(
                uow=uow,
                profile=actor_profile,
                donation_campaign_data=request.donation_campaign_data,
            )
        )

        organization = await self.organization_service.get_organization_by_id(
            uow=uow,
            entity_id=donation_campaign.organization_id,
        )

        return self.donations_view_factory.create_donation_campaign_view(
            donation_campaign=donation_campaign,
            money_raised=0,
            organization_name=organization.organization_name,
        )
