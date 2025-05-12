from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.pets_domain.entities import Pet
from infrastructure.uow_abstraction.unit_of_work_module import Session


class PetsRepository(ABC):
    @abstractmethod
    async def add_pet(self, session: Session, pet: Pet) -> None:
        pass

    @abstractmethod
    async def get_pet_by_id(
        self,
        session: Session,
        entity_id: str,
    ) -> Pet | None:
        pass

    @abstractmethod
    async def get_pet_by_adoption_animal_id(
        self,
        session: Session,
        adoption_animal_id: str,
    ) -> Pet | None:
        pass

    @abstractmethod
    async def get_pets(
        self,
        session: Session,
        limit: int | None = None,
        offset: int | None = 0,
        lost: bool | None = None,
        profile_id: str | None = None,
    ) -> Sequence[Pet]:
        pass

    @abstractmethod
    async def count_pets(
        self, session: Session, lost: bool | None = None, profile_id: str | None = None
    ) -> int:
        pass

    @abstractmethod
    async def delete_pets(self, session: Session, pet: Pet) -> None:
        pass
