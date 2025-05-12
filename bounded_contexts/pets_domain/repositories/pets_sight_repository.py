from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.pets_domain.entities import PetSight
from infrastructure.uow_abstraction.unit_of_work_module import Session


class PetsSightRepository(ABC):
    @abstractmethod
    async def add_pet_sight(self, session: Session, pet_sight: PetSight) -> None:
        pass

    @abstractmethod
    async def get_pet_sight_by_id(
        self, session: Session, entity_id: str
    ) -> PetSight | None:
        pass

    @abstractmethod
    async def get_pet_sights(
        self,
        session: Session,
        limit: int | None = None,
        offset: int | None = 0,
        pet_id: str | None = None,
        lost: bool | None = None,
    ) -> Sequence[PetSight]:
        pass

    @abstractmethod
    async def count_pet_sights(
        self, session: Session, pet_id: str | None = None, lost: bool | None = None
    ) -> int:
        pass

    @abstractmethod
    async def get_most_recent_lost_pet_sights(
        self, session: Session, limit: int | None = None, offset: int | None = 0
    ) -> Sequence[PetSight]:
        pass

    @abstractmethod
    async def count_most_recent_lost_pet_sights(self, session: Session) -> int:
        pass

    @abstractmethod
    async def delete(self, session: Session, pet_sights: Sequence[PetSight]) -> None:
        pass
