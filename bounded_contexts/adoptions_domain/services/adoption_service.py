from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from bounded_contexts.adoptions_domain.entities.adoption import Adoption
from bounded_contexts.adoptions_domain.exceptions import (
    AdoptionNotFoundByIdException,
    AdoptionNotFoundByApplicationIdException,
)
from bounded_contexts.adoptions_domain.repositories.adoptions_repository import (
    AdoptionsRepository,
)
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class AdoptionData:
    entity_id: str
    adoption_date: datetime
    adoption_application_id: str


class AdoptionService:
    def __init__(
        self,
        adoptions_repository: AdoptionsRepository,
    ) -> None:
        self.adoptions_repository = adoptions_repository

    async def create_adoption(
        self, uow: UnitOfWork, adoption_date: datetime, adoption_application_id: str
    ) -> Adoption:
        adoption_id: str = uuid4().hex

        adoption: Adoption = Adoption(
            entity_id=adoption_id,
            adoption_date=adoption_date,
            adoption_application_id=adoption_application_id,
        )

        await self.adoptions_repository.add_adoption(
            session=uow.session, adoption=adoption
        )

        return adoption

    async def get_adoption_by_id(self, uow: UnitOfWork, entity_id: str) -> Adoption:
        adoption: Adoption | None = await self.adoptions_repository.get_adoption_by_id(
            session=uow.session, entity_id=entity_id
        )

        if not adoption:
            raise AdoptionNotFoundByIdException(entity_id=entity_id)

        return adoption

    async def get_adoption_by_application_id(
        self, uow: UnitOfWork, adoption_application_id: str
    ) -> Adoption:
        adoption: Adoption | None = (
            await self.adoptions_repository.get_adoption_by_application_id(
                session=uow.session, adoption_application_id=adoption_application_id
            )
        )

        if not adoption:
            raise AdoptionNotFoundByApplicationIdException(
                adoption_application_id=adoption_application_id
            )

        return adoption
