from dataclasses import dataclass
from typing import cast

from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    IndividualDonation,
    MercadoPagoRequest,
    PayerInfo,
)
from bounded_contexts.donations_domain.services.donations_service import (
    DonationsService,
)
from bounded_contexts.donations_domain.services.mercado_pago_service import (
    MercadoPagoService,
)
from bounded_contexts.donations_domain.use_cases import BaseDonationCampaignUseCase
from bounded_contexts.donations_domain.views import (
    IndividualDonationView,
    DonationsViewFactory,
)
from bounded_contexts.social_domain.entities import (
    PersonalProfile,
    BaseProfile,
)
from bounded_contexts.social_domain.services.organization_service import (
    OrganizationService,
)
from bounded_contexts.social_domain.services.profile_service import ProfileService
from infrastructure.database import RepositoryUtils
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class DonateToCampaignUseCase(BaseDonationCampaignUseCase):
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

    @dataclass
    class Request:
        actor_account_id: str
        donation_campaign_id: str
        transaction_amount: float
        application_fee: float
        token: str
        description: str
        installments: int
        payment_method_id: str
        payment_type_id: str
        payer_email: str
        payer_identification_type: str
        payer_identification_number: str
        payer_name: str

    @unit_of_work
    async def execute(
        self,
        request: Request,
        uow: UnitOfWork,
    ) -> IndividualDonationView:
        actor_profile: BaseProfile = (
            await self.profile_service.get_profile_by_account_id(
                uow=uow,
                account_id=request.actor_account_id,
            )
        )

        donation_campaign: DonationCampaign = (
            await self.donations_service.get_donation_campaign(
                uow=uow,
                donation_campaign_id=request.donation_campaign_id,
            )
        )

        self.donations_service.validate_donation_to_campaign(
            profile=actor_profile,
            donation_campaign=donation_campaign,
            amount=request.transaction_amount,
        )

        organization = await self.organization_service.get_organization_by_id(
            uow=uow,
            entity_id=donation_campaign.organization_id,
        )

        merchant_data = organization.merchant_data

        assert merchant_data

        mp_request: MercadoPagoRequest = MercadoPagoRequest(
            transaction_amount=request.transaction_amount,
            token=request.token,
            description=request.description,
            installments=request.installments,
            payment_method_id=request.payment_method_id,
            payer=PayerInfo(
                email=request.payer_email,
                identification_type=request.payer_identification_type,
                identification_number=request.payer_identification_number,
                name=request.payer_name,
            ),
            application_fee=request.application_fee,
        )

        mp_response = await self.mercado_pago_service.pay_with_card(
            merchant_access_token=merchant_data.access_token, request=mp_request
        )

        mp_transaction_entity_id = (
            await self.mercado_pago_service.handle_transaction_response(
                uow=uow,
                mp_response=mp_response,
                donation_campaign_id=donation_campaign.entity_id,
            )
        )

        final_amount = mp_response.transaction_amount - mp_response.mercadopago_fee

        individual_donation: IndividualDonation = (
            await self.donations_service.donate_to_campaign(
                uow=uow,
                actor_profile=cast(PersonalProfile, actor_profile),
                donation_campaign=donation_campaign,
                amount=final_amount,
                mercadopago_fee=mp_response.mercadopago_fee,
                application_fee=mp_response.application_fee,
                mp_transaction_id=mp_transaction_entity_id,
            )
        )

        return self.donations_view_factory.create_individual_donation_view(
            actor_profile=cast(PersonalProfile, actor_profile),
            individual_donation_id=individual_donation.entity_id,
            donation_campaign=donation_campaign,
            amount=final_amount,
        )
