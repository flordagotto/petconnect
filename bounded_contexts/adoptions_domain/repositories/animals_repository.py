from abc import ABC, abstractmethod
from typing import Sequence

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.social_domain.entities import AnimalSpecies
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AdoptionAnimalsRepository(ABC):
    @abstractmethod
    async def add_animal(
        self, session: Session, adoption_animal: AdoptionAnimal
    ) -> None:
        pass

    @abstractmethod
    async def get_animal_by_id(
        self, session: Session, entity_id: str, get_all: bool
    ) -> AdoptionAnimal | None:
        pass

    @abstractmethod
    async def get_animals(
        self,
        session: Session,
        species: Sequence[AnimalSpecies] | None = None,
        limit: int | None = None,
        offset: int | None = 0,
        profile_id: str | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> Sequence[AdoptionAnimal]:
        pass

    @abstractmethod
    async def count_animals(
        self,
        session: Session,
        species: Sequence[AnimalSpecies] | None = None,
        profile_id: str | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_animals_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        species: Sequence[AnimalSpecies] | None = None,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionAnimal]:
        pass

    @abstractmethod
    async def count_animals_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        species: Sequence[AnimalSpecies] | None = None,
    ) -> int:
        pass
