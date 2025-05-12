from typing import Type, Sequence
from sqlalchemy import select, func, join

from bounded_contexts.adoptions_domain.entities import (
    AdoptionApplication,
    AdoptionAnimal,
)
from bounded_contexts.adoptions_domain.repositories.adoption_applications_repository import (
    AdoptionApplicationsRepository,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyAdoptionApplicationsRepository(AdoptionApplicationsRepository):
    def __init__(self) -> None:
        self.model: Type[AdoptionApplication] = AdoptionApplication
        self.animals_model: Type[AdoptionAnimal] = AdoptionAnimal

    async def add_application(
        self, session: Session, application: AdoptionApplication
    ) -> None:
        session.add(application)
        await session.flush([application])

    async def get_application_by_id(
        self, session: Session, entity_id: str
    ) -> AdoptionApplication | None:
        query = select(self.model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_application_by_animal_id(
        self, session: Session, adoption_animal_id: str
    ) -> AdoptionApplication | None:
        query = select(self.model).where(
            self.model.animal_id == adoption_animal_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_received_applications_by_animal_id(
        self,
        session: Session,
        adoption_animal_id: str,
    ) -> Sequence[AdoptionApplication]:
        query = (
            select(self.model)
            .where(
                self.model.animal_id == adoption_animal_id,  # type: ignore
            )
            .order_by(self.model.application_date)  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().all()

    async def get_received_applications_by_personal_profile(
        self,
        session: Session,
        profile_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        query = (
            select(self.model)
            .select_from(
                join(self.model, self.animals_model, self.animals_model.entity_id == self.model.animal_id)  # type: ignore
            )
            .where(
                self.animals_model.profile_id == profile_id,  # type: ignore
            )
            .order_by(self.model.application_date)  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_received_applications_by_personal_profile(
        self,
        session: Session,
        profile_id: str,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(
                join(self.model, self.animals_model, self.animals_model.entity_id == self.model.animal_id)  # type: ignore
            )
            .where(
                self.animals_model.profile_id == profile_id,  # type: ignore
            )
        )

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_received_applications_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        query = (
            select(self.model)
            .select_from(
                join(self.model, self.animals_model, self.animals_model.entity_id == self.model.animal_id)  # type: ignore
            )
            .where(
                self.animals_model.organization_id == organization_id,  # type: ignore
            )
            .order_by(self.model.application_date)  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_received_applications_by_organizational_profile(
        self,
        session: Session,
        organization_id: str,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(
                join(self.model, self.animals_model, self.animals_model.entity_id == self.model.animal_id)  # type: ignore
            )
            .where(
                self.animals_model.organization_id == organization_id,  # type: ignore
            )
        )

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_sent_applications(
        self,
        session: Session,
        profile_id: str,
        limit: int | None = None,
        offset: int | None = 0,
    ) -> Sequence[AdoptionApplication]:
        query = (
            select(self.model)
            .where(
                self.model.adopter_profile_id == profile_id,  # type: ignore
            )
            .order_by(self.model.application_date)  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    async def count_sent_applications(
        self,
        session: Session,
        profile_id: str,
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(self.model)
            .where(
                self.model.adopter_profile_id == profile_id,  # type: ignore
            )
        )

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def delete_applications(
        self, session: Session, application: AdoptionApplication
    ) -> None:
        await session.delete(application)
        await session.flush([application])
