from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.social_domain.entities import Organization
from infrastructure.uow_abstraction.unit_of_work_module import Session


class OrganizationsRepository(ABC):
    @abstractmethod
    async def get_organization_by_name(
        self, session: Session, organization_name: str
    ) -> Organization | None:
        pass

    @abstractmethod
    async def add_organization(
        self, session: Session, organization: Organization
    ) -> None:
        pass

    @abstractmethod
    async def get_organizations(
        self, session: Session, limit: int | None = None, offset: int | None = 0
    ) -> Sequence[Organization]:
        pass

    @abstractmethod
    async def count_organizations(self, session: Session) -> int:
        pass

    @abstractmethod
    async def get_organization_by_id(
        self, session: Session, entity_id: str
    ) -> Organization | None:
        pass

    @abstractmethod
    async def get_multiple_organizations_by_id(
        self, session: Session, organization_ids: list[str]
    ) -> Sequence[Organization]:
        pass
