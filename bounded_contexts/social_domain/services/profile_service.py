from dataclasses import dataclass
from datetime import date
from typing import Sequence
from uuid import uuid4

from bounded_contexts.auth.entities import Account
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    PersonalProfile,
    OrganizationalProfile,
)
from bounded_contexts.social_domain.enum import (
    OrganizationRoles,
)
from bounded_contexts.social_domain.events import (
    PersonalProfileCreatedEvent,
    OrganizationalProfileCreatedEvent,
)
from bounded_contexts.social_domain.exceptions import (
    ProfileAlreadyAssociatedToAccountException,
    ProfileNotFoundException,
    PersonalProfileNotFoundException,
    OrganizationalProfileNotFoundException,
    ViewOrganizationalProfilesUnauthorizedException,
    RegisterOrganizationAdminUnauthorizedException,
)
from bounded_contexts.social_domain.repositories import ProfileRepository
from infrastructure.date_utils import float_timestamp
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class ModifyProfileData:
    entity_id: str
    first_name: str
    surname: str
    phone_number: str
    government_id: str
    birthdate: date
    social_media_url: str | None = None


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    async def create_personal_profile(
        self,
        uow: UnitOfWork,
        account: Account,
        first_name: str,
        surname: str,
        phone_number: str,
        government_id: str,
        birthdate: date,
    ) -> PersonalProfile:
        if (
            await self.find_profile_by_account_id(uow=uow, account_id=account.entity_id)
            is not None
        ):
            raise ProfileAlreadyAssociatedToAccountException()

        profile: PersonalProfile = PersonalProfile(
            account=account,
            entity_id=uuid4().hex,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            birthdate=birthdate,
        )

        await self.profile_repository.add_profile(session=uow.session, profile=profile)

        self.__issue_personal_profile_created_event(
            uow=uow,
            profile=profile,
        )

        return profile

    async def get_profile_by_account_id(
        self, uow: UnitOfWork, account_id: str
    ) -> BaseProfile:
        profile: BaseProfile | None = (
            await self.profile_repository.get_profile_by_account_id(
                session=uow.session,
                account_id=account_id,
            )
        )

        if profile is None:
            raise ProfileNotFoundException()

        return profile

    async def get_profile(self, uow: UnitOfWork, entity_id: str) -> BaseProfile:
        profile: BaseProfile | None = await self.profile_repository.get_profile(
            session=uow.session,
            entity_id=entity_id,
        )

        if profile is None:
            raise ProfileNotFoundException()

        return profile

    async def find_profile_by_account_id(
        self, uow: UnitOfWork, account_id: str
    ) -> BaseProfile | None:
        return await self.profile_repository.get_profile_by_account_id(
            session=uow.session,
            account_id=account_id,
        )

    async def get_personal_profile(
        self, uow: UnitOfWork, entity_id: str
    ) -> PersonalProfile:
        profile: PersonalProfile | None = (
            await self.profile_repository.get_personal_profile(
                session=uow.session,
                entity_id=entity_id,
            )
        )

        if profile is None:
            raise PersonalProfileNotFoundException()

        return profile

    async def get_organizational_profile(
        self, uow: UnitOfWork, entity_id: str
    ) -> OrganizationalProfile:
        profile: OrganizationalProfile | None = (
            await self.profile_repository.get_organizational_profile(
                session=uow.session,
                entity_id=entity_id,
            )
        )

        if profile is None:
            raise OrganizationalProfileNotFoundException()

        return profile

    async def get_organizational_profile_by_account_id(
        self, uow: UnitOfWork, account_id: str
    ) -> OrganizationalProfile:
        profile: OrganizationalProfile | None = (
            await self.profile_repository.get_organizational_profile_by_account_id(
                session=uow.session,
                account_id=account_id,
            )
        )

        if profile is None:
            raise OrganizationalProfileNotFoundException()

        return profile

    async def get_personal_profile_by_account_id(
        self, uow: UnitOfWork, account_id: str
    ) -> PersonalProfile:
        profile: PersonalProfile | None = (
            await self.profile_repository.get_personal_profile_by_account_id(
                session=uow.session,
                account_id=account_id,
            )
        )

        if profile is None:
            raise PersonalProfileNotFoundException()

        return profile

    async def create_organization_admin_profile(
        self,
        uow: UnitOfWork,
        account: Account,
        first_name: str,
        surname: str,
        phone_number: str,
        government_id: str,
        organization_id: str,
        birthdate: date,
    ) -> OrganizationalProfile:
        return await self._create_organizational_profile(
            uow=uow,
            account=account,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            organization_id=organization_id,
            organization_role=OrganizationRoles.ADMIN,
            birthdate=birthdate,
            verified_by_organization=True,
        )

    async def create_organization_employee_profile(
        self,
        uow: UnitOfWork,
        account: Account,
        first_name: str,
        surname: str,
        phone_number: str,
        government_id: str,
        organization_id: str,
        birthdate: date,
        organization_role: OrganizationRoles,
    ) -> OrganizationalProfile:
        # There can only be one organization admin, the creator
        if organization_role == OrganizationRoles.ADMIN:
            raise RegisterOrganizationAdminUnauthorizedException()

        return await self._create_organizational_profile(
            uow=uow,
            account=account,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            organization_id=organization_id,
            organization_role=organization_role,
            birthdate=birthdate,
            verified_by_organization=False,
        )

    async def _create_organizational_profile(
        self,
        uow: UnitOfWork,
        account: Account,
        first_name: str,
        surname: str,
        phone_number: str,
        government_id: str,
        organization_id: str,
        organization_role: OrganizationRoles,
        birthdate: date,
        verified_by_organization: bool,
    ) -> OrganizationalProfile:
        if (
            await self.find_profile_by_account_id(uow=uow, account_id=account.entity_id)
            is not None
        ):
            raise ProfileAlreadyAssociatedToAccountException()

        profile: OrganizationalProfile = OrganizationalProfile(
            account=account,
            entity_id=uuid4().hex,
            first_name=first_name,
            surname=surname,
            phone_number=phone_number,
            government_id=government_id,
            organization_id=organization_id,
            organization_role=organization_role,
            birthdate=birthdate,
            verified_by_organization=verified_by_organization,
        )

        await self.profile_repository.add_profile(session=uow.session, profile=profile)

        self.__issue_organizational_profile_created_event(
            uow=uow,
            profile=profile,
        )

        return profile

    async def get_organization_profiles(
        self,
        uow: UnitOfWork,
        actor_profile: OrganizationalProfile,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Sequence[OrganizationalProfile]:
        if actor_profile.organization_role != OrganizationRoles.ADMIN:
            raise ViewOrganizationalProfilesUnauthorizedException(
                actor_account_id=actor_profile.account.entity_id
            )

        return await self.profile_repository.get_organization_profiles(
            session=uow.session,
            organization_id=actor_profile.organization_id,
            offset=offset,
            limit=limit,
        )

    async def get_organization_profiles_count(
        self,
        uow: UnitOfWork,
        actor_profile: OrganizationalProfile,
    ) -> int:
        if actor_profile.organization_role != OrganizationRoles.ADMIN:
            raise ViewOrganizationalProfilesUnauthorizedException(
                actor_account_id=actor_profile.account.entity_id
            )

        return await self.profile_repository.get_organization_profiles_count(
            session=uow.session,
            organization_id=actor_profile.organization_id,
        )

    async def get_multiple_personal_profiles_by_id(
        self, uow: UnitOfWork, profile_ids: list[str]
    ) -> Sequence[PersonalProfile]:
        return await self.profile_repository.get_multiple_personal_profiles_by_id(
            session=uow.session,
            profile_ids=profile_ids,
        )

    async def get_multiple_organizational_profiles_by_id(
        self, uow: UnitOfWork, profile_ids: list[str]
    ) -> Sequence[OrganizationalProfile]:
        return await self.profile_repository.get_multiple_organizational_profiles_by_id(
            session=uow.session,
            profile_ids=profile_ids,
        )

    async def get_multiple_organizational_profiles_by_account_id(
        self,
        uow: UnitOfWork,
        account_ids: list[str],
    ) -> Sequence[OrganizationalProfile]:
        return await self.profile_repository.get_multiple_organizational_profiles_by_account_id(
            session=uow.session,
            account_ids=account_ids,
        )

    @staticmethod
    async def edit_personal_profile(
        uow: UnitOfWork,
        profile: PersonalProfile,
        new_profile_data: ModifyProfileData,
    ) -> None:
        profile.first_name = new_profile_data.first_name
        profile.surname = new_profile_data.surname
        profile.phone_number = new_profile_data.phone_number
        profile.government_id = new_profile_data.government_id
        profile.birthdate = new_profile_data.birthdate
        profile.social_media_url = new_profile_data.social_media_url

        await uow.flush()

    @staticmethod
    def __issue_personal_profile_created_event(
        uow: UnitOfWork, profile: PersonalProfile
    ) -> None:
        uow.emit_event(
            PersonalProfileCreatedEvent(
                actor_account_id=profile.account.entity_id,
                email=profile.account.email,
                first_name=profile.first_name,
                issued=float_timestamp(),
            )
        )

    @staticmethod
    def __issue_organizational_profile_created_event(
        uow: UnitOfWork, profile: OrganizationalProfile
    ) -> None:
        uow.emit_event(
            OrganizationalProfileCreatedEvent(
                actor_account_id=profile.account.entity_id,
                email=profile.account.email,
                issued=float_timestamp(),
                first_name=profile.first_name,
                organization_role=profile.organization_role,
            )
        )
