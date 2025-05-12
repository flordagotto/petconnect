from typing import Type, Sequence
from sqlalchemy import select, func

from bounded_contexts.pets_domain.entities import Pet
from bounded_contexts.pets_domain.repositories.pets_repository import (
    PetsRepository,
)
from bounded_contexts.social_domain.enum import AnimalTypes
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyPetsRepository(PetsRepository):
    def __init__(self) -> None:
        self.model: Type[Pet] = Pet

    async def add_pet(self, session: Session, pet: Pet) -> None:
        session.add(pet)
        await session.flush([pet])

    async def get_pet_by_id(self, session: Session, entity_id: str) -> Pet | None:
        query = (
            select(self.model)
            .where(
                self.model.entity_id == entity_id,  # type: ignore
            )
            .where(self.model.animal_type == AnimalTypes.PET)  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_pet_by_adoption_animal_id(
        self,
        session: Session,
        adoption_animal_id: str,
    ) -> Pet | None:
        query = (
            select(self.model)
            .where(
                self.model.adoption_animal_id == adoption_animal_id,  # type: ignore
            )
            .where(self.model.animal_type == AnimalTypes.PET)  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_pets(
        self,
        session: Session,
        limit: int | None = None,
        offset: int | None = 0,
        lost: bool | None = None,
        profile_id: str | None = None,
    ) -> Sequence[Pet]:
        query = (
            select(self.model)
            .order_by("animal_name")
            .where(self.model.animal_type == AnimalTypes.PET)  # type: ignore
        )

        if profile_id:
            query = query.where(
                self.model.profile_id == profile_id,  # type: ignore
            )

        if lost is not None:
            query = query.where(
                self.model.lost == lost,  # type: ignore
            )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_pets(
        self, session: Session, lost: bool | None = None, profile_id: str | None = None
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.model)
            .where(self.model.animal_type == AnimalTypes.PET)  # type: ignore
        )
        if lost is not None:
            query = query.where(self.model.lost == lost)  # type: ignore

        if profile_id:
            query = query.where(self.model.profile_id == profile_id)  # type: ignore

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def delete_pets(self, session: Session, pet: Pet) -> None:
        await session.delete(pet)
        await session.flush([pet])
