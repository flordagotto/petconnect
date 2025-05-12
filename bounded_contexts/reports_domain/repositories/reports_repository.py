from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.reports_domain.dataclasses import AdoptedAnimal, CollectedMoney
from bounded_contexts.reports_domain.dataclasses.lost_and_found_pets import (
    LostAndFoundPets,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class ReportsRepository(ABC):
    @abstractmethod
    async def get_adopted_animals(
        self, session: Session, organization_id: str | None = None
    ) -> Sequence[AdoptedAnimal]:
        pass

    @abstractmethod
    async def get_collected_money(
        self, session: Session, organization_id: str | None
    ) -> Sequence[CollectedMoney]:
        pass

    @abstractmethod
    async def get_lost_and_found_pets(
        self, session: Session
    ) -> Sequence[LostAndFoundPets]:
        pass
