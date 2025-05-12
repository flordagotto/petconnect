from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.services.mercado_pago_service import (
    MercadoPagoService,
)
from bounded_contexts.donations_domain.use_cases import BaseDonationCampaignUseCase
from bounded_contexts.donations_domain.views import DonationsViewFactory
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.payment_gateway import MerchantData
from infrastructure.uow_abstraction import make_unit_of_work


class CreateMpInformation(BaseDonationCampaignUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        donations_service: DonationsService,
        profile_service: ProfileService,
        donations_view_factory: DonationsViewFactory,
        mercado_pago_service: MercadoPagoService,
        organization_service: OrganizationService,
    ) -> None:
        super().__init__(
            repository_utils=repository_utils,
            donations_service=donations_service,
            profile_service=profile_service,
            donations_view_factory=donations_view_factory,
            organization_service=organization_service,
        )

        self.mercado_pago_service = mercado_pago_service

    async def execute(self, actor_account_id: str, organization_id: str, code: str):
        merchant_data: MerchantData = (
            await self.mercado_pago_service.get_access_token_details(
                code=code,
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            organization = await self.organization_service.get_organization_by_id(
                uow=uow,
                entity_id=organization_id,
            )

            # Only organization admin can add bank details
            assert organization.creator_account_id == actor_account_id

            organization.verified_bank = True
            organization.merchant_data = merchant_data
