from dataclasses import dataclass
from typing import Sequence, cast
from uuid import uuid4
from bounded_contexts.donations_domain.entities import (
    DonationCampaign,
    IndividualDonation,
)
from bounded_contexts.donations_domain.exceptions import (
    CollaboratorUnauthorizedCampaignManagementException,
    CampaignAlreadyFinishedException,
    DonationCampaignNotFoundByIdException,
    MoneyAmountNotValidException,
    OrganizationalProfileUnauthorizedToDonateException,
    CloseNotOwnCampaignException,
)
from bounded_contexts.donations_domain.exceptions.personal_profile_unauthorized_campaign_management_exception import (
    PersonalProfileUnauthorizedCampaignManagementException,
)
from bounded_contexts.donations_domain.repositories import (
    DonationsRepository,
)
from bounded_contexts.social_domain.entities import (
    OrganizationalProfile,
    PersonalProfile,
    BaseProfile,
)
from bounded_contexts.social_domain.enum import OrganizationRoles, ProfileTypes
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class CreateDonationCampaignData:
    campaign_picture: str
    campaign_name: str
    money_goal: float
    campaign_description: str
    additional_information: str


class DonationsService:
    def __init__(self, donations_repository: DonationsRepository) -> None:
        self.donations_repository: DonationsRepository = donations_repository

    async def create_donation_campaign(
        self,
        uow: UnitOfWork,
        profile: BaseProfile,
        donation_campaign_data: CreateDonationCampaignData,
    ) -> DonationCampaign:
        self.__assert_not_personal_profile(profile=profile)

        actor_profile: OrganizationalProfile = cast(OrganizationalProfile, profile)
        self.__assert_not_collaborator_organizational_profile(profile=actor_profile)

        if donation_campaign_data.money_goal <= 0:
            raise MoneyAmountNotValidException()

        donation_campaign: DonationCampaign = DonationCampaign(
            entity_id=uuid4().hex,
            organization_id=actor_profile.organization_id,
            campaign_picture=donation_campaign_data.campaign_picture,
            campaign_name=donation_campaign_data.campaign_name,
            money_goal=donation_campaign_data.money_goal,
            campaign_description=donation_campaign_data.campaign_description,
            additional_information=donation_campaign_data.additional_information,
        )

        await self.donations_repository.add_donation_campaign(
            session=uow.session, donation_campaign=donation_campaign
        )

        return donation_campaign

    async def close_campaign(
        self, uow: UnitOfWork, profile: BaseProfile, donation_campaign: DonationCampaign
    ) -> None:
        self.__assert_profile_is_owner_of_campaign(
            profile=profile, donation_campaign=donation_campaign
        )
        if not donation_campaign.active:
            raise CampaignAlreadyFinishedException(donation_campaign.entity_id)
        donation_campaign.active = False

        await uow.flush()

    async def donate_to_campaign(
        self,
        uow: UnitOfWork,
        actor_profile: PersonalProfile,
        donation_campaign: DonationCampaign,
        mp_transaction_id: str,
        amount: float,
        mercadopago_fee: float,
        application_fee: float,
    ) -> IndividualDonation:
        campaign_donations_amount = await self.get_donation_campaign_amount(
            uow=uow,
            donation_campaign=donation_campaign,
        )

        individual_donation = IndividualDonation(
            entity_id=uuid4().hex,
            donation_campaign_id=donation_campaign.entity_id,
            donor_account_id=actor_profile.account.entity_id,
            amount=amount,
            mercadopago_fee=mercadopago_fee,
            application_fee=application_fee,
            mp_transaction_id=mp_transaction_id,
        )

        await self.donations_repository.add_individual_donation(
            session=uow.session,
            individual_donation=individual_donation,
        )

        if campaign_donations_amount + amount >= donation_campaign.money_goal:
            donation_campaign.active = False

        return individual_donation

    async def get_donation_campaign_amount(
        self, uow: UnitOfWork, donation_campaign: DonationCampaign
    ) -> int:
        return await self.donations_repository.get_donation_campaign_amount(
            session=uow.session,
            donation_campaign_id=donation_campaign.entity_id,
        )

    async def get_donation_campaign(
        self, uow: UnitOfWork, donation_campaign_id: str
    ) -> DonationCampaign:
        donation_campaign: DonationCampaign | None = await self.find_donation_campaign(
            uow=uow,
            donation_campaign_id=donation_campaign_id,
        )

        if donation_campaign is None:
            raise DonationCampaignNotFoundByIdException(entity_id=donation_campaign_id)

        return donation_campaign

    async def find_donation_campaign(
        self, uow: UnitOfWork, donation_campaign_id: str
    ) -> DonationCampaign | None:
        return await self.donations_repository.find_donation_campaign(
            session=uow.session,
            donation_campaign_id=donation_campaign_id,
        )

    async def get_all_donation_campaigns(
        self,
        uow: UnitOfWork,
        active: bool,
        limit: int | None = None,
        offset: int | None = 0,
        organization_id: str | None = None,
    ) -> Sequence[DonationCampaign]:
        return await self.donations_repository.get_donation_campaigns(
            session=uow.session,
            active=active,
            limit=limit,
            offset=offset,
            organization_id=organization_id,
        )

    async def get_all_donation_campaigns_count(
        self,
        uow: UnitOfWork,
        active: bool,
        organization_id: str | None = None,
    ) -> int:
        return await self.donations_repository.count_donation_campaigns(
            session=uow.session,
            active=active,
            organization_id=organization_id,
        )

    async def get_donation_campaign_amounts(
        self, uow: UnitOfWork, donation_campaign_ids: list[str]
    ) -> Sequence[tuple[str, int]]:
        return await self.donations_repository.get_donation_campaign_amounts(
            session=uow.session,
            donation_campaign_ids=donation_campaign_ids,
        )

    async def find_individual_donation(
        self, uow: UnitOfWork, individual_donation_id: str
    ) -> IndividualDonation | None:
        donation: IndividualDonation | None = (
            await self.donations_repository.get_individual_donation(
                session=uow.session,
                entity_id=individual_donation_id,
            )
        )

        return donation

    def __assert_profile_is_owner_of_campaign(
        self, profile: BaseProfile, donation_campaign: DonationCampaign
    ) -> None:
        self.__assert_organizational_profile(profile=profile)
        actor_profile = cast(OrganizationalProfile, profile)
        self.__assert_not_collaborator_organizational_profile(
            profile=actor_profile, donation_campaign_id=donation_campaign.entity_id
        )

        if donation_campaign.organization_id != actor_profile.organization_id:
            raise CloseNotOwnCampaignException(
                actor_account_id=profile.account.entity_id,
                campaign_id=donation_campaign.entity_id,
            )

    @staticmethod
    def validate_donation_to_campaign(
        profile: BaseProfile,
        donation_campaign: DonationCampaign,
        amount: float,
    ) -> None:
        if profile.profile_type != ProfileTypes.PERSONAL_PROFILE:
            raise OrganizationalProfileUnauthorizedToDonateException(
                actor_account_id=profile.account.entity_id
            )

        if not donation_campaign.active:
            raise CampaignAlreadyFinishedException(donation_campaign.entity_id)

        if amount <= 0:
            raise MoneyAmountNotValidException()

    @staticmethod
    def __assert_organizational_profile(profile: BaseProfile) -> None:
        if profile.profile_type is not ProfileTypes.ORGANIZATIONAL_PROFILE:
            raise PersonalProfileUnauthorizedCampaignManagementException(
                profile.entity_id
            )

    @staticmethod
    def __assert_not_collaborator_organizational_profile(
        profile: OrganizationalProfile, donation_campaign_id: str | None = None
    ):
        if profile.organization_role is OrganizationRoles.COLLABORATOR:
            raise CollaboratorUnauthorizedCampaignManagementException(
                profile.entity_id, donation_campaign_id
            )

    @staticmethod
    def __assert_not_personal_profile(profile: BaseProfile):
        if profile.profile_type != ProfileTypes.ORGANIZATIONAL_PROFILE:
            raise PersonalProfileUnauthorizedCampaignManagementException(
                actor_account_id=profile.account.entity_id
            )
