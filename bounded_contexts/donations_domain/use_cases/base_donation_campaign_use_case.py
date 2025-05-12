from typing import Sequence

from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.views import DonationsViewFactory
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import UnitOfWork


class BaseDonationCampaignUseCase(BaseUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        donations_service: DonationsService,
        profile_service: ProfileService,
        donations_view_factory: DonationsViewFactory,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
        )

        self.donations_service = donations_service
        self.profile_service = profile_service

        self.donations_view_factory = donations_view_factory
        self.organization_service = organization_service

    async def get_donation_campaign_raised_amounts(
        self, uow: UnitOfWork, donation_campaigns: Sequence[DonationCampaign]
    ) -> dict[str, int]:
        donation_campaign_ids = [
            donation_campaign.entity_id for donation_campaign in donation_campaigns
        ]

        donation_campaign_amounts: Sequence[
            tuple[str, int]
        ] = await self.donations_service.get_donation_campaign_amounts(
            uow=uow,
            donation_campaign_ids=donation_campaign_ids,
        )

        return {
            donation_campaign_id: amount
            for donation_campaign_id, amount in donation_campaign_amounts
        }

    async def get_donation_campaign_raised_amount(
        self, uow: UnitOfWork, donation_campaign: DonationCampaign
    ) -> int:
        return await self.donations_service.get_donation_campaign_amount(
            uow=uow,
            donation_campaign=donation_campaign,
        )
