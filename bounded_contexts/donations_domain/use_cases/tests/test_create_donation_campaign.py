from bounded_contexts.donations_domain.entities import DonationCampaign
from bounded_contexts.donations_domain.exceptions import (
    CollaboratorUnauthorizedCampaignManagementException,
    MoneyAmountNotValidException,
)
from bounded_contexts.donations_domain.exceptions.personal_profile_unauthorized_campaign_management_exception import (
    PersonalProfileUnauthorizedCampaignManagementException,
)
from bounded_contexts.donations_domain.services.donations_service import (
    CreateDonationCampaignData,
)
from bounded_contexts.donations_domain.use_cases import CreateDonationCampaignUseCase
from bounded_contexts.donations_domain.views import DonationCampaignView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork


class TestCreateDonationCampaign(BaseUseCaseTest, BaseTestingUtils):
    TEST_CAMPAIGN_PICTURE: str = (
        "https://petconnect.icu/campaign_picture/id_campaign_pepito.jpg"
    )
    TEST_CAMPAIGN_NAME: str = "Donate for Pepito!"
    TEST_MONEY_GOAL: float = 2500
    TEST_CAMPAIGN_DESCRIPTION: str = "Donate for Pepito's surgery"
    TEST_ADDITIONAL_INFORMATION: str = "Pepito needs a surgery for his kidney's stones"

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.personal_profile = await self.create_profile(uow=uow)
        self.organizational_profile = await self.create_organizational_profile(uow=uow)
        self.organizational_collaborator_profile = (
            await self.create_organizational_collaborator_profile(
                uow=uow,
                account_email="collaborator@gmail.com",
                organization_id=self.organizational_profile.organization.entity_id,
            )
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CreateDonationCampaignUseCase = self.dependencies.resolve(
            CreateDonationCampaignUseCase
        )

        await self.initial_data()

    async def test_create_donation_campaign_success(self) -> None:
        view: DonationCampaignView = await self.use_case.execute(
            CreateDonationCampaignUseCase.Request(
                actor_account_id=self.organizational_profile.profile_data.account_id,
                donation_campaign_data=CreateDonationCampaignData(
                    campaign_picture=self.TEST_CAMPAIGN_PICTURE,
                    campaign_name=self.TEST_CAMPAIGN_NAME,
                    money_goal=self.TEST_MONEY_GOAL,
                    campaign_description=self.TEST_CAMPAIGN_DESCRIPTION,
                    additional_information=self.TEST_ADDITIONAL_INFORMATION,
                ),
            )
        )

        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            donation_campaign: DonationCampaign = (
                await self.donation_service.get_donation_campaign(
                    uow=uow, donation_campaign_id=view.entity_id
                )
            )

            self.assertEqual(
                (
                    donation_campaign.entity_id,
                    donation_campaign.organization_id,
                    donation_campaign.campaign_picture,
                    donation_campaign.campaign_name,
                    donation_campaign.money_goal,
                    donation_campaign.campaign_description,
                    donation_campaign.additional_information,
                    donation_campaign.active,
                ),
                (
                    view.entity_id,
                    view.organization_id,
                    view.campaign_picture,
                    view.campaign_name,
                    view.money_goal,
                    view.campaign_description,
                    view.additional_information,
                    view.active,
                ),
            )

    async def test_create_campaign_from_collaborator_profile_fails(
        self,
    ) -> None:
        with self.assertRaises(CollaboratorUnauthorizedCampaignManagementException):
            await self.use_case.execute(
                CreateDonationCampaignUseCase.Request(
                    actor_account_id=self.organizational_collaborator_profile.profile_data.account_id,
                    donation_campaign_data=CreateDonationCampaignData(
                        campaign_picture=self.TEST_CAMPAIGN_PICTURE,
                        campaign_name=self.TEST_CAMPAIGN_NAME,
                        money_goal=self.TEST_MONEY_GOAL,
                        campaign_description=self.TEST_CAMPAIGN_DESCRIPTION,
                        additional_information=self.TEST_ADDITIONAL_INFORMATION,
                    ),
                )
            )

    async def test_create_campaign_from_personal_profile_fails(
        self,
    ) -> None:
        with self.assertRaises(PersonalProfileUnauthorizedCampaignManagementException):
            await self.use_case.execute(
                CreateDonationCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_data=CreateDonationCampaignData(
                        campaign_picture=self.TEST_CAMPAIGN_PICTURE,
                        campaign_name=self.TEST_CAMPAIGN_NAME,
                        money_goal=self.TEST_MONEY_GOAL,
                        campaign_description=self.TEST_CAMPAIGN_DESCRIPTION,
                        additional_information=self.TEST_ADDITIONAL_INFORMATION,
                    ),
                )
            )

    async def test_create_campaign_with_not_valid_money_goal_fails(self) -> None:
        with self.assertRaises(MoneyAmountNotValidException):
            await self.use_case.execute(
                CreateDonationCampaignUseCase.Request(
                    actor_account_id=self.organizational_profile.profile_data.account_id,
                    donation_campaign_data=CreateDonationCampaignData(
                        campaign_picture=self.TEST_CAMPAIGN_PICTURE,
                        campaign_name=self.TEST_CAMPAIGN_NAME,
                        money_goal=-5,
                        campaign_description=self.TEST_CAMPAIGN_DESCRIPTION,
                        additional_information=self.TEST_ADDITIONAL_INFORMATION,
                    ),
                )
            )
