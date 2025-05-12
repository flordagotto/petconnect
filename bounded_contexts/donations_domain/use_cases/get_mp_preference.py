from dataclasses import dataclass

from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.services.mercado_pago_service import (
    MercadoPagoService,
)
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from common.use_case import BaseUseCase
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import make_unit_of_work


class GetMpPreferenceUseCase(BaseUseCase):
    def __init__(
        self,
        repository_utils: RepositoryUtils,
        mercado_pago_service: MercadoPagoService,
        donations_service: DonationsService,
        organizations_service: OrganizationService,
    ) -> None:
        super().__init__(repository_utils=repository_utils)

        self.mercado_pago_service = mercado_pago_service
        self.donations_service = donations_service
        self.organizations_service = organizations_service

    @dataclass
    class Request:
        title: str
        price: float
        quantity: int
        purpose: str
        donation_campaign_id: str

    async def execute(self, request: Request) -> str:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            donation_campaign = await self.donations_service.get_donation_campaign(
                uow=uow, donation_campaign_id=request.donation_campaign_id
            )

            organization = await self.organizations_service.get_organization_by_id(
                uow=uow, entity_id=donation_campaign.organization_id
            )

            assert organization.merchant_data is not None

            merchant_access_token = organization.merchant_data.access_token

        return await self.mercado_pago_service.get_mp_preference_id(
            merchant_access_token=merchant_access_token,
            title=request.title,
            price=request.price,
            quantity=request.quantity,
            purpose=request.purpose,
        )
