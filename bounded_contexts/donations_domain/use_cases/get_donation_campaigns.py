from dataclasses import dataclass
from typing import Sequence

from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.donations_domain.use_cases import BaseDonationCampaignUseCase
from bounded_contexts.donations_domain.views import DonationCampaignView
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class GetDonationCampaignsUseCase(BaseDonationCampaignUseCase):
    @dataclass
    class Request:
        active: bool
        limit: int | None = None
        offset: int | None = None
        organization_id: str | None = None

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> list[DonationCampaignView]:
        donation_campaigns: Sequence[
            DonationCampaign
        ] = await self.donations_service.get_all_donation_campaigns(
            uow=uow,
            active=request.active,
            limit=request.limit,
            offset=request.offset,
            organization_id=request.organization_id,
        )

        donation_campaign_amounts: dict[
            str, int
        ] = await self.get_donation_campaign_raised_amounts(
            uow=uow, donation_campaigns=donation_campaigns
        )

        organizations = (
            await self.organization_service.get_multiple_organizations_by_id(
                uow=uow,
                organization_ids=[
                    donation_campaign.organization_id
                    for donation_campaign in donation_campaigns
                ],
            )
        )

        return self.donations_view_factory.create_multiple_donation_campaign_views(
            donation_campaigns=donation_campaigns,
            donation_campaign_amounts=donation_campaign_amounts,
            organization_names={
                organization.entity_id: organization.organization_name
                for organization in organizations
            },
        )
