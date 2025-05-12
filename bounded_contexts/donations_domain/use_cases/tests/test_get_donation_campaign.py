from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
)
from bounded_contexts.donations_domain.exceptions import (
    DonationCampaignNotFoundByIdException,
)
from bounded_contexts.donations_domain.use_cases import GetDonationCampaignUseCase
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork


class TestGetDonationCampaign(BaseUseCaseTest, BaseTestingUtils):
    TEST_DONATION_CAMPAIGN_ID: str = "12345"

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

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetDonationCampaignUseCase = self.dependencies.resolve(
            GetDonationCampaignUseCase
        )

        await self.initial_data()

    async def test_get_donation_campaign_success(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            campaign: DonationCampaign = (
                await self.donation_service.get_donation_campaign(
                    uow=uow, donation_campaign_id=self.donation_campaign.entity_id
                )
            )

        self.assertEqual(
            (
                campaign.entity_id,
                campaign.organization_id,
                campaign.campaign_picture,
                campaign.campaign_name,
                campaign.money_goal,
                campaign.campaign_description,
                campaign.additional_information,
                campaign.active,
            ),
            (
                self.donation_campaign.entity_id,
                self.donation_campaign.donation_campaign_data.organization_id,
                self.donation_campaign.donation_campaign_data.campaign_picture,
                self.donation_campaign.donation_campaign_data.campaign_name,
                self.donation_campaign.donation_campaign_data.money_goal,
                self.donation_campaign.donation_campaign_data.campaign_description,
                self.donation_campaign.donation_campaign_data.additional_information,
                self.donation_campaign.donation_campaign_data.active,
            ),
        )

    async def test_get_donation_campaign_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            with self.assertRaises(DonationCampaignNotFoundByIdException):
                await self.donation_service.get_donation_campaign(
                    uow=uow, donation_campaign_id=self.TEST_DONATION_CAMPAIGN_ID
                )
