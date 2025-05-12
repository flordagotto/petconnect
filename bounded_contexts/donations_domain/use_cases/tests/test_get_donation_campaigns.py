from bounded_contexts.donations_domain.services.donations_service import (
    CreateDonationCampaignData,
)
from bounded_contexts.donations_domain.use_cases import GetDonationCampaignsUseCase
from bounded_contexts.donations_domain.views import DonationCampaignView
from common.testing import BaseUseCaseTest
from common.testing.base_testing_utils import (
    BaseTestingUtils,
    DonationCampaignDataForTesting,
)
from infrastructure.uow_abstraction import unit_of_work, UnitOfWork


class TestGetDonationCampaigns(BaseUseCaseTest, BaseTestingUtils):
    TEST_NO_LIMIT = None
    TEST_OFFSET_ZERO = 0
    TEST_LIMIT = 2
    TEST_OFFSET = 1

    @unit_of_work
    async def initial_data(self, uow: UnitOfWork) -> None:
        self.organizational_profile1 = await self.create_organizational_profile(uow=uow)
        self.organizational_profile2 = await self.create_organizational_profile(
            uow=uow, account_email="peluditos@mail.com", organization_name="peluditos"
        )

        donation_campaign_data1: CreateDonationCampaignData = CreateDonationCampaignData(
            campaign_name="Donate for Pepito!",
            campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_pepito.jpg",
            money_goal=2500,
            campaign_description="Donate for Pepito's surgery",
            additional_information="Pepito needs a surgery for his kidney's stones",
        )

        donation_campaign1 = await self.create_donation_campaign(
            uow=uow,
            profile=self.organizational_profile1,
            donation_campaign_data=donation_campaign_data1,
        )

        donation_campaign_data2: CreateDonationCampaignData = CreateDonationCampaignData(
            campaign_name="Donate for Lola!",
            campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_lola.jpg",
            money_goal=100,
            campaign_description="Donate for Lola's surgery",
            additional_information="Lola needs a surgery for his kidney's stones",
        )

        donation_campaign2 = await self.create_donation_campaign(
            uow=uow,
            profile=self.organizational_profile1,
            donation_campaign_data=donation_campaign_data2,
        )

        donation_campaign_data3: CreateDonationCampaignData = CreateDonationCampaignData(
            campaign_name="All for Felipe",
            campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_felipe.jpg",
            money_goal=2500,
            campaign_description="Donate for Felipe's surgery",
            additional_information="Felipe needs a surgery for his kidney's stones",
        )

        donation_campaign3 = await self.create_donation_campaign(
            uow=uow,
            profile=self.organizational_profile2,
            donation_campaign_data=donation_campaign_data3,
        )

        donation_campaign_data4: CreateDonationCampaignData = CreateDonationCampaignData(
            campaign_name="All for Indio",
            campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_indio.jpg",
            money_goal=2000,
            campaign_description="Donate for Indio's treatment",
            additional_information="Indio needs medicine",
        )

        donation_campaign4 = await self.create_donation_campaign(
            uow=uow,
            profile=self.organizational_profile2,
            donation_campaign_data=donation_campaign_data4,
        )

        donation_campaign_data5: CreateDonationCampaignData = CreateDonationCampaignData(
            campaign_name="All for Rufus",
            campaign_picture="https://petconnect.icu/campaign_picture/id_campaign_rufus.jpg",
            money_goal=200,
            campaign_description="Donate for Rufus' surgery",
            additional_information="Rufus needs a surgery for his kidney's stones",
        )

        donation_campaign5 = await self.create_donation_campaign(
            uow=uow,
            profile=self.organizational_profile2,
            donation_campaign_data=donation_campaign_data5,
        )

        await self.close_campaign(
            uow=uow,
            donation_campaign_id=donation_campaign5.entity_id,
            profile_id=self.organizational_profile2.profile_data.profile_id,
        )

        campaigns_not_ordered: list[DonationCampaignDataForTesting] = [
            donation_campaign1,
            donation_campaign2,
            donation_campaign3,
            donation_campaign4,
            donation_campaign5,
        ]

        self.campaigns = sorted(
            campaigns_not_ordered,
            key=lambda campaign: campaign.donation_campaign_data.campaign_name,
        )

    async def setUp(self) -> None:
        await BaseUseCaseTest.setUp(self)

        self.use_case: GetDonationCampaignsUseCase = self.dependencies.resolve(
            GetDonationCampaignsUseCase
        )

        await self.initial_data()

    async def test_get_all_active_donation_campaigns_success(self) -> None:
        list_view: list[DonationCampaignView] = await self.use_case.execute(
            GetDonationCampaignsUseCase.Request(
                active=True,
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
            )
        )

        active_campaigns = [
            campaign
            for campaign in self.campaigns
            if campaign.donation_campaign_data.active
        ]
        for i in range(len(list_view)):
            campaign = active_campaigns[i].donation_campaign_data
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
                    list_view[i].entity_id,
                    list_view[i].organization_id,
                    list_view[i].campaign_picture,
                    list_view[i].campaign_name,
                    list_view[i].money_goal,
                    list_view[i].campaign_description,
                    list_view[i].additional_information,
                    list_view[i].active,
                ),
            )

    async def test_get_active_donation_campaigns_from_organization_success(
        self,
    ) -> None:
        list_view: list[DonationCampaignView] = await self.use_case.execute(
            GetDonationCampaignsUseCase.Request(
                active=True,
                limit=self.TEST_NO_LIMIT,
                offset=self.TEST_OFFSET_ZERO,
                organization_id=self.organizational_profile1.organization.entity_id,
            )
        )

        active_campaigns = [
            campaign
            for campaign in self.campaigns
            if campaign.donation_campaign_data.active
            and campaign.organization_id
            == self.organizational_profile1.organization.entity_id
        ]

        for i in range(len(list_view)):
            campaign = active_campaigns[i].donation_campaign_data
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
                    list_view[i].entity_id,
                    list_view[i].organization_id,
                    list_view[i].campaign_picture,
                    list_view[i].campaign_name,
                    list_view[i].money_goal,
                    list_view[i].campaign_description,
                    list_view[i].additional_information,
                    list_view[i].active,
                ),
            )
