from dataclasses import dataclass

from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.use_cases import BaseDonationCampaignUseCase
from bounded_contexts.donations_domain.views.donations_view_factory import (
    FullDonationCampaignView,
    DonationsViewFactory,
)
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class GetDonationCampaignUseCase(BaseDonationCampaignUseCase):
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
            donations_service=donations_service,
            profile_service=profile_service,
            donations_view_factory=donations_view_factory,
            organization_service=organization_service,
        )

    @dataclass
    class Request:
        donation_campaign_id: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> FullDonationCampaignView:
        donation_campaign = await self.donations_service.get_donation_campaign(
            uow=uow,
            donation_campaign_id=request.donation_campaign_id,
        )

        money_raised = await self.get_donation_campaign_raised_amount(
            uow=uow,
            donation_campaign=donation_campaign,
        )

        organization = await self.organization_service.get_organization_by_id(
            uow=uow,
            entity_id=donation_campaign.organization_id,
        )

        assert organization.merchant_data

        return self.donations_view_factory.create_full_donation_campaign_view(
            donation_campaign=donation_campaign,
            money_raised=money_raised,
            merchant_public_id=organization.merchant_data.public_key,
            organization_name=organization.organization_name,
        )
