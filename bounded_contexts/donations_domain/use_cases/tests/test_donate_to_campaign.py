from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    MercadoPagoResponse,
    PayerInfo,
    MercadoPagoRequest,
)
from bounded_contexts.donations_domain.exceptions import (
    MoneyAmountNotValidException,
    OrganizationalProfileUnauthorizedToDonateException,
    CampaignAlreadyFinishedException,
    MercadoPagoTransactionNotApprovedException,
)
from bounded_contexts.donations_domain.services.mercado_pago_service import (
    MercadoPagoService,
)
from bounded_contexts.donations_domain.use_cases.donate_to_campaign import (
    DonateToCampaignUseCase,
)
from bounded_contexts.donations_domain.views import IndividualDonationView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork
from unittest.mock import patch, AsyncMock


class TestCreateDonationCampaign(BaseUseCaseTest, BaseTestingUtils):
    REQUESTED_AMOUNT: float = 1000
    FINAL_AMOUNT: float = 959
    MERCADOPAGO_FEE: float = 41
    APPLICATION_FEE: float = 100
    TOKEN: str = "TOKEN"
    DESCRIPTION: str = "DESCRIPTION"
    INSTALLMENTS: int = 1
    PAYMENT_METHOD_ID: str = "VISA"
    PAYMENT_TYPE_ID: str = "CREDIT_CARD"
    PAYER_EMAIL: str = "PAYER_EMAIL@MAIL.COM"
    PAYER_ID_TYPE: str = "DNI"
    PAYER_ID_NUMBER: str = "22222222"
    PAYER_NAME: str = "PAYER_NAME"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organizational_profile = await self.create_organizational_profile(uow=uow)
        self.organizational_collaborator_profile = (
            await self.create_organizational_collaborator_profile(
                uow=uow,
                account_email="collaborator@gmail.com",
                organization_id=self.organizational_profile.organization.entity_id,
            )
        )
        self.donation_campaign = await self.create_donation_campaign(
            uow=uow, profile=self.organizational_profile
        )
        self.personal_profile = await self.create_profile(uow=uow)

        mp_payer = PayerInfo(
            email=self.PAYER_EMAIL,
            identification_type=self.PAYER_ID_TYPE,
            identification_number=self.PAYER_ID_NUMBER,
            name=self.PAYER_NAME,
        )

        self.mp_request = MercadoPagoRequest(
            transaction_amount=self.REQUESTED_AMOUNT,
            token=self.TOKEN,
            description=self.DESCRIPTION,
            installments=self.INSTALLMENTS,
            payment_method_id=self.PAYMENT_METHOD_ID,
            payer=mp_payer,
            application_fee=self.APPLICATION_FEE,
        )

        self.mp_response_success = MercadoPagoResponse(
            status="approved",
            status_detail="approved",
            id="id",
            date_approved="2024-02-23T00:01:10.000-04:00",
            payer=mp_payer,
            payment_type_id="credit_card",
            payment_method_id=self.PAYMENT_METHOD_ID,
            refunds=[],
            application_fee=self.APPLICATION_FEE,
            transaction_amount=self.REQUESTED_AMOUNT,
            mercadopago_fee=self.MERCADOPAGO_FEE,
        )

        self.mp_response_rejected = MercadoPagoResponse(
            status="rejected",
            status_detail="other_reasons",
            id="id",
            date_approved=None,
            payer=mp_payer,
            payment_type_id="credit_card",
            payment_method_id=self.PAYMENT_METHOD_ID,
            refunds=[],
            application_fee=self.APPLICATION_FEE,
            transaction_amount=self.REQUESTED_AMOUNT,
            mercadopago_fee=self.MERCADOPAGO_FEE,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: DonateToCampaignUseCase = self.dependencies.resolve(
            DonateToCampaignUseCase
        )

        await self.initial_data()

    @patch.object(MercadoPagoService, "pay_with_card", new_callable=AsyncMock)
    async def test_donate_to_campaign_success(self, mock_method) -> None:
        mock_method.return_value = self.mp_response_success

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            donation_campaign: DonationCampaign = (
                await self.donation_service.get_donation_campaign(
                    uow=uow, donation_campaign_id=self.donation_campaign.entity_id
                )
            )
            amount_before_donation = (
                await self.donation_service.get_donation_campaign_amount(
                    uow=uow, donation_campaign=donation_campaign
                )
            )

            view: IndividualDonationView = await self.use_case.execute(
                DonateToCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                    transaction_amount=self.REQUESTED_AMOUNT,
                    application_fee=self.APPLICATION_FEE,
                    token=self.TOKEN,
                    description=self.DESCRIPTION,
                    installments=self.INSTALLMENTS,
                    payment_method_id=self.PAYMENT_METHOD_ID,
                    payment_type_id=self.PAYMENT_TYPE_ID,
                    payer_email=self.PAYER_EMAIL,
                    payer_identification_type=self.PAYER_ID_TYPE,
                    payer_identification_number=self.PAYER_ID_NUMBER,
                    payer_name=self.PAYER_NAME,
                )
            )

            individual_donation = await self.donation_service.find_individual_donation(
                uow=uow, individual_donation_id=view.entity_id
            )

            assert individual_donation

            self.assertEqual(
                (
                    individual_donation.entity_id,
                    individual_donation.donation_campaign_id,
                ),
                (view.entity_id, view.donation_campaign_id),
            )

            assert individual_donation.mercadopago_fee == self.MERCADOPAGO_FEE
            assert individual_donation.application_fee == self.APPLICATION_FEE
            assert individual_donation.amount == view.amount == self.FINAL_AMOUNT

            amount_after_donation = (
                await self.donation_service.get_donation_campaign_amount(
                    uow=uow, donation_campaign=donation_campaign
                )
            )

            self.assertEqual(
                amount_before_donation + view.amount,
                amount_after_donation,
            )

            mock_method.assert_called_once_with(
                merchant_access_token="test_access_token", request=self.mp_request
            )

    @patch.object(MercadoPagoService, "pay_with_card", new_callable=AsyncMock)
    async def test_donate_twice(self, mock_method) -> None:
        mock_method.return_value = self.mp_response_success

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            donation_campaign: DonationCampaign = (
                await self.donation_service.get_donation_campaign(
                    uow=uow, donation_campaign_id=self.donation_campaign.entity_id
                )
            )

            for _ in range(2):
                await self.use_case.execute(
                    DonateToCampaignUseCase.Request(
                        actor_account_id=self.personal_profile.account_id,
                        donation_campaign_id=self.donation_campaign.entity_id,
                        transaction_amount=self.REQUESTED_AMOUNT,
                        application_fee=self.APPLICATION_FEE,
                        token=self.TOKEN,
                        description=self.DESCRIPTION,
                        installments=self.INSTALLMENTS,
                        payment_method_id=self.PAYMENT_METHOD_ID,
                        payment_type_id=self.PAYMENT_TYPE_ID,
                        payer_email=self.PAYER_EMAIL,
                        payer_identification_type=self.PAYER_ID_TYPE,
                        payer_identification_number=self.PAYER_ID_NUMBER,
                        payer_name=self.PAYER_NAME,
                    )
                )

            amount_raised = await self.donation_service.get_donation_campaign_amount(
                uow=uow, donation_campaign=donation_campaign
            )

            assert amount_raised == self.FINAL_AMOUNT * 2 == 959 * 2

    async def test_donate_with_organizational_profile_fails(self) -> None:
        with self.assertRaises(OrganizationalProfileUnauthorizedToDonateException):
            await self.use_case.execute(
                DonateToCampaignUseCase.Request(
                    actor_account_id=self.organizational_collaborator_profile.profile_data.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                    transaction_amount=self.REQUESTED_AMOUNT,
                    application_fee=self.APPLICATION_FEE,
                    token=self.TOKEN,
                    description=self.DESCRIPTION,
                    installments=self.INSTALLMENTS,
                    payment_method_id=self.PAYMENT_METHOD_ID,
                    payment_type_id=self.PAYMENT_TYPE_ID,
                    payer_email=self.PAYER_EMAIL,
                    payer_identification_type=self.PAYER_ID_TYPE,
                    payer_identification_number=self.PAYER_ID_NUMBER,
                    payer_name=self.PAYER_NAME,
                )
            )

    async def test_donate_to_already_finished_campaign_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            await self.close_campaign(
                uow=uow,
                donation_campaign_id=self.donation_campaign.entity_id,
                profile_id=self.organizational_profile.profile_data.profile_id,
            )
        with self.assertRaises(CampaignAlreadyFinishedException):
            await self.use_case.execute(
                DonateToCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                    transaction_amount=self.REQUESTED_AMOUNT,
                    application_fee=self.APPLICATION_FEE,
                    token=self.TOKEN,
                    description=self.DESCRIPTION,
                    installments=self.INSTALLMENTS,
                    payment_method_id=self.PAYMENT_METHOD_ID,
                    payment_type_id=self.PAYMENT_TYPE_ID,
                    payer_email=self.PAYER_EMAIL,
                    payer_identification_type=self.PAYER_ID_TYPE,
                    payer_identification_number=self.PAYER_ID_NUMBER,
                    payer_name=self.PAYER_NAME,
                )
            )

    async def test_donate_with_not_valid_money_amount_fails(self) -> None:
        with self.assertRaises(MoneyAmountNotValidException):
            await self.use_case.execute(
                DonateToCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                    transaction_amount=-1500,
                    application_fee=self.APPLICATION_FEE,
                    token=self.TOKEN,
                    description=self.DESCRIPTION,
                    installments=self.INSTALLMENTS,
                    payment_method_id=self.PAYMENT_METHOD_ID,
                    payment_type_id=self.PAYMENT_TYPE_ID,
                    payer_email=self.PAYER_EMAIL,
                    payer_identification_type=self.PAYER_ID_TYPE,
                    payer_identification_number=self.PAYER_ID_NUMBER,
                    payer_name=self.PAYER_NAME,
                )
            )

    @patch.object(MercadoPagoService, "pay_with_card", new_callable=AsyncMock)
    async def test_donate_to_campaign_donation_transaction_fails(
        self, mock_method
    ) -> None:
        mock_method.return_value = self.mp_response_rejected

        with self.assertRaises(MercadoPagoTransactionNotApprovedException):
            await self.use_case.execute(
                DonateToCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                    transaction_amount=self.REQUESTED_AMOUNT,
                    application_fee=self.APPLICATION_FEE,
                    token=self.TOKEN,
                    description=self.DESCRIPTION,
                    installments=self.INSTALLMENTS,
                    payment_method_id=self.PAYMENT_METHOD_ID,
                    payment_type_id=self.PAYMENT_TYPE_ID,
                    payer_email=self.PAYER_EMAIL,
                    payer_identification_type=self.PAYER_ID_TYPE,
                    payer_identification_number=self.PAYER_ID_NUMBER,
                    payer_name=self.PAYER_NAME,
                )
            )

        mock_method.assert_called_once_with(
            merchant_access_token="test_access_token", request=self.mp_request
        )
