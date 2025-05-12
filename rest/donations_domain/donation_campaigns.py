from pydantic import BaseModel
from bounded_contexts.auth.value_objects import TokenData
from bounded_contexts.donations_domain.services.donations_service import (
    CreateDonationCampaignData,
)
from bounded_contexts.donations_domain.use_cases import (
    CreateDonationCampaignUseCase,
    GetDonationCampaignsUseCase,
    GetDonationCampaignUseCase,
    CloseDonationCampaignUseCase,
    GetMpPreferenceUseCase,
    CreateMpInformation,
)
from bounded_contexts.donations_domain.use_cases.donate_to_campaign import (
    DonateToCampaignUseCase,
)
from bounded_contexts.donations_domain.views import (
    DonationCampaignView,
    IndividualDonationView,
)
from bounded_contexts.donations_domain.views.donations_view_factory import (
    FullDonationCampaignView,
)
from infrastructure.rest import BaseAPIController, TokenDependency


class PaymentData:
    def __init__(
        self,
        token: str,
        issuer_id: str,
        payment_method_id: str,
        transaction_amount: float,
        payer_email: str,
    ):
        self.token = token
        self.issuer_id = issuer_id
        self.payment_method_id = payment_method_id
        self.transaction_amount = transaction_amount
        self.payer_email = payer_email


class DonationCampaignsController(BaseAPIController):
    class CreateDonationCampaignBody(BaseModel):
        donation_campaigns_data: CreateDonationCampaignData

    async def post(
        self, token: TokenDependency, body: CreateDonationCampaignBody
    ) -> DonationCampaignView:
        token_data: TokenData = await self._get_token_data(token=token)

        use_case: CreateDonationCampaignUseCase = self.dependencies.resolve(
            CreateDonationCampaignUseCase
        )

        return await use_case.execute(
            CreateDonationCampaignUseCase.Request(
                actor_account_id=token_data.account_id,
                donation_campaign_data=body.donation_campaigns_data,
            )
        )

    class DonateToCampaignBody(BaseModel):
        donation_campaign_id: str
        transaction_amount: float
        application_fee: float
        token: str
        payment_method_id: str
        payer_email: str
        payer_type: str
        payer_number: str
        payer_name: str

    async def post_donation(
        self, token: TokenDependency, body: DonateToCampaignBody
    ) -> IndividualDonationView:
        token_data: TokenData = await self._get_token_data(token=token)

        use_case: DonateToCampaignUseCase = self.dependencies.resolve(
            DonateToCampaignUseCase
        )

        return await use_case.execute(
            DonateToCampaignUseCase.Request(
                actor_account_id=token_data.account_id,
                donation_campaign_id=body.donation_campaign_id,
                transaction_amount=body.transaction_amount,
                token=body.token,
                description="descripcion",
                installments=1,
                payment_method_id=body.payment_method_id,
                payment_type_id="credit_card",
                payer_email=body.payer_email,
                payer_identification_type=body.payer_type,
                payer_identification_number=body.payer_number,
                payer_name=body.payer_name,
                application_fee=body.application_fee,
            )
        )

    async def index_donation_campaigns(
        self, active: bool, organization_id: str | None = None
    ) -> list[DonationCampaignView]:
        use_case: GetDonationCampaignsUseCase = self.dependencies.resolve(
            GetDonationCampaignsUseCase
        )

        return await use_case.execute(
            GetDonationCampaignsUseCase.Request(
                active=active,
                organization_id=organization_id,
            )
        )

    async def get(self, donation_campaign_id: str) -> FullDonationCampaignView:
        use_case: GetDonationCampaignUseCase = self.dependencies.resolve(
            GetDonationCampaignUseCase
        )

        return await use_case.execute(
            GetDonationCampaignUseCase.Request(
                donation_campaign_id=donation_campaign_id,
            )
        )

    async def close_donation_campaign(
        self, token: TokenDependency, donation_campaign_id: str
    ) -> DonationCampaignView:
        use_case: CloseDonationCampaignUseCase = self.dependencies.resolve(
            CloseDonationCampaignUseCase
        )
        token_data: TokenData = await self._get_token_data(token=token)

        return await use_case.execute(
            CloseDonationCampaignUseCase.Request(
                actor_account_id=token_data.account_id,
                donation_campaign_id=donation_campaign_id,
            )
        )

    async def get_mp_preference_id(
        self,
        title: str,
        unit_price: int,
        quantity: int,
        purpose: str,
        donation_campaign_id: str,
    ) -> str:
        use_case: GetMpPreferenceUseCase = self.dependencies.resolve(
            GetMpPreferenceUseCase
        )

        return await use_case.execute(
            GetMpPreferenceUseCase.Request(
                title=title,
                price=unit_price,
                quantity=quantity,
                purpose=purpose,
                donation_campaign_id=donation_campaign_id,
            )
        )

    async def post_mercadopago_information(
        self,
        token: TokenDependency,
        organization_id: str,
        code: str,
    ) -> None:
        create_mp_information_use_case: CreateMpInformation = self.dependencies.resolve(
            CreateMpInformation,
        )

        token_data: TokenData = await self._get_token_data(token=token)

        await create_mp_information_use_case.execute(
            actor_account_id=token_data.account_id,
            organization_id=organization_id,
            code=code,
        )

        return

    def register_routes(self) -> None:
        PREFIX: str = "/donations/donation_campaign"

        # POST
        self._register_post_route(f"{PREFIX}", method=self.post)
        self._register_post_route(f"{PREFIX}/donate", method=self.post_donation)

        # GET
        self._register_get_route(f"{PREFIX}", method=self.get)
        self._register_get_route(f"{PREFIX}s", method=self.index_donation_campaigns)
        self._register_get_route(
            f"{PREFIX}/preference_id", method=self.get_mp_preference_id
        )

        # PUT

        self._register_put_route(f"{PREFIX}/close", method=self.close_donation_campaign)

        # -- Mercadopago
        self._register_post_route(
            "/mercadopago/merchant_information",
            method=self.post_mercadopago_information,
        )
