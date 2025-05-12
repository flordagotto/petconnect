from dataclasses import dataclass
from datetime import datetime
from typing import Sequence
from uuid import uuid4

from bounded_contexts.pets_domain.entities import PetSight, Pet
from bounded_contexts.pets_domain.events import PetSightingEvent
from bounded_contexts.pets_domain.exceptions import SightForNotLostPetException
from bounded_contexts.pets_domain.exceptions.pet_sight_not_found_exception import (
    PetSightNotFoundException,
)
from bounded_contexts.pets_domain.repositories import PetsSightRepository
from infrastructure.date_utils import datetime_now_tz, float_timestamp
from infrastructure.uow_abstraction import UnitOfWork


@dataclass
class PetSightData:
    entity_id: str
    pet_id: str
    latitude: float
    longitude: float
    account_id: str
    created_at: datetime


class PetSightService:
    def __init__(self, pets_sight_repository: PetsSightRepository) -> None:
        self.pets_sight_repository = pets_sight_repository

    async def create_pet_sight(
        self,
        uow: UnitOfWork,
        pet: Pet,
        latitude: float,
        longitude: float,
        account_id: str | None,
    ) -> PetSight:
        self.__assert_pet_is_lost(pet)

        pet_sight: PetSight = PetSight(
            entity_id=uuid4().hex,
            pet_id=pet.entity_id,
            latitude=latitude,
            longitude=longitude,
            account_id=account_id,
            created_at=datetime_now_tz(),
        )

        is_first_sight = await self.is_first_pet_sight(uow=uow, pet_id=pet.entity_id)

        await self.pets_sight_repository.add_pet_sight(
            session=uow.session, pet_sight=pet_sight
        )

        if not is_first_sight:
            self.__issue_pet_sight_event(
                uow=uow,
                pet=pet,
            )

        return pet_sight

    async def get_pet_sight_by_id(self, uow: UnitOfWork, entity_id: str) -> PetSight:
        pet_sight: PetSight | None = (
            await self.pets_sight_repository.get_pet_sight_by_id(
                session=uow.session, entity_id=entity_id
            )
        )

        if not pet_sight:
            raise PetSightNotFoundException(entity_id=entity_id)

        return pet_sight

    async def get_all_pet_sights(
        self,
        uow: UnitOfWork,
        limit: int | None = None,
        offset: int | None = 0,
        pet_id: str | None = None,
        lost: bool | None = None,
    ) -> Sequence[PetSight]:
        pet_sights: Sequence[
            PetSight
        ] = await self.pets_sight_repository.get_pet_sights(
            session=uow.session, limit=limit, offset=offset, pet_id=pet_id, lost=lost
        )

        return pet_sights

    async def get_all_pet_sights_count(
        self, uow: UnitOfWork, pet_id: str | None = None, lost: bool | None = None
    ) -> int:
        return await self.pets_sight_repository.count_pet_sights(
            session=uow.session, pet_id=pet_id, lost=lost
        )

    async def get_most_recent_lost_pet_sights(
        self, uow: UnitOfWork, limit: int | None = None, offset: int | None = 0
    ) -> Sequence[PetSight]:
        pet_sights: Sequence[
            PetSight
        ] = await self.pets_sight_repository.get_most_recent_lost_pet_sights(
            session=uow.session, limit=limit, offset=offset
        )

        return pet_sights

    async def get_most_recent_lost_pet_sights_count(self, uow: UnitOfWork) -> int:
        return await self.pets_sight_repository.count_most_recent_lost_pet_sights(
            session=uow.session
        )

    async def delete_pet_sights(
        self, uow: UnitOfWork, pet_sights: Sequence[PetSight]
    ) -> None:
        await self.pets_sight_repository.delete(
            session=uow.session, pet_sights=pet_sights
        )

    async def is_first_pet_sight(self, uow: UnitOfWork, pet_id: str) -> bool:
        pet_sights: Sequence[
            PetSight
        ] = await self.pets_sight_repository.get_pet_sights(
            session=uow.session, pet_id=pet_id, lost=True
        )

        return len(pet_sights) == 0

    @staticmethod
    def __assert_pet_is_lost(pet: Pet) -> None:
        if not pet.lost:
            raise SightForNotLostPetException(pet_id=pet.entity_id)

    @staticmethod
    def __issue_pet_sight_event(uow: UnitOfWork, pet: Pet) -> None:
        uow.emit_event(
            PetSightingEvent(
                issued=float_timestamp(),
                pet_id=pet.entity_id,
            )
        )
