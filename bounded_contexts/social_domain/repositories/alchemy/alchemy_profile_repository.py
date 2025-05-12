from typing import Type, Sequence
from sqlalchemy import select, func

from bounded_contexts.social_domain.enum import OrganizationRoles, ProfileTypes
from infrastructure.uow_abstraction.unit_of_work_module import Session
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    PersonalProfile,
    OrganizationalProfile,
)
from bounded_contexts.social_domain.repositories import ProfileRepository


class AlchemyProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self.model: Type[BaseProfile] = BaseProfile
        self.personal_profile_model: Type[PersonalProfile] = PersonalProfile
        self.organizational_profile_model: Type[
            OrganizationalProfile
        ] = OrganizationalProfile

    async def add_profile(self, session: Session, profile: BaseProfile) -> None:
        session.add(profile)
        await session.flush([profile])

    async def get_profile(self, session: Session, entity_id: str) -> BaseProfile | None:
        query = select(self.model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_personal_profile(
        self, session: Session, entity_id: str
    ) -> PersonalProfile | None:
        query = select(self.personal_profile_model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_organizational_profile(
        self, session: Session, entity_id: str
    ) -> OrganizationalProfile | None:
        query = select(self.organizational_profile_model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_profile_by_account_id(
        self, session: Session, account_id: str
    ) -> BaseProfile | None:
        query = select(self.model).where(
            self.model.account_id == account_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_personal_profile_by_account_id(
        self, session: Session, account_id: str
    ) -> PersonalProfile | None:
        query = select(self.personal_profile_model).where(
            self.model.account_id == account_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_organizational_profile_by_account_id(
        self,
        session: Session,
        account_id: str,
    ) -> OrganizationalProfile | None:
        query = select(self.organizational_profile_model).where(
            self.model.account_id == account_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_organization_profiles(
        self,
        session: Session,
        organization_id: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Sequence[OrganizationalProfile]:
        query = select(self.organizational_profile_model).where(
            self.model.organization_id == organization_id,  # type: ignore
            self.model.organization_role != OrganizationRoles.ADMIN,  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def get_organization_profiles_count(
        self, session: Session, organization_id: str
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.organizational_profile_model)
            .where(
                self.model.organization_id == organization_id,  # type: ignore
                self.model.organization_role != OrganizationRoles.ADMIN,  # type: ignore
            )
        )

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_multiple_personal_profiles_by_id(
        self, session: Session, profile_ids: list[str]
    ) -> Sequence[PersonalProfile]:
        query = select(self.personal_profile_model).where(
            self.personal_profile_model.entity_id.in_(profile_ids),  # type: ignore
            self.model.profile_type == ProfileTypes.PERSONAL_PROFILE,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().all()

    async def get_multiple_organizational_profiles_by_id(
        self, session: Session, profile_ids: list[str]
    ) -> Sequence[OrganizationalProfile]:
        query = select(self.organizational_profile_model).where(
            self.organizational_profile_model.entity_id.in_(profile_ids),  # type: ignore
            self.model.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().all()

    async def get_multiple_organizational_profiles_by_account_id(
        self,
        session: Session,
        account_ids: list[str],
    ) -> Sequence[OrganizationalProfile]:
        query = select(self.organizational_profile_model).where(
            self.organizational_profile_model.account_id.in_(account_ids),  # type: ignore
            self.model.profile_type == ProfileTypes.ORGANIZATIONAL_PROFILE,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().all()
