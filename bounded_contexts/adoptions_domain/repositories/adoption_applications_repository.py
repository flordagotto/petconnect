from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.adoptions_domain.entities import (
    AdoptionApplication,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AdoptionApplicationsRepository(ABC):
    @abstractmethod
    async def add_application(
        self, session: Session, application: AdoptionApplication
    ) -> None:
        pass

    @abstractmethod
    async def get_application_by_id(
        self,
        session: Session,
        entity_id: str,
    ) -> AdoptionApplication | None:
        pass

    @abstractmethod
    async def get_application_by_animal_id(
        self,
        session: Session,
        adoption_animal_id: str,
    ) -> AdoptionApplication | None:
        pass

    @abstractmethod
    async def get_received_applications_by_animal_id(
        self,
        session: Session,
        adoption_animal_id: str,
    ) -> Sequence[AdoptionApplication]:
        pass

    @abstractmethod
    async def get_received_applications_by_personal_profile(
        self,
        session: Session,
        profile_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        pass

    @abstractmethod
    async def count_received_applications_by_personal_profile(
        self,
        session: Session,
        profile_id: str,
    ) -> int:
        pass

    @abstractmethod
    async def get_received_applications_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        pass

    @abstractmethod
    async def count_received_applications_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
    ) -> int:
        pass

    @abstractmethod
    async def get_sent_applications(
        self,
        session: Session,
        profile_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        pass

    @abstractmethod
    async def count_sent_applications(
        self,
        session: Session,
        profile_id: str,
    ) -> int:
        pass

    @abstractmethod
    async def delete_applications(
        self, session: Session, application: AdoptionApplication
    ) -> None:
        pass
