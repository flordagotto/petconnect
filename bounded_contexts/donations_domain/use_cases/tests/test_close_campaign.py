from bounded_contexts.donations_domain.exceptions import (
    CampaignAlreadyFinishedException,
    CloseNotOwnCampaignException,
    PersonalProfileUnauthorizedCampaignManagementException,
    CollaboratorUnauthorizedCampaignManagementException,
)
from bounded_contexts.donations_domain.use_cases import CloseDonationCampaignUseCase
from bounded_contexts.donations_domain.views import DonationCampaignView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import BaseTestingUtils
from infrastructure.uow_abstraction import make_unit_of_work, unit_of_work, UnitOfWork


class TestCloseDonationCampaign(BaseUseCaseTest, BaseTestingUtils):
    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organizational_profile = await self.create_organizational_profile(uow=uow)
        self.organizational_profile2 = await self.create_organizational_profile(
            uow=uow, account_email="paws@gmailcom", organization_name="paws"
        )
        self.organizational_collaborator_profile = (
            await self.create_organizational_collaborator_profile(
                uow=uow,
                account_email="collaborator@gmail.com",
                organization_id=self.organizational_profile.organization.entity_id,
            )
        )
        self.personal_profile = await self.create_profile(uow=uow)
        self.donation_campaign = await self.create_donation_campaign(
            uow=uow, profile=self.organizational_profile
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: CloseDonationCampaignUseCase = self.dependencies.resolve(
            CloseDonationCampaignUseCase
        )

        await self.initial_data()

    async def test_close_campaign_success(self) -> None:
        view: DonationCampaignView = await self.use_case.execute(
            CloseDonationCampaignUseCase.Request(
                actor_account_id=self.organizational_profile.profile_data.account_id,
                donation_campaign_id=self.donation_campaign.entity_id,
            )
        )

        self.assertFalse(view.active)

    async def test_close_not_own_campaign_fails(self) -> None:
        with self.assertRaises(CloseNotOwnCampaignException):
            await self.use_case.execute(
                CloseDonationCampaignUseCase.Request(
                    actor_account_id=self.organizational_profile2.profile_data.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                )
            )

    async def test_close_campaign_from_collaborator_profile_fails(self) -> None:
        with self.assertRaises(CollaboratorUnauthorizedCampaignManagementException):
            await self.use_case.execute(
                CloseDonationCampaignUseCase.Request(
                    actor_account_id=self.organizational_collaborator_profile.profile_data.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                )
            )

    async def test_close_campaign_from_personal_profile_fails(self) -> None:
        with self.assertRaises(PersonalProfileUnauthorizedCampaignManagementException):
            await self.use_case.execute(
                CloseDonationCampaignUseCase.Request(
                    actor_account_id=self.personal_profile.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                )
            )

    async def test_close_finished_campaign_fails(self) -> None:
        async with make_unit_of_work(self.repository_utils.sessionmaker) as uow:
            await self.close_campaign(
                uow=uow,
                donation_campaign_id=self.donation_campaign.entity_id,
                profile_id=self.organizational_profile.profile_data.profile_id,
            )
        with self.assertRaises(CampaignAlreadyFinishedException):
            await self.use_case.execute(
                CloseDonationCampaignUseCase.Request(
                    actor_account_id=self.organizational_profile.profile_data.account_id,
                    donation_campaign_id=self.donation_campaign.entity_id,
                )
            )
