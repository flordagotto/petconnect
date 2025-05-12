from typing import Sequence
from uuid import uuid4
from bounded_contexts.social_domain.entities import Organization, OrganizationalProfile
from bounded_contexts.social_domain.enum import OrganizationRoles
from bounded_contexts.social_domain.events import OrganizationVerifiedEvent
from bounded_contexts.social_domain.exceptions import (
    OrganizationAlreadyRegisteredException,
    AcceptOrganizationMemberUnauthorizedException,
    DisableOrganizationMemberUnauthorizedException,
)
from bounded_contexts.social_domain.exceptions.organization_not_found_by_id import (
    OrganizationNotFoundByIdException,
)
from bounded_contexts.social_domain.exceptions.organization_not_found_by_name import (
    OrganizationNotFoundByNameException,
)
from bounded_contexts.social_domain.repositories import OrganizationsRepository
from infrastructure.date_utils import float_timestamp
from infrastructure.uow_abstraction import UnitOfWork


class OrganizationService:
    def __init__(
        self,
        organizations_repository: OrganizationsRepository,
    ) -> None:
        self.organizations_repository = organizations_repository

    async def create_organization(
        self,
        uow: UnitOfWork,
        organization_name: str,
        creator_account_id: str,
        phone_number: str,
        social_media_url: str | None = None,
    ) -> Organization:
        if await self.organizations_repository.get_organization_by_name(
            session=uow.session, organization_name=organization_name
        ):
            raise OrganizationAlreadyRegisteredException(
                organization_name=organization_name
            )

        organization: Organization = Organization(
            entity_id=uuid4().hex,
            organization_name=organization_name,
            creator_account_id=creator_account_id,
            verified=False,
            verified_bank=False,
            phone_number=phone_number,
            social_media_url=social_media_url,
        )

        await self.organizations_repository.add_organization(
            session=uow.session, organization=organization
        )

        return organization

    async def get_organization_by_name(
        self, uow: UnitOfWork, organization_name: str
    ) -> Organization:
        organization: Organization | None = (
            await self.organizations_repository.get_organization_by_name(
                session=uow.session,
                organization_name=organization_name,
            )
        )

        if not organization:
            raise OrganizationNotFoundByNameException(
                organization_name=organization_name
            )

        return organization

    async def get_all_organizations(
        self, uow: UnitOfWork, limit: int | None, offset: int | None
    ) -> Sequence[Organization]:
        organizations: Sequence[
            Organization
        ] = await self.organizations_repository.get_organizations(
            session=uow.session, limit=limit, offset=offset
        )

        return organizations

    async def get_all_organizations_count(self, uow: UnitOfWork) -> int:
        return await self.organizations_repository.count_organizations(
            session=uow.session
        )

    async def get_organization_by_id(
        self, uow: UnitOfWork, entity_id: str
    ) -> Organization:
        organization: Organization | None = (
            await self.organizations_repository.get_organization_by_id(
                session=uow.session,
                entity_id=entity_id,
            )
        )

        if not organization:
            raise OrganizationNotFoundByIdException(entity_id=entity_id)

        return organization

    async def accept_organization_profile(
        self,
        actor_profile: OrganizationalProfile,
        profile: OrganizationalProfile,
    ) -> None:
        if (actor_profile.organization_role != OrganizationRoles.ADMIN) or (
            actor_profile.organization_id != profile.organization_id
        ):
            raise AcceptOrganizationMemberUnauthorizedException(
                actor_account_id=actor_profile.account.entity_id,
            )

        profile.verified_by_organization = True

    async def disable_organization_profile(
        self,
        actor_profile: OrganizationalProfile,
        profile: OrganizationalProfile,
    ) -> None:
        if (actor_profile.organization_role != OrganizationRoles.ADMIN) or (
            actor_profile.organization_id != profile.organization_id
        ):
            raise DisableOrganizationMemberUnauthorizedException(
                actor_account_id=actor_profile.account.entity_id,
            )

        profile.verified_by_organization = False

    async def get_multiple_organizations_by_id(
        self, uow: UnitOfWork, organization_ids: list[str]
    ) -> Sequence[Organization]:
        organizations: Sequence[
            Organization
        ] = await self.organizations_repository.get_multiple_organizations_by_id(
            session=uow.session, organization_ids=organization_ids
        )

        return organizations

    async def verify_organization(
        self,
        uow: UnitOfWork,
        organization: Organization,
        profile: OrganizationalProfile,
    ):
        organization.verified = True

        self.__issue_organization_verified_event(
            uow=uow,
            profile=profile,
            organization=organization,
        )

    @staticmethod
    def __issue_organization_verified_event(
        uow: UnitOfWork, profile: OrganizationalProfile, organization: Organization
    ) -> None:
        uow.emit_event(
            OrganizationVerifiedEvent(
                actor_account_id=profile.account.entity_id,
                email=profile.account.email,
                issued=float_timestamp(),
                profile_first_name=profile.first_name,
                organization_name=organization.organization_name,
            )
        )
