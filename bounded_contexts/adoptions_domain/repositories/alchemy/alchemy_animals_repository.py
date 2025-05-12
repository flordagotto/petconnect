from typing import Type, Sequence
from sqlalchemy import select, func

from bounded_contexts.adoptions_domain.entities import AdoptionAnimal
from bounded_contexts.adoptions_domain.enum import AdoptionAnimalStates
from bounded_contexts.adoptions_domain.repositories.animals_repository import (
    AdoptionAnimalsRepository,
)
from bounded_contexts.social_domain.entities import (
    AnimalSpecies,
    OrganizationalProfile,
    Organization,
)
from bounded_contexts.social_domain.enum import AnimalTypes
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyAdoptionAnimalsRepository(AdoptionAnimalsRepository):
    def __init__(self) -> None:
        self.model: Type[AdoptionAnimal] = AdoptionAnimal
        self.profiles_model: Type[OrganizationalProfile] = OrganizationalProfile
        self.organizations_model: Type[Organization] = Organization

    async def add_animal(
        self, session: Session, adoption_animal: AdoptionAnimal
    ) -> None:
        session.add(adoption_animal)
        await session.flush([adoption_animal])

    async def get_animal_by_id(
        self, session: Session, entity_id: str, get_all: bool
    ) -> AdoptionAnimal | None:
        query = (
            select(self.model)
            .where(
                self.model.entity_id == entity_id,  # type: ignore
            )
            .where(
                self.model.animal_type == AnimalTypes.ANIMAL_FOR_ADOPTION  # type: ignore
            )
        )

        if not get_all:
            query = query.where(self.model.deleted == False)  # type: ignore

        result = await session.execute(query)
        return result.scalars().first()

    async def get_animals(
        self,
        session: Session,
        species: Sequence[AnimalSpecies] | None = None,
        limit: int | None = None,
        offset: int | None = 0,
        profile_id: str | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> Sequence[AdoptionAnimal]:
        query = (
            select(self.model)
            .where(self.model.animal_type == AnimalTypes.ANIMAL_FOR_ADOPTION)  # type: ignore
            .where(self.model.deleted == False)  # type: ignore
            .order_by(self.model.animal_name)  # type: ignore
        )

        if profile_id:
            query = query.where(
                self.model.profile_id == profile_id,  # type: ignore
            )

        if species:
            query = query.filter(self.model.species.in_(species))  # type: ignore

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if state:
            query = query.where(self.model.state == state)  # type: ignore

        result = await session.execute(query)
        return result.scalars().all()

    async def count_animals(
        self,
        session: Session,
        species: Sequence[AnimalSpecies] | None = None,
        profile_id: str | None = None,
        state: AdoptionAnimalStates | None = None,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.model)
            .where(self.model.animal_type == AnimalTypes.ANIMAL_FOR_ADOPTION)  # type: ignore
            .where(self.model.deleted == False)  # type: ignore
        )

        if profile_id:
            query = query.where(
                self.model.profile_id == profile_id,  # type: ignore
            )

        if species:
            query = query.filter(self.model.species.in_(species))  # type: ignore

        if state:
            query = query.where(self.model.state == state)  # type: ignore

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_animals_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        species: Sequence[AnimalSpecies] | None = None,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionAnimal]:
        query = (
            select(self.model)
            .where(self.model.animal_type == AnimalTypes.ANIMAL_FOR_ADOPTION)  # type: ignore
            .where(self.model.deleted == False)  # type: ignore
            .order_by(self.model.animal_name)  # type: ignore
        )

        query = query.where(
            self.model.organization_id == organization_id,  # type: ignore
        )

        if species:
            query = query.filter(self.model.species.in_(species))  # type: ignore

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_animals_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        species: Sequence[AnimalSpecies] | None = None,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.model)
            .where(self.model.animal_type == AnimalTypes.ANIMAL_FOR_ADOPTION)  # type: ignore
            .where(self.model.deleted == False)  # type: ignore
        )

        query = query.where(
            self.model.organization_id == organization_id,  # type: ignore
        )

        if species:
            query = query.filter(self.model.species.in_(species))  # type: ignore

        result = await session.execute(query)
        return result.scalar()  # type: ignore
