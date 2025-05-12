from abc import ABC, abstractmethod
from typing import Sequence

from infrastructure.uow_abstraction.unit_of_work_module import Session
from bounded_contexts.social_domain.entities import (
    BaseProfile,
    PersonalProfile,
    OrganizationalProfile,
)


class ProfileRepository(ABC):
    @abstractmethod
    async def add_profile(self, session: Session, profile: BaseProfile) -> None:
        pass

    @abstractmethod
    async def get_profile(self, session: Session, entity_id: str) -> BaseProfile | None:
        pass

    @abstractmethod
    async def get_personal_profile(
        self, session: Session, entity_id: str
    ) -> PersonalProfile | None:
        pass

    @abstractmethod
    async def get_organizational_profile(
        self, session: Session, entity_id: str
    ) -> OrganizationalProfile | None:
        pass

    @abstractmethod
    async def get_profile_by_account_id(
        self, session: Session, account_id: str
    ) -> BaseProfile | None:
        pass

    @abstractmethod
    async def get_personal_profile_by_account_id(
        self, session: Session, account_id: str
    ) -> PersonalProfile | None:
        pass

    @abstractmethod
    async def get_organizational_profile_by_account_id(
        self,
        session: Session,
        account_id: str,
    ) -> OrganizationalProfile | None:
        pass

    @abstractmethod
    async def get_organization_profiles(
        self,
        session: Session,
        organization_id: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Sequence[OrganizationalProfile]:
        pass

    @abstractmethod
    async def get_organization_profiles_count(
        self,
        session: Session,
        organization_id: str,
    ) -> int:
        pass

    @abstractmethod
    async def get_multiple_personal_profiles_by_id(
        self, session: Session, profile_ids: list[str]
    ) -> Sequence[PersonalProfile]:
        pass

    @abstractmethod
    async def get_multiple_organizational_profiles_by_id(
        self, session: Session, profile_ids: list[str]
    ) -> Sequence[OrganizationalProfile]:
        pass

    @abstractmethod
    async def get_multiple_organizational_profiles_by_account_id(
        self,
        session: Session,
        account_ids: list[str],
    ) -> Sequence[OrganizationalProfile]:
        pass
