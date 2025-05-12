from datetime import datetime
from typing import Sequence

from pydantic import BaseModel
from bounded_contexts.pets_domain.entities import PetSight


class PetSightView(BaseModel):
    entity_id: str
    pet_id: str
    latitude: float
    longitude: float
    account_id: str | None
    created_at: datetime


class PetSightListView(BaseModel):
    items: Sequence[PetSightView]
    total_count: int


class PetSightViewFactory:
    @staticmethod
    def create_pet_sight_view(pet_sight: PetSight) -> PetSightView:
        return PetSightView(
            entity_id=pet_sight.entity_id,
            pet_id=pet_sight.pet_id,
            latitude=pet_sight.latitude,
            longitude=pet_sight.longitude,
            account_id=pet_sight.account_id,
            created_at=pet_sight.created_at,
        )

    @staticmethod
    def create_pet_sight_list_view(
        pet_sights: Sequence[PetSight], total_count: int
    ) -> PetSightListView:
        pet_sights_list_view: list[PetSightView] = []

        for pet_sight in pet_sights:
            pet_sights_list_view.append(
                PetSightViewFactory.create_pet_sight_view(pet_sight=pet_sight)
            )
        return PetSightListView(items=pet_sights_list_view, total_count=total_count)
