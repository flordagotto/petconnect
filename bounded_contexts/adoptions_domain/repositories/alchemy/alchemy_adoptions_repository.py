from typing import Type
from sqlalchemy import select

from bounded_contexts.adoptions_domain.entities import (
    AdoptionAnimal,
)
from bounded_contexts.adoptions_domain.entities.adoption import Adoption
from bounded_contexts.adoptions_domain.repositories.adoptions_repository import (
    AdoptionsRepository,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyAdoptionsRepository(AdoptionsRepository):
    def __init__(self) -> None:
        self.model: Type[Adoption] = Adoption
        self.animals_model: Type[AdoptionAnimal] = AdoptionAnimal

    async def add_adoption(self, session: Session, adoption: Adoption) -> None:
        session.add(adoption)
        await session.flush([adoption])

    async def get_adoption_by_id(
        self, session: Session, entity_id: str
    ) -> Adoption | None:
        query = select(self.model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_adoption_by_application_id(
        self,
        session: Session,
        adoption_application_id: str,
    ) -> Adoption | None:
        query = select(self.model).where(
            self.model.adoption_application_id == adoption_application_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()
